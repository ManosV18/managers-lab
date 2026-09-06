import streamlit as st

from core.decision_plan import DecisionPlan
# Εισαγωγή του engine υπολογισμού υγείας/fragility από το domain/diagnostics layer
from diagnostics.cash_fragility import calculate_cash_fragility


# =========================================================
# FORMATTING
# =========================================================

def _fmt_eur(
    value: float,
    decimals: int = 0,
) -> str:
    value = float(value)
    if decimals == 0:
        return f"€ {value:,.0f}"
    return f"€ {value:,.{decimals}f}"


def _fmt_signed_eur(
    value: float,
    decimals: int = 0,
) -> str:
    value = float(value)
    if value > 0:
        return f"+€ {value:,.{decimals}f}"
    if value < 0:
        return f"-€ {abs(value):,.{decimals}f}"
    return f"€ {0:,.{decimals}f}"


def _fmt_rate(
    value: float,
) -> str:
    return f"{float(value) * 100.0:.2f}%"


def _margin(
    value: float,
    revenue: float,
) -> float:
    if revenue == 0:
        return 0.0
    return (
        float(value)
        / float(revenue)
        * 100.0
    )


# =========================================================
# DECISION PLAN
# =========================================================

def _get_decision_plan():
    plan = st.session_state.get("decision_plan")
    if isinstance(plan, DecisionPlan):
        if not plan.is_empty:
            return plan
    return None


# =========================================================
# DECISION DETECTION
# =========================================================

def _has_wacc_decision(decision_plan) -> bool:
    if decision_plan is None:
        return False

    for decision in decision_plan.decisions:
        changes = getattr(decision, "changes", {})
        if "wacc" in changes:
            return True

        category = str(getattr(decision, "category", "")).lower()
        name = str(getattr(decision, "name", "")).lower()

        if "capital_structure" in category and "wacc" in name:
            return True
        if "capital" in category and "wacc" in name:
            return True

    return False


def _has_working_capital_decision(decision_plan) -> bool:
    if decision_plan is None:
        return False

    wc_keys = (
        "ar_days",
        "ar_days_delta",
        "inventory_days",
        "inventory_days_delta",
        "ap_days",
        "ap_days_delta",
    )

    return any(
        any(key in getattr(decision, "changes", {}) for key in wc_keys)
        for decision in decision_plan.decisions
    )


def _has_operational_decision(decision_plan) -> bool:
    if decision_plan is None:
        return False

    operational_keys = (
        "price",
        "price_pct",
        "volume",
        "volume_pct",
        "variable_cost_per_unit",
        "variable_cost_per_unit_pct",
        "fixed_opex",
        "fixed_opex_pct",
        "depreciation",
        "depreciation_pct",
    )

    return any(
        any(key in getattr(decision, "changes", {}) for key in operational_keys)
        for decision in decision_plan.decisions
    )


# =========================================================
# PLAN CLASSIFICATION
# =========================================================

