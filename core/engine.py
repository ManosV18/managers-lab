import streamlit as st

def compute_core_metrics():
    s = st.session_state
    
    # --- 1. UNIT ECONOMICS (Accounting Basis) ---
    unit_contribution = s.get('price', 0) - s.get('variable_cost', 0)
    revenue_annual = s.get('price', 0) * s.get('volume', 0)
    cogs_annual = s.get('variable_cost', 0) * s.get('volume', 0)
    
    # --- 2. WORKING CAPITAL (Strategic Funding Requirement) ---
    # Υπολογισμός συνολικών αναγκών WC (Όχι ανά μονάδα, αλλά ως συνολικό κεφάλαιο)
    ar_req = revenue_annual * (s.get('ar_days', 45) / 365)
    inv_req = cogs_annual * (s.get('inventory_days', 60) / 365) * (1 + s.get('slow_moving_factor', 0.2))
    ap_offset = cogs_annual * (s.get('payables_days', 30) / 365)
    
    total_wc_requirement = ar_req + inv_req - ap_offset
    s.liquidity_drain_annual = total_wc_requirement # Συγχρονισμός με το state
    
    # --- 3. P&L & CASH DEBT SERVICE ---
    ebit = (unit_contribution * s.get('volume', 0)) - s.get('fixed_cost', 0)
    interest_expense = s.get('debt', 0) * s.get('interest_rate', 0.05)
    
    # Debt Service = Το συνολικό cash outflow για το δάνειο (Principal + Interest)
    annual_debt_service = s.get('annual_loan_payment', 0)
    principal_repayment = max(0, annual_debt_service - interest_expense)
    
    # Tax calculation
    ebt = ebit - interest_expense
    tax = max(0, ebt * s.get('tax_rate', 0.22))
    net_profit = ebt - tax

    # --- 4. TRUE CASH SURVIVAL BEP (The "Cold" Formula) ---
    # Cash Required = Fixed Costs + Full Debt Service + Total WC Requirement
    # Σημείωση: Το WC εδώ λειτουργεί ως "threshold barrier" για την επιβίωση
    total_cash_required = s.get('fixed_cost', 0) + annual_debt_service + total_wc_requirement
    
    if unit_contribution > 0:
        survival_bep = total_cash_required / unit_contribution
    else:
        survival_bep = float('inf')

    # --- 5. FREE CASH FLOW (FCF) & RUNWAY ---
    # FCF = Net Profit + Depreciation (εδώ 0) - WC Requirement - Principal Repayment
    fcf = net_profit - total_wc_requirement - principal_repayment
    
    opening_cash = s.get('opening_cash_balance', 0)
    ending_cash = opening_cash + fcf
    
    # Survival Horizon (Linear Burn)
    cash_survival_horizon = float('inf')
    if fcf < 0 and opening_cash > 0:
        cash_survival_horizon = abs(opening_cash / fcf)

    metrics = {
        "unit_contribution": unit_contribution,
        "ebit": ebit,
        "net_profit": net_profit,
        "fcf": fcf,
        "survival_bep": survival_bep,
        "total_wc_requirement": total_wc_requirement,
        "annual_debt_service": annual_debt_service,
        "ending_cash": ending_cash,
        "cash_survival_horizon": cash_survival_horizon
    }
    
    s.last_computed_metrics = metrics
    return metrics
