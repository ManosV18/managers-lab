import pandas as pd
import streamlit as st
import plotly.graph_objects as go

from diagnostics.monthly_survival import (
    calculate_monthly_survival,
)


def render_monthly_survival_lab(
    baseline_state,
    projected_state=None,
):
    st.header("📅 Monthly Cash Coverage Analysis")

    st.info(
        "Test whether this month's sales activity covers this month's "
        "cash obligations using the same receivables and supplier timing "
        "logic as Cash Management."
    )

    # =====================================================
    # CANONICAL BASELINE DEFAULTS
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
        float(
            b_capital.annual_debt_service
        )
        / 12.0
    )

    # =====================================================
    # MONTHLY SALES LEVEL
    # =====================================================

    st.subheader(
        "📈 Monthly Sales Scenario"
    )

    season_factor = st.slider(
        "Monthly Sales Level "
        "(100% = Average Month)",
        min_value=30,
        max_value=250,
        value=100,
        step=5,
        help=(
            "150% = strong month, "
            "70% = weak month."
        ),
    )

    multiplier = (
        season_factor / 100.0
    )

    # =====================================================
    # MONTHLY CONTROLS
    # =====================================================

    st.subheader(
        "🕹️ Monthly Scenario Controls"
    )

    c1, c2, c3 = st.columns(3)

    with c1:

        sim_price = st.number_input(
            "Unit Price (€)",
            value=float(b_price),
        )

        sim_vc = st.number_input(
            "Variable Cost (€)",
            value=float(b_vc),
        )

    with c2:

        sim_fc = st.number_input(
            "Monthly Fixed Costs (€)",
            value=float(b_monthly_fc),
        )

        sim_debt = st.number_input(
            "Monthly Debt Service (€)",
            value=float(b_monthly_debt),
        )

    with c3:

        sim_volume = st.number_input(
            "Forecasted Volume for this Month",
            value=float(
                b_monthly_volume
                * multiplier
            ),
        )

    # =====================================================
    # RUN DIAGNOSTIC
    # =====================================================

    try:

        result = calculate_monthly_survival(
            baseline_state=baseline_state,
            projected_state=projected_state,
            season_factor=season_factor,
            sim_price=sim_price,
            sim_vc=sim_vc,
            sim_fc=sim_fc,
            sim_debt=sim_debt,
            sim_volume=sim_volume,
        )

    except ValueError as exc:

        st.error(
            str(exc)
        )

        return

    # =====================================================
    # EXTRACT RESULTS
    # =====================================================

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

    existing_ar_cash_in = result[
        "existing_ar_cash_in"
    ]

    new_sales_cash_in = result[
        "current_sales_cash_in"
    ]

    existing_ap_cash_out = result[
        "existing_ap_cash_out"
    ]

    new_purchase_cash_out = result[
        "current_purchase_cash_out"
    ]

    # =====================================================
    # TIMING TRANSPARENCY
    # =====================================================

    st.divider()

    st.subheader(
        "💧 Cash Timing Used"
    )

    timing_col1, timing_col2 = st.columns(2)

    with timing_col1:

        st.metric(
            "Receivables Timing",
            f"{result['ar_days']:.0f} days",
        )

        if result["collection_profile"]:

            profile_text = " / ".join(
                f"M{int(delay) + 1}: "
                f"{percentage:.0%}"
                for delay, percentage
                in sorted(
                    result[
                        "collection_profile"
                    ].items()
                )
            )

            st.caption(
                f"New sales collection profile: "
                f"{profile_text}"
            )

        else:

            st.caption(
                "New sales use the current AR-day timing."
            )

    with timing_col2:

        st.metric(
            "Supplier Payment Timing",
            f"{result['ap_days']:.0f} days",
        )

        st.caption(
            "New purchases use the same AP timing "
            "as Cash Management."
        )

    # =====================================================
    # CASH FLOW BREAKDOWN
    # =====================================================

    st.subheader(
        "💰 This Month's Cash Flow"
    )

    flow1, flow2 = st.columns(2)

    with flow1:

        st.markdown(
            "#### Cash In"
        )

        st.metric(
            "Existing Receivables Collected",
            f"€{existing_ar_cash_in:,.0f}",
        )

        st.metric(
            "Current Sales Collected",
            f"€{new_sales_cash_in:,.0f}",
        )

        st.metric(
            "Total Cash In",
            f"€{total_monthly_cash_in:,.0f}",
        )

    with flow2:

        st.markdown(
            "#### Cash Out"
        )

        st.metric(
            "Existing Payables Paid",
            f"€{existing_ap_cash_out:,.0f}",
        )

        st.metric(
            "Current Purchases Paid",
            f"€{new_purchase_cash_out:,.0f}",
        )

        st.metric(
            "Total Supplier Cash Out",
            f"€{result['supplier_cash_out']:,.0f}",
        )

    # =====================================================
    # RESULTS DASHBOARD
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
    # CASH BEP
    # =====================================================

    if cash_bep is not None and cash_bep > 0:

        fig = go.Figure()

        fig.add_bar(
            name="Units Needed",
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
    # ASSESSMENT
    # =====================================================

    st.subheader(
        "💡 Cash Position Assessment"
    )

    if total_monthly_cash_in < total_cash_outflow:

        st.error(
            f"""
### Monthly Cash Shortfall

**Cash Inflows:** €{total_monthly_cash_in:,.0f}

**Cash Outflow:** €{total_cash_outflow:,.0f}

**Projected Cash Shortfall:** €{abs(cash_gap):,.0f}

The calculation includes:
- collections from existing receivables,
- collections from this month's sales,
- payments of existing payables,
- payments of this month's purchases,
- monthly operating expenses,
- monthly debt service.
"""
        )

    else:

        st.success(
            f"""
### Cash Obligations Covered

**Cash Inflows:** €{total_monthly_cash_in:,.0f}

**Cash Outflow:** €{total_cash_outflow:,.0f}

**Projected Cash Surplus:** €{cash_gap:,.0f}

Cash timing is calculated using the same rules as Cash Management.
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
### Negative Incremental Cash Contribution

**Cash received per additional unit this month:**
€{result['cash_revenue_per_unit']:,.2f}

**Cash paid to suppliers per additional unit this month:**
€{result['cash_purchase_cost_per_unit']:,.2f}

**Incremental cash contribution per unit:**
€{cash_contribution_per_unit:,.2f}

Under the current Receivables and Supplier timing,
additional sales do not generate positive cash contribution
during this month.

Possible levers:
- improve customer collection timing,
- negotiate longer supplier payment terms,
- reduce variable cost,
- change the sales/payment structure.
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
                    f"**{gap_units:,.0f} additional units** "
                    f"under the current cash timing assumptions "
                    f"to reach monthly cash break-even."
                )

                st.markdown(
                    f"That represents approximately "
                    f"**€{extra_revenue:,.0f}** "
                    f"of additional sales at the current price."
                )

                st.markdown(
                    "##### Cash levers"
                )

                st.markdown(
                    "- Improve collections from existing receivables."
                )

                st.markdown(
                    "- Improve the collection timing of new sales."
                )

                st.markdown(
                    "- Negotiate longer supplier payment terms."
                )

                st.markdown(
                    "- Reduce variable cost per unit."
                )

                st.markdown(
                    "- Defer non-critical fixed cash expenditure."
                )

            else:

                surplus_units = abs(
                    gap_units
                )

                st.success(
                    f"""
The scenario is approximately
**{surplus_units:,.0f} units above cash break-even**
under the current timing assumptions.

Monthly cash surplus:
**€{cash_gap:,.0f}**
"""
                )


show_monthly_survival_lab = render_monthly_survival_lab
