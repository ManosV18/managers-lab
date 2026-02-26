import streamlit as st
from core.sync import lock_baseline

def run_stage0():
    st.header("🏗️ Stage 0: Baseline Configuration")
    st.write("Ensure all global parameters in the sidebar are correct before locking.")

    # Clinical check of inputs
    if st.session_state.get('price', 0) <= st.session_state.get('variable_cost', 0):
        st.error("⚠️ Negative Margin detected. Adjust Price or Variable Cost in Sidebar.")
    
    st.divider()
    
    if st.button("🔒 Lock Baseline & Initialize Engine", use_container_width=True):
        lock_baseline() # This sets baseline_locked to True
        st.success("Baseline Locked. Strategic paths are now decrypted.")
        st.session_state.flow_step = "stage1"
        st.rerun()
