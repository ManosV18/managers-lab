import streamlit as st

def calculate_supplier_credit_gain(SupplierCreditDays, Discount, CashPrc, CurrentSales, UnitPrice, TotalUnitCost, InterestRateOnDebt):
    # Μετατροπή ποσοστών σε δεκαδικούς
    Discount = Discount / 100
    CashPrc = CashPrc / 100
    InterestRateOnDebt = InterestRateOnDebt / 100

    # 1. Gain from the discount on purchases
    # Το άμεσο κέρδος από την έκπτωση που προσφέρει ο προμηθευτής
    discount_gain = CurrentSales * Discount * CashPrc

    # 2. Opportunity cost from losing supplier credit
    # Υπολογισμός με βάση 365 ημέρες (User Instruction 2026-02-18)
    average_cost_ratio = TotalUnitCost / UnitPrice
    
    # Το κόστος του κεφαλαίου που απαιτείται για να καλυφθεί η πρόωρη πληρωμή
    # Αντί για 0% πίστωση προμηθευτή, χρησιμοποιούμε κεφάλαιο με επιτόκιο InterestRateOnDebt
    credit_benefit_lost = ((CurrentSales / (365 / SupplierCreditDays)) * average_cost_ratio * CashPrc) * InterestRateOnDebt

    net_gain = discount_gain - credit_benefit_lost
    return discount_gain, credit_benefit_lost, net_gain

def show_payables_manager():
    st.header("🤝 Payables Manager: Supplier Credit Analysis")
    st.info("Analytical Comparison: Cash Discounts vs. Supplier Credit Opportunity Cost.")

    s = st.session_state
    m = s.get("metrics", {})
    
    # 1. INPUT PARAMETERS
    st.subheader("1. Credit & Financial Terms")
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**Supplier Terms**")
        SupplierCreditDays = st.number_input("📆 Credit Period (Days)", min_value=0, value=60)
        Discount = st.number_input("💸 Cash Discount Offered (%)", min_value=0.0, value=2.0)
        CashPrc = st.slider("% of Purchases to Switch to Cash", 0, 100, 50) / 100

    with col2:
        st.markdown("**Internal Economics**")
        # Fetching current revenue as proxy for purchase volume if not specified
        CurrentSales = st.number_input("💰 Annual Purchase Volume ($)", min_value=0, value=int(m.get('revenue', 2000000)))
        InterestRateOnDebt = st.number_input("🏦 Cost of Capital / WACC (%)", min_value=0.0, value=float(s.get('wacc', 0.10)) * 100)

    # 2. CALCULATION ENGINE
    # Using default ratios if unit data is missing
    unit_p = float(s.get('price', 20.0))
    unit_c = float(s.get('variable_cost', 15.0))
    
    discount_gain, credit_cost, net_gain = calculate_supplier_credit_gain(
        SupplierCreditDays, Discount, CashPrc * 100,
        CurrentSales, unit_p, unit_c, InterestRateOnDebt
    )

    # 3. RESULTS DASHBOARD
    st.divider()
    st.subheader("2. Financial Impact Analysis")
    
    

    m1, m2, m3 = st.columns(3)
    m1.metric("Total Discount Gain", f"$ {discount_gain:,.0f}")
    m2.metric("Opportunity Cost", f"-$ {credit_cost:,.0f}", help="The interest cost of using your own cash instead of the supplier's free credit.")
    m3.metric("Net Economic Benefit", f"$ {net_gain:,.0f}", 
              delta=f"{net_gain:,.0f} $", 
              delta_color="normal" if net_gain >= 0 else "inverse")

    # 4. COLD ANALYTICAL VERDICT
    st.subheader("3. Strategic Verdict")
    if net_gain > 0:
        st.success(f"🎯 **Decision: EXECUTE CASH OPTION.** The {Discount:.1f}% discount is mathematically superior to the {SupplierCreditDays}-day credit. Internal ROI on this move is higher than your cost of debt.")
    else:
        st.error(f"🚨 **Decision: MAINTAIN CREDIT.** The value of the {SupplierCreditDays}-day 'interest-free loan' from your supplier is greater than the offered discount. Switching to cash would destroy $ {abs(net_gain):,.0f} in value.")

    # Navigation (Ευθυγραμμισμένο με το νέο app.py)
    st.divider()
    if st.button("⬅️ Back to Control Tower", use_container_width=True):
        st.session_state.flow_step = "home"
        st.session_state.selected_tool = None
        st.rerun()
    
