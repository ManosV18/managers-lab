import streamlit as st
from core.engine import calculate_metrics

def sync_global_state():
    """
    Gatekeeper function: Synchronizes sidebar inputs with the calculation engine.
    Returns calculated metrics ONLY if baseline_locked is True.
    """
    s = st.session_state

    if not s.get('baseline_locked', False):
        st.error("🚨 Baseline Not Defined. Please complete Stage 0 to initialize the engine.")
        st.stop()

    params = {
        'price': float(s.get('price', 0.0)),
        'volume': int(s.get('volume', 0)),
        'variable_cost': float(s.get('variable_cost', 0.0)),
        'fixed_cost': float(s.get('fixed_cost', 0.0)),
        'wacc': float(s.get('wacc', 0.15)),
        'tax_rate': float(s.get('tax_rate', 0.22)),
        'ar_days': float(s.get('ar_days', 0.0)),
        'inv_days': float(s.get('inventory_days', 0.0)),
        'ap_days': float(s.get('ap_days', 0.0)),
        'annual_debt_service': float(s.get('annual_debt_service', 0.0)),
        'opening_cash': float(s.get('opening_cash', 0.0))
    }

    return calculate_metrics(**params)

def lock_baseline():
    """
    Locks current sidebar state as baseline and saves calculated metrics.
    """
    metrics = sync_global_state()
    st.session_state.baseline = metrics
    st.session_state.baseline_locked = True

