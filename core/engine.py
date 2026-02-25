def calculate_metrics(price, volume, variable_cost, fixed_cost, wacc, tax_rate, ar_days, inv_days, ap_days, annual_debt, opening_cash):
    # P&L Logic
    unit_contribution = price - variable_cost
    revenue = price * volume
    total_vc = variable_cost * volume
    ebit = (unit_contribution * volume) - fixed_cost
    
    # Cash Flow Logic
    tax_payment = max(0, ebit * tax_rate)
    ocf = ebit - tax_payment
    fcf = ocf - annual_debt
    
    # Liquidity Logic
    daily_rev = revenue / 365
    daily_costs = (total_vc + fixed_cost) / 365
    wc_requirement = (daily_rev * ar_days) + (daily_costs * inv_days) - (daily_costs * ap_days)
    
    cash_reserve = opening_cash - wc_requirement
    monthly_net = fcf / 12
    
    # Runway Calculation
    if monthly_net >= 0:
        runway = 100.0 # Σύμβολο σταθερότητας
    else:
        runway = max(0.0, cash_reserve / abs(monthly_net))
        
    return {
        'unit_contribution': unit_contribution,
        'revenue': revenue,
        'ebit': ebit,
        'fcf': fcf,
        'ocf': ocf,
        'wc_requirement': wc_requirement,
        'cash_reserve': cash_reserve,
        'runway_months': runway,
        'survival_bep': (fixed_cost + annual_debt) / unit_contribution if unit_contribution > 0 else 0,
        'cash_wall': fixed_cost + annual_debt # Συνολικό σταθερό βάρος
    }
