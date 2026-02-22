import streamlit as st
from core.engine import compute_core_metrics

def show_supplier_credit_analysis():
    st.header("🤝 Supplier Credit Analysis")
    st.info("Analyze how supplier payment terms affect your working capital and cash position.")

    # 1. SYNC WITH SHARED CORE
    metrics = compute_core_metrics()
    # Χρησιμοποιούμε το πραγματικό Variable Cost * Volume ως βάση αγορών
    q = st.session_state.get('volume', 0)
    vc = st.session_state.get('variable_cost', 0.0)
    annual_cogs = q * vc
    
    # Τραβάμε το τρέχον AP Days από το baseline ή default 30
    current_ap_days = st.session_state.get('payables_days', 30)
    # Τραβάμε το κόστος χρήματος από το Stage 2
    cost_of_capital = st.session_state.get('interest_rate', 0.08)
    
    st.write(f"**🔗 Core Baseline Linked:** Annual Purchases: **{annual_cogs:,.2f} €** | Interest Rate: **{cost_of_capital:.1%}\n**")

    st.divider()

    # 2. SCENARIO INPUTS
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Current Terms")
        st.write(f"Current Days: **{current_ap_days}**")
        # Υπολογισμός με 365 ημέρες βάσει οδηγίας
        current_ap_value = (current_ap_days / 365) * annual_cogs
        st.metric("Financing from Suppliers", f"{current_ap_value:,.2f} €")

    with col2:
        st.subheader("Target Terms")
        new_ap_days = st.slider("New Payment Terms (Days)", 0, 180, int(current_ap_days + 15))
        new_ap_value = (new_ap_days / 365) * annual_cogs
        st.metric("New Financing Value", f"{new_ap_value:,.2f} €")

    # 3. IMPACT ANALYSIS
    cash_benefit = new_ap_value - current_ap_value
    
    st.divider()
    
    # 4. RESULTS & VISUALS
    
    
    res1, res2 = st.columns(2)
    
    with res1:
        if cash_benefit > 0:
            st.success(f"**Cash Inflow:** +{cash_benefit:,.2f} €")
            st.caption("This increase in Payables acts as an interest-free loan, improving your liquidity.")
        else:
            st.error(f"**Cash Outflow:** {abs(cash_benefit):,.2f} €")
            st.caption("Reducing payment days drains cash from your bank to your suppliers.")

    with res2:
        # Υπολογίζουμε το κέρδος από τους τόκους που ΔΕΝ θα πληρώσεις στην τράπεζα 
        # επειδή χρησιμοποιείς το χρήμα του προμηθευτή
        savings = cash_benefit * cost_of_capital
        st.metric("Annual Interest Benefit", f"{max(0.0, savings):,.2f} €", 
                  delta=f"{savings:,.2f} €" if savings != 0 else None)

    # 5. STRATEGIC INSIGHT (The Cold Truth)
    st.subheader("🔍 Strategic Verdict")
    if cash_benefit > 0:
        st.markdown(f"""
        **The Leverage Logic:** By delaying payment to **{new_ap_days} days**, you effectively extract **{cash_benefit:,.2f} €** from your supply chain to fund your operations. 
        
        If your **WACC** ({cost_of_capital:.1%}) is higher than any 'early payment discount' offered by the supplier, this is a mathematically superior move.
        """)
    
    st.warning("⚠️ **Cold Reminder:** Check for '2/10 net 30' terms. A 2% discount for paying 20 days early is an annualized return of ~36%. If your interest rate is lower than 36%, always take the discount instead of the credit.")

    if st.button("🔄 Sync with Global Baseline", use_container_width=True):
        st.session_state.payables_days = new_ap_days
        st.success(f"Global Baseline updated to {new_ap_days} days.")
        st.rerun()
