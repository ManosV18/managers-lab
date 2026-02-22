# path/step2_cash.py
"""
Stage 2: Cash Conversion Cycle (CCC)
Measures working capital efficiency and liquidity gap
"""

import streamlit as st
import pandas as pd


def run_step():
    """Stage 2: Cash Conversion Cycle Analysis"""
    
    st.header("💰 Stage 2: Cash Conversion Cycle (CCC)")
    st.info("Measures the time (in days) it takes to convert investments in inventory into cash flows from sales.")
    
    # ═══════════════════════════════════════════════════════════
    # 1. SYNC WITH SHARED CORE
    # ═══════════════════════════════════════════════════════════
    q = st.session_state.get('volume', 1000)
    vc = st.session_state.get('variable_cost', 12.0)
    p = st.session_state.get('price', 20.0)
    
    annual_cogs = q * vc 
    annual_revenue = q * p
    days_in_year = 365
    
    st.write(f"**Global Baseline:** Annual COGS: {annual_cogs:,.2f} € | Annual Revenue: {annual_revenue:,.2f} €")
    st.divider()
    
    # ═══════════════════════════════════════════════════════════
    # 2. INPUTS
    # ═══════════════════════════════════════════════════════════
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.subheader("📦 Inventory")
        inv_days = st.number_input(
            "Inventory Days", 
            min_value=0, 
            max_value=365,
            value=st.session_state.get('inventory_days', 60),
            help="Average days products sit in stock before being sold"
        )
        inventory_value = (inv_days / days_in_year) * annual_cogs
        st.caption(f"💰 Stock Value: **{inventory_value:,.2f} €**")
    
    with col2:
        st.subheader("💳 Receivables")
        ar_days = st.number_input(
            "Accounts Receivable Days", 
            min_value=0,
            max_value=365,
            value=st.session_state.get('ar_days', 45),
            help="Average days to collect payment from customers"
        )
        ar_value = (ar_days / days_in_year) * annual_revenue
        st.caption(f"💰 Owed by Clients: **{ar_value:,.2f} €**")
    
    with col3:
        st.subheader("💸 Payables")
        ap_days = st.number_input(
            "Accounts Payable Days", 
            min_value=0,
            max_value=365,
            value=st.session_state.get('payables_days', 30),
            help="Average days you take to pay suppliers"
        )
        ap_value = (ap_days / days_in_year) * annual_cogs
        st.caption(f"💰 Owed to Suppliers: **{ap_value:,.2f} €**")
    
    # ═══════════════════════════════════════════════════════════
    # 3. CALCULATIONS
    # ═══════════════════════════════════════════════════════════
    ccc = inv_days + ar_days - ap_days
    working_capital_req = inventory_value + ar_value - ap_value
    
    # ✅ LIQUIDITY DRAIN CALCULATION
    # Carrying cost for immobilized capital (default 8% annual)
    carrying_cost_rate = st.session_state.get('carrying_cost_rate', 0.08)
    liquidity_drain_annual = working_capital_req * carrying_cost_rate
    
    # Save all to session state
    st.session_state.inventory_days = inv_days
    st.session_state.ar_days = ar_days
    st.session_state.payables_days = ap_days
    st.session_state.ccc = ccc
    st.session_state.working_capital_req = working_capital_req
    st.session_state.liquidity_drain = liquidity_drain_annual  # ← ΚΡΙΣΙΜΟ!
    
    # ═══════════════════════════════════════════════════════════
    # 4. RESULTS & SYNC
    # ═══════════════════════════════════════════════════════════
    st.divider()
    
    res1, res2, res3 = st.columns(3)
    
    with res1:
        # Color coding
        if ccc < 0:
            color = "green"
            status = "Negative CCC (Excellent!)"
        elif ccc < 30:
            color = "green"
            status = "Healthy"
        elif ccc < 60:
            color = "orange"
            status = "Monitor"
        elif ccc < 90:
            color = "orange"
            status = "Caution"
        else:
            color = "red"
            status = "High Risk"
        
        st.metric(
            "Cash Conversion Cycle", 
            f"{ccc} Days", 
            delta=f"{ccc} days delay" if ccc > 0 else "Cash before payment!",
            delta_color="inverse" if ccc > 0 else "normal"
        )
        st.markdown(f"Status: :{color}[**{status}**]")
    
    with res2:
        st.metric(
            "Working Capital Requirement", 
            f"{working_capital_req:,.2f} €",
            help="Cash tied up in operations"
        )
    
    with res3:
        st.metric(
            "Annual Liquidity Drain",
            f"{liquidity_drain_annual:,.2f} €",
            help=f"Cost of capital tied up ({carrying_cost_rate*100:.0f}% annual rate)"
        )
    
    # ═══════════════════════════════════════════════════════════
    # 5. BREAKDOWN TABLE
    # ═══════════════════════════════════════════════════════════
    st.divider()
    
    st.subheader("📊 Working Capital Breakdown")
    
    breakdown_df = pd.DataFrame({
        "Component": [
            "Inventory (Stock)",
            "Receivables (Owed to us)",
            "Payables (Owed by us)",
            "Net Working Capital",
            f"Carrying Cost ({carrying_cost_rate*100:.0f}% p.a.)"
        ],
        "Days": [
            f"{inv_days} days",
            f"{ar_days} days",
            f"-{ap_days} days",
            f"{ccc} days",
            "—"
        ],
        "Value (€)": [
            f"{inventory_value:,.2f}",
            f"{ar_value:,.2f}",
            f"-{ap_value:,.2f}",
            f"{working_capital_req:,.2f}",
            f"{liquidity_drain_annual:,.2f}"
        ]
    })
    
    st.dataframe(breakdown_df, use_container_width=True, hide_index=True)
    
    # ═══════════════════════════════════════════════════════════
    # 6. COLD INSIGHT
    # ═══════════════════════════════════════════════════════════
    st.divider()
    
    daily_cash_release = annual_cogs / 365
    
    if ccc > 0:
        st.info(f"💡 **Cold Insight:** Every day you reduce the CCC, you release **~{daily_cash_release:,.2f} €** in cash.")
        
        # Additional insight about liquidity drain
        if liquidity_drain_annual > 0:
            st.warning(f"⚠️ **Hidden Cost:** Slow-moving capital costs you **{liquidity_drain_annual:,.2f} €/year** in opportunity cost.")
    else:
        st.success(f"🎯 **Negative CCC Achieved!** You get paid **before** you pay suppliers. This is a cash-generating machine!")
    
    # ═══════════════════════════════════════════════════════════
    # 7. ADVANCED SETTINGS
    # ═══════════════════════════════════════════════════════════
    with st.expander("⚙️ Advanced: Adjust Carrying Cost Rate", expanded=False):
        st.caption("The annual cost of capital tied up in working capital (opportunity cost, financing cost, or WACC).")
        
        new_carrying_rate = st.slider(
            "Carrying Cost Rate (%)", 
            min_value=0.0, 
            max_value=20.0, 
            value=carrying_cost_rate * 100,
            step=0.5
        ) / 100
        
        if new_carrying_rate != carrying_cost_rate:
            st.session_state.carrying_cost_rate = new_carrying_rate
            if st.button("Update Carrying Cost", type="secondary"):
                st.rerun()
    
    # ═══════════════════════════════════════════════════════════
    # 8. NAVIGATION
    # ═══════════════════════════════════════════════════════════
    st.divider()
    
    nav1, nav2 = st.columns(2)
    
    with nav1:
        if st.button("⬅️ Back to Survival Anchor"):
            st.session_state.flow_step = 1
            st.rerun()
    
    with nav2:
        if st.button("Proceed to Unit Economics ➡️", type="primary"):
            st.session_state.flow_step = 3
            st.rerun()
