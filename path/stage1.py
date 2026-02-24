# =========================================
# Stage 1: Break-Even Analysis
# =========================================
import streamlit as st
from core.engine import compute_core_metrics

def run_stage1():

    # --- DEFAULTS SAFETY CHECK ---
    st.session_state.setdefault("price", 0.0)
    st.session_state.setdefault("volume", 0)
    st.session_state.setdefault("variable_cost", 0.0)
    st.session_state.setdefault("fixed_cost", 0.0)
    
    st.header("📉 Stage 1: Break-Even Analysis")
    st.info("Analyze operating and survival break-even structure.")

    if st.session_state.price <= 0 or st.session_state.volume <= 0:
        st.warning("⚠️ Baseline data missing. Please return to Stage 0.")
        if st.button("⬅️ Back to Stage 0"):
            st.session_state.flow_step = 0
            st.rerun()
        return

    st.subheader("Annual Fixed Costs")
    st.session_state.fixed_cost = st.number_input(
        "Total Annual Fixed Costs (€)", 
        min_value=0.0, 
        value=float(st.session_state.fixed_cost), 
        step=1000.0
    )

    # --- CORE METRICS ---
    metrics = compute_core_metrics()
    price = st.session_state.price
    variable_cost = st.session_state.variable_cost
    fixed_cost = st.session_state.fixed_cost
    current_volume = st.session_state.volume

    unit_contribution = metrics.get("unit_contribution", 0)
    operating_bep = metrics.get("operating_bep", 0)
    survival_bep = metrics.get("survival_bep", 0)

    st.divider()
    col1, col2, col3 = st.columns(3)
    col1.metric("Operating Break-Even", f"{operating_bep:,.0f} units")
    col2.metric("Survival Break-Even", f"{survival_bep:,.0f} units")

    margin_of_safety = ((current_volume - survival_bep) / current_volume * 100) if current_volume > 0 else 0
    col3.metric("Margin of Safety", f"{margin_of_safety:.1f}%", delta=f"{current_volume - survival_bep:,.0f} units")

    # ------------------------
    # FCF & Cash Horizon
    # ------------------------
    col4, col5, col6 = st.columns(3)
    col4.metric("Free Cash Flow", f"{metrics.get('fcf',0):,.0f} €")
    col5.metric("Ending Cash", f"{metrics.get('ending_cash',0):,.0f} €")
    col6.metric("Cash Survival Horizon (years)", f"{metrics.get('cash_survival_horizon',0):.2f}")

    # =============================
    # NAVIGATION
    # =============================
    st.divider()
    nav1, nav2 = st.columns(2)
    with nav1:
        if st.button("⬅️ Back to Calibration"):
            st.session_state.flow_step = 0
            st.rerun()
    with nav2:
        if st.button("Proceed to Stage 2 ➡️", type="primary"):
            st.session_state.flow_step = 2
            st.rerun()
