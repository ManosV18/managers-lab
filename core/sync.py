import streamlit as st
from core.engine import calculate_metrics

def sync_global_state():
    """
    Orchestrator: Συλλέγει τα δεδομένα και τροφοδοτεί την engine.
    Επιστρέφει metrics μόνο αν το baseline είναι κλειδωμένο.
    """
    s = st.session_state
    
    if not s.get('baseline_locked', False):
        return {}

    try:
        # Instruction [2026-02-18]: Logic based on 365 days
        metrics = calculate_metrics(
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
        return metrics
    except Exception as e:
        st.error(f"Sync Engine Error: {e}")
        return {}

def lock_baseline():
    """Κλειδώνει το Baseline χρησιμοποιώντας τα τρέχοντα δεδομένα της οθόνης."""
    s = st.session_state
    # Άμεσος υπολογισμός για το κλείδωμα
    current_metrics = calculate_metrics(
        float(s.get('price', 100.0)), int(s.get('volume', 1000)),
        float(s.get('variable_cost', 50.0)), float(s.get('fixed_cost', 20000.0)),
        float(s.get('wacc', 0.15)), float(s.get('tax_rate', 0.22)),
        float(s.get('ar_days', 45.0)), float(s.get('inventory_days', 60.0)),
        float(s.get('ap_days', 30.0)), float(s.get('annual_debt_service', 0.0)),
        float(s.get('opening_cash', 10000.0))
    )
    if current_metrics:
        st.session_state.baseline = current_metrics
        st.session_state.baseline_locked = True

def compute_core_metrics():
    """Interface compatibility layer για τη βιβλιοθήκη εργαλείων."""
    return sync_global_state()
