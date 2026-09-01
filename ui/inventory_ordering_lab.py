import plotly.graph_objects as go
import streamlit as st

from diagnostics.inventory_ordering import (
    calculate_inventory_metrics,
)


# =========================================================
# INVENTORY ORDERING LAB
# =========================================================
#
# Standalone analytical tool.
#
# Question:
#
# "How much inventory should I order?"
#
# This Lab does not modify the locked baseline.
# It does not create a CompanyState decision.
#
# =========================================================


def render_inventory_ordering_lab(baseline_state=None):

    st.header("📦 How Much Inventory Should I Order?")

    st.caption(
        "Find the order quantity that minimizes inventory costs "
        "while balancing ordering costs, holding costs and capital tied up."
    )

    # =====================================================
    # EXPLANATION
    # =====================================================

    with st.expander(
        "💡 What question does this Lab answer?",
        expanded=True,
    ):
        st.markdown(
            """
            Inventory creates a trade-off.

            Ordering too frequently increases:

            - purchasing costs
            - administration
            - logistics costs

            Ordering too much increases:

            - inventory held in the warehouse
            - working capital tied up
            - financing costs
            - storage costs

            This Lab answers:

            **"What order quantity minimizes my inventory-related costs?"**

            The analysis is performed for one inventory item
            or SKU at a time.

            It is a standalone analysis and does not change
            the locked company baseline.
            """
        )

    # =====================================================
    # INPUTS
    # =====================================================

    st.divider()

    st.subheader("🛠️ Inventory & Cost Assumptions")

    col_a, col_b = st.columns(2)

    with col_a:

        annual_demand = st.number_input(
            "Annual Demand (Units)",
            min_value=1.0,
            value=10000.0,
            step=500.0,
            help=(
                "Expected annual demand for this inventory item."
            ),
        )

        unit_price = st.number_input(
            "Purchase Price per Unit ($)",
            min_value=0.01,
            value=30.0,
            step=1.0,
            help=(
                "Supplier purchase price per unit before discounts."
            ),
        )

        ordering_cost = st.number_input(
            "Ordering Cost per Order ($)",
            min_value=0.0,
            value=600.0,
            step=50.0,
            help=(
                "Administrative, shipping, handling and procurement "
                "cost incurred every time an order is placed."
            ),
        )

        discount_pct_input = st.number_input(
            "Supplier Discount (%)",
            min_value=0.0,
            max_value=99.0,
            value=0.0,
            step=1.0,
            help=(
                "Discount applied to the purchase price."
            ),
        )

        discount_pct = (
            discount_pct_input / 100.0
        )

    with col_b:

        annual_interest_rate_input = st.number_input(
            "Annual Cost of Capital (%)",
            min_value=0.0,
            max_value=100.0,
            value=5.0,
            step=0.5,
            help=(
                "Cost of financing the capital tied up in inventory."
            ),
        )

        annual_interest_rate = (
            annual_interest_rate_input / 100.0
        )

        maintenance_pm = st.number_input(
            "Warehouse Operating Cost ($/Month)",
            min_value=0.0,
            value=600.0,
            step=50.0,
            help=(
                "Monthly warehouse rent, utilities and maintenance."
            ),
        )

        insurance_pm = st.number_input(
            "Insurance & Handling ($/Month)",
            min_value=0.0,
            value=0.0,
            step=25.0,
        )

        months = st.number_input(
            "Analysis Period (Months)",
            min_value=1.0,
            max_value=60.0,
            value=12.0,
            step=1.0,
        )

    # =====================================================
    # CALCULATE
    # =====================================================

    result = calculate_inventory_metrics(
        unit_price=unit_price,
        annual_demand=annual_demand,
        ordering_cost=ordering_cost,
        discount_pct=discount_pct,
        insurance_pm=insurance_pm,
        annual_interest_rate=annual_interest_rate,
        months=months,
        maintenance_pm=maintenance_pm,
    )

    if result is None:

        st.error(
            "⚠️ The current assumptions cannot produce "
            "a valid EOQ calculation."
        )

        st.info(
            "Check that demand, price and the analysis period "
            "are positive and that the carrying cost is above zero."
        )

        return

    # =====================================================
    # RECOMMENDED ORDERING POLICY
    # =====================================================

    st.divider()

    st.subheader("📊 Recommended Ordering Policy")

    m1, m2, m3, m4 = st.columns(4)

    m1.metric(
        "Optimal Order Quantity",
        f"{result['eoq']:,.0f} units",
        help=(
            "The estimated order quantity that minimizes "
            "ordering and inventory carrying costs."
        ),
    )

    m2.metric(
        "Orders per Period",
        f"{result['orders']:.2f}",
    )

    m3.metric(
        "Average Cash Tied Up",
        f"${result['capital_tied_up']:,.0f}",
        help=(
            "Estimated average capital tied up in this inventory item."
        ),
    )

    m4.metric(
        "Total Inventory Cost",
        f"${result['total_cost']:,.0f}",
        help=(
            "Purchase cost plus ordering and holding costs."
        ),
    )

    # =====================================================
    # COST COMPONENTS
    # =====================================================

    st.divider()

    st.subheader("💰 Inventory Cost Breakdown")

    c1, c2, c3 = st.columns(3)

    c1.metric(
        "Purchase Cost",
        f"${result['purchase_cost']:,.0f}",
    )

    c2.metric(
        "Ordering Cost",
        f"${result['ordering_cost']:,.0f}",
    )

    c3.metric(
        "Holding & Capital Cost",
        f"${result['holding_cost']:,.0f}",
    )

    # =====================================================
    # CALCULATE ORDERING CADENCE
    # =====================================================

    days_between_orders = 0.0

    if result["orders"] > 0:

        days_between_orders = (
            months * 30.4375
        ) / result["orders"]

    # =====================================================
    # CHARTS
    # =====================================================

    st.divider()

    col_chart1, col_chart2 = st.columns(2)

    # -----------------------------------------------------
    # EOQ COST CURVE
    # -----------------------------------------------------

    with col_chart1:

        st.subheader("📈 Cost vs Order Quantity")

        q_min = max(
            1,
            int(result["eoq"] * 0.20),
        )

        q_max = max(
            q_min + 2,
            int(result["eoq"] * 2.50),
        )

        step = max(
            1,
            int((q_max - q_min) / 60),
        )

        q_range = list(
            range(q_min, q_max + 1, step)
        )

        ordering_costs = [
            (
                annual_demand / q
            ) * ordering_cost
            for q in q_range
        ]

        holding_costs = [
            result["carrying_rate"]
            * (q / 2.0)
            * unit_price
            for q in q_range
        ]

        total_operating_costs = [
            order_cost + holding_cost
            for order_cost, holding_cost
            in zip(
                ordering_costs,
                holding_costs,
            )
        ]

        fig_curve = go.Figure()

        fig_curve.add_trace(
            go.Scatter(
                x=q_range,
                y=ordering_costs,
                mode="lines",
                name="Ordering Cost",
            )
        )

        fig_curve.add_trace(
            go.Scatter(
                x=q_range,
                y=holding_costs,
                mode="lines",
                name="Holding Cost",
            )
        )

        fig_curve.add_trace(
            go.Scatter(
                x=q_range,
                y=total_operating_costs,
                mode="lines",
                name="Total Operating Cost",
            )
        )

        fig_curve.add_vline(
            x=result["eoq"],
            line_width=2,
            line_dash="dot",
            annotation_text=(
                f"EOQ: {result['eoq']:,.0f}"
            ),
        )

        fig_curve.update_layout(
            xaxis_title="Order Quantity (Units)",
            yaxis_title="Cost ($)",
            height=400,
            margin=dict(
                l=20,
                r=20,
                t=40,
                b=20,
            ),
            legend=dict(
                orientation="h",
                y=-0.20,
            ),
        )

        st.plotly_chart(
            fig_curve,
            use_container_width=True,
        )

    # -----------------------------------------------------
    # COST BREAKDOWN CHART
    # -----------------------------------------------------

    with col_chart2:

        st.subheader("📊 Where Your Inventory Money Goes")

        fig_bar = go.Figure()

        fig_bar.add_trace(
            go.Bar(
                x=[
                    "Purchase",
                    "Ordering",
                    "Holding",
                ],
                y=[
                    result["purchase_cost"],
                    result["ordering_cost"],
                    result["holding_cost"],
                ],
                text=[
                    f"${result['purchase_cost']:,.0f}",
                    f"${result['ordering_cost']:,.0f}",
                    f"${result['holding_cost']:,.0f}",
                ],
                textposition="auto",
            )
        )

        fig_bar.update_layout(
            yaxis_title="Amount ($)",
            height=400,
            margin=dict(
                l=20,
                r=20,
                t=40,
                b=20,
            ),
        )

        st.plotly_chart(
            fig_bar,
            use_container_width=True,
        )

    # =====================================================
    # OPERATIONAL INSIGHTS
    # =====================================================

    st.divider()

    st.subheader("💡 Operational Insights")

    col_diag1, col_diag2 = st.columns(2)

    with col_diag1:

        st.markdown("#### 🔍 Ordering Dynamics")

        st.markdown(
            f"""
            - **Recommended order size:** {result['eoq']:,.0f} units
            - **Orders during the period:** {result['orders']:.1f}
            - **Approximate time between orders:** {days_between_orders:.1f} days
            - **Inventory carrying rate:** {result['carrying_rate'] * 100:.2f}%
            """
        )

        if (
            result["ordering_cost"]
            > result["holding_cost"] * 1.30
        ):

            st.warning(
                "Ordering costs are materially higher than holding costs. "
                "Frequent ordering may be creating unnecessary procurement "
                "and administration costs."
            )

        elif (
            result["holding_cost"]
            > result["ordering_cost"] * 1.30
        ):

            st.warning(
                "Holding costs are materially higher than ordering costs. "
                "Large inventory positions may be tying up excessive capital."
            )

        else:

            st.success(
                "Ordering and holding costs are relatively balanced "
                "around the economic optimum."
            )

    with col_diag2:

        st.markdown("#### 💰 Working Capital Impact")

        potential_release = (
            result["capital_tied_up"] * 0.10
        )

        st.markdown(
            f"""
            - **Average capital tied up:** ${result['capital_tied_up']:,.0f}
            - **Cost of capital for the period:** {result['interest_pct'] * 100:.2f}%
            - **Storage cost rate:** {result['storage_pct'] * 100:.2f}%
            - **Illustrative cash released from a 10% reduction in average inventory:** ${potential_release:,.0f}
            """
        )

    # =====================================================
    # MANAGEMENT INTERPRETATION
    # =====================================================

    st.divider()

    st.subheader("🎯 Management Interpretation")

    if result["orders"] < 3:

        st.warning(
            "You place very few orders during the period. "
            "This may reduce procurement costs, but it can also "
            "increase inventory investment and cash tied up."
        )

    elif result["orders"] > 12:

        st.warning(
            "You reorder frequently. "
            "This keeps inventory lean but can make ordering "
            "and logistics costs more significant."
        )

    else:

        st.success(
            "Your recommended replenishment frequency represents "
            "a balance between procurement efficiency and "
            "inventory investment."
        )

    # =====================================================
    # EXECUTIVE RECOMMENDATION
    # =====================================================

    st.divider()

    st.subheader("📝 Executive Recommendation")

    if (
        result["ordering_cost"]
        > result["holding_cost"] * 1.30
    ):

        recommendation = f"""
Your current economics indicate relatively high ordering friction.

The estimated cost-minimizing order quantity is **{result['eoq']:,.0f} units**.

This corresponds to approximately **{result['orders']:.1f} orders**
during the analysis period, or one order roughly every
**{days_between_orders:.0f} days**.

The main management issue is the cost of placing and processing
orders. Larger order batches may reduce procurement friction,
provided that inventory carrying costs remain under control.
"""

    elif (
        result["holding_cost"]
        > result["ordering_cost"] * 1.30
    ):

        recommendation = f"""
Your inventory economics indicate significant carrying pressure.

The estimated cost-minimizing order quantity is **{result['eoq']:,.0f} units**.

Average inventory at this policy ties up approximately
**${result['capital_tied_up']:,.0f}** in capital.

The main management priority is avoiding unnecessary inventory
investment while maintaining adequate product availability.
Smaller and more frequent replenishment may be economically
preferable if ordering costs can be controlled.
"""

    else:

        recommendation = f"""
Your ordering economics are relatively balanced.

The estimated cost-minimizing order quantity is **{result['eoq']:,.0f} units**.

This corresponds to approximately **{result['orders']:.1f} orders**
during the analysis period, or roughly one order every
**{days_between_orders:.0f} days**.

Under the current assumptions, this policy balances procurement
costs against inventory holding and capital costs.
"""

    st.info(recommendation)

    # =====================================================
    # KEY TAKEAWAYS
    # =====================================================

    st.divider()

    st.subheader("📌 Key Takeaways")

    st.markdown(
        f"""
        - **Recommended Order Quantity:** {result['eoq']:,.0f} units
        - **Orders During Period:** {result['orders']:.1f}
        - **Average Time Between Orders:** {days_between_orders:.0f} days
        - **Average Cash Locked in Inventory:** ${result['capital_tied_up']:,.0f}
        - **Total Inventory Cost:** ${result['total_cost']:,.0f}
        """
    )
