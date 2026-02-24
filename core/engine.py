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
        "annual_loan_payment": 12000.0, # Προσθήκη για Principal + Interest
        "interest_rate": 0.05,
        "wacc": 0.12,
        "tax_rate": 0.22,
        "tax_input_field": 22.0,
        "interest_input_field": 5.0,
        "wacc_input_field": 12.0,
        
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
    p = s.get('price', 50.0)
    v = s.get('volume', 15000)
    vc = s.get('variable_cost', 25.0)
    fc = s.get('fixed_cost', 200000.0)
    debt = s.get('debt', 20000.0)
    int_rate = s.get('interest_rate', 0.05)
    tax_rate = s.get('tax_rate', 0.22)
    
    # 2. P&L Calculations (Standard Accrual)
    unit_contribution = p - vc
    revenue = p * v
    cogs = vc * v
    ebit = (unit_contribution * v) - fc
    
    interest_expense = debt * int_rate
    ebt = ebit - interest_expense
    tax_amount = max(0, ebt * tax_rate)
    net_profit = ebt - tax_amount # Καθαρό κέρδος (Λογιστικό)

    # 3. Working Capital & Liquidity (Cash Flow Impact)
    # Χρήση 365 ημερών βάσει οδηγίας
    curr_ar = revenue * (s.get('ar_days', 45) / 365)
    curr_inv = cogs * (s.get('inventory_days', 60) / 365)
    curr_pay = cogs * (s.get('payables_days', 30) / 365)
    
    wc_base = curr_ar + curr_inv - curr_pay
    inv_friction = curr_inv * s.get('slow_moving_factor', 0.2)
    
    # Το Liquidity Drain είναι η συνολική δέσμευση μετρητών στην επιχείρηση
    total_liquidity_drain = wc_base + inv_friction
    s['liquidity_drain_annual'] = total_liquidity_drain

    # 4. Cash Flow Logic
    opening_cash = 0.05 * revenue # Buffer ασφαλείας
    
    # FCF = Net Profit + Non-Cash - CapEx - ΔWC
    # Εδώ ως ΔWC θεωρούμε όλο το liquidity drain για την πρώτη περίοδο
    fcf = net_profit - total_liquidity_drain
    ending_cash = opening_cash + fcf

    # 5. Break-Even Analysis (The "Cold" Thresholds)
    # Operating BEP: Καλύπτει μόνο Fixed Costs
    op_bep = fc / unit_contribution if unit_contribution > 0 else 0
    
    # Survival BEP: Πρέπει να καλύψει Fixed Costs + Τόκους + Δέσμευση WC
    # Σημείωση: Το WC εξαρτάται από το volume, οπότε χρησιμοποιούμε το WC per unit
    wc_per_unit = total_liquidity_drain / v if v > 0 else 0
    
    # Survival BEP Formula: (FC + Interest) / (Unit Contribution - WC per Unit)
    # Δείχνει πόσες μονάδες πρέπει να πουλήσεις για να μην "στεγνώσεις" από μετρητά
    denominator = unit_contribution - wc_per_unit
    surv_bep = (fc + interest_expense) / denominator if denominator > 0 else 0

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
        "cash_survival_horizon": opening_cash / abs(fcf) if fcf < 0 else float('inf'),
        "liquidity_drain": total_liquidity_drain
    }
