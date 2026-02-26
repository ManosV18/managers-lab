import streamlit as st

def lock_baseline():
    """Activates the engine by locking the initial parameters."""
    st.session_state.baseline_locked = True

def sync_global_state():
    """
    Gatekeeper function: Synchronizes sidebar inputs with the calculation engine.
    Returns calculated metrics only if baseline_locked is True.
    """
    s = st.session_state

    # 1. Verification Lock
    if not s.get('baseline_locked', False):
        st.error("🚨 Baseline Not Defined. Please complete Stage 0 to initialize the engine.")
        st.stop()

    # 2. Data Retrieval from Sidebar/Session
    # We use .get() with defaults to ensure the engine never receives 'None'
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
        'opening_cash': float(s.get('opening_cash', 0.0))
    }

    # 3. Execution of your Calculation Logic
    return calculate_metrics(**params)

def calculate_metrics(price, volume, variable_cost, fixed_cost, wacc, tax_rate, ar_days, inv_days, ap_days, annual_debt_service, opening_cash):
    # P&L Logic
    unit_contribution = price - variable_cost
    revenue = price * volume
    total_vc = variable_cost * volume
    contribution_margin = unit_contribution * volume
    ebit = contribution_margin - fixed_cost
    
    # Tax & Cash Flow
    tax_payment = max(0, ebit * tax_rate)
    fcf = ebit - tax_payment - annual_debt_service
    
    # Working Capital & Liquidity (Instruction [2026-02-18]: 365 Days Base)
    daily_rev = revenue / 365 if revenue > 0 else 0
    daily_costs = (total_vc + fixed_cost) / 365
    
    accounts_receivable = daily_rev * ar_days
    inventory_val = daily_costs * inv_days
    accounts_payable = daily_costs * ap_days
    
    wc_requirement = accounts_receivable + inventory_val - accounts_payable
    
    # Updated key name to match Stages 3 & 4
    net_cash_position = opening_cash - wc_requirement 
    
    # Survival Metrics
    monthly_net = fcf / 12
    # Runway calculation
    if monthly_net >= 0:
        runway = 100.0
    else:
        runway = max(0.0, net_cash_position / abs(monthly_net))

    # Return dictionary with standardized keys for all Stages
    return {
        'unit_contribution': unit_contribution,
        'contribution_margin': contribution_margin,
        'ebit': ebit,
        'fcf': fcf,
        'ocf': ebit - tax_payment,
        'ccc': ar_days + inv_days - ap_days,
        'bep_units': (fixed_cost + annual_debt_service) / unit_contribution if unit_contribution > 0 else 0,
        'revenue': revenue,
        'wc_requirement': wc_requirement,
        'net_cash_position': net_cash_position,
        'runway_months': runway,
        'cash_wall': fixed_cost + annual_debt_service,
        'accounts_receivable': accounts_receivable,
        'contribution_ratio': unit_contribution / price if price > 0 else 0
    }
