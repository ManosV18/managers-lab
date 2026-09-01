import streamlit as st

from diagnostics.pricing_threshold import (
    calculate_pricing_threshold,
)


def render_pricing_threshold(
    baseline_state,
):
    """
    Pricing Threshold Diagnostic.

    Read-only diagnostic based on CompanyState.
    It does not create or modify Decisions.
    """

    st.title("🎯 Pricing Threshold Diagnostic")

    st.markdown(
        """
        Test how much revenue pressure the business can absorb
        after a price reduction while still covering its fixed costs.
        """
    )

    # =====================================================
    # COMPANY STATE
    # =====================================================

    drivers = baseline_state.drivers

    price = float(drivers.price)
    volume = float(drivers.volume)
    variable_cost = float(
        drivers.variable_cost_per_unit
    )
    fixed_cost = float(
        drivers.fixed_opex
    )

    current_revenue = price * volume
    current_contribution = (
        price - variable_cost
    ) * volume

    current_operating_profit = (
        current_contribution - fixed_cost
    )

    # =====================================================
    # BASELINE SNAPSHOT
    # =====================================================

    st.subheader("Current Pricing Economics")

    c1, c2, c3, c4 = st.columns(4)

    c1.metric(
        "Selling Price",
        f"€{price:,.2f}",
    )

    c2.metric(
        "Revenue",
        f"€{current_revenue:,.0f}",
    )

    c3.metric(
        "Contribution",
        f"€{current_contribution:,.0f}",
    )

    c4.metric(
        "Operating Profit",
        f"€{current_operating_profit:,.0f}",
    )

    st.divider()

    # =====================================================
    # PRICE REDUCTION
    # =====================================================

    st.subheader("Price Reduction")

    price_cut_pct = st.slider(
        "Proposed Price Reduction",
        min_value=0.0,
        max_value=50.0,
        value=10.0,
        step=0.5,
        format="%.1f%%",
        key="pricing_threshold_cut",
    )

    # =====================================================
    # DIAGNOSTIC
    # =====================================================

    result = calculate_pricing_threshold(
        price=price,
        variable_cost=variable_cost,
        volume=volume,
        fixed_cost=fixed_cost,
        price_cut_pct=price_cut_pct,
    )

    if result is None:
        st.error(
            "The pricing threshold cannot be calculated "
            "because the current economics are not valid "
            "for this diagnostic."
        )
        return

    st.divider()

    st.subheader("🏁 Pricing Resilience")

    # =====================================================
    # KEY RESULT
    # =====================================================

    maximum_revenue_loss_pct = result[
        "maximum_revenue_loss_pct"
    ]

    maximum_revenue_loss = result[
        "maximum_revenue_loss"
    ]

    if maximum_revenue_loss_pct > 0:

        st.success(
            f"""
            **At a {price_cut_pct:.1f}% price reduction, the business
            can tolerate up to {maximum_revenue_loss_pct:.1f}%
            revenue loss before contribution falls below the level
            required to cover fixed costs.**
            """
        )

    else:

        st.error(
            """
            There is no revenue-loss cushion at this price reduction.
            The business would need to maintain essentially all of
            its current revenue to cover fixed costs.
            """
        )

    # =====================================================
    # THRESHOLD METRICS
    # =====================================================

    c1, c2, c3 = st.columns(3)

    c1.metric(
        "Maximum Revenue Loss",
        f"{maximum_revenue_loss_pct:.1f}%",
    )

    c2.metric(
        "Maximum Revenue Loss",
        f"€{maximum_revenue_loss:,.0f}",
    )

    c3.metric(
        "Threshold Revenue",
        f"€{result['threshold_revenue']:,.0f}",
    )

    st.divider()

    # =====================================================
    # CONTRIBUTION MARGIN
    # =====================================================

    st.subheader("Contribution Margin Impact")

    margin_delta = (
        result["new_contribution_margin_pct"]
        - result["current_contribution_margin_pct"]
    )

    c1, c2 = st.columns(2)

    c1.metric(
        "Current Contribution Margin",
        f"{result['current_contribution_margin_pct']:.1f}%",
    )

    c2.metric(
        "After Price Reduction",
        f"{result['new_contribution_margin_pct']:.1f}%",
        delta=f"{margin_delta:+.1f} pp",
    )
    # =====================================================
    # PRICE IMPACT
    # =====================================================

    st.divider()

    st.subheader("Price Impact")

    c1, c2, c3 = st.columns(3)

    c1.metric(
        "Current Price",
        f"€{price:,.2f}",
    )

    c2.metric(
        "Price After Reduction",
        f"€{result['price_after_cut']:,.2f}",
    )

    c3.metric(
        "Contribution / Unit After Reduction",
        f"€{result['new_contribution_per_unit']:,.2f}",
    )

    # =====================================================
    # THRESHOLD INTERPRETATION
    # =====================================================

    st.divider()

    st.subheader("💡 What Does This Mean?")

    st.markdown(
        f"""
        The proposed **{price_cut_pct:.1f}% price reduction** lowers
        the selling price to **€{result['price_after_cut']:,.2f}**.

        At that price, the business needs approximately
        **{result['required_volume_at_threshold']:,.0f} units**
        of sales to cover its fixed operating costs.

        This corresponds to a revenue threshold of approximately
        **€{result['threshold_revenue']:,.0f}**.

        Therefore, relative to the current revenue of
        **€{result['current_revenue']:,.0f}**, the business can tolerate
        approximately **{maximum_revenue_loss_pct:.1f}%**
        revenue loss before fixed-cost coverage is reached.
        """
    )

    # =====================================================
    # METHODOLOGY
    # =====================================================

    with st.expander(
        "ℹ️ How this diagnostic works",
        expanded=False,
    ):

        st.markdown(
            """
            The diagnostic does not forecast demand.

            It answers a financial resilience question:

            **If the company reduces price, how much revenue can it
            afford to lose before the remaining contribution is no
            longer sufficient to cover fixed operating costs?**

            The calculation uses:

            - current selling price,
            - variable cost per unit,
            - current sales volume,
            - fixed operating costs,
            - proposed price reduction.

            The diagnostic is read-only and does not create or modify
            a Decision or CompanyState.
            """
        )
