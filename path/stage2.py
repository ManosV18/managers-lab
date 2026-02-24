import streamlit as st
from core.engine import compute_core_metrics

def run_stage2():
    st.header("💰 Stage 2: Capital & Operational Liquidity")
    st.caption("Strategic Audit: Analyzing debt burden and the cost of trapped inventory.")

    # 1. INITIAL FETCH
    metrics = compute_core_metrics()
    
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Financing & Debt")
        st.session_state.debt = st.number_input(
            "Total Outstanding Debt (€)",
            min_value=0.0,
            value=float(st.session_state.get('debt', 0.0))
        )
        input_rate = st.number_input("Annual Interest Rate (%)", value=float(st.session_state.get('interest_rate', 0.0) * 100))
        st.session_state.interest_rate = input_rate / 100

    with col2:
        st.subheader("Inventory & Cash Velocity")
        dio = st.number_input("Inventory Days (DIO)", value=st.session_state.get('inventory_days', 60))
        
        # Slow-Moving Factor logic integration
        slow_moving_pct = st.slider(
            "Slow-Moving / Buffer Stock (%)", 
            0, 100, 20,
            help="Percentage of inventory that is not fast-turning and requires permanent financing."
        )
        st.session_state.slow_moving_factor = slow_moving_pct / 100
        
        dso = st.number_input("Receivable Days (DSO)", value=st.session_state.get('ar_days', 45))
        dpo = st.number_input("Payable Days (DPO)", value=st.session_state.get('payables_days', 30))

    # =====================================================
    # 2. ADVANCED LIQUIDITY CALCULATION
    # =====================================================
    ccc = dio + dso - dpo
    st.session_state.ccc = ccc
    
    annual_costs = st.session_state.volume * st.session_state.variable_cost
    
    # Calculation: Base WC + Extra friction from slow-moving stock
    base_wc = (ccc / 365) * annual_costs
    inventory_friction = (dio / 365) * annual_costs * st.session_state.slow_moving_factor
    
    st.session_state.liquidity_drain_annual = base_wc + inventory_friction
    
    # RE-COMPUTE METRICS with the new liquidity drain
    metrics = compute_core_metrics()

    st.divider()
    
    # 
    
    c1, c2, c3 = st.columns(3)
    c1.metric("Survival BEP", f"{metrics.get('survival_bep', 0):,.0f} units")
    
    # The Drain as the "Cold Truth"
    c2.metric("Total Liquidity Friction", f"{st.session_state.liquidity_drain_annual:,.0f} €", 
              delta=f"Incl. {slow_moving_pct}% Slow-Stock", delta_color="inverse")
    
    c3.metric("Net Economic Profit", f"{metrics.get('net_profit', 0):,.0f} €")

    c4, c5, c6 = st.columns(3)
    c4.metric("Free Cash Flow", f"{metrics['fcf']:,.0f} €")
    c5.metric("Ending Cash", f"{metrics['ending_cash']:,.0f} €")
    c6.metric("Cash Survival Horizon (years)", f"{metrics['cash_survival_horizon']:.2f}")

    # =====================================================
    # 3. COLD VERDICT (Fixed Indentation)
    # =====================================================
    op_profit = metrics.get('operating_profit', 0.0) 
    drain = st.session_state.get('liquidity_drain_annual', 0.0)

    if drain > op_profit and op_profit > 0:
        st.error(
            "🚨 **Liquidity Trap:** Your slow-moving inventory and credit terms are consuming "
            f"{ (drain/op_profit)*100:.1f}% of your operating profit. You are growing yourself into bankruptcy."
        )
    elif op_profit <= 0:
        st.error("🚨 **Structural Failure:** Operating profit is zero or negative. The business cannot sustain its own operations.")
    else:
        st.success("✅ **Balanced Liquidity:** Your cash cycle is sustainable even with the current inventory buffers.")
    
    # 4. NAVIGATION
    st.divider()
    nav1, nav2 = st.columns(2)
    with nav1:
        if st.button("⬅️ Back"):
            st.session_state.flow_step = 1
            st.rerun()
    with nav2:
        if st.button("Next: CLV Analysis ➡️", type="primary"):
            st.session_state.flow_step = 3
            st.rerun()
