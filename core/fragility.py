def compute_fragility(fcf: float, current_cash: float, monthly_net: float):
    """
    Measures system resilience.
    Higher score = Lower ability to absorb market shocks.
    """
    
    # 1. Burn Rate Assessment
    is_burning_cash = monthly_net < 0
    
    # 2. Coverage Months (Runway)
    if is_burning_cash:
        coverage_months = current_cash / abs(monthly_net)
    else:
        coverage_months = 100.0 # Σταθερό σύστημα
        
    # 3. Fragility Index (0.0 to 1.0)
    # 1.0 σημαίνει ότι η κατάρρευση είναι άμεση
    if coverage_months >= 12:
        fragility_score = 0.2
    elif coverage_months <= 0:
        fragility_score = 1.0
    else:
        # Linear scale: όσο λιγότεροι μήνες, τόσο μεγαλύτερο το fragility
        fragility_score = 1.0 - (coverage_months / 12)
        
    return {
        "fragility_score": fragility_score,
        "coverage_months": coverage_months,
        "is_high_risk": fragility_score > 0.7,
        "status": "CRITICAL" if fragility_score > 0.8 else "STABLE"
    }