def _classify_decision_plan(
    baseline_state,
    projected_state,
    financial_impact,
    decision_plan,
):
    if decision_plan is None:
        return "baseline"

    revenue_delta = float(financial_impact.revenue_delta)
    ebitda_delta = float(financial_impact.ebitda_delta)
    net_profit_delta = float(financial_impact.net_profit_delta)
    fcfe_delta = float(financial_impact.fcfe_delta)
    nwc_cash_impact = float(financial_impact.nwc_cash_impact_delta)

    baseline_wacc = float(baseline_state.capital_structure.wacc)
    projected_wacc = float(projected_state.capital_structure.wacc)
    wacc_delta = projected_wacc - baseline_wacc

    wacc_present = _has_wacc_decision(decision_plan)
    operational_present = _has_operational_decision(decision_plan)
    wc_present = _has_working_capital_decision(decision_plan)

    capital_cost_negative = wacc_present and wacc_delta > 1e-9
    capital_cost_positive = wacc_present and wacc_delta < -1e-9

    operating_positive = (
        revenue_delta > 1e-9
        or ebitda_delta > 1e-9
        or net_profit_delta > 1e-9
        or fcfe_delta > 1e-9
        or nwc_cash_impact > 1e-9
    )

    operating_negative = (
        revenue_delta < -1e-9
        and ebitda_delta < -1e-9
        and net_profit_delta < -1e-9
        and fcfe_delta < -1e-9
    )

    if wacc_present and not operational_present and not wc_present:
        if capital_cost_negative:
            return "capital_negative"
        if capital_cost_positive:
            return "capital_positive"
        return "capital_neutral"

    no_financial_change = (
        abs(revenue_delta) < 1e-9
        and abs(ebitda_delta) < 1e-9
        and abs(net_profit_delta) < 1e-9
        and abs(fcfe_delta) < 1e-9
        and abs(nwc_cash_impact) < 1e-9
    )

    if no_financial_change:
        if capital_cost_negative:
            return "mixed"
        if capital_cost_positive:
            return "capital_positive"
        return "neutral"

    if capital_cost_negative and operating_positive:
        return "mixed"

    if capital_cost_positive and operating_negative:
        return "mixed"

    if operating_negative:
        return "negative"

    if operating_positive:
        return "positive"

    return "mixed"


# =========================================================
# EXECUTIVE DECISION
# =========================================================

def _render_executive_decision(
    baseline_state,
    projected_state,
    baseline_fin,
    projected_fin,
    financial_impact,
    decision_plan,
):
    p = projected_fin.income_statement

    revenue_delta = float(financial_impact.revenue_delta)
    ebitda_delta = float(financial_impact.ebitda_delta)
    net_profit_delta = float(financial_impact.net_profit_delta)
    fcfe_delta = float(financial_impact.fcfe_delta)
    wc_cash_impact = float(financial_impact.nwc_cash_impact_delta)

    status = _classify_decision_plan(
        baseline_state=baseline_state,
        projected_state=projected_state,
        financial_impact=financial_impact,
        decision_plan=decision_plan,
    )

    if status == "baseline":
        st.info("🔵 BASELINE VIEW — No Decision Plan is currently selected. Projected financials equal the locked baseline.")
    elif status == "capital_negative":
        st.warning(f"🟠 CAPITAL COST INCREASE — '{decision_plan.name}' increases the company's cost of capital / valuation hurdle rate.")
    elif status == "capital_positive":
        st.success(f"🟢 CAPITAL COST IMPROVEMENT — '{decision_plan.name}' decreases the company's cost of capital / valuation hurdle rate.")
    elif status == "positive":
        st.success(f"🟢 POSITIVE FINANCIAL IMPACT — '{decision_plan.name}' improves the company's operating and/or cash-flow position.")
    elif status == "negative":
        st.error(f"🔴 NEGATIVE FINANCIAL IMPACT — '{decision_plan.name}' deteriorates the company's operating and cash-flow position.")
    elif status == "mixed":
        st.warning(f"🟡 MIXED FINANCIAL IMPACT — '{decision_plan.name}' improves operating performance and/or cash flow, while another financial layer moves in the opposite direction.")
    else:
        st.info(f"⚪ NEUTRAL DECISION PLAN — '{decision_plan.name}' has no material incremental financial effect.")

    if decision_plan is not None:
        st.markdown(
            f"### 🎯 Selected Business Decision Plan\n\n"
            f"**{decision_plan.name}**\n\n"
            f"**{decision_plan.decision_count} decisions** are being evaluated together against the locked baseline."
        )

        plan_rows = [
            {
                "Order": position,
                "Decision": plan_decision.name,
                "Category": plan_decision.category,
                "ID": plan_decision.id,
            }
            for position, plan_decision in enumerate(decision_plan.decisions, start=1)
        ]

        st.dataframe(
            plan_rows,
            use_container_width=True,
            hide_index=True,
        )

    st.subheader("🧭 Management Summary")
    c1, c2, c3, c4 = st.columns(4)

    c1.metric("Revenue", _fmt_eur(p.revenue), _fmt_signed_eur(revenue_delta))
    c2.metric("EBITDA", _fmt_eur(p.ebitda), _fmt_signed_eur(ebitda_delta))
    c3.metric("Net Profit", _fmt_eur(projected_state.net_profit), _fmt_signed_eur(net_profit_delta))
    c4.metric("FCFE", _fmt_eur(projected_fin.fcfe), _fmt_signed_eur(fcfe_delta))

    if wc_cash_impact < 0:
        st.warning(f"💧 Working capital absorbs {_fmt_eur(abs(wc_cash_impact))} of additional cash.")
    elif wc_cash_impact > 0:
        st.success(f"💧 Working capital releases {_fmt_eur(wc_cash_impact)} of cash.")
    else:
        st.info("💧 Working capital has no incremental cash impact.")


