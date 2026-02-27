import streamlit as st

def calculate_supplier_credit_gain(SupplierCreditDays, Discount, CashPrc, CurrentSales, UnitPrice, TotalUnitCost, InterestRateOnDebt):
    # Μετατροπή ποσοστών σε δεκαδικούς
    Discount = Discount / 100
    CashPrc = CashPrc / 100
    InterestRateOnDebt = InterestRateOnDebt / 100

    # 1. Gain from the discount on purchases
    # Χρήση 365 ημερών βάσει των οδηγιών σου
    discount_gain = CurrentSales * Discount * CashPrc

    # 2. Opportunity cost from losing supplier credit
    average_cost_ratio = TotalUnitCost / UnitPrice
    
    # Κόστος χρήσης ιδίων κεφαλαίων αντί για την άτοκη πίστωση του προμηθευτή
    credit_benefit_lost = ((CurrentSales / (365 / SupplierCreditDays)) * average_cost_ratio * CashPrc) * InterestRateOnDebt

    net_gain = discount_gain - credit_benefit_lost
    return discount_gain, credit_benefit_lost, net_gain

def format_currency(amount):
    return f"€ {amount:,.0f}".replace(",", "X").replace(".", ",").replace("X", ".")

# ΑΛΛΑΓΗ ΟΝΟΜΑΤΟΣ ΕΔΩ ΓΙΑ ΝΑ ΤΑΙΡΙΑΖΕΙ ΜΕ ΤΟ LIBRARY
def show_payables_manager():
    st.header("🤝 Payables Manager: Supplier Credit Analysis")
    st.markdown("Evaluate whether paying **cash for a discount** is more profitable than utilizing **supplier credit lines**.")

    with st.form("supplier_credit_form"):
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("Credit Terms")
            SupplierCreditDays = st.number_input("📆 Supplier Credit Period (Days)", min_value=0, value=60)
            Discount = st.number_input("💸 Cash Discount Offered (%)", min_value=0.0, value=2.0)
            CashPrc = st.number_input("👥 % of Purchases Paid in Cash", min_value=0.0, max_value=100.0, value=50.0)

        with col2:
            st.subheader("Financial Data")
            CurrentSales = st.number_input("💰 Annual Sales / Purchases Volume (€)", min_value=0, value=2000000)
            UnitPrice = st.number_input("📦 Unit Sale Price (€)", min_value=0.01, value=20.0)
            TotalUnitCost = st.number_input("🧾 Total Unit Cost (€)", min_value=0.01, value=18.0)
            InterestRateOnDebt = st.number_input("🏦 Annual Cost of Debt/Capital (%)", min_value=0.0, value=10.0)

        submitted = st.form_submit_button("🔍 Run Analysis", use_container_width=True)

    if submitted:
        discount_gain, credit_cost, net_gain = calculate_supplier_credit_gain(
            SupplierCreditDays, Discount, CashPrc,
            CurrentSales, UnitPrice, TotalUnitCost, InterestRateOnDebt
        )

        st.divider()
        st.subheader("📊 Financial Impact")
        
        m1, m2, m3 = st.columns(3)
        m1.metric("Total Discount Gain", format_currency(discount_gain))
        m2.metric("Lost Credit Opportunity Cost", f"-{format_currency(credit_cost)}")
        m3.metric("Net Financial Benefit", format_currency(net_gain), 
                  delta=f"{net_gain:,.0f} €", 
                  delta_color="normal" if net_gain >= 0 else "inverse")

        if net_gain > 0:
            st.success("✅ **Verdict:** The cash discount outweighs the cost of capital. **Switch to Cash Payments.**")
        else:
            st.error("⚠️ **Verdict:** The supplier credit is more valuable than the discount. **Maintain Credit Terms.**")

    st.divider()
    if st.button("Back to Library Hub"):
        st.session_state.selected_tool = None
        st.rerun()
