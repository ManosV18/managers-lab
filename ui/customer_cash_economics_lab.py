import pandas as pd
import streamlit as st

from diagnostics.customer_cash_economics import (
    calculate_customer_cash_cost,
    calculate_customer_portfolio_metrics,
    calculate_released_capital,
    identify_customer_extremes,
)


def render_customer_cash_economics_lab(baseline_state=None):
    st.header("👥 Customer Cash & Economics Lab")

    st.caption(
        "Which customers create economic value — and which customers consume cash?"
    )

    with st.expander(
        "💡 What question does this Lab answer?",
        expanded=False,
    ):
        st.markdown(
            """
            Not every profitable customer is economically attractive.

            A customer may generate accounting profit while consuming
            significant working capital through long payment periods,
            inventory requirements, and limited supplier credit.

            This Lab combines:

            - profitability
            - cash tied up
            - funding gap
            - cost of capital
            - economic profit

            The analysis is **diagnostic only**. It does not change the
            locked company baseline.
            """
        )

    # =========================================================
    # BASELINE WACC
    # =========================================================

    wacc = 0.0

    if baseline_state is not None:
        try:
            wacc = float(
                baseline_state.capital_structure.wacc
            )
        except (AttributeError, TypeError, ValueError):
            try:
                wacc = float(baseline_state.wacc)
            except (AttributeError, TypeError, ValueError):
                wacc = 0.0

    if baseline_state is None:
        st.warning(
            "⚠️ Lock your company baseline before running Customer Economics."
        )
        return

    # =========================================================
    # CUSTOMER INPUTS
    # =========================================================

    st.subheader("👥 Customer Portfolio")

    st.caption(
        "Enter the economics of the customers you want to compare. "
        "These inputs are used only for this diagnostic."
    )

    if "customer_economics_rows" not in st.session_state:
        st.session_state.customer_economics_rows = [
            {
                "Customer": "Customer 1",
                "Annual Revenue ($)": 500000.0,
                "Annual Gross Profit ($)": 150000.0,
                "Inventory Days": 30.0,
                "Customer Payment Days": 60.0,
                "Supplier Credit Days": 30.0,
            }
        ]

    rows = st.session_state.customer_economics_rows

    # =========================================================
    # CUSTOMER EDITORS
    # =========================================================

    updated_rows = []

    for i, row in enumerate(rows):

        with st.expander(
            f"👤 {row['Customer']}",
            expanded=(i == 0),
        ):

            c1, c2 = st.columns(2)

            customer_name = c1.text_input(
                "Customer",
                value=row["Customer"],
                key=f"customer_name_{i}",
            )

            revenue = c2.number_input(
                "Annual Revenue ($)",
                min_value=0.0,
                value=float(row["Annual Revenue ($)"]),
                step=10000.0,
                key=f"customer_revenue_{i}",
            )

            c3, c4 = st.columns(2)

            gross_profit = c3.number_input(
                "Annual Gross Profit ($)",
                min_value=0.0,
                value=float(row["Annual Gross Profit ($)"]),
                step=5000.0,
                key=f"customer_gp_{i}",
            )

            inventory_days = c4.number_input(
                "Inventory Days",
                min_value=0.0,
                value=float(row["Inventory Days"]),
                step=5.0,
                key=f"customer_inventory_{i}",
            )

            c5, c6 = st.columns(2)

            payment_days = c5.number_input(
                "Customer Payment Days",
                min_value=0.0,
                value=float(row["Customer Payment Days"]),
                step=5.0,
                key=f"customer_payment_{i}",
            )

            supplier_credit_days = c6.number_input(
                "Supplier Credit Days",
                min_value=0.0,
                value=float(row["Supplier Credit Days"]),
                step=5.0,
                key=f"customer_supplier_credit_{i}",
            )

            updated_rows.append(
                {
                    "Customer": customer_name,
                    "Annual Revenue ($)": revenue,
                    "Annual Gross Profit ($)": gross_profit,
                    "Inventory Days": inventory_days,
                    "Customer Payment Days": payment_days,
                    "Supplier Credit Days": supplier_credit_days,
                }
            )

    st.session_state.customer_economics_rows = updated_rows

    # =========================================================
    # ADD CUSTOMER
    # =========================================================

    if st.button(
        "➕ Add Customer",
        use_container_width=True,
    ):
        number = len(st.session_state.customer_economics_rows) + 1

        st.session_state.customer_economics_rows.append(
            {
                "Customer": f"Customer {number}",
                "Annual Revenue ($)": 0.0,
                "Annual Gross Profit ($)": 0.0,
                "Inventory Days": 0.0,
                "Customer Payment Days": 0.0,
                "Supplier Credit Days": 0.0,
            }
        )

        st.rerun()

    # =========================================================
    # BUILD DATAFRAME
    # =========================================================

    df = pd.DataFrame(
        st.session_state.customer_economics_rows
    )

    if df.empty:
        st.info("Add at least one customer to run the analysis.")
        return

    # =========================================================
    # COST OF CAPITAL
    # =========================================================

    st.divider()
    st.subheader("🏦 Cost of Capital")

    st.metric(
        "Baseline WACC",
        f"{wacc:.2%}",
    )

    st.caption(
        "The diagnostic uses the locked company WACC. "
        "It does not modify the baseline."
    )

    # =========================================================
    # CALCULATIONS
    # =========================================================

    result = calculate_customer_cash_cost(
        df=df,
        wacc=wacc * 100.0,
    )

    metrics = calculate_customer_portfolio_metrics(
        result
    )

    # =========================================================
    # PORTFOLIO ECONOMICS
    # =========================================================

    st.divider()
    st.subheader("📊 Portfolio Economics")

    m1, m2, m3, m4 = st.columns(4)

    m1.metric(
        "Annual Revenue",
        f"${metrics['annual_revenue']:,.0f}",
    )

    m2.metric(
        "Cash Tied Up",
        f"${metrics['cash_tied_up']:,.0f}",
    )

    m3.metric(
        "Capital Cost",
        f"${metrics['capital_cost']:,.0f}",
    )

    economic_profit = metrics["economic_profit"]

    m4.metric(
        "Economic Profit",
        f"${economic_profit:,.0f}",
    )

    if economic_profit < 0:
        st.error(
            "⚠️ The customer portfolio is economically destructive "
            "after the cost of capital."
        )
    else:
        st.success(
            "✅ The customer portfolio generates positive economic profit "
            "after the cost of capital."
        )

    # =========================================================
    # CUSTOMER BREAKDOWN
    # =========================================================

    st.divider()
    st.subheader("👥 Customer Economics Breakdown")

    display_columns = [
        "Customer",
        "Annual Revenue ($)",
        "Annual Gross Profit ($)",
        "Funding Gap Days",
        "Capital Locked ($)",
        "Capital Cost ($)",
        "Economic Profit ($)",
        "Economic Profit Margin %",
        "Classification",
    ]

    st.dataframe(
        result[display_columns],
        use_container_width=True,
        hide_index=True,
    )

    # =========================================================
    # CUSTOMER EXTREMES
    # =========================================================

    worst_customer, best_customer = identify_customer_extremes(
        result
    )

    if (
        not worst_customer.empty
        and not best_customer.empty
    ):
        st.divider()
        st.subheader("🔎 Customer Extremes")

        c1, c2 = st.columns(2)

        with c1:
            st.markdown("### 🔴 Lowest Economic Profit")

            st.markdown(
                f"**{worst_customer['Customer']}**"
            )

            st.metric(
                "Economic Profit",
                f"${worst_customer['Economic Profit ($)']:,.0f}",
            )

            st.caption(
                f"Funding gap: "
                f"{worst_customer['Funding Gap Days']:.0f} days"
            )

        with c2:
            st.markdown("### 🟢 Highest Economic Profit")

            st.markdown(
                f"**{best_customer['Customer']}**"
            )

            st.metric(
                "Economic Profit",
                f"${best_customer['Economic Profit ($)']:,.0f}",
            )

            st.caption(
                f"Funding gap: "
                f"{best_customer['Funding Gap Days']:.0f} days"
            )

    # =========================================================
    # WHAT IF CUSTOMERS PAID FASTER?
    # =========================================================

    st.divider()
    st.subheader("💧 What if customers paid faster?")

    reduction_days = st.slider(
        "Reduce customer payment days by",
        min_value=0,
        max_value=120,
        value=15,
        step=5,
        key="customer_economics_reduction_days",
    )

    released_capital = calculate_released_capital(
        result,
        reduction_days=reduction_days,
    )

    st.metric(
        "Estimated Cash Released",
        f"${released_capital:,.0f}",
    )

    st.caption(
        "Analytical estimate only. "
        "No company state or baseline assumption is changed."
    )
