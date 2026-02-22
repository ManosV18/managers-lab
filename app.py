import streamlit as st

def compute_core_metrics():
    """Central derived calculations"""

    p = st.session_state.price
    v = st.session_state.volume
    vc = st.session_state.variable_cost
    fc = st.session_state.fixed_cost
    debt = st.session_state.debt
    rate = st.session_state.interest_rate
    liquidity = st.session_state.liquidity_drain_annual

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
