import streamlit as st

def compute_core_metrics():
    s = st.session_state
    
    # --- 1. Unit Economics & Liquidity Tax ---
    unit_contribution = s.price - s.variable_cost
    
    # Υπολογισμός WC per unit (Cash 'Tax' on every unit sold)
    # DSO (on Revenue) + DIO (on VC) - DPO (on VC)
    wc_per_unit = (s.price * (s.ar_days / 365)) + \
                  (s.variable_cost * (s.inventory_days / 365) * (1 + s.slow_moving_factor)) - \
                  (s.variable_cost * (s.payables_days / 365))
    
    cash_contribution_per_unit = unit_contribution - wc_per_unit
    
    # --- 2. Operating Performance (P&L) ---
    ebit = (unit_contribution * s.volume) - s.fixed_cost
    interest_expense = s.get('debt', 0) * s.get('interest_rate', 0)
    ebt = ebit - interest_expense
    tax = max(0, ebt * s.get('tax_rate', 0.22))
    net_profit = ebt - tax
    
    # --- 3. Cash Flow Reality (The 'Cold' Truth) ---
    total_wc_requirement = wc_per_unit * s.volume
    
    # Principal = Total Payment - Interest
    principal_repayment = max(0, s.get('annual_loan_payment', 0) - interest_expense)
    
    # FCF = Net Profit - Total WC Requirement - Principal Repayment
    # (Εδώ το total_wc_requirement θεωρείται το 'steady state' cash tie-up)
    fcf = net_profit - total_wc_requirement - principal_repayment
    
    # --- 4. Survival & Horizon ---
    fixed_obligations = s.fixed_cost + s.get('annual_loan_payment', 0)
    
    if cash_contribution_per_unit > 0:
        survival_bep = fixed_obligations / cash_contribution_per_unit
    else:
        survival_bep = float('inf')
        
    # Cash Survival Horizon (σε έτη) αν το FCF είναι αρνητικό
    ending_cash = s.get('ending_cash_balance', 0) # αν υπάρχει στο state
    cash_survival_horizon = float('inf')
    if fcf < 0 and ending_cash > 0:
        cash_survival_horizon = abs(ending_cash / fcf)

    # Επιστροφή όλων των metrics για live χρήση
    metrics = {
        "unit_contribution": unit_contribution,
        "wc_per_unit": wc_per_unit,
        "cash_contribution_per_unit": cash_contribution_per_unit,
        "ebit": ebit,
        "ebit_margin": ebit / (s.price * s.volume) if s.volume > 0 else 0,
        "net_profit": net_profit,
        "fcf": fcf,
        "survival_bep": survival_bep,
        "principal_repayment": principal_repayment,
        "total_wc_requirement": total_wc_requirement,
        "cash_survival_horizon": cash_survival_horizon
    }
    
    # Ενημέρωση του session_state για πρόσβαση από το UI sidebar/header
    s.last_computed_metrics = metrics
    return metrics
