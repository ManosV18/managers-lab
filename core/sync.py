import streamlit as st

def calculate_metrics(price, volume, variable_cost, fixed_cost):
    """Basic BEP / Revenue / EBIT / FCF calculation"""
    unit_contribution = price - variable_cost
    revenue = price * volume
    total_vc = variable_cost * volume
    contribution_margin = unit_contribution * volume
    ebit = contribution_margin - fixed_cost
    fcf = ebit  # Simplified for demo
    bep_units = fixed_cost / unit_contribution if unit_contribution > 0 else 0

    return {
        "unit_contribution": unit_contribution,
        "revenue": revenue,
        "contribution_margin": contribution_margin,
        "ebit": ebit,
        "fcf": fcf,
        "bep_units": bep_units
    }

def sync_global_state():
    s = st.session_state
    if not s.get("baseline_locked", False):
        return {}
    return calculate_metrics(
        price=float(s.get("price", 0.0)),
        volume=float(s.get("volume", 0.0)),
        variable_cost=float(s.get("variable_cost", 0.0)),
        fixed_cost=float(s.get("fixed_cost", 0.0))
    )

def lock_baseline():
    s = st.session_state
    s.baseline_locked = True
    metrics = sync_global_state()
    if metrics:
        s.baseline = metrics
        st.success("✅ Baseline locked successfully.")
    else:
        s.baseline_locked = False
        st.error("❌ Failed to lock baseline. Check inputs.")
