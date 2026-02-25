import streamlit as st
from core.sync import sync_global_state

def run_stage4():
    st.header("🌪️ Stage 4: Strategic Stress Testing")
    
    m = sync_global_state()
    s = st.session_state
    st.caption("Testing system resilience against adverse market shifts.")
    st.divider()

    # Stress Sliders
    st.subheader("Select Shock Parameters")
    vol_shock = st.slider("Volume Drop (%)", 0, 50, 20)
    cost_shock = st.slider("Variable Cost Increase (%)", 0, 30, 10)

    # Simulation Logic
    sim_vol = s.get('volume', 1000) * (1 - vol_shock/100)
    sim_vc = s.get('variable_cost', 0.0) * (1 + cost_shock/100)
    sim_ebit = ( (s.get('price', 0.0) - sim_vc) * sim_vol ) - s.get('fixed_cost', 0.0)

    st.divider()
    st.subheader("Shock Results")
    c1, c2 = st.columns(2)
    
    delta_ebit = sim_ebit - m.get('ebit', 0.0)
    c1.metric("Simulated EBIT", f"{sim_ebit:,.0f} €", delta=f"{delta_ebit:,.0f} €", delta_color="inverse")
    
    status = "RELIANT" if sim_ebit > 0 else "COLLAPSED"
    c2.write(f"**System Status under Stress:** {status}")

    # Navigation
    st.divider()
    col_prev, col_next = st.columns(2)
    with col_prev:
        if st.button("⬅️ Back to Stage 3"):
            st.session_state.flow_step = "stage3"
            st.rerun()
    with col_next:
        if st.button("Final Synthesis ➡️"):
            st.session_state.flow_step = "stage5"
            st.rerun()
