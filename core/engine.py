import streamlit as st

def refresh_global_metrics():
    """
    The Single Source of Truth. 
    This calculates all core numbers and locks the baseline.
    """
    # FETCH INPUTS
    price = st.session_state.get('price', 100.0)
    volume = st.session_state.get('volume', 1000)
    variable_cost = st.session_state.get('variable_cost', 60.0)
    fixed_costs = st.session_state.get('fixed_costs', 20000.0)
    wacc = st.session_state.get('wacc', 0.15)

    # CORE CALCULATIONS
    revenue = price * volume
    total_vc = variable_cost * volume
    contribution_margin = revenue - total_vc
    ebit = contribution_margin - fixed_costs
    margin_pct = (contribution_margin / revenue) if revenue > 0 else 0
    break_even = fixed_costs / (price - variable_cost) if (price - variable_cost) > 0 else 0

    # BASELINE LOCK LOGIC (Saves the 'Original' state)
    if not st.session_state.get('baseline_locked', False):
        st.session_state.baseline = {
            'revenue': revenue,
            'ebit': ebit,
            'margin_pct': margin_pct,
            'wacc': wacc
        }
    
    # UPDATE GLOBAL STATE
    # This makes these variables available everywhere
    st.session_state.revenue = revenue
    st.session_state.ebit = ebit
    st.session_state.contribution_margin = contribution_margin
    st.session_state.break_even_units = break_even
    
    return True

def compute_core_metrics():
    # Helper to return the variables we just updated
    return {
        'revenue': st.session_state.get('revenue', 0),
        'ebit': st.session_state.get('ebit', 0),
        'contribution_margin': st.session_state.get('contribution_margin', 0),
        'wacc': st.session_state.get('wacc', 0.15)
    }
