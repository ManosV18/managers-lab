import streamlit as st
from core.engine import calculate_metrics


def sync_global_state():
    """
    Orchestrator: Collects session_state inputs and feeds the engine.
    Returns metrics ONLY if baseline_locked is True.
    """
    s = st.session_state

    if not s.get('baseline_locked', False):
        return {}

    try:
        return calculate_metrics(
            float(s.get('price', 100.0)),
            int(s.get('volume', 1000)),
            float(s.get('variable_cost', 50.0)),
            float(s.get('fixed_cost', 20000.0)),
            float(s.get('wacc', 0.15)),
            float(s.get('tax_rate', 0.22)),
            float(s.get('ar_days', 45.0)),
            float(s.get('inventory_days', 60.0)),
            float(s.get('ap_days', 30.0)),
            float(s.get('annual_debt_service', 0.0)),
            float(s.get('opening_cash', 10000.0))
        )
    except Exception as e:
        st.error(f"Sync Engine Error: {e}")
        return {}


def lock_baseline():
    """
    Locks current state as baseline.
    """
    metrics = sync_global_state()
    if metrics:
        st.session_state.baseline = metrics
        st.session_state.baseline_locked = True


def compute_core_metrics():
    """
    Compatibility alias for legacy tools.
    """
    return sync_global_state()
