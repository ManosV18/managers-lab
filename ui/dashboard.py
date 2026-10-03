import streamlit as st

from core.decision_plan import DecisionPlan

# Domain / diagnostics layer
from diagnostics.cash_fragility import calculate_cash_fragility

# Cash Management timing layer
from ui.cash_management_lab import build_cash_management_summary


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
        changes = getattr(
            decision,
            "changes",
            {},
        )

        if "wacc" in changes:
            return True

        category = str(
            getattr(
                decision,
                "category",
                "",
            )
        ).lower()

        name = str(
            getattr(
                decision,
                "name",
                "",
            )
        ).lower()

        if (
            "capital_structure" in category
            and "wacc" in name
        ):
            return True

        if (
            "capital" in category
            and "wacc" in name
        ):
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
        any(
            key in getattr(
                decision,
                "changes",
                {},
            )
            for key in wc_keys
        )
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
        any(
            key in getattr(
                decision,
                "changes",
                {},
            )
            for key in operational_keys
        )
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

    revenue_delta = float(
        financial_impact.revenue_delta
    )

    ebitda_delta = float(
        financial_impact.ebitda_delta
    )

    net_profit_delta = float(
        financial_impact.net_profit_delta
    )

    fcfe_delta = float(
        financial_impact.fcfe_delta
    )

    nwc_cash_impact = float(
        financial_impact.nwc_cash_impact_delta
    )

    baseline_wacc = float(
        baseline_state.capital_structure.wacc
    )

    projected_wacc = float(
        projected_state.capital_structure.wacc
    )

    wacc_delta = (
        projected_wacc
        - baseline_wacc
    )

    wacc_present = _has_wacc_decision(
        decision_plan
    )

    operational_present = _has_operational_decision(
        decision_plan
    )

    wc_present = _has_working_capital_decision(
        decision_plan
    )

    capital_cost_negative = (
        wacc_present
        and wacc_delta > 1e-9
    )

    capital_cost_positive = (
        wacc_present
        and wacc_delta < -1e-9
    )

    profitability_positive = (
        ebitda_delta > 1e-9
        or net_profit_delta > 1e-9
    )

    profitability_negative = (
        ebitda_delta < -1e-9
        and net_profit_delta < -1e-9
    )

    cash_positive = (
        fcfe_delta > 1e-9
    )

    cash_negative = (
        fcfe_delta < -1e-9
    )

    operating_positive = (
        profitability_positive
        or cash_positive
    )

    operating_negative = (
        profitability_negative
        and cash_negative
    )

    if (
        profitability_positive
        and cash_negative
    ):
        return "mixed"

    if (
        profitability_negative
        and cash_positive
    ):
        return "mixed"

    if (
        wacc_present
        and not operational_present
        and not wc_present
    ):
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

    if (
        capital_cost_negative
        and operating_positive
    ):
        return "mixed"

    if (
        capital_cost_positive
        and operating_negative
    ):
        return "mixed"

    if operating_negative:
        return "negative"

    if operating_positive:
        return "positive"

    return "mixed"


# =========================================================
# EXECUTIVE DECISION — FIRST VIEW
# =========================================================