# =========================================================
# CAPITAL COST / VALUATION
# =========================================================

def _render_capital_cost(
    baseline_state,
    projected_state,
    decision_plan,
):
    baseline_capital = baseline_state.capital_structure
    projected_capital = projected_state.capital_structure

    baseline_wacc = float(baseline_capital.wacc)
    projected_wacc = float(projected_capital.wacc)
    wacc_delta_pp = (projected_wacc - baseline_wacc) * 100.0

    wacc_decision = _has_wacc_decision(decision_plan)

    st.subheader("🏦 Capital Cost / Valuation")

    c1, c2, c3 = st.columns(3)
    c1.metric("Baseline WACC", _fmt_rate(baseline_wacc))
    c2.metric("Projected WACC", _fmt_rate(projected_wacc), f"{wacc_delta_pp:+.2f} pp", delta_color="inverse")
    c3.metric("WACC Decision", "Applied" if wacc_decision else "None")

    if not wacc_decision:
        st.caption("No WACC decision is included in the current Decision Plan.")
        return

    if wacc_delta_pp < -1e-9:
        st.success(f"📉 Capital efficiency improved: WACC decreased from {_fmt_rate(baseline_wacc)} to {_fmt_rate(projected_wacc)}.")
    elif wacc_delta_pp > 1e-9:
        st.warning(f"📈 Capital cost increased: WACC increased from {_fmt_rate(baseline_wacc)} to {_fmt_rate(projected_wacc)}.")
    else:
        st.info("WACC decision is present, but the projected WACC is unchanged versus baseline.")

    st.caption(
        "WACC is treated exclusively as a capital-cost / valuation driver. "
        "It does not directly change Net Profit, Interest Expense or FCFE in FinancialEngine v1."
    )


# =========================================================
# VALUATION IMPACT
# =========================================================

def _render_valuation_impact(
    baseline_state,
    projected_state,
    decision_plan,
):
    if decision_plan is None or not _has_wacc_decision(decision_plan):
        return

    baseline_wacc = float(baseline_state.capital_structure.wacc)
    projected_wacc = float(projected_state.capital_structure.wacc)
    delta_wacc = projected_wacc - baseline_wacc

    st.subheader("📉 Valuation Impact")

    c1, c2, c3 = st.columns(3)
    c1.metric("Baseline Discount Rate", _fmt_rate(baseline_wacc))
    c2.metric("Projected Discount Rate", _fmt_rate(projected_wacc), f"{delta_wacc * 100.0:+.2f} pp", delta_color="inverse")

    if delta_wacc > 1e-9:
        valuation_signal = "Negative"
        c3.metric("Valuation Signal", "🔴 Downward")
        st.error("🔴 Higher WACC increases the discount rate applied to future FCFF and therefore creates downward pressure on Enterprise Value, all else equal.")
    elif delta_wacc < -1e-9:
        valuation_signal = "Positive"
        c3.metric("Valuation Signal", "🟢 Upward")
        st.success("🟢 Lower WACC reduces the discount rate applied to future FCFF and therefore creates upward pressure on Enterprise Value, all else equal.")
    else:
        valuation_signal = "Neutral"
        c3.metric("Valuation Signal", "⚪ Neutral")
        st.info("WACC is unchanged; there is no incremental valuation signal from the discount-rate layer.")

    st.markdown("#### Valuation Interpretation")
    if valuation_signal == "Negative":
        st.write("The Decision Plan improves the company's operating and/or cash-flow metrics, but the higher WACC makes future cash flows less valuable in a DCF framework.")
    elif valuation_signal == "Positive":
        st.write("The Decision Plan improves the company's capital efficiency because the lower WACC reduces the discount rate applied to future FCFF.")
    else:
        st.write("The Decision Plan produces no incremental valuation effect through the WACC layer.")

    st.caption(
        "Important: FinancialEngine v1 does not calculate FCFF, terminal value or Enterprise Value. "
        "Therefore this section intentionally reports the directional valuation effect of the WACC change rather than inventing a € valuation impact."
    )


