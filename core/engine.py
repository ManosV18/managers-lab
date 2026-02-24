import streamlit as st

def compute_core_metrics():
    s = st.session_state
    
    # --- 1. UNIT ECONOMICS ---
    unit_contribution = s.get('price', 0.0) - s.get('variable_cost', 0.0)
    
    # --- 2. WORKING CAPITAL (Upfront Funding Requirement) ---
    rev_annual = s.get('price', 0.0) * s.get('volume', 0.0)
    cogs_annual = s.get('variable_cost', 0.0) * s.get('volume', 0.0)
    
    ar_req = rev_annual * (s.get('ar_days', 0) / 365)
    inv_req = cogs_annual * (s.get('inventory_days', 0) / 365) * (1 + s.get('slow_moving_factor', 0.0))
    ap_offset = cogs_annual * (s.get('payables_days', 0) / 365)
    
    total_wc_req = ar_req + inv_req - ap_offset
    
    # --- 3. DEBT & INTEREST LOGIC (Option B) ---
    # Ο χρήστης δίνει Annual Loan Payment & Interest Rate. Το Principal προκύπτει.
    interest_expense = s.get('debt', 0.0) * s.get('interest_rate', 0.0)
    annual_debt_service = s.get('annual_loan_payment', 0.0)
    principal_repayment = max(0.0, annual_debt_service - interest_expense)
    
    # --- 4. CASH WALL (Survival Threshold) ---
    # Cash Wall = Fixed Costs + Full Debt Service + Total WC Requirement
    cash_wall = s.get('fixed_cost', 0.0) + annual_debt_service + total_wc_req
    survival_bep = cash_wall / unit_contribution if unit_contribution > 0 else float('inf')
    
    # --- 5. P&L & TRUE FCF ---
    ebit = (unit_contribution * s.get('volume', 0.0)) - s.get('fixed_cost', 0.0)
    ebt = ebit - interest_expense
    tax = max(0.0, ebt * s.get('tax_rate', 0.22))
    net_profit = ebt - tax
    
    # FCF = Net Profit - Principal (Το WC είναι upfront στο Month 0, όχι recurring outflow)
    fcf = net_profit - principal_repayment
    
    metrics = {
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