def _render_executive_decision(
    baseline_state,
    projected_state,
    baseline_fin,
    projected_fin,
    financial_impact,
    decision_plan,
):
    if decision_plan is None:
        st.info(
            "🔵 BASELINE VIEW — No Decision Plan is currently selected. "
            "Projected financials equal the locked baseline."
        )
        return

    p = projected_fin.income_statement

    revenue_delta = float(
        financial_impact.revenue_delta
    )

    net_profit_delta = float(
        financial_impact.net_profit_delta
    )

    fcfe_delta = float(
        financial_impact.fcfe_delta
    )

    wc_cash_impact = float(
        financial_impact.nwc_cash_impact_delta
    )

    # -----------------------------------------------------
    # CASH TIMING RESULT
    # -----------------------------------------------------

    cash_result = build_cash_management_summary(
        baseline_state=baseline_state,
    )

    funding_required = 0.0
    lowest_cash = None

    if (
        cash_result is not None
        and cash_result.get("valid", True)
    ):
        funding_required = float(
            cash_result.get(
                "funding_required",
                0.0,
            )
        )

        lowest_cash_value = cash_result.get(
            "lowest_projected_cash"
        )

        if lowest_cash_value is not None:
            lowest_cash = float(
                lowest_cash_value
            )

    # -----------------------------------------------------
    # TOP DECISION MESSAGE
    # -----------------------------------------------------

    st.subheader(
        f"🎯 {decision_plan.name}"
    )

    if (
        net_profit_delta > 0
        and fcfe_delta < 0
        and wc_cash_impact < 0
    ):
        if funding_required > 0:
            st.warning(
                f"🟠 **More profit — more pressure on cash.** "
                f"The decision increases Net Profit by "
                f"**{_fmt_signed_eur(net_profit_delta)}**, "
                f"but ties up **{_fmt_eur(abs(wc_cash_impact))}** "
                f"in working capital. "
                f"Projected cash also falls below the minimum reserve."
            )
        else:
            st.warning(
                f"🟠 **More profit — more pressure on cash.** "
                f"The decision increases Net Profit by "
                f"**{_fmt_signed_eur(net_profit_delta)}**, "
                f"but ties up **{_fmt_eur(abs(wc_cash_impact))}** "
                f"in working capital. "
                f"Cash remains above the minimum reserve, "
                f"but the liquidity cushion is tighter."
            )

    elif (
        net_profit_delta > 0
        and fcfe_delta >= 0
    ):
        st.success(
            f"🟢 **More profit without additional cash pressure.** "
            f"Net Profit increases by "
            f"**{_fmt_signed_eur(net_profit_delta)}** "
            f"and cash generation also improves."
        )

    elif (
        net_profit_delta < 0
        and fcfe_delta < 0
    ):
        st.error(
            f"🔴 **Lower profit and lower cash generation.** "
            f"Net Profit changes by "
            f"**{_fmt_signed_eur(net_profit_delta)}** "
            f"and cash generation changes by "
            f"**{_fmt_signed_eur(fcfe_delta)}**."
        )

    else:
        st.info(
            f"🟡 **Mixed financial effect.** "
            f"Net Profit changes by "
            f"**{_fmt_signed_eur(net_profit_delta)}** "
            f"while cash generation changes by "
            f"**{_fmt_signed_eur(fcfe_delta)}**."
        )

    # -----------------------------------------------------
    # FOUR CORE BUSINESS CARDS
    # -----------------------------------------------------

    st.markdown(
        "### The Decision in 4 Numbers"
    )

    c1, c2, c3, c4 = st.columns(4)

    # Revenue
    c1.metric(
        "💰 Revenue",
        _fmt_eur(p.revenue),
    )
    c1.caption(
        f"Change vs baseline: "
        f"{_fmt_signed_eur(revenue_delta)}"
    )

    # Profit
    c2.metric(
        "📈 Net Profit",
        _fmt_eur(p.net_profit),
    )
    c2.caption(
        f"Change vs baseline: "
        f"{_fmt_signed_eur(net_profit_delta)}"
    )

    # Cash / owner cash flow
    c3.metric(
        "💶 Cash Generation",
        _fmt_eur(projected_fin.fcfe),
    )
    c3.caption(
        f"Change vs baseline: "
        f"{_fmt_signed_eur(fcfe_delta)}"
    )

    # Lowest cash
    if lowest_cash is not None:
        c4.metric(
            "💧 Lowest Cash",
            _fmt_eur(lowest_cash),
        )

        if funding_required > 0:
            c4.caption(
                "🔴 Below minimum reserve"
            )
        else:
            c4.caption(
                "🟢 Above minimum reserve"
            )
    else:
        c4.metric(
            "💧 Lowest Cash",
            "—",
        )
        c4.caption(
            "Cash timing unavailable"
        )

    # -----------------------------------------------------
    # SHORT CAUSAL EXPLANATION
    # -----------------------------------------------------

    if wc_cash_impact < 0:
        st.caption(
            f"💧 **Cash pressure:** "
            f"{_fmt_eur(abs(wc_cash_impact))} "
            f"is tied up in working capital."
        )

    elif wc_cash_impact > 0:
        st.caption(
            f"💧 **Cash released:** "
            f"{_fmt_eur(wc_cash_impact)} "
            f"is released from working capital."
        )

    else:
        st.caption(
            "💧 Working capital has no incremental cash impact."
        )


