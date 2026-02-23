import streamlit as st

def compute_core_metrics():
    """Central derived calculations incorporating Taxes, WACC and Interest Rate"""
    
    # 1. Fetch values safely from session state
    s = st.session_state
    p = s.get('price', 30.0)
    v = s.get('volume', 10000)
    vc = s.get('variable_cost', 15.0)
    fc = s.get('fixed_cost', 50000.0)
    debt = s.get('debt', 0.0)
    
    # 2. Rates & Tax
    cost_of_debt = s.get('interest_rate', 0.05)
    wacc = s.get('wacc', 0.12)
    tax_rate = s.get('tax_rate', 0.22) # Default 22% (Ελληνικός συντελεστής)
    
    # 3. Cash Flow adjustments
    liquidity = s.get('liquidity_drain_annual', 0.0)

    # 4. Financial Logic (The P&L Ladder)
    unit_contribution = p - vc
    revenue = p * v
    ebit = (unit_contribution * v) - fc
    
    # Interest is calculated ONLY on Interest Rate (Cost of Debt)
    interest_expense = debt * cost_of_debt
    
    # EBT (Earnings Before Taxes)
    ebt = ebit - interest_expense - liquidity
    
    # Tax Calculation & Net Profit
    tax_amount = max(0, ebt * tax_rate) # Φόρος μόνο αν υπάρχει κέρδος
    net_profit = ebt - tax_amount

    # 5. Break-Even Analysis
    operating_bep = fc / unit_contribution if unit_contribution > 0 else 0
    total_fixed_burden = fc + interest_expense + liquidity
    survival_bep = total_fixed_burden / unit_contribution if unit_contribution > 0 else 0

    return {
        "unit_contribution": unit_contribution,
        "revenue": revenue,
        "ebit": ebit,
        "ebt": ebt,
        "tax_amount": tax_amount,
        "net_profit": net_profit,
        "operating_bep": operating_bep,
        "survival_bep": survival_bep,
        "wacc": wacc,
        "interest_rate": cost_of_debt,
        "tax_rate": tax_rate
    }
