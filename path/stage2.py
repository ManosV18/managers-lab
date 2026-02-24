import streamlit as st
from core.engine import compute_core_metrics

def run_stage2():
    st.header("💰 Stage 2: Capital & Operational Liquidity")
    st.caption("Strategic Audit: Analyzing debt burden and the cost of trapped inventory.")

    # 1. Fetch live data from engine
    metrics = compute_core_metrics()
    
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Financing & Debt")
        # Ενημέρωση του Debt
        st.session_state.debt = st.number_input(
            "Total Outstanding Debt (€)", 
            min_value=0.0, 
            value=float(st.session_state.get('debt', 20000.0)),
            key="debt_input_s2"
        )
        
        interest_in = st.number_input(
            "Annual Interest Rate (%)", 
            min_value=0.0,
            max_value=100.0,
            value=float(st.session_state.get('interest_input_field', 5.0)),
            key="interest_input_s2" 
        )
        st.session_state.interest_input_field = interest_in
        st.session_state.interest_rate = interest_in / 100

    with col2:
        st.subheader("Inventory & Cash Velocity")
        st.session_state.inventory_days = st.number_input(
            "Inventory Days (DIO)", 
            min_value=0, 
            value=int(st.session_state.get('inventory_days', 60)),
            key="inv_days_s2"
        )
        
        slow_pct = st.slider(
            "Slow-Moving / Buffer Stock (%)", 
            0, 100, 
            int(st.session_state.get('slow_moving_factor', 0.2) * 100),
            key="slow_moving_slider_s2"
        )
        st.session_state.slow_moving_factor = slow_pct / 100
        
        st.session_state.ar_days = st.number_input(
            "Receivable Days (DSO)", 
            min_value=0, 
            value=int(st.session_state.get('ar_days', 45)),
            key="ar_days_s2"
        )
        st.session_state.payables_days = st.number_input(
            "Payable Days (DPO)", 
            min_value=0, 
            value=int(st.session_state.get('payables_days', 30)),
            key="pay_days_s2"
        )

    # 2. Refresh metrics after inputs
    # Ο Engine υπολογίζει αυτόματα το liquidity_drain_annual εσωτερικά
    metrics = compute_core_metrics()
    drain = st.session_state.get('liquidity_drain_annual', 0)

    # 3. Dashboard Metrics
    st.divider()
    c1, c2, c3 = st.columns(3)
    c1.metric("Survival BEP", f"{metrics.get('survival_bep', 0):,.0f} units")
    c2.metric("Total Liquidity Friction", f"{drain:,.0f} €", 
              delta=f"Incl. {slow_pct}% Slow-Stock", delta_color="inverse")
    c3.metric("Net Profit (Post-Tax)", f"{metrics.get('net_profit', 0):,.0f} €")

    c4, c5, c6 = st.columns(3)
    c4.metric("Free Cash Flow", f"{metrics.get('fcf', 0):,.0f} €")
    c5.metric("Ending Cash Balance", f"{metrics.get('ending_cash', 0):,.0f} €")
    
    horizon = metrics.get('cash_survival_horizon', 0)
    horizon_disp = "Stable" if horizon == float('inf') else f"{horizon:.2f} yrs"
    c6.metric("Cash Runway", horizon_disp)

    # 4. The "Cold" Liquidity Audit
    st.divider()
    ebit = metrics.get('ebit', 0.0)
    
    st.subheader("⚠️ Liquidity Stress Test")
    if ebit > 0:
        usage_ratio = min(drain / ebit, 2.0) # Cap at 200% for visualization
        st.write(f"Operational Profit consumed by Working Capital: **{usage_ratio:.1%}**")
        st.progress(usage_ratio if usage_ratio <= 1.0 else 1.0)

    if drain > ebit and ebit > 0:
        st.error(f"🚨 **Liquidity Trap:** Operational friction ({drain:,.0f}€) exceeds Operating Profit ({ebit:,.0f}€). The business is a 'Black Hole' for cash despite being P&L profitable.")
    elif ebit <= 0:
        st.error("🚨 **Structural Failure:** Negative EBIT. The business model cannot sustain its own existence, let alone its liquidity.")
    else:
        st.success("✅ **Balanced Liquidity:** Your operating profit can self-fund the working capital cycle. Structural integrity is maintained.")

    # 5. Navigation
    st.divider()
    nav1, nav2 = st.columns(2)
    with nav1:
        if st.button("⬅️ Back to Stage 1", use_container_width=True):
            st.session_state.flow_step = 1
            st.rerun()
    with nav2:
        if st.button("Next: Stage 3 (CLV & Growth) ➡️", type="primary", use_container_width=True):
            st.session_state.flow_step = 3
            st.rerun()