# =========================================================
# REVENUE BRIDGE
# =========================================================

def _render_revenue_bridge(financial_impact):
    st.subheader(
        "📈 Why did Revenue change?"
    )

    price_effect = float(
        financial_impact.price_effect
    )

    volume_effect = float(
        financial_impact.volume_effect
    )

    revenue_delta = float(
        financial_impact.revenue_delta
    )

    c1, c2, c3 = st.columns(3)

    c1.metric(
        "Price Change Impact",
        _fmt_signed_eur(
            price_effect
        ),
    )

    c2.metric(
        "Volume Change Impact",
        _fmt_signed_eur(
            volume_effect
        ),
    )

    c3.metric(
        "Total Revenue Change",
        _fmt_signed_eur(
            revenue_delta
        ),
    )


# =========================================================
# PROFITABILITY
# =========================================================

def _render_profitability_snapshot(
    baseline_state,
    projected_state,
    projected_fin,
):
    p = projected_fin.income_statement

    st.subheader(
        "📌 Profitability"
    )

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
        p.net_profit,
        projected_revenue,
    )

    net_profit_change = (
        p.net_profit
        - baseline_state.net_profit
    )

    margin_change = (
        proj_net_margin
        - base_net_margin
    )

    c1, c2, c3 = st.columns(3)

    c1.metric(
        "Net Profit",
        _fmt_eur(p.net_profit),
    )
    c1.caption(
        f"Change vs baseline: "
        f"{_fmt_signed_eur(net_profit_change)}"
    )

    c2.metric(
        "Profit Margin — Before",
        f"{base_net_margin:.1f}%",
    )

    c3.metric(
        "Profit Margin — After",
        f"{proj_net_margin:.1f}%",
    )

    if margin_change > 0:
        c3.caption(
            f"🟢 Margin improved: "
            f"+{margin_change:.1f} percentage points"
        )
    elif margin_change < 0:
        c3.caption(
            f"🟠 Margin reduced: "
            f"{margin_change:.1f} percentage points"
        )
    else:
        c3.caption(
            "Margin unchanged"
        )


# =========================================================
# WORKING CAPITAL — EXECUTIVE VIEW
# =========================================================

def _render_working_capital(
    baseline_fin,
    projected_fin,
    financial_impact,
):
    st.subheader(
        "💧 Cash tied up in Working Capital"
    )

    b = baseline_fin.working_capital
    p = projected_fin.working_capital

    cash_impact = float(
        financial_impact.nwc_cash_impact_delta
    )

    nwc_change = p.nwc - b.nwc

    c1, c2, c3 = st.columns(3)

    c1.metric(
        "Before",
        _fmt_eur(b.nwc),
    )

    c2.metric(
        "After",
        _fmt_eur(p.nwc),
    )
    c2.caption(
        f"Change vs baseline: "
        f"{_fmt_signed_eur(nwc_change)}"
    )

    c3.metric(
        "Cash Change",
        _fmt_signed_eur(
            cash_impact
        ),
    )

    if cash_impact < 0:
        st.warning(
            f"🟠 The decision ties up "
            f"**{_fmt_eur(abs(cash_impact))}** "
            f"of additional cash in working capital."
        )

    elif cash_impact > 0:
        st.success(
            f"🟢 The decision releases "
            f"**{_fmt_eur(cash_impact)}** "
            f"of cash from working capital."
        )

    else:
        st.info(
            "Working capital has no incremental cash effect."
        )

    # -----------------------------------------------------
    # TECHNICAL NWC TABLE
    # -----------------------------------------------------

    with st.expander(
        "Show Working Capital Breakdown",
        expanded=False,
    ):
        rows = [
            {
                "Metric": "Accounts Receivable",
                "Before": _fmt_eur(b.ar),
                "After": _fmt_eur(p.ar),
                "Change vs baseline": _fmt_signed_eur(
                    p.ar - b.ar
                ),
            },
            {
                "Metric": "Inventory",
                "Before": _fmt_eur(b.inventory),
                "After": _fmt_eur(p.inventory),
                "Change vs baseline": _fmt_signed_eur(
                    p.inventory - b.inventory
                ),
            },
            {
                "Metric": "Accounts Payable",
                "Before": _fmt_eur(b.ap),
                "After": _fmt_eur(p.ap),
                "Change vs baseline": _fmt_signed_eur(
                    p.ap - b.ap
                ),
            },
            {
                "Metric": "Net Working Capital",
                "Before": _fmt_eur(b.nwc),
                "After": _fmt_eur(p.nwc),
                "Change vs baseline": _fmt_signed_eur(
                    p.nwc - b.nwc
                ),
            },
        ]

        st.dataframe(
            rows,
            use_container_width=True,
            hide_index=True,
        )