# =========================================================
# FINANCIAL IMPACT
# =========================================================

def _render_financial_impact(financial_impact):
    st.subheader("📊 Executive Financial Impact")
    c1, c2, c3, c4 = st.columns(4)

    c1.metric("Revenue Δ", _fmt_signed_eur(financial_impact.revenue_delta))
    c2.metric("EBITDA Δ", _fmt_signed_eur(financial_impact.ebitda_delta))
    c3.metric("Net Profit Δ", _fmt_signed_eur(financial_impact.net_profit_delta))
    c4.metric("FCFE Δ", _fmt_signed_eur(financial_impact.fcfe_delta))


# =========================================================
# PROFITABILITY
# =========================================================

def _render_profitability_snapshot(
    baseline_state,
    projected_state,
    projected_fin,
):
    p = projected_fin.income_statement

    st.subheader("📌 Profitability Snapshot")

    baseline_revenue = (
        baseline_state.drivers.price
        * baseline_state.drivers.volume
    )

    projected_revenue = p.revenue

    base_net_margin = _margin(
        baseline_state.net_profit,
        baseline_revenue,
    )

    proj_net_margin = _margin(
        projected_state.net_profit,
        projected_revenue,
    )

    c1, c2 = st.columns(2)

    c1.metric(
        "Baseline Net Margin",
        f"{base_net_margin:.1f}%",
    )

    c2.metric(
        "Projected Net Margin",
        f"{proj_net_margin:.1f}%",
        f"{proj_net_margin - base_net_margin:+.1f} pp",
    )


# =========================================================
# REVENUE BRIDGE
# =========================================================

def _render_revenue_bridge(financial_impact):
    st.subheader("📈 Revenue Bridge")

    price_effect = float(financial_impact.price_effect)
    volume_effect = float(financial_impact.volume_effect)
    revenue_delta = float(financial_impact.revenue_delta)

    c1, c2, c3 = st.columns(3)

    c1.metric("Price Effect", _fmt_signed_eur(price_effect))
    c2.metric("Volume Effect", _fmt_signed_eur(volume_effect))
    c3.metric("Total Revenue Δ", _fmt_signed_eur(revenue_delta))


# =========================================================
# WORKING CAPITAL
# =========================================================

def _render_working_capital(
    baseline_fin,
    projected_fin,
    financial_impact,
):
    st.subheader("💧 Working Capital")

    b = baseline_fin.working_capital
    p = projected_fin.working_capital

    cash_impact = float(financial_impact.nwc_cash_impact_delta)

    c1, c2, c3 = st.columns(3)

    c1.metric("Baseline NWC", _fmt_eur(b.nwc))
    c2.metric("Projected NWC", _fmt_eur(p.nwc))
    c3.metric("Incremental Cash Impact", _fmt_signed_eur(cash_impact))

    rows = [
        {
            "Metric": "Accounts Receivable",
            "Baseline": _fmt_eur(b.ar),
            "Projected": _fmt_eur(p.ar),
            "Δ": _fmt_signed_eur(p.ar - b.ar),
        },
        {
            "Metric": "Inventory",
            "Baseline": _fmt_eur(b.inventory),
            "Projected": _fmt_eur(p.inventory),
            "Δ": _fmt_signed_eur(p.inventory - b.inventory),
        },
        {
            "Metric": "Accounts Payable",
            "Baseline": _fmt_eur(b.ap),
            "Projected": _fmt_eur(p.ap),
            "Δ": _fmt_signed_eur(p.ap - b.ap),
        },
        {
            "Metric": "Net Working Capital (NWC)",
            "Baseline": _fmt_eur(b.nwc),
            "Projected": _fmt_eur(p.nwc),
            "Δ": _fmt_signed_eur(p.nwc - b.nwc),
        },
    ]

    st.dataframe(
        rows,
        use_container_width=True,
        hide_index=True,
    )


