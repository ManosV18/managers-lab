import streamlit as st

# ===== Calculation Logic =====
def calculate_supplier_credit_gain(
    supplier_credit_days,
    discount_pct,
    clients_pct,
    current_sales,
    unit_price,
    total_unit_cost,
    interest_rate_pct
):
    """
    Compute the financial impact of taking supplier credit versus paying early for a discount.

    Returns:
        discount_gain: Gain from paying early and taking the discount
        credit_cost: Opportunity cost of giving up credit terms
        net_gain: Net benefit of paying early
    """
    discount = discount_pct / 100
    clients = clients_pct / 100
    interest_rate = interest_rate_pct / 100

    # Gain from discount for early payment
    discount_gain = current_sales * discount * clients

    # Opportunity cost from lost supplier credit
    average_cost_ratio = total_unit_cost / unit_price
    credit_benefit = (
        (current_sales / (360 / supplier_credit_days)) * average_cost_ratio
        - ((current_sales * (1 - clients)) / (360 / supplier_credit_days)) * average_cost_ratio
    ) * interest_rate

    net_gain = discount_gain - credit_benefit
    return discount_gain, credit_benefit, net_gain

# ===== Utility =====
def format_currency(amount):
    return f"€ {amount:,.0f}".replace(",", ".")

# ===== Streamlit UI =====
def show_supplier_credit_analysis():
    st.title("🏦 Supplier Credit Analysis")
    st.caption(
        "Evaluate whether **early payment with a discount** is more profitable than taking supplier credit."
    )

    # ===== Input Form =====
    with st.form("supplier_credit_form"):
        st.header("🔢 Input Data")

        st.subheader("📋 Supplier Terms & Discount")
        col1, col2 = st.columns(2)

        with col1:
            supplier_credit_days = st.number_input(
                "📆 Supplier Credit Days",
                min_value=0,
                value=60
            )
            st.caption("Number of days the supplier allows you to delay payment without penalty.")

            discount_pct = st.number_input(
                "💸 Early Payment Discount (%)",
                min_value=0.0,
                value=2.0
            )
            st.caption("Percentage discount offered if you pay earlier than the credit period.")

            clients_pct = st.number_input(
                "👥 % of Sales Paid in Cash",
                min_value=0.0,
                max_value=100.0,
                value=50.0
            )
            st.caption("Proportion of sales where customers pay immediately (cash) vs on credit.")

        with col2:
            current_sales = st.number_input(
                "💰 Current Sales (€)",
                min_value=0.0,
                value=2_000_000.0,
                step=1_000.0,
                format="%.0f"
            )
            st.caption("Total revenue from sales over the period considered.")

            unit_price = st.number_input(
                "📦 Unit Price (€)",
                min_value=0.01,
                value=20.0
            )
            st.caption("Price per unit sold.")

            total_unit_cost = st.number_input(
                "🧾 Total Unit Cost (€)",
                min_value=0.01,
                value=18.0
            )
            st.caption("Total cost per unit including materials, labor, and overhead.")

            interest_rate_pct = st.number_input(
                "🏦 Cost of Capital (%)",
                min_value=0.0,
                value=10.0
            )
            st.caption("Opportunity cost of capital (annualized rate).")

        submitted = st.form_submit_button("🔍 Calculate")

    # ===== Results =====
    if submitted:
        discount_gain, credit_cost, net_gain = calculate_supplier_credit_gain(
            supplier_credit_days, discount_pct, clients_pct,
            current_sales, unit_price, total_unit_cost, interest_rate_pct
        )

        st.markdown("---")
        st.subheader("📊 Results")

        col1, col2, col3 = st.columns(3)
        col1.metric("✅ Gain from Discount", format_currency(discount_gain))
        col2.metric("💸 Credit Opportunity Cost", format_currency(credit_cost))
        col3.metric(
            "🏁 Net Benefit",
            format_currency(net_gain),
            delta_color="normal" if net_gain >= 0 else "inverse"
        )

        st.caption(
            "Discount Gain: benefit from paying early.\n"
            "Credit Opportunity Cost: value lost by not using supplier credit.\n"
            "Net Benefit: overall financial impact of the early payment decision."
        )

        if net_gain > 0:
            st.success("👉 Early payment with this discount is profitable.")
        else:
            st.error("⚠️ Early payment with this discount is not profitable.")
