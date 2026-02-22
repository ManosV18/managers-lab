import streamlit as st

def initialize_system_state():
    """Initializes the 5 pillars of the system + UI State."""
    # UI State
    if 'mode' not in st.session_state: st.session_state.mode = "home"
    if 'flow_step' not in st.session_state: st.session_state.flow_step = 0
    if 'baseline_locked' not in st.session_state: st.session_state.baseline_locked = False
    if 'selected_tool' not in st.session_state: st.session_state.selected_tool = None

    # 1. Revenue Engine
    if 'price' not in st.session_state: st.session_state.price = 30.0
    if 'volume' not in st.session_state: st.session_state.volume = 10000

    # 2. Cost Structure
    if 'variable_cost' not in st.session_state: st.session_state.variable_cost = 15.0
    if 'fixed_cost' not in st.session_state: st.session_state.fixed_cost = 5000.0

    # 3. Time & Cash Pressure
    if 'ar_days' not in st.session_state: st.session_state.ar_days = 45
    if 'inventory_days' not in st.session_state: st.session_state.inventory_days = 60
    if 'payables_days' not in st.session_state: st.session_state.payables_days = 30
    if 'liquidity_drain' not in st.session_state: st.session_state.liquidity_drain = 0.0

    # 4. Capital & Financing
    if 'debt' not in st.session_state: st.session_state.debt = 20000.0
    if 'interest_rate' not in st.session_state: st.session_state.interest_rate = 0.05

    # 5. Durability
    if 'retention_rate' not in st.session_state: st.session_state.retention_rate = 0.85
