import streamlit as st
from core.engine import compute_core_metrics

def run_stage0():
    st.header("🔵 Stage 0: Structural Setup")
    st.caption("Define the business DNA. Once locked, these values form the baseline for all simulations.")

    # 1. Inputs
    with st.expander("💰 Unit Economics & Volume", expanded=True):
        col1, col2 = st.columns(2)
        price = col1.number_input("Unit Selling Price (€)", min_value=0.0, value=100.0)
        v_cost = col2.number_input("Unit Variable Cost (€)", min_value=0.0, value=60.0)
        volume = st.number_input("Current Annual Volume (Units)", min_value=1, value=5000)

    with st.expander("🏢 Fixed Costs & Debt", expanded=True):
        f_cost = st.number_input("Total Annual Fixed Costs (€)", min_value=0.0, value=150000.0)
        debt_payment = st.number_input("Annual Debt Service (Principal + Interest) (€)", min_value=0.0, value=24000.0)

    with st.expander("🌊 Working Capital & Cash", expanded=True):
        col3, col4 = st.columns(2)
        ar_days = col3.number_input("Receivable Days (DSO)", value=45)
        inv_days = col4.number_input("Inventory Days (DIO)", value=60)
        pay_days = col3.number_input("Payable Days (DPO)", value=30)
        opening_cash = col4.number_input("Opening Cash Balance (€)", value=50000.0)

    # 2. The Lock Mechanism
    if st.button("🔒 LOCK BASELINE & PROCEED", type="primary", use_container_width=True):
        st.session_state.price = price
        st.session_state.variable_cost = v_cost
        st.session_state.volume = volume
        st.session_state.fixed_cost = f_cost
        st.session_state.annual_loan_payment = debt_payment
        st.session_state.ar_days = ar_days
        st.session_state.inventory_days = inv_days
        st.session_state.payables_days = pay_days
        st.session_state.opening_cash = opening_cash
        
        # Initial Compute
        metrics = compute_core_metrics()
        st.session_state.baseline_locked = True
        st.session_state.flow_step = 1
        st.rerun()
