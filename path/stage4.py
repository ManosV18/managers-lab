import streamlit as st
from core.sync import sync_global_state

def run_stage4():
    st.header("🌪️ Stage 4: Stress Testing")
    
    metrics = sync_global_state()
    st.subheader("Scenario Analysis")
    
    # Example: 10%, 20%, 30% drop in volume
    vol = st.session_state.get('volume', 0)
    scenarios = [0.9, 0.8, 0.7]
    
    for s in scenarios:
        new_vol = vol * s
        st.write(f"Volume {new_vol:,.0f} → BEP Units: {metrics.get('bep_units',0):,.0f}, EBIT: €{metrics.get('ebit',0):,.0f}")
