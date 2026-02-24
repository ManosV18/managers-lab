# =========================================
# Managers' Lab: Stages 0 → 3 Safe Defaults
# =========================================
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from core.engine import compute_core_metrics

# =============================
# Stage 0: System Calibration
# =============================
def run_stage0():
    st.header("⚙️ Stage 0: System Calibration")
    st.caption("Establish the core economic parameters of the enterprise.")

    # --- DEFAULTS SAFETY CHECK ---
    defaults = {
        "price": 50.0,            # €/unit
        "volume": 15000,           # units/year
        "variable_cost": 25.0,     # €/unit (50% margin)
        "fixed_cost": 200000.0,    # €/year
        "ar_days": 45,
        "inventory_days": 60,
        "payables_days": 30,
        "baseline_locked": False
    }
    for key, val in defaults.items():
        st.session_state.setdefault(key, val)

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Revenue Structure")
        st.session_state.price = st.number_input("Price per Unit (€)", value=float(st.session_state.price))
        st.session_state.volume = st.number_input("Annual Volume (Units)", value=int(st.session_state.volume))
        revenue = st.session_state.price * st.session_state.volume
        st.metric("Annual Revenue", f"{revenue:,.0f} €")

    with col2:
        st.subheader("Cost Structure")
        st.session_state.variable_cost = st.number_input("Variable Cost per Unit (€)", value=float(st.session_state.variable_cost))
        st.session_state.fixed_cost = st.number_input("Annual Fixed Costs (€)", value=float(st.session_state.fixed_cost))

        p = st.session_state.price
        vc = st.session_state.variable_cost
        margin = (p - vc) / p if p > 0 else 0
        if p <= 0:
            st.error("❌ Price must be greater than zero.")
        elif p <= vc:
            st.error(f"❌ Critical: Negative/Zero Margin ({margin:.1%})")
        elif margin < 0.20:
            st.warning(f"⚠️ Low structural buffer ({margin:.1%})")
        else:
            st.success(f"✅ Healthy Margin: {margin:.1%}")

    st.divider()
    metrics = compute_core_metrics()
    col_b1, col_b2 = st.columns(2)
    col_b1.metric("Operating Break-Even (Units)", f"{metrics['operating_bep']:,.0f}")
    col_b2.metric("Unit Contribution", f"{metrics['unit_contribution']:,.2f} €")

    # Working Capital
    st.divider()
    st.subheader("⏳ Cash Timing & Durability")
    with st.expander("Configure Working Capital Cycle"):
        c1, c2, c3 = st.columns(3)
        st.session_state.ar_days = c1.number_input("Receivables Days", value=int(st.session_state.ar_days))
        st.session_state.inventory_days = c2.number_input("Inventory Days", value=int(st.session_state.inventory_days))
        st.session_state.payables_days = c3.number_input("Payables Days", value=int(st.session_state.payables_days))

    ar = st.session_state.ar_days
    inv = st.session_state.inventory_days
    pay = st.session_state.payables_days
    ccc = ar + inv - pay
    st.session_state.ccc = ccc
    working_capital_required = st.session_state.price * st.session_state.volume * (ccc / 365)
    st.session_state.working_capital_req = working_capital_required
    st.session_state.liquidity_drain_annual = working_capital_required

    col_c1, col_c2 = st.columns(2)
    col_c1.metric("Cash Conversion Cycle (Days)", f"{ccc}")
    col_c2.metric("Working Capital Required (€)", f"{working_capital_required:,.0f}")

    # Financial Structure
    st.divider()
    st.subheader("🏦 Financial Structure")
    f1, f2, f3 = st.columns(3)
    tax_input = f1.number_input("Corporate Tax Rate (%)", value=22.0)
    interest_input = f2.number_input("Cost of Debt (%)", value=5.0)
    wacc_input = f3.number_input("WACC (%)", value=8.0)
    st.session_state.tax_rate = tax_input / 100
    st.session_state.interest_rate = interest_input / 100
    st.session_state.wacc = wacc_input / 100

    st.divider()
    if st.button("Lock Baseline & Continue ➡️"):
        if st.session_state.price > st.session_state.variable_cost:
            st.session_state.baseline_locked = True
            st.session_state.flow_step = 1
            st.rerun()
        else:
            st.error("Cannot lock: Non-viable economic structure.")
