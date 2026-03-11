import streamlit as st

# ------------------------------------------------
# CORE CALCULATION ENGINE
# ------------------------------------------------

def calculate_metrics(price, volume, variable_cost, fixed_cost,
                      ar_days, inv_days, ap_days,
                      annual_debt_service, opening_cash,
                      target_profit=0.0):

    unit_contribution = price - variable_cost
    revenue = price * volume
    total_vc = variable_cost * volume

    contribution_margin = unit_contribution * volume
    ebit = contribution_margin - fixed_cost
    
    # --------------------------------------------
    # Working Capital (365 day rule - [2026-02-18])
    # --------------------------------------------
    daily_rev = revenue / 365 if revenue > 0 else 0
    daily_costs = (total_vc + fixed_cost) / 365 if (total_vc + fixed_cost) > 0 else 0

    accounts_receivable = daily_rev * ar_days
    inventory_val = daily_costs * inv_days
    accounts_payable = daily_costs * ap_days

    wc_requirement = accounts_receivable + inventory_val - accounts_payable
    
    # REAL LIQUIDITY: Opening Cash - WC Requirement
    net_cash_position = opening_cash - wc_requirement

    # Survival Point (Cash Wall)
    cash_wall = fixed_cost + annual_debt_service + target_profit

    # Analytical Fix: None if margin is negative or zero
    if unit_contribution > 0:
        bep_units = cash_wall / unit_contribution
    else:
        bep_units = None

    return {
        "unit_contribution": unit_contribution,
        "revenue": revenue,
        "ebit": ebit,
        "cash_wall": cash_wall,
        "bep_units": bep_units,
        "wc_requirement": wc_requirement,
        "net_cash_position": net_cash_position,
        "ccc": ar_days + inv_days - ap_days
    }

def sync_global_state():
    s = st.session_state
    if not s.get("baseline_locked"):
        return {}

    params = {
        "price": float(s.get("price", 100.0)),
        "volume": float(s.get("volume", 1000.0)),
        "variable_cost": float(s.get("variable_cost", 60.0)),
        "fixed_cost": float(s.get("fixed_cost", 20000.0)),
        "ar_days": float(s.get("ar_days", 45.0)),
        "inv_days": float(s.get("inventory_days", 60.0)),
        "ap_days": float(s.get("ap_days", 30.0)),
        "annual_debt_service": float(s.get("annual_debt_service", 0.0)),
        "opening_cash": float(s.get("opening_cash", 10000.0)),
        "target_profit": float(s.get("target_profit_goal", 0.0))
    }

    metrics = calculate_metrics(**params)
    st.session_state.metrics = metrics
    return metrics
