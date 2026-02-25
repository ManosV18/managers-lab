import streamlit as st

def calculate_metrics(price, volume, variable_cost, fixed_cost, wacc):
    """
    Pure Logic Layer. No session_state access.
    """
    revenue = price * volume
    total_vc = variable_cost * volume
    contribution_margin = revenue - total_vc
    ebit = contribution_margin - fixed_cost
    margin_pct = (contribution_margin / revenue) if revenue > 0 else 0
    break_even = fixed_cost / (price - variable_cost) if (price - variable_cost) > 0 else 0
    
    return {
        'revenue': revenue,
        'ebit': ebit,
        'contribution_margin': contribution_margin,
        'margin_pct': margin_pct,
        'break_even_units': break_even,
        'wacc': wacc
    }
