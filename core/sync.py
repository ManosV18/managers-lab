def sync_global_state():
    """Collects inputs from session_state and updates calculated metrics."""
    s = st.session_state
    try:
        # Στέλνουμε τις τιμές ΜΟΝΟ ως τιμές, διατηρώντας την αυστηρή σειρά των 11 ορισμάτων
        metrics = calculate_metrics(
            s.get('price', 100.0),           # 1
            s.get('volume', 1000),          # 2
            s.get('variable_cost', 50.0),   # 3
            s.get('fixed_cost', 20000.0),   # 4
            s.get('wacc', 0.15),            # 5
            s.get('tax_rate', 0.22),        # 6
            s.get('ar_days', 45),           # 7
            s.get('inventory_days', 60),    # 8
            s.get('ap_days', 30),           # 9
            s.get('annual_loan_payment', 0.0), # 10 (Debt)
            s.get('opening_cash', 10000.0)  # 11
        )
        return metrics
    except TypeError as e:
        st.error(f"Engine Argument Mismatch: {e}")
        return {}
    except Exception as e:
        st.error(f"Sync Error: {e}")
        return {}
