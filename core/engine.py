import streamlit as st

def initialize_system_state():
    """Αρχικοποιεί το DNA της επιχείρησης με ενιαίο naming convention."""
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
        'opening_cash': 50000.0, # Διορθωμένο naming
        'flow_step': 0,
        'baseline_locked': False
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

def compute_core_metrics():
    """Single Source of Truth για όλους τους υπολογισμούς."""
    s = st.session_state
    
    # 1. Unit Economics
    unit_contribution = s.get('price', 0.0) - s.get('variable_cost', 0.0)
    
    # 2. Working Capital (Upfront Funding Requirement)
    rev_annual = s.get('price', 0.0) * s.get('volume', 0.0)
    cogs_annual = s.get('variable_cost', 0.0) * s.get('volume', 0.0)
    
    ar_req = rev_annual * (s.get('ar_days', 0) / 365)
    inv_req = cogs_annual * (s.get('inventory_days', 0) / 365) * (1 + s.get('slow_moving_factor', 0.0))
    ap_offset = cogs_annual * (s.get('payables_days', 0) / 365)
    
    total_wc_req = ar_req + inv_req - ap_offset
    
    # 3. Structural Debt Logic
    interest_expense = s.get('debt', 0.0) * s.get('interest_rate', 0.0)
    annual_debt_service = s.get('annual_loan_payment', 0.0)
    principal_repayment = max(0.0, annual_debt_service - interest_expense)
    
    # 4. Cash Wall (Survival Threshold)
    cash_wall = s.get('fixed_cost', 0.0) + annual_debt_service + total_wc_req
    survival_bep = cash_wall / unit_contribution if unit_contribution > 0 else float('inf')
    
    # 5. P&L & Cash Flow
    ebit = (unit_contribution * s.get('volume', 0.0)) - s.get('fixed_cost', 0.0)
    ebt = ebit - interest_expense
    tax = max(0.0, ebt * s.get('tax_rate', 0.22))
    net_profit = ebt - tax
    
    # FCF = Net Profit - Principal (WC is upfront in Stage 3)
    fcf = net_profit - principal_repayment
    
    metrics = {
        "revenue": rev_annual,
        "unit_contribution": unit_contribution,
        "total_wc_requirement": total_wc_req,
        "cash_wall": cash_wall,
        "survival_bep": survival_bep,
        "ebit": ebit,
        "net_profit": net_profit,
        "fcf": fcf,
        "annual_debt_service": annual_debt_service,
        "interest_expense": interest_expense,
        "principal_repayment": principal_repayment
    }
    
    s.last_computed_metrics = metrics
    return metrics
