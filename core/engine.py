def calculate_metrics(price, volume, variable_cost, fixed_cost, wacc, tax_rate, 
                      ar_days, inv_days, ap_days, annual_debt, opening_cash):
    """
    Pure Mathematical Engine. 
    Υπολογίζει το Operating Model 365 ημερών.
    """
    # 1. P&L Mechanics
    unit_contribution = price - variable_cost
    revenue = price * volume
    total_vc = variable_cost * volume
    ebit = (unit_contribution * volume) - fixed_cost
    
    # 2. Tax & Cash Flow
    tax_payment = max(0, ebit * tax_rate)
    fcf = ebit - tax_payment - annual_debt
    
    # 3. Working Capital & Liquidity
    daily_rev = revenue / 365
    daily_costs = (total_vc + fixed_cost) / 365
    
    # Physics of Cash
    accounts_receivable = daily_rev * ar_days
    inventory_val = daily_costs * inv_days
    accounts_payable = daily_costs * ap_days
    
    wc_requirement = accounts_receivable + inventory_val - accounts_payable
    cash_reserve = opening_cash - wc_requirement
    
    # 4. Survival Metrics
    monthly_net = fcf / 12
    runway = max(0.0, cash_reserve / abs(monthly_net)) if monthly_net < 0 else 100.0

    return {
        'unit_contribution': unit_contribution,
        'revenue': revenue,
        'ebit': ebit,
        'fcf': fcf,
        'ocf': ebit - tax_payment, # Operating Cash Flow
        'wc_requirement': wc_requirement,
        'cash_reserve': cash_reserve,
        'runway_months': runway,
        'survival_bep': (fixed_cost + annual_debt) / unit_contribution if unit_contribution > 0 else 0,
        'cash_wall': fixed_cost + annual_debt,
        'accounts_receivable': accounts_receivable,
        'contribution_ratio': unit_contribution / price if price > 0 else 0
    }
