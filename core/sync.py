import streamlit as st
from core.engine import calculate_metrics

def sync_global_state():
    """
    Orchestrator: Collects session_state inputs and feeds the engine.
    Returns metrics ONLY if baseline_locked is True.
    """
    s = st.session_state

    # 1. Verification Lock - Αν δεν είναι κλειδωμένο, επιστρέφουμε κενό λεξικό
    if not s.get('baseline_locked', False):
        return {}

    # 2. Data Retrieval with Defaults (Cold Analysis Logic)
    try:
        metrics = calculate_metrics(
            price=float(s.get('price', 100.0)),
            volume=float(s.get('volume', 1000.0)),
            variable_cost=float(s.get('variable_cost', 60.0)),
            fixed_cost=float(s.get('fixed_cost', 20000.0)),
            wacc=float(s.get('wacc', 0.15)),
            tax_rate=float(s.get('tax_rate', 0.22)),
            ar_days=float(s.get('ar_days', 45.0)),
            inv_days=float(s.get('inventory_days', 60.0)),
            ap_days=float(s.get('ap_days', 30.0)),
            annual_debt_service=float(s.get('annual_debt_service', 0.0)),
            opening_cash=float(s.get('opening_cash', 10000.0))
        )
        
        # Ενημέρωση του baseline για καθολική πρόσβαση
        s.baseline = metrics
        return metrics

    except Exception as e:
        st.error(f"🚨 Sync Engine Error: {e}")
        return {}

def lock_baseline():
    """
    Atomic Lock: Calculates and saves metrics, then locks the system.
    This prevents 'Engine returned no metrics' errors.
    """
    s = st.session_state
    
    # Προσωρινό bypass για να μπορέσει η sync_global_state να τρέξει μία φορά
    s.baseline_locked = True 
    
    metrics = sync_global_state()
    
    if metrics:
        s.baseline = metrics
        st.success("✅ Baseline locked successfully.")
    else:
        s.baseline_locked = False
        st.error("❌ Failed to lock baseline. Check your inputs.")

def compute_core_metrics():
    """Compatibility alias for legacy tools."""
    return sync_global_state()

