import streamlit as st
from core.sync import sync_global_state

def run_cash_cycle_app():
    """Stage 2: Cash Conversion Cycle Analysis"""
    metrics = sync_global_state()
    st.header("💰 Cash Conversion Cycle (CCC)")
    st.caption("Strategic Liquidity Analysis: Measuring the efficiency of working capital.")
    
    # 1. SYNC WITH SHARED CORE
    # Χρησιμοποιούμε τις μεταβλητές που ορίσαμε στον Orchestrator/Sidebar
    q = st.session_state.get('volume', 0)
    vc = st.session_state.get('variable_cost', 0.0)
    p = st.session_state.get('price', 0.0)
    
    annual_cogs = q * vc 
    annual_revenue = q * p
    days_in_year = 365 
    
    st.write(f"**Baseline Context:** Annual COGS: {annual_cogs:,.0f} € | Annual Revenue: {annual_revenue:,.0f} €")
    st.divider()
    
    # 2. INPUTS (Με συγχρονισμένα ονόματα μεταβλητών)
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.subheader("📦 Inventory")
        inv_days = st.number_input(
            "Days Inventory Outstanding (DIO)", 
            min_value=0, 
            value=int(st.session_state.get('inventory_days', 60)),
            key="ccc_inv"
        )
        inventory_value = (inv_days / days_in_year) * annual_cogs
        st.caption(f"Capital tied in Stock: **{inventory_value:,.0f} €**")
    
    with col2:
        st.subheader("💳 Receivables")
        ar_days = st.number_input(
            "Days Sales Outstanding (DSO)", 
            min_value=0, 
            value=int(st.session_state.get('ar_days', 45)),
            key="ccc_ar"
        )
        ar_value = (ar_days / days_in_year) * annual_revenue
        st.caption(f"Capital tied in Receivables: **{ar_value:,.0f} €**")
    
    with col3:
        st.subheader("💸 Payables")
        ap_days = st.number_input(
            "Days Payables Outstanding (DPO)", 
            min_value=0, 
            value=int(st.session_state.get('ap_days', 30)), # Συγχρονισμένο με Sidebar
            key="ccc_ap"
        )
        ap_value = (ap_days / days_in_year) * annual_cogs
        st.caption(f"Capital financed by Suppliers: **{ap_value:,.0f} €**")
    
    # 3. CALCULATIONS
    ccc = inv_days + ar_days - ap_days
    working_capital_req = inventory_value + ar_value - ap_value
    
    # PUSH TO GLOBAL STATE: Εδώ γίνεται η αυτόματη σύνδεση με τα Stages
    st.session_state.inventory_days = inv_days
    st.session_state.ar_days = ar_days
    st.session_state.ap_days = ap_days 

    # 4. RESULTS DISPLAY
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

    # 5. VISUAL TIMELINE
    st.subheader("📅 Operational Timeline")
    # Απλή οπτική απεικόνιση του κενού
    st.write(f"Inventory Held ({inv_days}d) + Collection Time ({ar_days}d) - Supplier Credit ({ap_days}d) = **{ccc} days to fund.**")
    
    

    # 6. COLD INSIGHT
    daily_cash_impact = (annual_cogs / days_in_year)
    st.info(f"💡 **Cold Insight:** Every single day reduced from your CCC releases approximately **{daily_cash_impact:,.0f} €** in trapped cash flow.")
    
    if st.button("Apply & Back to Library Hub", type="primary"):
        st.session_state.selected_tool = None
        st.rerun()