# =========================================================
# CASH MANAGEMENT — EXECUTIVE TIMING VIEW
# =========================================================

def _render_cash_management_summary(
    baseline_state,
):
    st.subheader(
        "💶 Cash Timing"
    )

    result = build_cash_management_summary(
        baseline_state=baseline_state,
    )

    if result is None:
        st.warning(
            "Cash Management cannot be calculated because "
            "the baseline company state is not available."
        )
        return

    if not result.get("valid", True):
        st.warning(
            result.get(
                "reason",
                "Cash Management assumptions are not valid.",
            )
        )
        return

    lowest_cash = float(
        result.get(
            "lowest_projected_cash",
            0.0,
        )
    )

    lowest_month = result.get(
        "lowest_cash_month"
    )

    minimum_cash = float(
        result.get(
            "minimum_cash_reserve",
            0.0,
        )
    )

    funding_required = float(
        result.get(
            "funding_required",
            0.0,
        )
    )

    c1, c2, c3 = st.columns(3)

    c1.metric(
        "Lowest Cash Available",
        _fmt_eur(lowest_cash),
    )

    c2.metric(
        "Lowest Point",
        (
            f"Month {lowest_month}"
            if lowest_month is not None
            else "—"
        ),
    )

    c3.metric(
        "Minimum Cash Reserve",
        _fmt_eur(minimum_cash),
    )

    if funding_required > 0:
        st.warning(
            f"🟠 Cash falls below the minimum reserve. "
            f"Estimated funding required: "
            f"**{_fmt_eur(funding_required)}**."
        )
    else:
        st.success(
            "🟢 Cash remains above the minimum reserve "
            "throughout the six-month period."
        )

    with st.expander(
        "Show Cash Timing Details",
        expanded=False,
    ):
        st.metric(
            "Funding Required",
            _fmt_eur(funding_required),
        )

        st.caption(
            "The full six-month cash table remains in "
            "Cash Management. This section shows only "
            "the executive timing result."
        )


# =========================================================
# COMPANY HEALTH DIAGNOSTICS
# =========================================================

