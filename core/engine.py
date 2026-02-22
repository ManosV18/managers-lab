import streamlit as st

def compute_core_metrics():
    """Central derived calculations"""
    # Χρησιμοποιούμε .get() για ασφάλεια κατά το πρώτο run
    p = st.session_state.get('price', 0.0)
    v = st.session_state.get('volume', 0)
    vc = st.session_state.get('variable_cost', 0.0)
    fc = st.session_state.get('fixed_cost', 0.0)
    debt = st.session_state.get('debt', 0.0)
    rate = st.session_state.get('interest_rate', 0.0)
    liquidity = st.session_state.get('liquidity_drain_annual', 0.0)

    unit_contribution = p - vc
    revenue = p * v
    ebit = (unit_contribution * v) - fc
    interest = debt * rate
    net_profit = ebit - interest - liquidity

    operating_bep = fc / unit_contribution if unit_contribution > 0 else 0
    full_fixed = fc + interest + liquidity
    survival_bep = full_fixed / unit_contribution if unit_contribution > 0 else 0

    return {
        "unit_contribution": unit_contribution,
        "revenue": revenue,
        "ebit": ebit,
        "interest": interest,
        "net_profit": net_profit,
        "operating_bep": operating_bep,
        "survival_bep": survival_bep
    }
