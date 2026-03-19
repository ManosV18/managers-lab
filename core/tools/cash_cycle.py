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
    # Χρησιμοποιούμε τα ίδια ονόματα μεταβλητών με το home.py
    q = float(s.get('volume', 0))
    vc = float(s.get('variable_cost', 0.0))
    p = float(s.get('price', 0.0))
    days_in_year = 365 
    
    annual_cogs = q * vc 
    annual_revenue = q * p
    
    st.write(f"**🔗 Linked Metrics:** Revenue: ${annual_revenue:,.0f} | COGS: ${annual_cogs:,.0f}")
    st.divider()

    # 2. INPUTS & DYNAMIC WRITING
    # ΣΗΜΑΝΤΙΚΟ: Χρησιμοποιούμε τα κλειδιά ar_days, inv_days, ap_days για να συγχρονίζονται με το Home
    col1, col2, col3 = st.columns(3)
    
    with col1:
        inv_days = st.number_input("DIO (Inventory)", 0, 365, int(s.get('inv_days', 45)), key="inv_days_input")
    with col2:
        ar_days = st.number_input("DSO (Receivables)", 0, 365, int(s.get('ar_days', 60)), key="ar_days_input")
    with col3:
        ap_days = st.number_input("DPO (Payables)", 0, 365, int(s.get('ap_days', 30)), key="ap_days_input")

    # 3. GLOBAL UPDATE (Συγχρονισμός με το κεντρικό State)
    s.inv_days = inv_days
    s.ar_days = ar_days
    s.ap_days = ap_days

    # 4. CALCULATIONS (Η λογική McKinsey)
    ccc = inv_days + ar_days - ap_days
    
    # Υπολογισμός Working Capital Requirement (WCR)
    # Χρησιμοποιούμε COGS για Inventory/Payables και Revenue για Receivables
    wcr = ((inv_days/days_in_year) * annual_cogs) + \
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
        st.metric("Working Capital Requirement", f"${wcr:,.0f}")
        st.caption("The amount of net cash trapped in operations.")

    # 6. VISUAL TIMELINE
    st.subheader("📅 Operational Timeline")
    st.write(f"Inventory Held ({inv_days}d) + Collection Time ({ar_days}d) - Supplier Credit ({ap_days}d) = **{ccc} days to fund.**")
    
    

    # 7. COLD INSIGHT
    # Ο πραγματικός αντίκτυπος στο ταμείο ανά ημέρα βελτίωσης
    daily_cash_impact = (annual_revenue / days_in_year) # Χρησιμοποιούμε revenue για πιο "επιθετική" εκτίμηση release
    st.info(f"💡 **Cold Insight:** Every single day reduced from your CCC releases approximately **${daily_cash_impact:,.0f}** in trapped cash flow.")
    
    if st.button("Apply & Back to Library Hub", type="primary", use_container_width=True):
        s.flow_step = "home"
        s.selected_tool = None
        st.rerun()
