import streamlit as st
from core.engine import calculate_metrics

def sync_global_state():
    """Synchronizes sidebar inputs with engine. Returns metrics only if baseline_locked."""
    s = st.session_state

    if not s.get('baseline_locked', False):
        return {}

    params = {
        'price': float(s.get('price', 0.0)),
        'volume': float(s.get('volume', 0.0)),
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

    try:
        metrics = calculate_metrics(**params)
        s.baseline = metrics
        return metrics
    except Exception as e:
        st.error(f"🚨 Engine Error: {e}")
        return {}

def lock_baseline():
    """Locks baseline and calculates metrics once."""
    s = st.session_state
    s.baseline_locked = True
    metrics = sync_global_state()
    if metrics:
        s.baseline = metrics
        st.success("✅ Baseline locked successfully.")
    else:
        s.baseline_locked = False
        st.error("❌ Failed to lock baseline. Check inputs.")
