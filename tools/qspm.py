"""
tools/qspm.py

QSPM Strategic Evaluation Tool.

Evaluates a DecisionPlan through the canonical
FinancialProjection produced by DecisionEvaluator
and FinancialEngine.

Architecture:

    CompanyState
        +
    DecisionPlan
        ↓
    DecisionEvaluator
        ↓
    FinancialProjection
        ↓
    QSPM

QSPM is read-only.
It does not create Decisions.
It does not modify CompanyState.
It does not recalculate financial statements.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional


# =========================================================
# BASIC HELPERS
# =========================================================

def _safe_float(obj: Any, attr: str, default: float = 0.0) -> float:
    """Safely fetch a float attribute from an object or dictionary."""
    if isinstance(obj, dict):
        val = obj.get(attr, default)
    else:
        val = getattr(obj, attr, default)
    
    if val is None:
        return default
    try:
        return float(val)
    except (ValueError, TypeError):
        return default


def _growth(base: float, projected: float) -> float:
    """
    Percentage growth from baseline to projected.
    Uses absolute baseline as denominator so the function
    remains stable when the baseline is negative.
    """
    if base == 0.0:
        if projected > 0.0:
            return 1.0  # 100% growth equivalent if moving from 0 to positive
        elif projected < 0.0:
            return -1.0
        return 0.0

    return (projected - base) / abs(base)


def _margin(profit: float, revenue: float) -> float:
    """
    Profit margin calculation with zero-division safety.
    """
    if revenue == 0.0:
        return 0.0

    return profit / revenue


# =========================================================
# SCORE FUNCTIONS
# =========================================================

def _profitability_score(growth: float) -> int:
    """
    Score profitability improvement.
    1 = strongly negative, 3 = neutral, 5 = strong improvement
    """
    if growth >= 0.15:
        return 5
    if growth > 0.0:
        return 4
    if growth == 0.0:
        return 3
    if growth > -0.10:
        return 2
    return 1


def _liquidity_score(fcfe_delta: float) -> int:
    """
    Score liquidity / shareholder cash impact.
    """
    if fcfe_delta > 20_000:
        return 5
    if fcfe_delta > 0:
        return 4
    if fcfe_delta == 0:
        return 3
    if fcfe_delta > -20_000:
        return 2
    return 1


def _execution_complexity_score(decision_count: int) -> int:
    """
    Score implementation complexity based on number of decisions.
    Fewer decisions imply lower coordination requirements.
    """
    if decision_count <= 1:
        return 5
    if decision_count <= 3:
        return 3
    return 2


def _capital_intensity_score(nwc_change: float) -> int:
    """
    Score capital intensity based on NWC commitment.
    Lower additional working capital requirements score higher.
    """
    if nwc_change <= 0:  # Released cash or neutral
        return 5
    if nwc_change <= 15_000:
        return 4
    if nwc_change <= 50_000:
        return 3
    return 2


def _risk_score(
    baseline_margin: float,
    projected_margin: float,
    fcfe_delta: float,
) -> int:
    """
    Combined risk score based on margin movement and FCFE stability.
    """
    margin_change = projected_margin - baseline_margin

    if margin_change > 0 and fcfe_delta >= 0:
        return 5
    if margin_change >= 0 or fcfe_delta >= 0:
        return 4
    if margin_change > -0.05 and fcfe_delta > -20_000:
        return 3
    if margin_change > -0.10:
        return 2
    return 1


# =========================================================
# MAIN QSPM ASSESSMENT
# =========================================================

def build_strategy_assessment(
    strategy_type: str,
    financial_projection: Any,
    scenarios: Optional[List[Any]] = None,
) -> Dict[str, Any]:
    """
    Evaluate a strategy from the canonical FinancialEngine.FinancialProjection.
    """

    if financial_projection is None:
        raise ValueError("financial_projection is required.")

    scenarios = scenarios or []

    # =====================================================
    # CANONICAL FINANCIAL PROJECTION
    # =====================================================

    baseline = getattr(financial_projection, "baseline", None)
    projected = getattr(financial_projection, "projected", None)
    impact = getattr(financial_projection, "impact", None)

    if baseline is None or projected is None or impact is None:
        raise ValueError("Invalid financial_projection structure. Missing baseline, projected, or impact.")

    # =====================================================
    # INCOME STATEMENTS & ATTRIBUTE EXTRACTION
    # =====================================================

    base_is = getattr(baseline, "income_statement", baseline)
    proj_is = getattr(projected, "income_statement", projected)

    baseline_ebit = _safe_float(base_is, "ebit")
    projected_ebit = _safe_float(proj_is, "ebit")

    baseline_revenue = _safe_float(base_is, "revenue")
    projected_revenue = _safe_float(proj_is, "revenue")

    baseline_margin = _margin(baseline_ebit, baseline_revenue)
    projected_margin = _margin(projected_ebit, projected_revenue)

    ebit_growth = _growth(baseline_ebit, projected_ebit)

    # =====================================================
    # FCFE & WORKING CAPITAL (WITH SAFE FALLBACKS)
    # =====================================================

    # FCFE can be on FinancialStatements or CashFlowStatement
    base_cfs = getattr(baseline, "cash_flow_statement", baseline)
    proj_cfs = getattr(projected, "cash_flow_statement", projected)

    baseline_fcfe = _safe_float(base_cfs, "fcfe", _safe_float(baseline, "fcfe", 0.0))
    projected_fcfe = _safe_float(proj_cfs, "fcfe", _safe_float(projected, "fcfe", 0.0))
    fcfe_delta = _safe_float(impact, "fcfe_delta", projected_fcfe - baseline_fcfe)

    # Working capital extraction
    base_nwc_obj = getattr(baseline, "working_capital", None)
    proj_nwc_obj = getattr(projected, "working_capital", None)

    base_nwc = _safe_float(base_nwc_obj, "nwc", 0.0) if base_nwc_obj else 0.0
    proj_nwc = _safe_float(proj_nwc_obj, "nwc", 0.0) if proj_nwc_obj else 0.0
    nwc_change = proj_nwc - base_nwc

    # =====================================================
    # DIMENSION SCORES
    # =====================================================

    profitability_score = _profitability_score(ebit_growth)
    liquidity_score = _liquidity_score(fcfe_delta)
    decision_count = len(scenarios)

    capital_intensity_score = _capital_intensity_score(nwc_change)
    execution_complexity_score = _execution_complexity_score(decision_count)

    risk_score = _risk_score(
        baseline_margin,
        projected_margin,
        fcfe_delta,
    )

    scores = [
        profitability_score,
        liquidity_score,
        capital_intensity_score,
        execution_complexity_score,
        risk_score,
    ]

    # =====================================================
    # OVERALL SCORE & VERDICT
    # =====================================================

    overall_score = sum(scores) / len(scores)

    if overall_score >= 4.5:
        verdict = "Strong"
    elif overall_score >= 3.5:
        verdict = "Favorable"
    elif overall_score >= 2.5:
        verdict = "Mixed"
    elif overall_score >= 1.5:
        verdict = "Weak"
    else:
        verdict = "Unfavorable"

    # =====================================================
    # RETURN RESULT DICT
    # =====================================================

    return {
        "strategy_type": strategy_type,
        "scenario_count": decision_count,
        "overall_score": round(overall_score, 2),
        "verdict": verdict,
        "scores": scores,
        "dimension_scores": {
            "profitability": profitability_score,
            "liquidity": liquidity_score,
            "capital_intensity": capital_intensity_score,
            "execution_complexity": execution_complexity_score,
            "risk": risk_score,
        },
        "financial_impact": {
            "baseline_revenue": baseline_revenue,
            "projected_revenue": projected_revenue,
            "revenue_delta": _safe_float(impact, "revenue_delta", projected_revenue - baseline_revenue),
            "revenue_growth": _growth(baseline_revenue, projected_revenue),
            "price_effect": _safe_float(impact, "price_effect", 0.0),
            "volume_effect": _safe_float(impact, "volume_effect", 0.0),
            "baseline_ebit": baseline_ebit,
            "projected_ebit": projected_ebit,
            "ebit_growth": ebit_growth,
            "ebitda_delta": _safe_float(impact, "ebitda_delta", 0.0),
            "gross_profit_delta": _safe_float(impact, "gross_profit_delta", 0.0),
            "baseline_net_profit": _safe_float(base_is, "net_profit", 0.0),
            "projected_net_profit": _safe_float(proj_is, "net_profit", 0.0),
            "net_profit_delta": _safe_float(impact, "net_profit_delta", 0.0),
            "baseline_ebit_margin": baseline_margin,
            "projected_ebit_margin": projected_margin,
            "margin_change": projected_margin - baseline_margin,
            "baseline_fcfe": baseline_fcfe,
            "projected_fcfe": projected_fcfe,
            "fcfe_delta": fcfe_delta,
            "nwc_change": nwc_change,
            "nwc_cash_impact_delta": _safe_float(impact, "nwc_cash_impact_delta", 0.0),
        },
    }


# =========================================================
# CONVENIENCE API
# =========================================================

def build_strategy_assessment_from_evaluation(
    strategy_type: str,
    evaluation: Any,
    scenarios: Optional[List[Any]] = None,
) -> Dict[str, Any]:
    """
    Convenience wrapper for DecisionEvaluation.
    Expected object: DecisionEvaluation.financial_projection
    """
    projection = getattr(evaluation, "financial_projection", None)

    if projection is None:
        raise ValueError("Evaluation has no financial_projection.")

    return build_strategy_assessment(
        strategy_type=strategy_type,
        financial_projection=projection,
        scenarios=scenarios,
    )
