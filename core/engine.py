import streamlit as st

def compute_core_metrics():
    s = st.session_state
    
    # --- 1. UNIT ECONOMICS & VIABILITY GUARDRAIL ---
    unit_contribution = s.get('price', 0.0) - s.get('variable_cost', 0.0)
    # Explicit Flag για δομική βιωσιμότητα
    is_non_viable = unit_contribution <= 0
    
    # --- 2. WORKING CAPITAL (Upfront Drain) ---
    rev_annual = s.get('price', 0.0) * s.get('volume', 0.0)
    cogs_annual = s.get('variable_cost', 0.0) * s.get('volume', 0.0)
    
    ar_req = rev_annual * (s.get('ar_days', 0) / 365)
    inv_req = cogs_annual * (s.get('inventory_days', 0) / 365) * (1 + s.get('slow_moving_factor', 0.0))
    ap_offset = cogs_annual * (s.get('payables_days', 0) / 365)
    
    total_wc_req = ar_req + inv_req - ap_offset
    
    # --- 3. OPERATING CASH FLOW (OCF) LAYER ---
    ebit = (unit_contribution * s.get('volume', 0.0)) - s.get('fixed_cost', 0.0)
    # Tax on EBIT (προ τόκων για καθαρό OCF)
    tax_on_ebit = max(0.0, ebit * s.get('tax_rate', 0.22))
    nopat = ebit - tax_on_ebit
    
    # OCF (Εδώ το WC αφαιρείται upfront στο Stage 3, οπότε το OCF είναι το recurring flow)
    # OCF = NOPAT + Depreciation (εδώ 0)
    ocf = nopat 
    
    # --- 4. DEBT SERVICE & FCF ---
    interest_expense = s.get('debt', 0.0) * s.get('interest_rate', 0.0)
    annual_debt_service = s.get('annual_loan_payment', 0.0)
    principal_repayment = max(0.0, annual_debt_service - interest_expense)
    
    # FCF = OCF - Debt Service
    fcf = ocf - annual_debt_service
    
    # --- 5. SURVIVAL WALL ---
    cash_wall = s.get('fixed_cost', 0.0) + annual_debt_service + total_wc_req
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
        "fcf": fcf,
        "annual_debt_service": annual_debt_service,
        "principal_repayment": principal_repayment
    }
    
    s.last_computed_metrics = metrics
    return metrics
