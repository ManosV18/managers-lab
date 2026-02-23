import streamlit as st

def initialize_system_state():
    """Single Source of Truth - Separating WACC from Interest Rate"""
    
    # Define all defaults
    defaults = {
        # UI & Flow
        "mode": "home",
        "flow_step": 0,
        "baseline_locked": False,
        "selected_tool": None,
        
        # Revenue & Costs
        "price": 30.0,
        "volume": 10000,
        "variable_cost": 15.0,
        "fixed_cost": 50000.0,
        
        # Working Capital
        "ar_days": 45,
        "inventory_days": 60,
        "payables_days": 30,
        "ccc": 0,
        "working_capital_req": 0.0,
        "liquidity_drain_annual": 0.0,
        
        # Capital & Financing (THE FIX: Distinct Rates)
        "debt": 20000.0,
        "interest_rate": 0.05,  # Cost of Debt (for Payables/Loans)
        "wacc": 0.12,           # Weighted Average Cost of Capital (for NPV/Receivables)
        "annual_loan_payment": 12000.0,
        
        # Customer
        "retention_rate": 0.85,
        "cac": 150.0,
        "purch_per_year": 4.0
    }

    # Safe batch update
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value