# =========================================================
# COMPANY HEALTH DIAGNOSTICS (PRESENTATION LAYER)
# =========================================================

def _render_cash_fragility_diagnostic(
    baseline_state,
    projected_state,
    financial_projection,
):
    st.subheader(
        "🩺 Financial Health & Cash Fragility"
    )

    # -----------------------------------------------------
    # RUN DIAGNOSTIC ENGINE
    # -----------------------------------------------------

    baseline_diag = calculate_cash_fragility(
        baseline_state=baseline_state,
    )

    projected_diag = calculate_cash_fragility(
        baseline_state=baseline_state,
        projected_state=projected_state,
        financial_projection=financial_projection,
    )

    # -----------------------------------------------------
    # DELTAS
    # -----------------------------------------------------

    runway_delta = (
        projected_diag["cash_runway"]
        - baseline_diag["cash_runway"]
    )

    ccc_delta = (
        projected_diag["ccc_days"]
        - baseline_diag["ccc_days"]
    )

    score_delta = (
        projected_diag["fragility_score"]
        - baseline_diag["fragility_score"]
    )

    net_runway_delta = (
        projected_diag["runway_after_cycle"]
        - baseline_diag["runway_after_cycle"]
    )

    # -----------------------------------------------------
    # HEALTH SIGNAL
    # -----------------------------------------------------

    health_improved = (
        ccc_delta < 0
        and (
            net_runway_delta > 0
            or score_delta < 0
            or runway_delta > 0
        )
    )

    health_deteriorated = (
        ccc_delta > 0
        and (
            net_runway_delta < 0
            or score_delta > 0
            or runway_delta < 0
        )
    )

    if health_improved:

        health_signal = "🟢 Improved"

    elif health_deteriorated:

        health_signal = "🔴 Deteriorated"

    else:

        health_signal = "🟡 Mixed / Neutral"

    # -----------------------------------------------------
    # DIAGNOSTIC COMPARISON
    # -----------------------------------------------------

    rows = [
        {
            "Diagnostic Metric": "Cash Runway",
            "Baseline": (
                f'{baseline_diag["cash_runway"]:.1f} days'
            ),
            "Projected": (
                f'{projected_diag["cash_runway"]:.1f} days'
            ),
            "Δ": (
                f"{runway_delta:+.1f} days"
            ),
        },
        {
            "Diagnostic Metric": "Cash Conversion Cycle",
            "Baseline": (
                f'{baseline_diag["ccc_days"]:.1f} days'
            ),
            "Projected": (
                f'{projected_diag["ccc_days"]:.1f} days'
            ),
            "Δ": (
                f"{ccc_delta:+.1f} days"
            ),
        },
        {
            "Diagnostic Metric": "Runway After CCC",
            "Baseline": (
                f'{baseline_diag["runway_after_cycle"]:+.1f} days'
            ),
            "Projected": (
                f'{projected_diag["runway_after_cycle"]:+.1f} days'
            ),
            "Δ": (
                f"{net_runway_delta:+.1f} days"
            ),
        },
        {
            "Diagnostic Metric": "Fragility Score",
            "Baseline": (
                f'{baseline_diag["fragility_score"]:.2f}'
            ),
            "Projected": (
                f'{projected_diag["fragility_score"]:.2f}'
            ),
            "Δ": (
                f"{score_delta:+.2f}"
            ),
        },
        {
            "Diagnostic Metric": "Liquidity Status",
            "Baseline": (
                baseline_diag["status"]
            ),
            "Projected": (
                projected_diag["status"]
            ),
            "Δ": health_signal,
        },
    ]

    st.dataframe(
        rows,
        use_container_width=True,
        hide_index=True,
    )

    # -----------------------------------------------------
    # INTERPRETATION
    # -----------------------------------------------------

    if health_improved:

        st.success(
            "🟢 The company's liquidity health "
            "improves versus the locked baseline."
        )

    elif health_deteriorated:

        st.error(
            "🔴 The company's liquidity health "
            "deteriorates versus the locked baseline."
        )

    else:

        st.warning(
            "🟡 The company's liquidity diagnostics "
            "show a mixed or neutral movement versus baseline."
        )

    # -----------------------------------------------------
    # DETAILED INTERPRETATION
    # -----------------------------------------------------

    with st.expander(
        "🧭 Diagnostic Interpretation",
        expanded=False,
    ):

        st.markdown("**Baseline**")
        st.info(
            baseline_diag["interpretation"]
        )

        st.markdown("**Projected**")
        st.success(
            projected_diag["interpretation"]
        )


