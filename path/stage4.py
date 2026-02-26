import streamlit as st
from core.sync import sync_global_state

def run_stage4():
    st.header("🌪️ Stage 4: Strategic Stress Testing")
    
    # Secure connection to the Engine
    m = sync_global_state()
    s = st.session_state
    
    st.caption("Evaluating structural resilience against exogenous market shocks.")
    st.divider()

    # 1. Shock Parameters
    st.subheader("Shock Parameters")
    vol_shock = st.slider("Volume Contraction (%)", 0, 50, 20)
    cost_shock = st.slider("Variable Cost Inflation (%)", 0, 30, 10)

    # 2. Simulation Logic (Cold Analysis)
    # We use float() and get() with defaults to prevent calculation errors
    price = float(s.get('price', 0.0))
    current_vol = float(s.get('volume', 0.0))
    current_vc = float(s.get('variable_cost', 0.0))
    fixed_cost = float(s.get('fixed_cost', 0.0))
    
    sim_vol = current_vol * (1 - vol_shock/100)
    sim_vc = current_vc * (1 + cost_shock/100)
    
    # Formula: (Price - Simulated Variable Cost) * Simulated Volume - Fixed Costs
    sim_ebit = ((price - sim_vc) * sim_vol) - fixed_cost

    # 3. Simulation Results
    st.subheader("Simulation Results")
    c1, c2 = st.columns(2)
    
    current_ebit = float(m.get('ebit', 0.0))
    delta_ebit = sim_ebit - current_ebit
    
    c1.metric("Simulated EBIT", f"€ {sim_ebit:,.0f}", delta=f"€ {delta_ebit:,.0f}", delta_color="inverse")
    
    status = "RESILIENT" if sim_ebit > 0 else "VULNERABLE"
    color = "green" if status == "RESILIENT" else "red"
    c2.markdown(f"**System Status under Stress:** :{color}[{status}]")

    

    # 4. Navigation (Sync with Sidebar)
    st.divider()
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("⬅️ Back to Stage 3", use_container_width=True):
            st.session_state.flow_step = "stage3"
            st.rerun()
            
    with col2:
        if st.button("Proceed to Stage 5 ➡️", use_container_width=True):
            st.session_state.flow_step = "stage5"
            st.rerun()
