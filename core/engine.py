import streamlit as st

def calculate_metrics(price, volume, variable_cost, fixed_cost,
                     ar_days, inv_days, ap_days,
                     annual_debt_service, opening_cash,
                     total_debt=0.0,    
                     fixed_assets=0.0,  
                     target_profit=0.0,
                     tax_rate=22.0,      
                     annual_interest=0.0,
                     equity=0.0,         # New: McKinsey Logic Requirement
                     depreciation=0.0    # New: For Tax Shield & Cash Flow accuracy
                     ):
    
    # 1. Base Unit Economics
    unit_contribution = price - variable_cost
    revenue = price * volume
    total_vc = variable_cost * volume
    
    # EBIT (Operating Profit) - Adjusted for Depreciation
    # EBITDA = Contribution - Fixed Cash Costs
    # EBIT = EBITDA - Depreciation
    ebitda = (unit_contribution * volume) - fixed_cost
    ebit = ebitda - depreciation
    
    # 2. Taxes, Interest & Net Profit
    # EBT (Earnings Before Tax) = EBIT - Interest
    ebt = ebit - annual_interest
    
    # Corporate Tax calculation on EBT
    tax_factor = tax_rate / 100
    tax_amount = max(0, ebt * tax_factor)
    
    # Net Profit (The actual bottom line)
    net_profit = ebt - tax_amount
    
    # NOPAT (For ROIC calculation)
    nopat = ebit * (1 - tax_factor) if ebit > 0 else ebit

    # 3. 365-Day Logic [User Instruction 2026-02-18]
    daily_rev = revenue / 365 if revenue > 0 else 0
    daily_vc = total_vc / 365 if total_vc > 0 else 0

    # 4. Operating Working Capital (OWC) - The Netting Logic
    ar_value = daily_rev * ar_days
    inv_value = daily_vc * inv_days
    ap_value = daily_vc * ap_days
    # Net Working Capital: Απαιτήσεις + Αποθέματα - Προμηθευτές
    net_working_capital = ar_value + inv_value - ap_value
    
    # 5. Invested Capital (McKinsey Lean Approach)
    # Περιορισμός μετρητών στο 2% των πωλήσεων για το ROIC
    operating_cash_limit = revenue * 0.02
    effective_cash_for_roic = min(opening_cash, operating_cash_limit)
    
    # Invested Capital = Net Working Capital + Net Fixed Assets + Operating Cash
    invested_capital = net_working_capital + fixed_assets + effective_cash_for_roic
    
    # 6. ROIC (Return on Invested Capital)
    invested_capital_for_roic = max(invested_capital, 1.0)
    roic = nopat / invested_capital_for_roic if nopat > 0 else 0
    
    # Return on Equity (ROE)
    roe = net_profit / max(equity, 1.0) if equity > 0 else 0

    # 7. Debt & Liquidity Analysis
    net_debt = total_debt - opening_cash

    # 8. Final Cash Position (The "Survival" Metric)
    # Προσθέτουμε depreciation πίσω γιατί δεν είναι ταμειακή εκροή
    # net_cash = Ταμείο + Net Profit + Αποσβέσεις - Καθαρές πληρωμές χρέους - Μεταβολή NWC
    net_cash = opening_cash + net_profit + depreciation - (annual_debt_service - annual_interest) - net_working_capital
    
    # 9. Break-Even Analysis (Cash Basis)
    # Χρησιμοποιούμε μόνο τα Cash Fixed Costs. Οι αποσβέσεις εξαιρούνται γιατί δεν είναι ταμειακή εκροή.
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

    # 11. Cash Burn & Runway Engine (Monthly perspective)
    # Προσθέτουμε depreciation για να βρούμε το πραγματικό μηνιαίο cash flow
    monthly_cf = (net_profit + depreciation - (annual_debt_service - annual_interest)) / 12
    if monthly_cf < 0:
        runway = opening_cash / abs(monthly_cf)
    else:
        runway = float('inf')

    # --- ROIC AUDIT DATA ---
    roic_debug = {
        "EBIT": ebit,
        "NOPAT": nopat,
        "NWC (Net)": net_working_capital,
        "Operating Cash (2%)": effective_cash_for_roic,
        "Invested Capital": invested_capital,
        "Final ROIC": roic
    }

    # --- RETURN FULL DICTIONARY ---
    return {
        "unit_contribution": unit_contribution,
        "revenue": revenue,
        "total_costs": total_vc + fixed_cost + depreciation,
        "ebit": ebit,
        "ebt": ebt,
        "tax_amount": tax_amount,
        "tax_rate": tax_rate,
        "annual_interest": annual_interest,
        "nopat": nopat,
        "net_profit": net_profit,
        "roe": roe,
        "bep_units": bep_units,
        "margin_of_safety": margin_of_safety,
        "net_cash_position": net_cash,
        "net_working_capital": net_working_capital,
        "invested_capital": invested_capital,
        "roic": roic,
        "roic_debug": roic_debug,
        "net_debt": net_debt,
        "total_debt": total_debt,
        "ar_value": ar_value,
        "inv_value": inv_value,
        "ap_value": ap_value,
        "ccc": ccc,
        "dol": dol,
        "runway_months": runway,
        "monthly_burn": abs(min(0, monthly_cf))
    }
