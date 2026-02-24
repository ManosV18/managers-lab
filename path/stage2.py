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
        # Ενημέρωση του Debt απευθείας στο state
        st.session_state.debt = st.number_input(
            "Total Outstanding Debt (€)", 
            min_value=0.0, 
            value=float(st.session_state.get('debt', 20000.0))
        )
        # Χρήση του UI field για το επιτόκιο (συγχρονισμός με Stage 0)
        interest_in = st.number_input(
            "Annual Interest Rate (%)", 
            value=float(st.session_state.get('interest_input_field', 5.0)),
            key="interest_input_stage2" # Διαφορετικό key για να μην συγκρούεται, αλλά ενημερώνει το ίδιο value
        )
        st.session_state.interest_input_field = interest_in
        st.session_state.interest_rate = interest_in / 100

    with col2:
        st.subheader("Inventory & Cash Velocity")
        st.session_state.inventory_days = st.number_input("Inventory Days (DIO)", value=int(st.session_state.inventory_days))
        
        slow_pct = st.slider("Slow-Moving / Buffer Stock (%)", 0, 100, int(st.session_state.get('slow_moving_factor', 0.2) * 100))
        st.session_state.slow_moving_factor = slow_pct / 100
        
        st.session_state.ar_days = st.number_input("Receivable Days (DSO)", value=int(st.session_state.ar_days))
        st.session_state.payables_days = st.number_input("Payable Days (DPO)", value=int(st.session_state.payables_days))

    # 2. Working Capital Physics (365 Days)
    ccc = st.session_state.ar_days + st.session_state.inventory_days - st.session_state.payables_days
    st.session_state.ccc = ccc
    
    # Υπολογισμός βάσει κόστους (COGS) για μεγαλύτερη ακρίβεια στο Inventory Friction
    annual_revenue = st.session_state.volume * st.session_state.price
    annual_cogs = st.session_state.volume * st.session_state.variable_cost
    
    base_wc = (ccc / 365) * annual_revenue # WC ανάγκη βάσει κύκλου εργασιών
    inventory_friction = (st.session_state.inventory_days / 365) * annual_cogs * st.session_state.slow_moving_factor
    
    st.session_state.liquidity_drain_annual = base_wc + inventory_friction

    # 3. Refresh metrics after inputs
    metrics = compute_core_metrics()

    # 4. Dashboard Metrics
    st.divider()
    c1, c2, c3 = st.columns(3)
    c1.metric("Survival BEP", f"{metrics.get('survival_bep', 0):,.0f} units")
    c2.metric("Total Liquidity Friction", f"{st.session_state.liquidity_drain_annual:,.0f} €", 
              delta=f"Incl. {slow_pct}% Slow-Stock", delta_color="inverse")
    c3.metric("Net Profit (Post-Tax)", f"{metrics.get('net_profit', 0):,.0f} €")

    c4, c5, c6 = st.columns(3)
    c4.metric("Free Cash Flow", f"{metrics.get('fcf', 0):,.0f} €")
    c5.metric("Ending Cash", f"{metrics.get('ending_cash', 0):,.0f} €")
    
    horizon = metrics.get('cash_survival_horizon', 0)
    horizon_disp = "Stable" if horizon == float('inf') else f"{horizon:.2f} yrs"
    c6.metric("Cash Survival", horizon_disp)

    # 5. The "Cold" Liquidity Audit
    st.divider()
    op_profit = metrics.get('ebit', 0.0) # ΔΙΟΡΘΩΣΗ: Χρήση του ebit από τον engine
    drain = st.session_state.liquidity_drain_annual
    
    

    if drain > op_profit and op_profit > 0:
        st.error(f"🚨 **Liquidity Trap:** Operational friction ({drain:,.0f}€) exceeds Operating Profit ({op_profit:,.0f}€). You are profitable on paper, but losing cash.")
    elif op_profit <= 0:
        st.error("🚨 **Structural Failure:** Negative EBIT. Liquidity is the least of your concerns.")
    else:
        st.success("✅ **Balanced Liquidity:** Your operating profit can self-fund the working capital cycle.")

    # 6. Navigation
    st.divider()
    nav1, nav2 = st.columns(2)
    with nav1:
        if st.button("⬅️ Back to Stage 1", use_container_width=True):
            st.session_state.flow_step = 1
            st.rerun()
    with nav2:
        if st.button("Next: CLV Analysis ➡️", type="primary", use_container_width=True):
            st.session_state.flow_step = 3
            st.rerun()
