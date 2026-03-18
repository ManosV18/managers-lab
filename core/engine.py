import streamlit as st

def calculate_metrics(price, volume, variable_cost, fixed_cost,
                     ar_days, inv_days, ap_days,
                     annual_debt_service, opening_cash,
                     total_debt=0.0,    
                     fixed_assets=0.0,  
                     target_profit=0.0):
    
    # 1. Base Unit Economics
    unit_contribution = price - variable_cost
    revenue = price * volume
    total_vc = variable_cost * volume
    total_costs = total_vc + fixed_cost
    ebit = (unit_contribution * volume) - fixed_cost
    
    # 2. Taxes & NOPAT (22% Corporate Tax)
    tax_rate = 0.22
    net_profit = ebit * (1 - tax_rate) if ebit > 0 else ebit
    nopat = ebit * (1 - tax_rate)

    # 3. 365-Day Logic [User Instruction 2026-02-18]
    daily_rev = revenue / 365 if revenue > 0 else 0
    daily_vc = total_vc / 365 if total_vc > 0 else 0

    # 4. Operating Working Capital (OWC)
    ar_value = daily_rev * ar_days
    inv_value = daily_vc * inv_days
    ap_value = daily_vc * ap_days
    
    net_working_capital = ar_value + inv_value - ap_value
    
    # 5. Invested Capital (Total Capital View - As requested)
    # Περιλαμβάνει NWC, Πάγια ΚΑΙ το Διαθέσιμο Μετρητό
    invested_capital = net_working_capital + fixed_assets + opening_cash
    
    # 6. ROIC (Return on Invested Capital)
    invested_capital_for_roic = max(invested_capital, 1.0)
    roic = nopat / invested_capital_for_roic if nopat > 0 else 0

    # 7. Debt & Liquidity Analysis
    net_debt = total_debt - opening_cash

    # 8. Final Cash Position (The "Survival" Metric)
    net_cash = opening_cash + net_profit - annual_debt_service - net_working_capital
    
    # 9. Break-Even Analysis (Cash Basis)
    cash_wall_requirements = fixed_cost + annual_debt_service + target_profit
    
    if unit_contribution > 0:
        bep_units = cash_wall_requirements / unit_contribution
        margin_of_safety = (volume - bep_units) / volume if volume > 0 else -1.0
    else:
        bep_units = None
        margin_of_safety = -1.0

    # 10. Efficiency & Risk Metrics
    ccc = ar_days + inv_days - ap_days
    contribution_margin = unit_contribution * volume
    dol = contribution_margin / ebit if ebit != 0 else 0

    # 11. Cash Burn & Runway Engine
    monthly_cf = (net_profit - annual_debt_service) / 12
    if monthly_cf < 0:
        runway = opening_cash / abs(monthly_cf)
    else:
        runway = float('inf')

    # --- RETURN FULL DICTIONARY ---
    return {
        "unit_contribution": unit_contribution,
        "revenue": revenue,
        "total_costs": total_costs,
        "ebit": ebit,
        "nopat": nopat,
        "net_profit": net_profit,
        "bep_units": bep_units,
        "margin_of_safety": margin_of_safety,
        "net_cash_position": net_cash,
        "net_working_capital": net_working_capital,
        "wc_requirement": net_working_capital, 
        "invested_capital": invested_capital,
        "roic": roic,
        "net_debt": net_debt,
        "total_debt": total_debt,
        "ar_value": ar_value,
        "inv_value": inv_value,
        "ap_value": ap_value,
        "receivables_euro": ar_value,  
        "inventory_euro": inv_value,    
        "payables_euro": ap_value,      
        "ccc": ccc,
        "dol": dol,
        "runway_months": runway,
        "monthly_burn": abs(min(0, monthly_cf))
    }
