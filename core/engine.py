import streamlit as st

def initialize_system_state():
    """Single Source of Truth: Initialize all defaults once."""
    defaults = {
        # UI & Flow
        "mode": "home",
        "flow_step": 0,
        "baseline_locked": False,
        
        # Revenue & Costs
        "price": 50.0,
        "volume": 15000,
        "variable_cost": 25.0,
        "fixed_cost": 200000.0,
        
        # Financial Structure
        "debt": 20000.0,
        "interest_rate": 0.05,
        "wacc": 0.12,
        "tax_rate": 0.22,
        "tax_input_field": 22.0,      # Για τα UI widgets
        "interest_input_field": 5.0,  # Για τα UI widgets
        "wacc_input_field": 12.0,     # Για τα UI widgets
        
        # Working Capital
        "ar_days": 45,
        "inventory_days": 60,
        "payables_days": 30,
        "slow_moving_factor": 0.2,
        "ccc": 0,
        "working_capital_req": 0.0,
        "liquidity_drain_annual": 0.0
    }

    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

def compute_core_metrics():
    """Central Engine: Calculates all P&L and Cash Flow metrics."""
    s = st.session_state

    # 1. Fetch Inputs
    price = s.get('price', 50.0)
    volume = s.get('volume', 15000)
    variable_cost = s.get('variable_cost', 25.0)
    fixed_cost = s.get('fixed_cost', 200000.0)
    debt = s.get('debt', 20000.0)
    interest_rate = s.get('interest_rate', 0.05)
    tax_rate = s.get('tax_rate', 0.22)
    ar_days = s.get('ar_days', 45)
    inv_days = s.get('inventory_days', 60)
    pay_days = s.get('payables_days', 30)
    slow_factor = s.get('slow_moving_factor', 0.2)

    # 2. P&L Calculations
    unit_contribution = price - variable_cost
    revenue = price * volume
    cogs = variable_cost * volume
    ebit = (unit_contribution * volume) - fixed_cost
    interest_expense = debt * interest_rate
    ebt = ebit - interest_expense
    tax_amount = max(0, ebt * tax_rate)
    net_profit = ebt - tax_amount

    # 3. Working Capital & Liquidity
    # Current
    curr_ar = revenue * (ar_days / 365)
    curr_inv = cogs * (inv_days / 365)
    curr_pay = cogs * (pay_days / 365)
    wc_current = curr_ar + curr_inv - curr_pay
    
    inv_friction = (inv_days / 365) * cogs * slow_factor
    liquidity_drain = wc_current + inv_friction
    s['liquidity_drain_annual'] = liquidity_drain

    # 4. Cash Flow
    opening_cash = 0.05 * revenue
    # Σε single-period, το change_in_wc θεωρείται η δέσμευση του wc_current
    fcf = net_profit - wc_current 
    ending_cash = opening_cash + fcf

    # 5. Break-Even
    op_bep = fixed_cost / unit_contribution if unit_contribution > 0 else 0
    total_burden = fixed_cost + interest_expense + liquidity_drain
    surv_bep = total_burden / unit_contribution if unit_contribution > 0 else 0

    return {
        "unit_contribution": unit_contribution,
        "revenue": revenue,
        "ebit": ebit,
        "net_profit": net_profit,
        "tax_amount": tax_amount,
        "operating_bep": op_bep,
        "survival_bep": surv_bep,
        "fcf": fcf,
        "ending_cash": ending_cash,
        "cash_survival_horizon": opening_cash / abs(fcf) if fcf < 0 else float('inf')
    }
