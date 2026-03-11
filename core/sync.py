import streamlit as st

def calculate_metrics(price, volume, variable_cost, fixed_cost, wacc, tax_rate, 
                      ar_days, inv_days, ap_days, annual_debt_service, opening_cash, target_profit=0.0):
    
    # --- P&L Logic ---
    unit_contribution = price - variable_cost
    revenue = price * volume
    total_vc = variable_cost * volume
    ebit = (unit_contribution * volume) - fixed_cost
    
    # --- Tax & Cash Flow ---
    tax_payment = max(0, ebit * tax_rate)
    # fcf = Λειτουργικά κέρδη - Φόροι - Δόσεις Δανείων
    fcf = ebit - tax_payment - annual_debt_service
    
    # --- Working Capital (365 Days Base - Instruction [2026-02-18]) ---
    daily_rev = revenue / 365 if revenue > 0 else 0
    daily_costs = (total_vc + fixed_cost) / 365
    
    accounts_receivable = daily_rev * ar_days
    inventory_val = daily_costs * inv_days
    accounts_payable = daily_costs * ap_days
    wc_requirement = accounts_receivable + inventory_val - accounts_payable
    
    # --- Liquidity & Survival ---
    net_cash_position = opening_cash - wc_requirement 
    monthly_net = fcf / 12
    
    if monthly_net >= 0:
        runway = 100.0
    else:
        runway = max(0.0, net_cash_position / abs(monthly_net))

    # --- Cash-Flow Break-Even (The "Cold" Logic) ---
    # Υπολογίζουμε πόσες μονάδες χρειάζονται για να καλυφθούν: Σταθερά + Δάνεια + Επιθυμητό Κέρδος
    cash_wall = fixed_cost + annual_debt_service + target_profit
    bep_units = cash_wall / unit_contribution if unit_contribution > 0 else 0

    return {
        'unit_contribution': unit_contribution,
        'ebit': ebit,
        'fcf': fcf,
        'revenue': revenue,
        'wc_requirement': wc_requirement,
        'net_cash_position': net_cash_position,
        'runway_months': runway,
        'cash_wall': cash_wall,
        'bep_units': bep_units,
        'contribution_ratio': unit_contribution / price if price > 0 else 0
    }

def sync_global_state():
    s = st.session_state
    if not s.get('baseline_locked', False):
        st.error("🚨 Baseline Not Defined. Please lock the baseline in Home.")
        st.stop()

    # Εδώ διορθώσαμε τα ονόματα των κλειδιών για να ταυτίζονται με το home.py
    params = {
        'price': float(s.get('price', 0.0)),
        'volume': float(s.get('volume', 0.0)),
        'variable_cost': float(s.get('variable_cost', 0.0)),
        'fixed_cost': float(s.get('fixed_cost', 0.0)),
        'wacc': float(s.get('wacc', 0.15)),
        'tax_rate': float(s.get('tax_rate', 0.22)),
        'ar_days': float(s.get('ar_days', 0.0)),
        'inv_days': float(s.get('inventory_days', 0.0)),
        'ap_days': float(s.get('ap_days', 0.0)),
        'annual_debt_service': float(s.get('annual_debt_service', 0.0)),
        'opening_cash': float(s.get('opening_cash', 0.0)),
        'target_profit': float(s.get('target_profit_goal', 0.0)) # Νέο πεδίο
    }
    return calculate_metrics(**params)
