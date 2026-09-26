import pandas as pd
import streamlit as st
import plotly.graph_objects as go

from diagnostics.monthly_survival import (
    calculate_monthly_survival,
)

from ui.cash_management_lab import (
    build_monthly_cash_coverage,
    _get_cash_management_assumptions,
    _selected_ar_decision,
    _selected_ap_decision,
    _existing_profile_from_session,
    DEFAULT_EXISTING_AR_PROFILE,
    DEFAULT_EXISTING_AP_PROFILE,
)


def render_monthly_survival_lab(
    baseline_state,
    projected_state=None,
):
    st.header(
        "📅 Monthly Cash Coverage Analysis"
    )

    st.info(
        "Test a monthly operating scenario using the same "
        "cash timing rules as Cash Management. "
        "Receivables and Supplier timing are taken from "
        "the current decisions and Cash Management assumptions."
    )

    # =====================================================
    # STATE
    # =====================================================

    state = (
        projected_state
        if projected_state is not None
        else baseline_state
    )

    b_drivers = state.drivers
    b_capital = state.capital_structure

    b_price = float(
        b_drivers.price
    )

    b_vc = float(
        b_drivers.variable_cost_per_unit
    )

    b_monthly_volume = (
        float(b_drivers.volume)
        / 12.0
    )

    b_monthly_fc = (
        float(b_drivers.fixed_opex)
        / 12.0
    )

    b_monthly_debt = (
        float(b_capital.annual_debt_service)
        / 12.0
    )

    # =====================================================
    # CURRENT DECISIONS
    # =====================================================

    ar_decision = _selected_ar_decision()
    ap_decision = _selected_ap_decision()

    # =====================================================
    # CASH MANAGEMENT ASSUMPTIONS
    # =====================================================

    cash_assumptions = (
        _get_cash_management_assumptions(
            baseline_state
        )
    )

    monthly_opex_default = (
        cash_assumptions[
            "monthly_opex"
        ]
    )

    monthly_debt_default = (
        cash_assumptions[
            "monthly_debt"
        ]
    )

    # =====================================================
    # MONTHLY SCENARIO
    # =====================================================

    st.subheader(
        "🕹️ Monthly Scenario"
    )

    st.caption(
        "Change the operating assumptions for this month. "
        "Cash timing itself comes from Cash Management."
    )

    season_factor = st.slider(
        "Monthly Sales Level "
        "(100% = Average Month)",
        min_value=30,
        max_value=250,
        value=100,
        step=5,
        help=(
            "This changes the suggested monthly volume. "
            "You can then override the volume below."
        ),
    )

    multiplier = (
        season_factor / 100.0
    )

    c1, c2, c3 = st.columns(3)

    with c1:

        sim_price = st.number_input(
            "Unit Price (€)",
            min_value=0.0,
            value=b_price,
            step=1.0,
        )

        sim_vc = st.number_input(
            "Variable Cost (€)",
            min_value=0.0,
            value=b_vc,
            step=1.0,
        )

    with c2:

        sim_fc = st.number_input(
            "Monthly Fixed Costs (€)",
            min_value=0.0,
            value=monthly_opex_default,
            step=1000.0,
            format="%.0f",
        )

        sim_debt = st.number_input(
            "Monthly Debt Service (€)",
            min_value=0.0,
            value=monthly_debt_default,
            step=1000.0,
            format="%.0f",
        )

    with c3:

        sim_volume = st.number_input(
            "Forecasted Volume for this Month",
            min_value=0.0,
            value=b_monthly_volume * multiplier,
            step=100.0,
        )

    # =====================================================
    # CURRENT CASH TIMING
    # =====================================================

    st.subheader(
        "💧 Cash Timing Used"
    )

    st.caption(
        "These are not separate assumptions. "
        "They are inherited from Cash Management."
    )

    existing_ar_profile = (
        _existing_profile_from_session(
            session_key="cash_existing_ar_profile",
            default_profile=DEFAULT_EXISTING_AR_PROFILE,
        )
    )

    existing_ap_profile = (
        _existing_profile_from_session(
            session_key="cash_existing_ap_profile",
            default_profile=DEFAULT_EXISTING_AP_PROFILE,
        )
    )

    collection_profile = None

    # We intentionally do not reproduce the collection
    # extraction logic here. Cash Management owns it.
    #
    # build_monthly_cash_coverage() will resolve the
    # current Receivables Decision and its collection
    # profile.

    timing_preview = (
        build_monthly_cash_coverage(
            baseline_state=baseline_state,
            sales_amount=(
                sim_volume
                * sim_price
            ),
            purchases_amount=(
                sim_volume
                * sim_vc
            ),
            monthly_opex=sim_fc,
            monthly_debt=sim_debt,
            ar_decision=ar_decision,
            ap_decision=ap_decision,
            existing_ar_profile=existing_ar_profile,
            existing_ap_profile=existing_ap_profile,
        )
    )

    if not timing_preview.get(
        "valid",
        False,
    ):

        st.error(
            timing_preview.get(
                "reason",
                "Cash Management timing could not be calculated.",
            )
        )

        return

    ar_timing_source = (
        timing_preview.get(
            "ar_timing_source",
            "Cash Management",
        )
    )

    ap_days = float(
        timing_preview.get(
            "ap_days",
            0.0,
        )
    )

    existing_ar_receipts = float(
        timing_preview.get(
            "existing_ar_receipts",
            0.0,
        )
    )

    new_sales_receipts = float(
        timing_preview.get(
            "new_sales_receipts",
            0.0,
        )
    )

    existing_ap_payments = float(
        timing_preview.get(
            "existing_ap_payments",
            0.0,
        )
    )

    new_purchase_payments = float(
        timing_preview.get(
            "new_purchase_payments",
            0.0,
        )
    )

    timing_col1, timing_col2 = st.columns(2)

    with timing_col1:

        st.markdown(
            "**Receivables timing**"
        )

        st.write(
            f"Existing receivables arriving this month: "
            f"€{existing_ar_receipts:,.0f}"
        )

        st.write(
            f"Current-month sales collected this month: "
            f"€{new_sales_receipts:,.0f}"
        )

        st.caption(
            f"Timing source: {ar_timing_source}"
        )

    with timing_col2:

        st.markdown(
            "**Supplier timing**"
        )

        st.write(
            f"Existing payables paid this month: "
            f"€{existing_ap_payments:,.0f}"
        )

        st.write(
            f"Current-month purchases paid this month: "
            f"€{new_purchase_payments:,.0f}"
        )

        st.caption(
            f"Current Supplier payment timing: "
            f"{ap_days:.0f} days"
        )

    # =====================================================
    # RUN DIAGNOSTIC
    # =====================================================

    result = calculate_monthly_survival(
        baseline_state=baseline_state,
        projected_state=projected_state,
        season_factor=season_factor,
        sim_price=sim_price,
        sim_vc=sim_vc,
        sim_fc=sim_fc,
        sim_debt=sim_debt,
        sim_volume=sim_volume,
        cash_timing=timing_preview,
    )

    if not result.get(
        "valid",
        True,
    ):

        st.error(
            result.get(
                "reason",
                "Monthly Cash Coverage could not be calculated.",
            )
        )

        return

    total_cash_outflow = result[
        "total_cash_outflow"
    ]

    total_monthly_cash_in = result[
        "total_monthly_cash_in"
    ]

    cash_gap = result[
        "cash_gap"
    ]

    cash_bep = result[
        "cash_bep"
    ]

    cash_contribution_per_unit = result[
        "cash_contribution_per_unit"
    ]

    # =====================================================
    # RESULTS
    # =====================================================

    st.divider()

    res1, res2, res3 = st.columns(3)

    res1.metric(
        "Cash Outflow",
        f"€{total_cash_outflow:,.0f}",
    )

    res2.metric(
        "Cash Inflows",
        f"€{total_monthly_cash_in:,.0f}",
    )

    delta_color = (
        "normal"
        if cash_gap >= 0
        else "inverse"
    )

    res3.metric(
        "Monthly Cash Balance",
        f"€{cash_gap:,.0f}",
        delta=(
            "Surplus"
            if cash_gap >= 0
            else "Deficit"
        ),
        delta_color=delta_color,
    )

    # =====================================================
    # CASH WATERFALL
    # =====================================================

    st.subheader(
        "Cash movement this month"
    )

    waterfall = pd.DataFrame(
        {
            "": [
                "Existing receivables collected",
                "Current-month sales collected",
                "Existing payables paid",
                "Current-month purchases paid",
                "Fixed operating costs",
                "Debt service",
                "Net monthly cash",
            ],
            "Amount": [
                result[
                    "existing_ar_receipts"
                ],
                result[
                    "new_sales_receipts"
                ],
                -result[
                    "existing_ap_payments"
                ],
                -result[
                    "new_purchase_payments"
                ],
                -result[
                    "monthly_fixed_costs"
                ],
                -result[
                    "monthly_debt_service"
                ],
                result[
                    "cash_gap"
                ],
            ],
        }
    )

    waterfall["Amount"] = waterfall[
        "Amount"
    ].map(
        lambda x: f"€{x:,.0f}"
    )

    st.dataframe(
        waterfall,
        use_container_width=True,
        hide_index=True,
    )

    # =====================================================
    # CASH BREAK-EVEN
    # =====================================================

    if cash_bep is not None and cash_bep > 0:

        fig = go.Figure()

        fig.add_bar(
            name="Units Needed (Cash Basis)",
            x=["Monthly Target"],
            y=[cash_bep],
        )

        fig.add_bar(
            name="Forecasted Units",
            x=["Monthly Target"],
            y=[sim_volume],
        )

        fig.update_layout(
            barmode="group",
            height=350,
            margin=dict(
                t=30,
                b=20,
            ),
            yaxis_title="Units",
        )

        st.plotly_chart(
            fig,
            use_container_width=True,
        )

    # =====================================================
    # VERDICT
    # =====================================================

    st.subheader(
        "💡 Cash Position Assessment"
    )

    if total_monthly_cash_in < total_cash_outflow:

        st.error(
            f"""
### Monthly Cash Shortfall

**Cash arriving this month:** €{total_monthly_cash_in:,.0f}

**Cash obligations this month:** €{total_cash_outflow:,.0f}

**Projected monthly cash shortfall:** €{abs(cash_gap):,.0f}

The calculation uses the same receivables and supplier
timing logic as Cash Management.
"""
        )

    else:

        st.success(
            f"""
### Cash Obligations Covered

**Cash arriving this month:** €{total_monthly_cash_in:,.0f}

**Cash obligations this month:** €{total_cash_outflow:,.0f}

**Projected monthly cash surplus:** €{cash_gap:,.0f}

The calculation uses the same receivables and supplier
timing logic as Cash Management.
"""
        )

    # =====================================================
    # MANAGEMENT RESPONSES
    # =====================================================

    with st.expander(
        "🔍 Management Responses"
    ):

        if cash_bep is None:

            st.error(
                f"""
### Negative Cash Contribution per Unit

**Cash generated from current-month sales per unit:**
€{result["cash_revenue_per_unit"]:,.2f}

**Cash paid for current-month purchases per unit:**
€{result["cash_variable_cost_per_unit"]:,.2f}

**Cash Contribution per Unit:**
Negative ({cash_contribution_per_unit:,.2f})

Under the current timing assumptions, additional sales
do not generate positive current-month cash contribution.

### Areas to examine

- Improve customer collection timing.
- Reduce variable cost per unit.
- Review supplier payment timing.
- Review whether additional sales volume actually improves
  short-term cash under the current payment terms.
"""
            )

        else:

            gap_units = (
                cash_bep
                - sim_volume
            )

            if gap_units > 0:

                extra_revenue = (
                    gap_units
                    * sim_price
                )

                st.markdown(
                    f"You need approximately "
                    f"**{gap_units:,.0f} more units** "
                    f"to reach monthly cash break-even "
                    f"under the current timing assumptions."
                )

                st.markdown(
                    f"That represents approximately "
                    f"**€{extra_revenue:,.0f}** "
                    f"in additional sales at the current price."
                )

                st.markdown(
                    "##### Areas to examine"
                )

                st.markdown(
                    "- Improve customer collection timing."
                )

                st.markdown(
                    "- Review supplier payment timing."
                )

                st.markdown(
                    "- Reduce variable cost per unit."
                )

                st.markdown(
                    "- Review non-critical fixed cash outflows."
                )

            else:

                surplus_units = abs(
                    gap_units
                )

                st.success(
                    f"You are approximately "
                    f"**{surplus_units:,.0f} units** "
                    f"above cash break-even for this month."
                )

                st.markdown(
                    f"Current projected monthly cash surplus: "
                    f"**€{cash_gap:,.0f}**."
                )
