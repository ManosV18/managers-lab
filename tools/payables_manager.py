import streamlit as st
from core.sync import sync_global_state

def calculate_supplier_credit_gain(SupplierCreditDays, Discount, CashPrc, CurrentSales, UnitPrice, TotalUnitCost, InterestRateOnDebt):
    # Conversion to decimals
    Discount = Discount / 100
    CashPrc = CashPrc / 100
    InterestRateOnDebt = InterestRateOnDebt / 100

    # 1. Gain from the discount on purchases (Total volume of purchases approached via Sales/Cost Ratio)
    # Using 365 days as per instructions
    discount_gain = CurrentSales * Discount * CashPrc

    # 2. Opportunity cost from losing supplier credit
    # We measure the cost of replacing interest-free supplier capital with bank debt/own capital
    average_cost_ratio = TotalUnitCost / UnitPrice if UnitPrice > 0 else 0
    
    # Capital needed = (Daily Purchases * Credit Days) * % shifted to cash
    credit_benefit_lost = ((CurrentSales / 365) * SupplierCreditDays * average_cost_ratio * CashPrc) * InterestRateOnDebt

    net_gain = discount_gain - credit_benefit_lost
    return discount_gain, credit_benefit_lost, net_gain

def format_currency(amount):
    return f"€ {amount:,.0f}"

def show_payables_manager():
    # 1. SYNC WITH GLOBAL BASELINE
    metrics = sync_global_state()
    s = st.session_state
    
    # Auto-fetch constants from Stage 0
    sys_sales = float(metrics.get('revenue', 0.0))
    sys_unit_price = float(s.get('price', 1.0))
    sys_unit_cost = float(s.get('variable_cost', 0.0)) + (float(s.get('fixed_costs', 0.0)) / float(s.get('volume', 1)) if float(s.get('volume', 1)) > 0 else 0)
    sys_wacc = float(s.get('wacc', 0.10))
    sys_ap_days = float(s.get('ap_days', 60))

    st.header("🤝 Payables Manager: Supplier Credit Analysis")
    st.info("Decision Matrix: Compare the benefit of a Cash Discount vs. the value of Interest-Free Supplier Credit.")

    with st.form("supplier_credit_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### ⚙️ Credit Policy Assumptions")
            # Editable: The terms the supplier is offering now
            Discount = st.number_input("💸 Cash Discount Offered (%)", min_value=0.0, value=2.0, step=0.1)
            CashPrc = st.number_input("👥 % of Purchases to Shift to Cash", min_value=0.0, max_value=100.0, value=100.0)
            
            st.markdown("### 🔒 Locked Baseline Constants")
            # Locked: Sourced from Stage 0
            SupplierCreditDays = st.number_input("📆 Current Credit Period (Days)", value=int(sys_ap_days), disabled=True)
            CurrentSales = st.number_input("💰 Annual Sales Volume (€)", value=sys_sales, disabled=True)

        with col2:
            st.markdown("### 📊 Financial Framework")
            # Locked: Cost of Capital and Margins
            InterestRateOnDebt = st.number_input("🏦 Annual Cost of Capital (WACC %)", value=sys_wacc * 100, disabled=True)
            UnitPrice = st.number_input("📦 Unit Sale Price (€)", value=sys_unit_price, disabled=True)
            TotalUnitCost = st.number_input("🧾 Total Unit Cost (€)", value=sys_unit_cost, disabled=True)

        submitted = st.form_submit_button("🔍 Run Financial Analysis", use_container_width=True)

    if submitted:
        discount_gain, credit_cost, net_gain = calculate_supplier_credit_gain(
            SupplierCreditDays, Discount, CashPrc,
            CurrentSales, UnitPrice, TotalUnitCost, InterestRateOnDebt
        )

        st.divider()
        st.subheader("📈 Results & Verdict")
        
        m1, m2, m3 = st.columns(3)
        m1.metric("Discount Gain", format_currency(discount_gain))
        m2.metric("Cost of Capital Replace", f"-{format_currency(credit_cost)}")
        m3.metric("Net Economic Benefit", format_currency(net_gain), 
                  delta=f"{net_gain:,.0f} €", 
                  delta_color="normal" if net_gain >= 0 else "inverse")

        

        if net_gain > 0:
            st.success("✅ **STRATEGIC VERDICT:** The discount is mathematically superior. Paying cash generates more value than the credit line.")
            if st.button("🚀 Update Baseline AP Days to 0 (Cash)"):
                st.session_state.ap_days = 0
                st.rerun()
        else:
            st.error("⚠️ **STRATEGIC VERDICT:** The interest-free credit is more valuable than the discount. Do NOT pay cash.")

    st.divider()
    if st.button("Back to Library Hub"):
        st.session_state.selected_tool = None
        st.rerun()