def _render_cash_fragility_diagnostic(
    baseline_state,
    projected_state,
    financial_projection,
):
    st.subheader(
        "🩺 Financial Health"
    )

    baseline_diag = calculate_cash_fragility(
        baseline_state=baseline_state,
    )

    projected_diag = calculate_cash_fragility(
        baseline_state=baseline_state,
        projected_state=projected_state,
        financial_projection=financial_projection,
    )

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
        health_signal = "🟠 More fragile"
    else:
        health_signal = "🟡 Mixed / Neutral"

    # -----------------------------------------------------
    # EXECUTIVE MESSAGE
    # -----------------------------------------------------

    if health_improved:
        st.success(
            "🟢 Liquidity resilience improves versus the "
            "locked baseline."
        )

    elif health_deteriorated:
        st.warning(
            "🟠 Liquidity resilience deteriorates versus "
            "the locked baseline. This does not necessarily "
            "mean an immediate cash shortfall."
        )

    else:
        st.info(
            "🟡 Liquidity resilience shows a mixed or "
            "limited change versus baseline."
        )

    # -----------------------------------------------------
    # TECHNICAL DIAGNOSTICS
    # -----------------------------------------------------

    with st.expander(
        "Show Financial Health Diagnostics",
        expanded=False,
    ):
        rows = [
            {
                "Diagnostic Metric": "Cash Runway",
                "Before": (
                    f'{baseline_diag["cash_runway"]:.1f} days'
                ),
                "After": (
                    f'{projected_diag["cash_runway"]:.1f} days'
                ),
                "Change vs baseline": (
                    f"{runway_delta:+.1f} days"
                ),
            },
            {
                "Diagnostic Metric": "Cash Conversion Cycle",
                "Before": (
                    f'{baseline_diag["ccc_days"]:.1f} days'
                ),
                "After": (
                    f'{projected_diag["ccc_days"]:.1f} days'
                ),
                "Change vs baseline": (
                    f"{ccc_delta:+.1f} days"
                ),
            },
            {
                "Diagnostic Metric": "Runway After CCC",
                "Before": (
                    f'{baseline_diag["runway_after_cycle"]:+.1f} days'
                ),
                "After": (
                    f'{projected_diag["runway_after_cycle"]:+.1f} days'
                ),
                "Change vs baseline": (
                    f"{net_runway_delta:+.1f} days"
                ),
            },
            {
                "Diagnostic Metric": "Fragility Score",
                "Before": (
                    f'{baseline_diag["fragility_score"]:.2f}'
                ),
                "After": (
                    f'{projected_diag["fragility_score"]:.2f}'
                ),
                "Change vs baseline": (
                    f"{score_delta:+.2f}"
                ),
            },
            {
                "Diagnostic Metric": "Liquidity Status",
                "Before": (
                    baseline_diag["status"]
                ),
                "After": (
                    projected_diag["status"]
                ),
                "Change vs baseline": health_signal,
            },
        ]

        st.dataframe(
            rows,
            use_container_width=True,
            hide_index=True,
        )

        st.markdown(
            "#### Diagnostic Interpretation"
        )

        st.markdown("**Baseline**")
        st.info(
            baseline_diag["interpretation"]
        )

        st.markdown("**Projected**")
        st.info(
            projected_diag["interpretation"]
        )


# =========================================================
# CAPITAL COST / WACC
# =========================================================

def _render_capital_cost(
    baseline_state,
    projected_state,
    decision_plan,
):
    baseline_capital = (
        baseline_state.capital_structure
    )

    projected_capital = (
        projected_state.capital_structure
    )

    baseline_wacc = float(
        baseline_capital.wacc
    )

    projected_wacc = float(
        projected_capital.wacc
    )

    wacc_delta_pp = (
        projected_wacc
        - baseline_wacc
    ) * 100.0

    wacc_decision = _has_wacc_decision(
        decision_plan
    )

    st.subheader(
        "🏦 Capital Cost / Valuation"
    )

    c1, c2, c3 = st.columns(3)

    c1.metric(
        "Baseline WACC",
        _fmt_rate(baseline_wacc),
    )

    c2.metric(
        "Projected WACC",
        _fmt_rate(projected_wacc),
        f"{wacc_delta_pp:+.2f} pp",
        delta_color="inverse",
    )

    c3.metric(
        "WACC Decision",
        "Applied" if wacc_decision else "None",
    )

    if not wacc_decision:
        st.caption(
            "No WACC decision is included in the current "
            "Decision Plan."
        )
        return

    if wacc_delta_pp < -1e-9:
        st.success(
            f"📉 Capital cost decreased from "
            f"{_fmt_rate(baseline_wacc)} to "
            f"{_fmt_rate(projected_wacc)}."
        )

    elif wacc_delta_pp > 1e-9:
        st.warning(
            f"📈 Capital cost increased from "
            f"{_fmt_rate(baseline_wacc)} to "
            f"{_fmt_rate(projected_wacc)}."
        )

    else:
        st.info(
            "WACC decision is present, but projected WACC "
            "is unchanged versus baseline."
        )

    st.caption(
        "WACC is treated exclusively as a capital-cost / "
        "valuation driver. It does not directly change "
        "Net Profit, Interest Expense or FCFE in "
        "FinancialEngine v1."
    )


