import streamlit as st

def initialize_system_state():
    """Αρχικοποιεί το DNA της επιχείρησης. Single Source of Truth για τα κλειδιά."""
    defaults = {
        'price': 100.0,
        'variable_cost': 60.0,
        'volume': 5000,
        'fixed_cost': 150000.0,
        'annual_loan_payment': 24000.0,
        'debt': 200000.0,
        'interest_rate': 0.05,
        'ar_days': 45,
        'inventory_days': 60,
        'payables_days': 30,
        'slow_moving_factor': 0.2,
        'tax_rate': 0.22,
        'opening_cash': 50000.0,
        'flow_step': 0,
        'baseline_locked': False
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

def compute_core_metrics():
    """Εκτελεί το 'Cold' Cash Physics Engine."""
    s = st.session_state
    
    # 1. Unit Economics & Viability Guardrail
    unit_contribution = s.get('price', 0.0) - s.get('variable_cost', 0.0)
    is_non_viable = unit_contribution <= 0
    
    # 2. Working Capital (Upfront Funding Requirement)
    rev_annual = s.get('price', 0.0) * s.get('volume', 0.0)
    cogs_annual = s.get('variable_cost', 0.0) * s.get('volume', 0.0)
    
    ar_req = rev_annual * (s.get('ar_days', 0) / 365)
    inv_req = cogs_annual * (s.get('inventory_days', 0) / 365) * (1 + s.get('slow_moving_factor', 0.0))
    ap_offset = cogs_annual * (s.get('payables_days', 0) / 365)
    total_wc_req = ar_req + inv_req - ap_offset
    
    # 3. Operating Cash Flow (OCF) Layer
    ebit = (unit_contribution * s.get('volume', 0.0)) - s.get('fixed_cost', 0.0)
    tax_on_ebit = max(0.0, ebit * s.get('tax_rate', 0.22))
    ocf = ebit - tax_on_ebit # Recurring operational cash generation
    
    # 4. Debt Service & FCF
    # Σημείωση: Το annual_loan_payment περιλαμβάνει Principal + Interest
    fcf = ocf - s.get('annual_loan_payment', 0.0)
    
    # 5. Survival Wall
    cash_wall = s.get('fixed_cost', 0.0) + s.get('annual_loan_payment', 0.0) + total_wc_req
    survival_bep = cash_wall / unit_contribution if not is_non_viable else float('inf')
    
    metrics = {
        "revenue": rev_annual,
        "unit_contribution": unit_contribution,
        "is_non_viable": is_non_viable,
        "total_wc_requirement": total_wc_req,
        "cash_wall": cash_wall,
        "survival_bep": survival_bep,
        "ebit": ebit,
        "ocf": ocf,
        "fcf": fcf
    }
    
    s.last_computed_metrics = metrics
    return metrics
