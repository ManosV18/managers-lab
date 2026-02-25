import streamlit as st
from core.engine import calculate_metrics

def sync_global_state():
    """
    Orchestrator: Συλλέγει τα δεδομένα από το session_state και τροφοδοτεί 
    την engine με τα 11 υποχρεωτικά ορίσματα.
    """
    s = st.session_state
    
    # Defaults σε περίπτωση που το session_state δεν έχει αρχικοποιηθεί πλήρως
    defaults = {
        'price': 100.0, 'volume': 1000, 'variable_cost': 50.0, 
        'fixed_cost': 20000.0, 'wacc': 0.15, 'tax_rate': 0.22, 
        'ar_days': 45.0, 'inventory_days': 60.0, 'ap_days': 30.0, 
        'annual_debt': 0.0, 'opening_cash': 10000.0
    }

    try:
        # Δημιουργία λίστας ορισμάτων με βάση τα defaults ή το session_state
        params = [float(s.get(k, defaults[k])) for k in [
            'price', 'volume', 'variable_cost', 'fixed_cost', 
            'wacc', 'tax_rate', 'ar_days', 'inventory_days', 
            'ap_days', 'annual_debt', 'opening_cash'
        ]]

        # Κλήση της engine (Position-based arguments)
        metrics = calculate_metrics(*params)
        return metrics
        
    except Exception as e:
        # Ψυχρή καταγραφή σφάλματος χωρίς διακοπή της ροής
        st.sidebar.error(f"Sync Error: {e}")
        return {}

def compute_core_metrics():
    """Alias για συμβατότητα με παλαιότερα εργαλεία (QSPM κλπ)"""
    return sync_global_state()
