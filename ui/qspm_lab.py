"""
ui/qspm_lab.py

QSPM Strategic Evaluation UI.
Evaluates the current DecisionPlan against the locked baseline.
"""

from __future__ import annotations

import streamlit as st
from typing import Any, Dict

from core.decision_evaluator import DecisionEvaluator
from core.decision_plan import DecisionPlan
from core.models import CompanyState
from tools.qspm import build_strategy_assessment


# =========================================================
# FORMATTING HELPERS
# =========================================================

def _money(value: float) -> str:
    return f"€{value:,.0f}"


def _pct(value: float) -> str:
    return f"{value * 100:.1f}%"


def _delta_money(value: float) -> str:
    if value > 0:
        return f"+€{value:,.0f}"
    if value < 0:
        return f"-€{abs(value):,.0f}"
    return "€0"


def _delta_pct(value: float) -> str:
    if value > 0:
        return f"+{value * 100:.1f} pp"
    if value < 0:
        return f"{value * 100:.1f} pp"
    return "0.0 pp"


# =========================================================
# MAIN UI
# =========================================================

def render_qspm_lab(
    baseline_state: CompanyState,
    decision_plan: DecisionPlan,
) -> None:

    st.markdown("## 🧠 QSPM — Strategic Evaluation")
    st.caption("Evaluate the current Decision Plan against the locked company baseline.")

    # -----------------------------------------------------
    # EMPTY PLAN CHECK
    # -----------------------------------------------------
    is_empty_plan = getattr(decision_plan, "is_empty", False)
    if is_empty_plan:
        st.info("🎯 No decisions are currently selected. QSPM will evaluate the locked baseline.")

    # -----------------------------------------------------
    # PLAN HEADER
    # -----------------------------------------------------
    st.markdown("### 🎯 Current Strategy")
    plan_summary = (
        decision_plan.summary()
        if hasattr(decision_plan, "summary")
        else f"Plan: {getattr(decision_plan, 'name', 'Default Strategy')}"
    )
    st.info(plan_summary)

    # -----------------------------------------------------
    # EVALUATION ENGINE PIPELINE
    # -----------------------------------------------------
    try:
        evaluation = DecisionEvaluator.evaluate(
            baseline_state=baseline_state,
            plan=decision_plan,
        )
    except Exception as exc:
        st.error(f"Unable to evaluate the current Decision Plan: {exc}")
        return

    # Extract scenario sequence safely to feed into build_strategy_assessment
    decisions = getattr(decision_plan, "decisions", [])
    if not decisions and hasattr(decision_plan, "decision_count"):
        count = getattr(decision_plan, "decision_count", 0)
        decisions = [None] * count

    # -----------------------------------------------------
    # QSPM CALCULATIONS
    # -----------------------------------------------------
    plan_name = getattr(decision_plan, "name", "Current Decision Plan")

    result: Dict[str, Any] = build_strategy_assessment(
        strategy_type=plan_name,
        financial_projection=evaluation.financial_projection,
        scenarios=decisions,
    )

    overall_score = result.get("overall_score", 0.0)
    dim_scores = result.get("dimension_scores", {})
    impact = result.get("financial_impact", {})
    verdict = result.get("verdict", "N/A")

    # -----------------------------------------------------
    # OVERALL SCORE DISPLAY
    # -----------------------------------------------------
    st.markdown("### ⭐ Strategic Score")
    score_col1, score_col2 = st.columns([0.3, 0.7], gap="large")

    with score_col1:
        st.metric(
            label="Overall QSPM Score",
            value=f"{overall_score:.2f} / 5.00",
            delta=verdict,
        )

    with score_col2:
        st.caption(
            "The score summarizes the strategic quality of the projected state "
            "across profitability, liquidity, capital intensity, execution complexity, and risk control."
        )

    # -----------------------------------------------------
    # SCORE BREAKDOWN BY DIMENSION
    # -----------------------------------------------------
    st.markdown("### 📊 Score Breakdown")
    if dim_scores:
        score_cols = st.columns(len(dim_scores))
        labels_map = {
            "profitability": "Profitability",
            "liquidity": "Liquidity",
            "capital_intensity": "Cap. Intensity",
            "execution_complexity": "Execution",
            "risk": "Risk Control",
        }

        for column, (key, score) in zip(score_cols, dim_scores.items()):
            with column:
                st.metric(
                    label=labels_map.get(key, key.replace("_", " ").title()),
                    value=f"{score} / 5",
                )

    # -----------------------------------------------------
    # BEFORE / AFTER METRIC TABLE
    # -----------------------------------------------------
    st.markdown("### 🔄 Company Impact — Before vs After")

    base_rev = impact.get("baseline_revenue", 0.0)
    proj_rev = impact.get("projected_revenue", 0.0)
    rev_delta = impact.get("revenue_delta", proj_rev - base_rev)

    base_ebit = impact.get("baseline_ebit", 0.0)
    proj_ebit = impact.get("projected_ebit", 0.0)

    base_margin = impact.get("baseline_ebit_margin", 0.0)
    proj_margin = impact.get("projected_ebit_margin", 0.0)
    margin_delta = impact.get("margin_change", proj_margin - base_margin)

    base_np = impact.get("baseline_net_profit", 0.0)
    proj_np = impact.get("projected_net_profit", 0.0)
    np_delta = impact.get("net_profit_delta", proj_np - base_np)

    nwc_change = impact.get("nwc_change", 0.0)

    base_fcfe = impact.get("baseline_fcfe", 0.0)
    proj_fcfe = impact.get("projected_fcfe", 0.0)
    fcfe_delta = impact.get("fcfe_delta", proj_fcfe - base_fcfe)

    rows = [
        ("Revenue", _money(base_rev), _money(proj_rev), _delta_money(rev_delta)),
        ("EBIT", _money(base_ebit), _money(proj_ebit), _delta_money(proj_ebit - base_ebit)),
        ("EBIT Margin", _pct(base_margin), _pct(proj_margin), _delta_pct(margin_delta)),
        ("Net Profit", _money(base_np), _money(proj_np), _delta_money(np_delta)),
        ("Working Capital Shift", "€0", _money(nwc_change), _delta_money(nwc_change)),
        ("FCFE", _money(base_fcfe), _money(proj_fcfe), _delta_money(fcfe_delta)),
    ]

    st.table(
        {
            "Metric": [r[0] for r in rows],
            "Locked Baseline": [r[1] for r in rows],
            "Projected State": [r[2] for r in rows],
            "Impact / Delta": [r[3] for r in rows],
        }
    )

    # -----------------------------------------------------
    # STRATEGIC FLAGS & READOUT
    # -----------------------------------------------------
    st.markdown("### 🔎 Strategic Readout")
    flags = []

    if fcfe_delta < 0:
        flags.append((False, f"Free Cash Flow to Equity deteriorates by {_money(abs(fcfe_delta))}."))
    elif fcfe_delta > 0:
        flags.append((True, f"Free Cash Flow to Equity improves by {_money(fcfe_delta)}."))

    if margin_delta < -0.005:
        flags.append((False, f"EBIT Margin contracts by {_delta_pct(margin_delta)}."))
    elif margin_delta > 0.005:
        flags.append((True, f"EBIT Margin expands by {_delta_pct(margin_delta)}."))

    if nwc_change > 25_000:
        flags.append((False, f"Significant Working Capital absorption: {_money(nwc_change)} tied up in operations."))

    if not flags:
        st.info("No critical strategic flags triggered.")
    else:
        for is_positive, msg in flags:
            if is_positive:
                st.success(f"✓ {msg}")
            else:
                st.warning(f"⚠️ {msg}")

    # -----------------------------------------------------
    # VERDICT & INTERPRETATION
    # -----------------------------------------------------
    st.markdown("### 🧭 Interpretation")

    if overall_score >= 4.0:
        st.success("The current Decision Plan produces a strategically robust outcome across key financial dimensions.")
    elif overall_score >= 3.0:
        st.info("The current Decision Plan produces a balanced outcome with acceptable trade-offs.")
    else:
        st.warning("The current Decision Plan introduces structural risks or margin compression. Review recommended.")

    st.caption(
        "QSPM is read-only. It evaluates the projected CompanyState "
        "generated by DecisionEvaluator without altering the locked baseline."
    )
