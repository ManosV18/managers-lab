import streamlit as st
from core.engine import calculate_metrics

def sync_global_state():
    """Collects inputs from session_state and updates calculated metrics."""
    s = st.session_state
    try:
        # Καλούμε τον κινητήρα με τα 11 υποχρεωτικά ορίσματα
        metrics = calculate_metrics(
            price=s.get('price', 100.0),
            volume=s.get('volume', 1000),
            variable_cost=s.get('variable_cost', 50.0),
            fixed_cost=s.get('fixed_cost', 20000.0),
            wacc=s.get('wacc', 0.15),
            tax_rate=s.get('tax_rate', 0.22),
            ar_days=s.get('ar_days', 45),
            inv_days=s.get('inventory_days', 60),
            ap_days=s.get('ap_days', 30),
            annual_debt=s.get('annual_loan_payment', 0.0),
            opening_cash=s.get('opening_cash', 10000.0)
        )
        return metrics
    except Exception as e:
        st.error(f"Sync Error: {e}")
        return {}

def lock_baseline():
    """Freezes current session state values as a baseline for comparisons."""
    if 'baseline' not in st.session_state:
        # 1. Παίρνουμε τα τρέχοντα metrics
        st.session_state.baseline = sync_global_state()
        # 2. Ενημερώνουμε το flag για το Sidebar
        st.session_state.baseline_locked = True 
        st.success("✅ Baseline Locked. Scenario analysis is now active.")
