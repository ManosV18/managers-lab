def calculate_metrics(price, volume, variable_cost, fixed_cost, wacc, tax_rate, ar_days, inv_days, ap_days, annual_debt, opening_cash):
    # P&L Logic
    unit_contribution = price - variable_cost
    revenue = price * volume
    total_vc = variable_cost * volume
    contribution_margin = unit_contribution * volume
    ebit = contribution_margin - fixed_cost
    
    # Tax & Cash Flow
    tax_payment = max(0, ebit * tax_rate)
    fcf = ebit - tax_payment - annual_debt
    
    # Working Capital & Liquidity
    daily_rev = revenue / 365 if revenue > 0 else 0
    daily_costs = (total_vc + fixed_cost) / 365
    
    accounts_receivable = daily_rev * ar_days
    inventory_val = daily_costs * inv_days
    accounts_payable = daily_costs * ap_days
    
    wc_requirement = accounts_receivable + inventory_val - accounts_payable
    cash_reserve = opening_cash - wc_requirement
    
    # Survival Metrics
    monthly_net = fcf / 12
    # Runway calculation
    if monthly_net >= 0:
        runway = 100.0
    else:
        runway = max(0.0, cash_reserve / abs(monthly_net))

    # Επιστροφή καθαρού λεξικού χωρίς διπλά κλειδιά
    return {
        'unit_contribution': unit_contribution,
        'contribution_margin': contribution_margin,
        'ebit': ebit,
        'fcf': fcf,
        'ocf': ebit - tax_payment,
        'ccc': ar_days + inv_days - ap_days,
        'survival_bep': (fixed_cost + annual_debt) / unit_contribution if unit_contribution > 0 else 0,
        'revenue': revenue,
        'wc_requirement': wc_requirement,
        'cash_reserve': cash_reserve,
        'runway_months': runway,
        'cash_wall': fixed_cost + annual_debt,
        'accounts_receivable': accounts_receivable,
        'contribution_ratio': unit_contribution / price if price > 0 else 0
    }
