import streamlit as st
from core.engine import calculate_metrics

def sync_global_state():
    """
    Controller Layer: Collects inputs, runs engine, and updates state.
    """
    # Use FIXED_COST (Singular) as per sidebar naming
    results = calculate_metrics(
        price=st.session_state.get('price', 100.0),
        volume=st.session_state.get('volume', 1000),
        variable_cost=st.session_state.get('variable_cost', 60.0),
        fixed_cost=st.session_state.get('fixed_cost', 20000.0), # FIXED NAMING
        wacc=st.session_state.get('wacc', 0.15)
    )
    
    # Update Session State with results
    st.session_state.update(results)

def lock_baseline():
    """
    Deterministic Baseline Lock.
    Called ONLY when the user clicks the 'Lock' button.
    """
    sync_global_state() # Ensure we have the latest metrics
    st.session_state.baseline = {
        'revenue': st.session_state.revenue,
        'ebit': st.session_state.ebit,
        'margin_pct': st.session_state.margin_pct,
        'wacc': st.session_state.wacc
    }
    st.session_state.baseline_locked = True
