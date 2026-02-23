import streamlit as st

def compute_core_metrics():
    """Central derived calculations incorporating WACC and Interest Rate"""
    
    # Fetch values safely
    s = st.session_state
    p = s.get('price', 30.0)
    v = s.get('volume', 10000)
    vc = s.get('variable_cost', 15.0)
    fc = s.get('fixed_cost', 50000.0)
    debt = s.get('debt', 0.0)
    
    # Distinct Rates
    cost_of_debt = s.get('interest_rate', 0.05)
    wacc = s.get('wacc', 0.12)
    
    liquidity = s.get('liquidity_drain_annual', 0.0)

    # Financial Logic
    unit_contribution = p - vc
    revenue = p * v
    ebit = (unit_contribution * v) - fc
    
    # Interest is calculated ONLY on Interest Rate (Cost of Debt)
    interest_expense = debt * cost_of_debt
    
    net_profit = ebit - interest_expense - liquidity

    # Break-Even Analysis
    operating_bep = fc / unit_contribution if unit_contribution > 0 else 0
    total_fixed_burden = fc + interest_expense + liquidity
    survival_bep = total_fixed_burden / unit_contribution if unit_contribution > 0 else 0

    return {
        "unit_contribution": unit_contribution,
        "revenue": revenue,
        "ebit": ebit,
        "interest": interest_expense,
        "net_profit": net_profit,
        "operating_bep": operating_bep,
        "survival_bep": survival_bep,
        "wacc": wacc,          # Available for Receivables/NPV
        "interest_rate": cost_of_debt # Available for Payables/Loans
    }
