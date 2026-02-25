import streamlit as st
from core.engine import calculate_metrics

def sync_global_state():
    """
    The ultimate bridge. It collects all 11 required arguments 
    from session_state and feeds them into the engine.
    """
    s = st.session_state

    # Collect all 11 arguments with safe defaults
    try:
        metrics = calculate_metrics(
            price=s.get('price', 100.0),
            volume=s.get('volume', 1000),
            variable_cost=s.get('variable_cost', 50.0),
            fixed_cost=s.get('fixed_cost', 20000.0),
            wacc=s.get('wacc', 0.15),
            tax_rate=s.get('tax_rate', 0.22),
            ar_days=s.get('ar_days', 45),
            inv_days=s.get('inventory_days', 60), # Careful with key names
            ap_days=s.get('ap_days', 30),
            annual_debt=s.get('annual_loan_payment', 0.0),
            opening_cash=s.get('opening_cash', 10000.0)
        )
        
        # Update session state with calculated metrics for global access
        for key, value in metrics.items():
            s[f"m_{key}"] = value
            
        return metrics
    except Exception as e:
        st.error(f"Critical Sync Error: {e}")
        return {}
