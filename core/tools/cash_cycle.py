import streamlit as st

def run_cash_cycle_app():
    s = st.session_state
    
    # Έλεγχος αν υπάρχουν metrics από τον Engine
    metrics = s.get("metrics", {})
    if not metrics:
        st.warning("⚠️ Baseline not locked. Please lock parameters in Home first.")
        return
    
    st.header("💰 Cash Conversion Cycle (CCC)")
    
    # 1. FETCH BASELINE DATA (Σύμφωνα με τις οδηγίες 365 ημέρες)
    q = float(s.get('volume', 0))
    vc = float(s.get('variable_cost', 0.0))
    p = float(s.get('price', 0.0))
    days_in_year = 365 
    
    annual_cogs = q * vc 
    annual_revenue = q * p
    
    st.write(f"**🔗 Linked Metrics:** Revenue: {annual_revenue:,.0f}€ | COGS: {annual_cogs:,.0f}€")
    st.divider()

    # 2. INPUTS & DYNAMIC WRITING
    col1, col2, col3 = st.columns(3)
    
    with col1:
        inv_days = st.number_input("DIO (Inventory)", 0, 365, int(s.get('inventory_days', 60)), key="ccc_inv")
    with col2:
        ar_days = st.number_input("DSO (Receivables)", 0, 365, int(s.get('ar_days', 45)), key="ccc_ar")
    with col3:
        ap_days = st.number_input("DPO (Payables)", 0, 365, int(s.get('ap_days', 30)), key="ccc_ap")

    # 3. GLOBAL UPDATE (Ενημέρωση του Session State για συγχρονισμό με το Home)
    s.inventory_days = inv_days
    s.ar_days = ar_days
    s.ap_days = ap_days

    # 4. CALCULATIONS (Αμετάβλητη Λογική)
    ccc = inv_days + ar_days - ap_days
    
    # Υπολογισμός Απαιτήσεων Κεφαλαίου Κίνησης (Working Capital Requirement)
    working_capital_req = ((inv_days/days_in_year) * annual_cogs) + \
                          ((ar_days/days_in_year) * annual_revenue) - \
                          ((ap_days/days_in_year) * annual_cogs)
    
    # 5. RESULTS DISPLAY
    st.divider()
    res1, res2 = st.columns(2)
    
    with res1:
        color = "red" if ccc > 90 else "orange" if ccc > 60 else "green"
        status = 'Critical' if ccc > 90 else 'Optimal' if ccc < 45 else 'Stable'
        st.metric("Cash Conversion Cycle", f"{ccc} Days", delta=f"{ccc} days gap", delta_color="inverse")
        st.markdown(f"Liquidity Status: :{color}[**{status}**]")
    
    with res2:
        st.metric("Working Capital Requirement", f"{working_capital_req:,.0f} €")
        st.caption("The amount of net cash required to sustain current operations.")

    # 6. VISUAL TIMELINE
    st.subheader("📅 Operational Timeline")
    st.write(f"Inventory Held ({inv_days}d) + Collection Time ({ar_days}d) - Supplier Credit ({ap_days}d) = **{ccc} days to fund.**")
    
    

    # 7. COLD INSIGHT
    daily_cash_impact = (annual_cogs / days_in_year)
    st.info(f"💡 **Cold Insight:** Every single day reduced from your CCC releases approximately **{daily_cash_impact:,.0f} €** in trapped cash flow.")
    
    # Ο Router στο app.py παρέχει ήδη κουμπί επιστροφής, αλλά αν θες και αυτό:
    if st.button("Apply & Back to Library Hub", type="primary"):
        st.session_state.flow_step = "home"
        st.session_state.selected_tool = None
        st.rerun()