# =========================================================
# DECISION DIAGNOSTICS
# =========================================================

def _render_decision_diagnostics(
    baseline_state,
    projected_state,
    baseline_fin,
    projected_fin,
    financial_impact,
    decision_plan,
):
    if decision_plan is None:
        return

    st.subheader("🔍 Decision Impact Diagnostics")

    # =====================================================
    # DRIVER PRESENCE
    # =====================================================

    wacc_present = _has_wacc_decision(
        decision_plan
    )

    wc_present = _has_working_capital_decision(
        decision_plan
    )

    operational_present = _has_operational_decision(
        decision_plan
    )

    # =====================================================
    # WACC
    # =====================================================

    baseline_wacc = float(
        baseline_state.capital_structure.wacc
    )

    projected_wacc = float(
        projected_state.capital_structure.wacc
    )

    wacc_delta_pp = (
        projected_wacc
        - baseline_wacc
    ) * 100.0

    # =====================================================
    # DRIVER LAYER SUMMARY
    # =====================================================

    rows = [
        {
            "Driver Layer": "Operational",
            "Present": (
                "Yes"
                if operational_present
                else "No"
            ),
            "Financial Effect": (
                _fmt_signed_eur(
                    financial_impact.ebitda_delta
                )
                if operational_present
                else "€ 0"
            ),
        },
        {
            "Driver Layer": "Working Capital",
            "Present": (
                "Yes"
                if wc_present
                else "No"
            ),
            "Financial Effect": (
                _fmt_signed_eur(
                    financial_impact.nwc_cash_impact_delta
                )
                if wc_present
                else "€ 0"
            ),
        },
        {
            "Driver Layer": "WACC / Valuation",
            "Present": (
                "Yes"
                if wacc_present
                else "No"
            ),
            "Financial Effect": (
                f"{wacc_delta_pp:+.2f} pp WACC"
                if wacc_present
                else "—"
            ),
        },
    ]

    st.dataframe(
        rows,
        use_container_width=True,
        hide_index=True,
    )

    # =====================================================
    # WORKING CAPITAL BREAKDOWN
    # =====================================================

    if not wc_present:
        return

    st.markdown(
        "#### 💧 Working Capital Driver Breakdown"
    )

    b = baseline_fin.working_capital
    p = projected_fin.working_capital

    # -----------------------------------------------------
    # CASH EFFECT BY COMPONENT
    # -----------------------------------------------------

    ar_cash_effect = (
        b.ar - p.ar
    )

    inventory_cash_effect = (
        b.inventory - p.inventory
    )

    ap_cash_effect = (
        p.ap - b.ap
    )

    total_cash_effect = (
        ar_cash_effect
        + inventory_cash_effect
        + ap_cash_effect
    )

    # =====================================================
    # DRIVER TABLE
    # =====================================================

    wc_rows = [
        {
            "Working Capital Driver": "Accounts Receivable",
            "Baseline": _fmt_eur(b.ar),
            "Projected": _fmt_eur(p.ar),
            "Change": _fmt_signed_eur(
                p.ar - b.ar
            ),
            "Cash Effect": _fmt_signed_eur(
                ar_cash_effect
            ),
        },
        {
            "Working Capital Driver": "Inventory",
            "Baseline": _fmt_eur(b.inventory),
            "Projected": _fmt_eur(p.inventory),
            "Change": _fmt_signed_eur(
                p.inventory - b.inventory
            ),
            "Cash Effect": _fmt_signed_eur(
                inventory_cash_effect
            ),
        },
        {
            "Working Capital Driver": "Accounts Payable",
            "Baseline": _fmt_eur(b.ap),
            "Projected": _fmt_eur(p.ap),
            "Change": _fmt_signed_eur(
                p.ap - b.ap
            ),
            "Cash Effect": _fmt_signed_eur(
                ap_cash_effect
            ),
        },
        {
            "Working Capital Driver": "TOTAL",
            "Baseline": _fmt_eur(b.nwc),
            "Projected": _fmt_eur(p.nwc),
            "Change": _fmt_signed_eur(
                p.nwc - b.nwc
            ),
            "Cash Effect": _fmt_signed_eur(
                total_cash_effect
            ),
        },
    ]

    st.dataframe(
        wc_rows,
        use_container_width=True,
        hide_index=True,
    )

    # =====================================================
    # RECONCILIATION CHECK
    # =====================================================

    engine_cash_effect = float(
        financial_impact.nwc_cash_impact_delta
    )

    reconciliation_difference = (
        total_cash_effect
        - engine_cash_effect
    )

    if abs(reconciliation_difference) < 0.01:

        st.success(
            f"✅ Working capital cash release reconciles to "
            f"{_fmt_signed_eur(engine_cash_effect)}."
        )

    else:

        st.error(
            f"⚠️ Working capital reconciliation mismatch: "
            f"{_fmt_signed_eur(reconciliation_difference)}."
        )


