import streamlit as st

def compute_core_metrics():
    s = st.session_state
    
    # Ασφαλής ανάκτηση δεδομένων με defaults
    price = s.get('price', 0.0)
    v_cost = s.get('variable_cost', 0.0)
    vol = s.get('volume', 0.0)
    f_cost = s.get('fixed_cost', 0.0)
    debt_service = s.get('annual_loan_payment', 0.0)
    
    # 1. Unit Economics
    unit_contribution = price - v_cost
    
    # 2. Working Capital Physics (Annual)
    # DSO (on Revenue) + DIO (on COGS) - DPO (on COGS)
    revenue_annual = price * vol
    cogs_annual = v_cost * vol
    
    ar_req = revenue_annual * (s.get('ar_days', 0) / 365)
    inv_req = cogs_annual * (s.get('inventory_days', 0) / 365) * (1 + s.get('slow_moving_factor', 0.0))
    ap_offset = cogs_annual * (s.get('payables_days', 0) / 365)
    
    total_wc_req = ar_req + inv_req - ap_offset
    
    # 3. Cash Wall & Survival BEP
    cash_wall = f_cost + debt_service + total_wc_req
    survival_bep = cash_wall / unit_contribution if unit_contribution > 0 else float('inf')
    
    # 4. Profitability (Accounting)
    ebit = (unit_contribution * vol) - f_cost
    interest_expense = s.get('debt', 0.0) * s.get('interest_rate', 0.0)
    ebt = ebit - interest_expense
    tax = max(0.0, ebt * s.get('tax_rate', 0.22))
    net_profit = ebt - tax
    
    # 5. Cash Flow (FCF)
    # Net Profit - Principal - WC Requirement
    principal = max(0.0, debt_service - interest_expense)
    fcf = net_profit - total_wc_req - principal
    
    metrics = {
        "unit_contribution": unit_contribution,
        "total_wc_requirement": total_wc_req,
        "cash_wall": cash_wall,
        "survival_bep": survival_bep,
        "net_profit": net_profit,
        "fcf": fcf,
        "ebit": ebit
    }
    
    s.last_computed_metrics = metrics
    return metrics
