import math

import pandas as pd
import streamlit as st

from diagnostics.customer_cash_economics import (
    calculate_break_even_gross_profit,
    calculate_break_even_lifetime,
    calculate_customer_cash_cost,
    calculate_customer_npv,
    calculate_customer_portfolio_metrics,
    calculate_expected_customer_lifespan,
    calculate_released_capital,
    identify_customer_extremes,
)


def _get_baseline_wacc(baseline_state) -> float:
    try:
        return float(
            baseline_state.capital_structure.wacc
        )
    except (AttributeError, TypeError, ValueError):
        try:
            return float(baseline_state.wacc)
        except (AttributeError, TypeError, ValueError):
            return 0.0


def _get_baseline_wc(baseline_state):
    try:
        wc = baseline_state.working_capital

        return {
            "ar_days": float(wc.ar_days),
            "inventory_days": float(wc.inventory_days),
            "ap_days": float(wc.ap_days),
        }

    except (AttributeError, TypeError, ValueError):
        return {
            "ar_days": 60.0,
            "inventory_days": 30.0,
            "ap_days": 30.0,
        }


def render_customer_cash_economics_lab(
    baseline_state=None,
):

    st.header("👥 Customer Value")

    st.caption(
        "Which customers are really worth keeping — and under what conditions?"
    )

    if baseline_state is None:
        st.warning(
            "⚠️ Lock your company baseline before running Customer Cash Economics."
        )
        return

    wacc = _get_baseline_wacc(
        baseline_state
    )

    baseline_wc = _get_baseline_wc(
        baseline_state
    )

    # =====================================================
    # EXPLANATION
    # =====================================================

    with st.expander(
        "💡 What question does this Lab answer?",
        expanded=False,
    ):
        st.markdown(
            """
            See how much value a customer creates, how much cash they require,
            and how that value changes when key conditions change.
            """
        )

    # =====================================================
    # CUSTOMER INPUT
    # =====================================================

    st.subheader("👤 Customer Economics")

    st.caption(
        "Enter the economics of the customer you want to evaluate."
    )

    c1, c2 = st.columns(2)

    customer_name = c1.text_input(
        "Customer",
        value="Customer 1",
        key="customer_cash_economics_name",
    )

    annual_revenue = c2.number_input(
        "Annual Revenue (€)",
        min_value=0.0,
        value=500000.0,
        step=10000.0,
        key="customer_cash_economics_revenue",
    )

    c3, c4 = st.columns(2)

    annual_gross_profit = c3.number_input(
        "Annual Gross Profit (€)",
        min_value=0.0,
        value=150000.0,
        step=5000.0,
        key="customer_cash_economics_gp",
    )

    customer_specific_costs = c4.number_input(
        "Annual Customer-Specific Costs (€)",
        min_value=0.0,
        value=0.0,
        step=1000.0,
        help=(
            "Only directly attributable recurring costs: "
            "special service, commissions, dedicated logistics, "
            "customer-specific marketing, etc."
        ),
        key="customer_cash_economics_direct_costs",
    )

    # =====================================================
    # WORKING CAPITAL
    # =====================================================

    st.divider()
    st.subheader("💧 Customer Cash Requirement")

    use_baseline_wc = st.checkbox(
        "Use company working-capital baseline as starting assumptions",
        value=True,
        key="customer_cash_economics_use_baseline_wc",
    )

    if use_baseline_wc:
        payment_default = baseline_wc["ar_days"]
        inventory_default = baseline_wc["inventory_days"]
        supplier_default = baseline_wc["ap_days"]

        st.caption(
            "Values below start from the locked company working-capital baseline. "
            "You can still adjust them for this customer."
        )
    else:
        payment_default = 60.0
        inventory_default = 30.0
        supplier_default = 30.0

    c5, c6, c7 = st.columns(3)

    payment_days = c5.number_input(
        "Customer Payment Days",
        min_value=0.0,
        value=float(payment_default),
        step=5.0,
        key="customer_cash_economics_payment_days",
    )

    inventory_days = c6.number_input(
        "Inventory Days",
        min_value=0.0,
        value=float(inventory_default),
        step=5.0,
        key="customer_cash_economics_inventory_days",
    )

    supplier_credit_days = c7.number_input(
        "Supplier Credit Days",
        min_value=0.0,
        value=float(supplier_default),
        step=5.0,
        key="customer_cash_economics_supplier_days",
    )

    # =====================================================
    # CURRENT ECONOMICS
    # =====================================================

    df = pd.DataFrame(
        [
            {
                "Customer": customer_name,
                "Annual Revenue ($)": annual_revenue,
                "Annual Gross Profit ($)": annual_gross_profit,
                "Inventory Days": inventory_days,
                "Customer Payment Days": payment_days,
                "Supplier Credit Days": supplier_credit_days,
            }
        ]
    )

    current_result = calculate_customer_cash_cost(
        df=df,
        wacc=wacc * 100.0,
    )

    row = current_result.iloc[0]

    st.divider()
    st.subheader("📊 Current Customer Value")

    m1, m2, m3, m4 = st.columns(4)

    m1.metric(
        "Annual Gross Profit",
        f"€ {annual_gross_profit:,.0f}",
    )

    m2.metric(
        "Cash Tied Up",
        f"€ {row['Capital Locked ($)']:,.0f}",
    )

    m3.metric(
        "Annual Capital Cost",
        f"€ {row['Capital Cost ($)']:,.0f}",
    )

    m4.metric(
        "Economic Profit",
        f"€ {row['Economic Profit ($)']:,.0f}",
    )

    st.caption(
        f"Funding gap: {row['Funding Gap Days']:.0f} days  |  "
        f"Baseline WACC: {wacc:.2%}"
    )

    # =====================================================
    # CUSTOMER VALUE ASSUMPTIONS
    # =====================================================

    st.divider()
    st.subheader("📈 Customer Value Over Time")

    st.caption(
        "See whether the customer creates enough value over the expected relationship lifetime."
    )

    c8, c9 = st.columns(2)

    cac = c8.number_input(
        "Customer Acquisition Cost — CAC (€)",
        min_value=0.0,
        value=150.0,
        step=10.0,
        help="Initial customer acquisition investment.",
        key="customer_cash_economics_cac",
    )

    retention_rate = c9.slider(
        "Annual Customer Retention Rate",
        min_value=0,
        max_value=100,
        value=80,
        step=1,
        key="customer_cash_economics_retention",
    )

    expected_lifetime = calculate_expected_customer_lifespan(
        retention_rate
    )

    st.info(
        f"Expected customer lifetime from retention: "
        f"**{expected_lifetime:.1f} years**"
    )

    use_expected_lifetime = st.checkbox(
        "Use expected lifetime for the NPV analysis",
        value=True,
        key="customer_cash_economics_use_expected_lifetime",
    )

    if use_expected_lifetime:
        lifetime_years = max(
            1,
            min(
                15,
                int(math.ceil(expected_lifetime)),
            ),
        )
    else:
        lifetime_years = st.slider(
            "Analysis Horizon (Years)",
            min_value=1,
            max_value=15,
            value=max(
                1,
                min(
                    15,
                    int(math.ceil(expected_lifetime)),
                ),
            ),
            step=1,
            key="customer_cash_economics_lifetime",
        )

    st.caption(
        f"Discount rate / WACC: **{wacc:.2%}**"
    )

    # =====================================================
    # NPV
    # =====================================================

    npv_result = calculate_customer_npv(
        annual_revenue=annual_revenue,
        annual_gross_profit=annual_gross_profit,
        customer_specific_annual_costs=customer_specific_costs,
        cac=cac,
        retention_rate_pct=float(retention_rate),
        discount_rate_pct=wacc * 100.0,
        payment_days=payment_days,
        inventory_days=inventory_days,
        supplier_credit_days=supplier_credit_days,
        lifetime_years=lifetime_years,
    )

    customer_npv = npv_result["npv"]
    initial_nwc = npv_result["initial_working_capital"]
    initial_investment = npv_result["initial_investment"]
    payback_year = npv_result["payback_year"]

    n1, n2, n3, n4 = st.columns(4)

    n1.metric(
        "Customer Economic NPV",
        f"€ {customer_npv:,.0f}",
    )

    n2.metric(
        "Initial Working Capital",
        f"€ {initial_nwc:,.0f}",
    )

    n3.metric(
        "Initial Investment",
        f"€ {initial_investment:,.0f}",
    )

    n4.metric(
        "Payback",
        (
            f"Year {payback_year}"
            if payback_year is not None
            else "Not reached"
        ),
    )

    if customer_npv >= 0:
        st.success(
            f"🟢 {customer_name} produces positive discounted economic value "
            f"under the current assumptions."
        )
    else:
        st.warning(
            f"🟠 {customer_name} does not recover its initial investment "
            f"within the analysed customer lifetime."
        )

    # =====================================================
    # CASH FLOW TABLE
    # =====================================================

    st.subheader("📅 Customer Cash Flow")

    yearly_df = pd.DataFrame(
        npv_result["yearly_data"]
    )

    display_yearly = yearly_df.copy()

    display_yearly["Survival Probability"] = (
        display_yearly["Survival_Probability"] * 100.0
    )

    display_yearly = display_yearly[
        [
            "Year",
            "Survival Probability",
            "Customer_Contribution",
            "Working_Capital_Investment",
            "Net_Cash_Flow",
            "Discounted_Cash_Flow",
            "Cumulative_NPV",
        ]
    ].rename(
        columns={
            "Customer_Contribution":
                "Customer Contribution (€)",
            "Working_Capital_Investment":
                "Working Capital Change (€)",
            "Net_Cash_Flow":
                "Net Cash Flow (€)",
            "Discounted_Cash_Flow":
                "Discounted Cash Flow (€)",
            "Cumulative_NPV":
                "Cumulative NPV (€)",
        }
    )

    st.dataframe(
        display_yearly,
        use_container_width=True,
        hide_index=True,
    )

    # =====================================================
    # BREAK-EVEN
    # =====================================================

    st.divider()
    st.subheader("🎯 Economic Break-Even")

    st.caption(
        "What condition must change for this customer relationship to reach NPV = €0?"
    )

    max_cac = npv_result["npv"] + cac

    break_even_gp = calculate_break_even_gross_profit(
        annual_revenue=annual_revenue,
        customer_specific_annual_costs=customer_specific_costs,
        cac=cac,
        retention_rate_pct=float(retention_rate),
        discount_rate_pct=wacc * 100.0,
        payment_days=payment_days,
        inventory_days=inventory_days,
        supplier_credit_days=supplier_credit_days,
        lifetime_years=lifetime_years,
    )

    break_even_margin = (
        break_even_gp / annual_revenue * 100.0
        if annual_revenue > 0
        else 0.0
    )

    break_even_lifetime = calculate_break_even_lifetime(
        annual_revenue=annual_revenue,
        annual_gross_profit=annual_gross_profit,
        customer_specific_annual_costs=customer_specific_costs,
        cac=cac,
        retention_rate_pct=float(retention_rate),
        discount_rate_pct=wacc * 100.0,
        payment_days=payment_days,
        inventory_days=inventory_days,
        supplier_credit_days=supplier_credit_days,
    )

    b1, b2, b3 = st.columns(3)

    b1.metric(
        "Maximum CAC",
        f"€ {max_cac:,.0f}",
    )

    b2.metric(
        "Break-Even Gross Margin",
        f"{break_even_margin:.1f}%",
    )

    b3.metric(
        "Break-Even Lifetime",
        (
            f"{break_even_lifetime} years"
            if break_even_lifetime is not None
            else ">15 years"
        ),
    )

    # =====================================================
    # CURRENT vs BREAK-EVEN
    # =====================================================

    current_margin = (
        annual_gross_profit
        / annual_revenue
        * 100.0
        if annual_revenue > 0
        else 0.0
    )

    st.markdown(
        f"""
        **Current conditions**

        - Gross margin: **{current_margin:.1f}%**
        - CAC: **€ {cac:,.0f}**
        - Expected lifetime: **{expected_lifetime:.1f} years**
        - Customer payment: **{payment_days:.0f} days**
        - Customer NPV: **€ {customer_npv:,.0f}**
        """
    )

    st.caption(
        "Break-even figures are analytical thresholds. "
        "They do not change the company baseline or create a Decision Plan."
    )

    # ============================================================
    # DISCOUNT SENSITIVITY
    # ============================================================

    st.subheader("How much discount can this customer absorb?")

    current_npv = npv_result["npv"]
    gross_margin_pct = (
        annual_gross_profit / annual_revenue * 100
        if annual_revenue > 0
        else 0.0
    )

    max_discount = 0.0

    if current_npv > 0 and gross_margin_pct > 0:
        low = 0.0
        high = gross_margin_pct

        for _ in range(60):
            mid = (low + high) / 2

            discount_factor = mid / 100.0

            discounted_revenue = annual_revenue * (1 - discount_factor)

            discounted_gross_profit = max(
                annual_gross_profit - annual_revenue * discount_factor,
                0.0,
            )

            test_npv = calculate_customer_npv(
                annual_revenue=discounted_revenue,
                annual_gross_profit=discounted_gross_profit,
                customer_specific_annual_costs=customer_specific_costs,
                cac=cac,
                retention_rate_pct=retention_rate,
                discount_rate_pct=wacc * 100.0,
                payment_days=payment_days,
                inventory_days=inventory_days,
                supplier_credit_days=supplier_credit_days,
                lifetime_years=lifetime_years,
            )["npv"]

            if test_npv >= 0:
                low = mid
            else:
                high = mid

        max_discount = low

    st.error("How much discount can this customer absorb?")
    discount = st.slider(
        "Customer discount (%)",
        min_value=0.0,
        max_value=float(gross_margin_pct),
        value=0.0,
        step=0.5,
        key="clv_discount_sensitivity",
    )

    discount_factor = discount / 100.0
    discounted_revenue = annual_revenue * (1 - discount_factor)
    discounted_gross_profit = max(
        annual_gross_profit - annual_revenue * discount_factor,
        0.0,
    )

    discounted_npv_result = calculate_customer_npv(
        annual_revenue=discounted_revenue,
        annual_gross_profit=discounted_gross_profit,
        customer_specific_annual_costs=customer_specific_costs,
        cac=cac,
        retention_rate_pct=retention_rate,
        discount_rate_pct=wacc * 100.0,
        payment_days=payment_days,
        inventory_days=inventory_days,
        supplier_credit_days=supplier_credit_days,
        lifetime_years=lifetime_years,
    )

    discounted_npv = discounted_npv_result["npv"]

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Discount", f"{discount:.1f}%")

    with col2:
        st.metric(
            "Discount Value",
            f"€{annual_revenue * discount_factor:,.0f}"
        )

    with col3:
        st.metric(
            "Customer NPV",
            f"€{discounted_npv:,.0f}"
        )

    if max_discount > 0:
        st.success(
            f"Maximum sustainable discount: **{max_discount:.1f}%** "
            f"before customer NPV reaches zero."
        )
    elif current_npv <= 0:
        st.warning(
            "This customer is already at or below zero economic NPV. "
            "There is no sustainable discount."
        )
    else:
        st.warning(
            "No additional discount is economically sustainable."
        )

    # =====================================================
    # EXISTING CASH WHAT-IF
    # =====================================================

    st.divider()
    st.subheader("💧 What if the customer paid faster?")

    reduction_days = st.slider(
        "Reduce customer payment days by",
        min_value=0,
        max_value=120,
        value=15,
        step=5,
        key="customer_cash_economics_reduction_days",
    )

    released_capital = calculate_released_capital(
        current_result,
        reduction_days=reduction_days,
    )

    st.metric(
        "Estimated Cash Released",
        f"€ {released_capital:,.0f}",
    )

    st.caption(
        "Analytical estimate only. No company state or baseline assumption is changed."
    )
