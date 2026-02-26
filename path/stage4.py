import streamlit as st
from core.sync import sync_global_state

def run_stage4():
    st.header("🌪️ Stage 4: Strategic Stress Testing")
    m = sync_global_state()
    s = st.session_state
    st.caption("Evaluating structural resilience against exogenous market shocks.")
    st.divider()

    st.subheader("Shock Parameters")
    vol_shock = st.slider("Volume Contraction (%)", 0, 50, 20)
    cost_shock = st.slider("Variable Cost Inflation (%)", 0, 30, 10)

    sim_vol = float(s.get('volume', 0)) * (1 - vol_shock/100)
    sim_vc = float(s.get('variable_cost', 0)) * (1 + cost_shock/100)
    sim_ebit = ((float(s.get('price', 0)) - sim_vc) * sim_vol) - float(s.get('fixed_cost', 0))

    

    st.subheader("Simulation Results")
    c1, c2 = st.columns(2)
    delta_ebit = sim_ebit - float(m.get('ebit', 0))
    c1.metric("Simulated EBIT", f"€ {sim_ebit:,.0f}", delta=f"€ {delta_ebit:,.0f}", delta_color="inverse")
    
    status = "RESILIENT" if sim_ebit > 0 else "VULNERABLE"
    c2.write(f"**System Status under Stress:** {status}")

    st.divider()
    col1, col2 = st.columns(2)
    if col1.button("⬅️ Back to Stage 3"): st.session_state.flow_step = "stage3"; st.rerun()
    if col2.button("Proceed to Final Synthesis ➡️"): st.session_state.flow_step = "stage5"; st.rerun()
