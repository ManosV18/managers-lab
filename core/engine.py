def calculate_metrics(price, volume, variable_cost, fixed_cost, wacc, tax_rate, ar_days, inv_days, ap_days, annual_debt):
    """
    Pure Logic Layer. 
    Calculates everything from P&L to Cash Flow metrics.
    """
    # P&L Metrics
    revenue = price * volume
    total_vc = variable_cost * volume
    contribution_margin = revenue - total_vc
    ebit = contribution_margin - fixed_cost
    
    # Ratios
    contribution_ratio = (contribution_margin / revenue) if revenue > 0 else 0
    margin_pct = contribution_ratio * 100
    
    # Cash Flow & Survival
    # Simplified FCF: EBIT - Tax - Debt Service
    tax_payment = max(0, ebit * tax_rate)
    fcf = ebit - tax_payment - annual_debt
    
    # Efficiency metrics
    ccc = ar_days + inv_days - ap_days
    
    # Break-even
    # Survival BEP includes debt coverage
    survival_bep = (fixed_cost + annual_debt) / (price - variable_cost) if (price - variable_cost) > 0 else 0
    
    return {
        'revenue': revenue,
        'ebit': ebit,
        'contribution_margin': contribution_margin,
        'contribution_ratio': contribution_ratio,
        'fcf': fcf,
        'ccc': ccc,
        'survival_bep': survival_bep,
        'wacc': wacc
    }
