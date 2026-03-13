def calculate_metrics(price, volume, variable_cost, fixed_cost,
                      ar_days, inv_days, ap_days,
                      annual_debt_service, opening_cash,
                      target_profit=0.0):
    
    # 1. Βασικοί Υπολογισμοί Unit Economics
    unit_contribution = price - variable_cost
    revenue = price * volume
    total_vc = variable_cost * volume
    ebit = (unit_contribution * volume) - fixed_cost
    
    # Φόρος 22% (Cold Logic)
    tax_rate = 0.22
    net_profit = ebit * (1 - tax_rate) if ebit > 0 else ebit

    # 2. 365-Day Logic [User Instruction 2026-02-18]
    daily_rev = revenue / 365 if revenue > 0 else 0
    daily_vc = total_vc / 365 if total_vc > 0 else 0

    # 3. Working Capital & Cash Position
    ar_value = daily_rev * ar_days
    inv_value = daily_vc * inv_days
    ap_value = daily_vc * ap_days
    wc_req = ar_value + inv_value - ap_value
    
    # Η τελική ταμειακή θέση
    net_cash = opening_cash + net_profit - annual_debt_service - wc_req

    # 4. Break-Even Analysis (Cash Basis)
    cash_wall_requirements = fixed_cost + annual_debt_service + target_profit
    
    if unit_contribution > 0:
        bep_units = cash_wall_requirements / unit_contribution
        margin_of_safety = (volume - bep_units) / volume if volume > 0 else -1.0
    else:
        bep_units = None
        margin_of_safety = -1.0

    # 5. Cash Conversion Cycle (CCC)
    ccc = ar_days + inv_days - ap_days

    # ========================================================
    # ΠΡΟΣΘΗΚΗ ΝΕΩΝ ΥΠΟΛΟΓΙΣΜΩΝ (WC ENGINE, DOL, RUNWAY)
    # ========================================================
    
    # 6. Operating Leverage (DOL)
    # DOL = Contribution Margin / Operating Profit (EBIT)
    contribution_margin = unit_contribution * volume
    dol = contribution_margin / ebit if ebit != 0 else 0

    # 7. Cash Burn & Runway Engine
    # Μηνιαίο Cash Flow (Net Profit - Δόσεις - Μεταβολή WC) / 12
    # Χρησιμοποιούμε το EBIT - Φόρος - Δόσεις για να δούμε αν "μπαίνει μέσα" το μαγαζί
    monthly_cf = (net_profit - annual_debt_service) / 12
    
    if monthly_cf < 0:
        runway = opening_cash / abs(monthly_cf)
    else:
        runway = float('inf')

    return {
        "unit_contribution": unit_contribution,
        "revenue": revenue,
        "ebit": ebit,
        "net_profit": net_profit,
        "bep_units": bep_units,
        "margin_of_safety": margin_of_safety,
        "net_cash_position": net_cash,
        "wc_requirement": wc_req,
        "ar_value": ar_value,
        "inv_value": inv_value,
        "ap_value": ap_value,
        "receivables_euro": ar_value,  # Alias για συμβατότητα με το UI
        "inventory_euro": inv_value,    # Alias για συμβατότητα με το UI
        "payables_euro": ap_value,      # Alias για συμβατότητα με το UI
        "ccc": ccc,
        "dol": dol,
        "runway_months": runway,
        "monthly_burn": abs(min(0, monthly_cf))
    }