# =========================================================
# VALUATION IMPACT
# =========================================================

def _render_valuation_impact(
    baseline_state,
    projected_state,
    decision_plan,
):
    if (
        decision_plan is None
        or not _has_wacc_decision(decision_plan)
    ):
        return

    baseline_wacc = float(
        baseline_state.capital_structure.wacc
    )

    projected_wacc = float(
        projected_state.capital_structure.wacc
    )

    delta_wacc = (
        projected_wacc
        - baseline_wacc
    )

    st.subheader(
        "📉 Valuation Impact"
    )

    c1, c2, c3 = st.columns(3)

    c1.metric(
        "Baseline Discount Rate",
        _fmt_rate(baseline_wacc),
    )

    c2.metric(
        "Projected Discount Rate",
        _fmt_rate(projected_wacc),
        f"{delta_wacc * 100.0:+.2f} pp",
        delta_color="inverse",
    )

    if delta_wacc > 1e-9:
        c3.metric(
            "Valuation Signal",
            "🔴 Downward",
        )

        st.warning(
            "Higher WACC increases the discount rate applied "
            "to future FCFF and therefore creates downward "
            "pressure on Enterprise Value, all else equal."
        )

    elif delta_wacc < -1e-9:
        c3.metric(
            "Valuation Signal",
            "🟢 Upward",
        )

        st.success(
            "Lower WACC reduces the discount rate applied "
            "to future FCFF and therefore creates upward "
            "pressure on Enterprise Value, all else equal."
        )

    else:
        c3.metric(
            "Valuation Signal",
            "⚪ Neutral",
        )

        st.info(
            "WACC is unchanged; there is no incremental "
            "valuation signal from the discount-rate layer."
        )

    st.markdown(
        "#### Valuation Interpretation"
    )

    if delta_wacc > 1e-9:
        st.write(
            "The Decision Plan may improve operating and/or "
            "cash-flow metrics, but the higher WACC makes "
            "future cash flows less valuable in a DCF framework."
        )

    elif delta_wacc < -1e-9:
        st.write(
            "The Decision Plan reduces the discount rate "
            "applied to future FCFF."
        )

    else:
        st.write(
            "The Decision Plan produces no incremental "
            "valuation effect through the WACC layer."
        )

    st.caption(
        "FinancialEngine v1 does not calculate FCFF, "
        "terminal value or Enterprise Value. This section "
        "therefore reports only the directional valuation "
        "effect of the WACC change."
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

    st.subheader(
        "🔍 Decision Impact Diagnostics"
    )

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
                f"EBITDA Impact: "
                f"{_fmt_signed_eur(financial_impact.ebitda_delta)}"
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
                f"Cash Impact: "
                f"{_fmt_signed_eur(financial_impact.nwc_cash_impact_delta)}"
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

    wc_rows = [
        {
            "Working Capital Driver": "Accounts Receivable",
            "Baseline": _fmt_eur(b.ar),
            "Projected": _fmt_eur(p.ar),
            "Change vs baseline": _fmt_signed_eur(
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
            "Change vs baseline": _fmt_signed_eur(
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
            "Change vs baseline": _fmt_signed_eur(
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
            "Change vs baseline": _fmt_signed_eur(
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

    st.title(
        "📊 Executive Dashboard"
    )

    decision_plan = _get_decision_plan()

    # =====================================================
    # BASELINE VIEW — NO DECISION PLAN
    # =====================================================

    if decision_plan is None:
        st.info(
            "🔵 **BASELINE VIEW** — No Decision Plan is currently selected. "
            "The figures below show the locked baseline of the business."
        )

        st.markdown(
            "### Baseline Business Snapshot"
        )

        baseline_p = baseline_fin.income_statement

        baseline_revenue = float(
            baseline_p.revenue
        )

        baseline_net_profit = float(
            baseline_p.net_profit
        )

        baseline_margin = _margin(
            baseline_net_profit,
            baseline_revenue,
        )

        cash_result = build_cash_management_summary(
            baseline_state=baseline_state,
        )

        lowest_cash = None

        if (
            cash_result is not None
            and cash_result.get("valid", True)
        ):
            lowest_cash_value = cash_result.get(
                "lowest_projected_cash"
            )

            if lowest_cash_value is not None:
                lowest_cash = float(
                    lowest_cash_value
                )

        c1, c2, c3, c4 = st.columns(4)

        c1.metric(
            "💰 Revenue",
            _fmt_eur(baseline_revenue),
        )

        c2.metric(
            "📈 Net Profit",
            _fmt_eur(baseline_net_profit),
        )

        c3.metric(
            "📊 Profit Margin",
            f"{baseline_margin:.1f}%",
        )

        c4.metric(
            "💧 Lowest Cash",
            (
                _fmt_eur(lowest_cash)
                if lowest_cash is not None
                else "—"
            ),
        )

        st.divider()

        st.subheader(
            "💧 Working Capital"
        )

        st.metric(
            "Net Working Capital",
            _fmt_eur(
                baseline_fin.working_capital.nwc
            ),
        )

        st.caption(
            "Locked baseline position."
        )

        st.divider()

        _render_cash_management_summary(
            baseline_state=baseline_state,
        )

        return

    # =====================================================
    # 1. EXECUTIVE DECISION / 5-SECOND VIEW
    # =====================================================

    _render_executive_decision(
        baseline_state=baseline_state,
        projected_state=projected_state,
        baseline_fin=baseline_fin,
        projected_fin=projected_fin,
        financial_impact=financial_impact,
        decision_plan=decision_plan,
    )

    st.divider()

    # =====================================================
    # 2. SALES / REVENUE — WHY DID IT CHANGE?
    # =====================================================

    _render_revenue_bridge(
        financial_impact
    )

    st.divider()

    # =====================================================
    # 3. PROFITABILITY
    # =====================================================

    _render_profitability_snapshot(
        baseline_state=baseline_state,
        projected_state=projected_state,
        projected_fin=projected_fin,
    )

    st.divider()

    # =====================================================
    # 4. WORKING CAPITAL / CASH PRESSURE
    # =====================================================

    _render_working_capital(
        baseline_fin=baseline_fin,
        projected_fin=projected_fin,
        financial_impact=financial_impact,
    )

    st.divider()

    # =====================================================
    # 5. CASH TIMING
    # =====================================================

    _render_cash_management_summary(
        baseline_state=baseline_state,
    )

    st.divider()

    # =====================================================
    # 6. TECHNICAL BREAKDOWN
    # =====================================================

    with st.expander(
        "🔧 Technical Breakdown",
        expanded=False,
    ):

        # -------------------------------------------------
        # CAPITAL COST / WACC
        # -------------------------------------------------

        _render_capital_cost(
            baseline_state=baseline_state,
            projected_state=projected_state,
            decision_plan=decision_plan,
        )

        st.divider()

        # -------------------------------------------------
        # VALUATION
        # -------------------------------------------------

        _render_valuation_impact(
            baseline_state=baseline_state,
            projected_state=projected_state,
            decision_plan=decision_plan,
        )

        st.divider()

        # -------------------------------------------------
        # FINANCIAL HEALTH
        # -------------------------------------------------

        _render_cash_fragility_diagnostic(
            baseline_state=baseline_state,
            projected_state=projected_state,
            financial_projection=financial_projection,
        )

        st.divider()

        # -------------------------------------------------
        # DECISION DIAGNOSTICS
        # -------------------------------------------------

        _render_decision_diagnostics(
            baseline_state=baseline_state,
            projected_state=projected_state,
            baseline_fin=baseline_fin,
            projected_fin=projected_fin,
            financial_impact=financial_impact,
            decision_plan=decision_plan,
        )
