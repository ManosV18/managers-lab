import streamlit as st

def run_cash_cycle_app():
    """Stage 2: Cash Conversion Cycle Analysis"""
    
    st.header("💰 Stage 2: Cash Conversion Cycle (CCC)")
    st.caption("Strategic Liquidity Analysis: Measuring the efficiency of working capital.")
    
    st.info(
        "The CCC measures the time (in days) it takes to convert investments in inventory "
        "and other resources into cash flows from sales."
    )
    
    # =========================================================
    # 1. SYNC WITH SHARED CORE
    # =========================================================
    q = st.session_state.get('volume', 0)
    vc = st.session_state.get('variable_cost', 0.0)
    p = st.session_state.get('price', 0.0)
    
    annual_cogs = q * vc 
    annual_revenue = q * p
    days_in_year = 365 # As per global configuration
    
    st.write(f"**Baseline Context:** Annual COGS: {annual_cogs:,.2f} € | Annual Revenue: {annual_revenue:,.2f} €")
    st.divider()
    
    # =========================================================
    # 2. INPUTS (Days Inventory, Receivables, Payables)
    # =========================================================
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.subheader("📦 Inventory")
        inv_days = st.number_input(
            "Days Inventory Outstanding (DIO)", 
            min_value=0, 
            value=st.session_state.get('inventory_days', 60),
            help="Average days products remain in stock before being sold."
        )
        inventory_value = (inv_days / days_in_year) * annual_cogs
        st.caption(f"Capital tied in Stock: **{inventory_value:,.2f} €**")
    
    with col2:
        st.subheader("💳 Receivables")
        ar_days = st.number_input(
            "Days Sales Outstanding (DSO)", 
            min_value=0, 
            value=st.session_state.get('ar_days', 45),
            help="Average days to collect payment from customers after a sale."
        )
        ar_value = (ar_days / days_in_year) * annual_revenue
        st.caption(f"Capital tied in Receivables: **{ar_value:,.2f} €**")
    
    with col3:
        st.subheader("💸 Payables")
        ap_days = st.number_input(
            "Days Payables Outstanding (DPO)", 
            min_value=0, 
            value=st.session_state.get('payables_days', 30),
            help="Average days you take to pay your suppliers."
        )
        ap_value = (ap_days / days_in_year) * annual_cogs
        st.caption(f"Capital financed by Suppliers: **{ap_value:,.2f} €**")
    
    # =========================================================
    # 3. CALCULATIONS & RADAR DATA
    # =========================================================
    ccc = inv_days + ar_days - ap_days
    working_capital_req = inventory_value + ar_value - ap_value
    
    # Save to session state for Global Engine sync
    st.session_state.inventory_days = inv_days
    st.session_state.ar_days = ar_days
    st.session_state.payables_days = ap_days
    st.session_state.ccc = ccc
    st.session_state.working_capital_req = working_capital_req

    # =========================================================
    # 4. RESULTS DISPLAY
    # =========================================================
    st.divider()
    res1, res2 = st.columns(2)
    
    with res1:
        color = "red" if ccc > 90 else "orange" if ccc > 60 else "green"
        status = 'Critical' if ccc > 90 else 'Optimal' if ccc < 45 else 'Stable'
        
        st.metric(
            "Cash Conversion Cycle", 
            f"{ccc} Days", 
            delta=f"{ccc} days gap", 
            delta_color="inverse"
        )
        st.markdown(f"Liquidity Status: :{color}[**{status}**]")
    
    with res2:
        st.metric("Working Capital Requirement", f"{working_capital_req:,.2f} €")
        st.caption("The amount of net cash required to sustain current operations.")

    # =========================================================
    # 5. VISUAL TIMELINE
    # =========================================================
    
    
    # =========================================================
    # 6. COLD INSIGHT
    # =========================================================
    daily_cogs = annual_cogs / days_in_year
    st.info(f"💡 **Cold Insight:** Every single day reduced from your CCC releases approximately **{daily_cogs:,.2f} €** in trapped cash flow.")
    
    if working_capital_req > st.session_state.get('liquidity_drain_annual', 0):
        st.warning("⚠️ **Liquidity Alert:** Your Working Capital Requirement exceeds your annual liquidity reserves. Growth may trigger a cash crisis.")

    # =========================================================
    # 7. NAVIGATION
    # =========================================================
    st.divider()
    nav1, nav2 = st.columns(2)
    with nav1:
        if st.button("⬅️ Previous: Survival Anchor"):
            st.session_state.flow_step = 1
            st.rerun()
    with nav2:
        if st.button("Next: Unit Economics ➡️", type="primary"):
            st.session_state.flow_step = 3
            st.rerun()

