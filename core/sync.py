import streamlit as st
from core.engine import calculate_metrics

def sync_global_state():
    """
    Orchestrator: Συλλέγει τα δεδομένα από το session_state και τροφοδοτεί 
    την engine με τα 11 υποχρεωτικά ορίσματα θέσης.
    """
    s = st.session_state
    try:
        # Η σειρά των ορισμάτων πρέπει να είναι ΑΚΡΙΒΩΣ αυτή που ορίζει η engine
        metrics = calculate_metrics(
            float(s.get('price', 100.0)),           # 1. Τιμή
            int(s.get('volume', 1000)),             # 2. Όγκος
            float(s.get('variable_cost', 50.0)),    # 3. Μεταβλητό Κόστος
            float(s.get('fixed_cost', 20000.0)),    # 4. Σταθερά Έξοδα
            float(s.get('wacc', 0.15)),             # 5. Κόστος Κεφαλαίου
            float(s.get('tax_rate', 0.22)),         # 6. Φορολογία
            float(s.get('ar_days', 45)),            # 7. Ημέρες Είσπραξης
            float(s.get('inventory_days', 60)),     # 8. Ημέρες Αποθέματος
            float(s.get('ap_days', 30)),            # 9. Ημέρες Πληρωμής
            float(s.get('annual_debt', 0.0)),       # 10. Ετήσιο Τοκοχρεολύσιο
            float(s.get('opening_cash', 10000.0))   # 11. Αρχικά Μετρητά
        )
        return metrics
    except Exception as e:
        st.error(f"Sync Error: {e}")
        return {}

def lock_baseline():
    """
    Scenario Baseline: Κλειδώνει την τρέχουσα κατάσταση ως σημείο αναφοράς
    για συγκρίσεις (Scenario Analysis).
    """
    if 'baseline' not in st.session_state:
        # 1. Εκτέλεση συγχρονισμού
        current_metrics = sync_global_state()
        if current_metrics:
            st.session_state.baseline = current_metrics
            st.session_state.baseline_locked = True
            st.success("✅ Baseline Locked. Scenario analysis is now active.")
