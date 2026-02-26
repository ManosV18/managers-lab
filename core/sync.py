import streamlit as st
from core.engine import calculate_metrics

def sync_global_state():
    """
    Synchronizes sidebar inputs with calculation engine.

    Returns:
        dict with fresh metrics if baseline is locked
        None if baseline is NOT locked
    """

    s = st.session_state

    if not s.get("baseline_locked", False):
        return None

    try:
        # Explicit mapping for safety
        metrics = calculate_metrics(
            price=float(s.get("price", 0.0)),
            volume=float(s.get("volume", 0.0)),
            variable_cost=float(s.get("variable_cost", 0.0)),
            fixed_cost=float(s.get("fixed_cost", 0.0)),
            wacc=float(s.get("wacc", 0.0)),
            tax_rate=float(s.get("tax_rate", 0.0)),
            ar_days=float(s.get("ar_days", 0.0)),
            inventory_days=float(s.get("inventory_days", 0.0)),
            ap_days=float(s.get("ap_days", 0.0)),
            annual_debt_service=float(s.get("annual_debt_service", 0.0)),
            opening_cash=float(s.get("opening_cash", 0.0))
        )

        # Always update baseline → Data Freshness
        s.baseline = metrics

        return metrics

    except Exception:
        return None