# =========================================================
# MAIN DASHBOARD RENDERER
# =========================================================

def render_dashboard(
    baseline_state,
    projected_state,
    financial_projection,
    trace,
):
    baseline_fin = (
        financial_projection.baseline
    )

    projected_fin = (
        financial_projection.projected
    )

    financial_impact = (
        financial_projection.impact
    )

    st.title("📊 Executive Dashboard")

    decision_plan = _get_decision_plan()

    _render_executive_decision(
        baseline_state=baseline_state,
        projected_state=projected_state,
        baseline_fin=baseline_fin,
        projected_fin=projected_fin,
        financial_impact=financial_impact,
        decision_plan=decision_plan,
    )

    st.divider()

    _render_capital_cost(
        baseline_state=baseline_state,
        projected_state=projected_state,
        decision_plan=decision_plan,
    )

    st.divider()

    _render_valuation_impact(
        baseline_state=baseline_state,
        projected_state=projected_state,
        decision_plan=decision_plan,
    )

    st.divider()

    _render_financial_impact(
        financial_impact
    )

    st.divider()

    _render_profitability_snapshot(
        baseline_state=baseline_state,
        projected_state=projected_state,
        projected_fin=projected_fin,
    )

    st.divider()

    _render_revenue_bridge(
        financial_impact
    )

    st.divider()

    _render_working_capital(
        baseline_fin=baseline_fin,
        projected_fin=projected_fin,
        financial_impact=financial_impact,
    )

    st.divider()

    _render_cash_fragility_diagnostic(
        baseline_state=baseline_state,
        projected_state=projected_state,
        financial_projection=financial_projection,
    )

    with st.expander(
        "🔍 Decision Impact Diagnostics"
    ):
        _render_decision_diagnostics(
            baseline_state=baseline_state,
            projected_state=projected_state,
            baseline_fin=baseline_fin,
            projected_fin=projected_fin,
            financial_impact=financial_impact,
            decision_plan=decision_plan,
        )
