import streamlit as st

def calculate_metrics(price, volume, variable_cost, fixed_cost,
                      ar_days, inv_days, ap_days,
                      annual_debt_service, opening_cash,
                      target_profit=0.0):
    
    # 1. Base Unit Economics
    unit_contribution = price - variable_cost
    revenue = price * volume
    total_vc = variable_cost * volume
    ebit = (unit_contribution * volume) - fixed_cost
    
    # 22% Corporate Tax (Cold Logic)
    tax_rate = 0.22
    net_profit = ebit * (1 - tax_rate) if ebit > 0 else ebit

    # 2. NOPAT (Net Operating Profit After Taxes)
    # Crucial for ROIC: Performance regardless of financing structure
    nopat = ebit * (1 - tax_rate)

    # 3. 365-Day Logic [User Instruction 2026-02-18]
    daily_rev = revenue / 365 if revenue > 0 else 0
    daily_vc = total_vc / 365 if total_vc > 0 else 0

    # 4. Working Capital & Invested Capital
    ar_value = daily_rev * ar_days
    inv_value = daily_vc * inv_days
    ap_value = daily_vc * ap_days
    wc_req = ar_value + inv_value - ap_value
    
    # Invested Capital = Working Capital + Operating Assets (represented by Opening Cash/Equity here)
    invested_capital = opening_cash + wc_req
    
    # 5. ROIC (Return on Invested Capital)
    # The gold standard for value creation
    roic = nopat / invested_capital if invested_capital > 0 else 0

    # 6. Final Cash Position
    net_cash = opening_cash + net_profit - annual_debt_service - wc_req

    # 7. Break-Even Analysis (Cash Basis)
    cash_wall_requirements = fixed_cost + annual_debt_service + target_profit
    
    if unit_contribution > 0:
        bep_units = cash_wall_requirements / unit_contribution
        margin_of_safety = (volume - bep_units) / volume if volume > 0 else -1.0
    else:
        bep_units = None
        margin_of_safety = -1.0

    # 8. Efficiency & Risk Metrics
    ccc = ar_days + inv_days - ap_days
    contribution_margin = unit_contribution * volume
    dol = contribution_margin / ebit if ebit != 0 else 0

    # 9. Cash Burn & Runway Engine
    monthly_cf = (net_profit - annual_debt_service) / 12
    if monthly_cf < 0:
        runway = opening_cash / abs(monthly_cf)
    else:
        runway = float('inf')

    return {
        "unit_contribution": unit_contribution,
        "revenue": revenue,
        "ebit": ebit,
        "nopat": nopat,
        "net_profit": net_profit,
        "bep_units": bep_units,
        "margin_of_safety": margin_of_safety,
        "net_cash_position": net_cash,
        "wc_requirement": wc_req,
        "invested_capital": invested_capital,
        "roic": roic,
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
