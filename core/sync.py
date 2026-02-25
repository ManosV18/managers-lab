import streamlit as st
from core.engine import calculate_metrics

def sync_global_state():
    """
    Controller Layer: Collects inputs from Sidebar, runs Engine, and updates State.
    """
    # We fetch every single input from the session_state
    results = calculate_metrics(
        price=st.session_state.get('price', 100.0),
        volume=st.session_state.get('volume', 1000),
        variable_cost=st.session_state.get('variable_cost', 60.0),
        fixed_cost=st.session_state.get('fixed_cost', 20000.0),
        wacc=st.session_state.get('wacc', 0.15),
        tax_rate=st.session_state.get('tax_rate', 0.22),
        ar_days=st.session_state.get('ar_days', 60),
        inv_days=st.session_state.get('inventory_days', 45),
        ap_days=st.session_state.get('ap_days', 30),
        annual_debt=st.session_state.get('annual_loan_payment', 0.0)
    )
    # This pushes the calculated metrics (Revenue, FCF, etc.) back to session_state
    st.session_state.update(results)
    return results

def lock_baseline():
    """
    Deterministic Snapshot. Only runs when the 'Lock' button is pressed.
    """
    metrics = sync_global_state() # Fresh calculation before locking
    st.session_state.baseline = {
        'revenue': metrics['revenue'],
        'ebit': metrics['ebit'],
        'fcf': metrics['fcf'],
        'wacc': metrics['wacc'],
        'margin_pct': metrics['contribution_ratio'] * 100
    }
    st.session_state.baseline_locked = True
