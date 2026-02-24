import streamlit as st
import plotly.graph_objects as go
from core.engine import compute_core_metrics


def run_stage1():

    st.header("📉 Stage 1: Break-Even Analysis")
    st.info("Analyze operating and survival break-even structure.")

    # =====================================================
    # VALIDATION (Baseline must exist)
    # =====================================================
    if st.session_state.price <= 0 or st.session_state.volume <= 0:
        st.warning("⚠️ Baseline data missing. Please return to Stage 0.")
        if st.button("⬅️ Back to Stage 0"):
            st.session_state.flow_step = 0
            st.rerun()
        return

    # =====================================================
    # FIXED COST EDIT (GLOBAL SYNC)
    # =====================================================
    st.subheader("Annual Fixed Costs")

    st.session_state.fixed_cost = st.number_input(
        "Total Annual Fixed Costs (€)",
        min_value=0.0,
        value=float(st.session_state.fixed_cost),
        step=1000.0
    )

    # =====================================================
    # CORE METRICS (Single Source of Truth)
    # =====================================================
    metrics = compute_core_metrics()

    price = st.session_state.price
    variable_cost = st.session_state.variable_cost
    fixed_cost = st.session_state.fixed_cost
    current_volume = st.session_state.volume

    unit_contribution = metrics["unit_contribution"]
    operating_bep = metrics["operating_bep"]
    survival_bep = metrics["survival_bep"]

    # =====================================================
    # RESULTS
    # =====================================================
    st.divider()

    col1, col2, col3 = st.columns(3)

    col1.metric("Operating Break-Even", f"{operating_bep:,.0f} units")
    col2.metric("Survival Break-Even", f"{survival_bep:,.0f} units")

    margin_of_safety = (
        (current_volume - survival_bep) / current_volume * 100
        if current_volume > 0 else 0
    )

    col3.metric(
        "Margin of Safety",
        f"{margin_of_safety:.1f}%",
        delta=f"{current_volume - survival_bep:,.0f} units"
    )

    col4, col5, col6 = st.columns(3)
    col4.metric("Free Cash Flow", f"{metrics['fcf']:,.0f} €")
    col5.metric("Ending Cash", f"{metrics['ending_cash']:,.0f} €")
    col6.metric("Cash Survival Horizon (years)", f"{metrics['cash_survival_horizon']:.2f}")

    # =====================================================
    # VISUALIZATION
    # =====================================================
    st.divider()

    max_x = int(max(survival_bep, current_volume) * 1.4)
    if max_x <= 0:
        max_x = 100

    step = max(1, max_x // 40)
    x_vals = list(range(0, max_x, step))

    revenue_line = [x * price for x in x_vals]
    operating_cost_line = [fixed_cost + (x * variable_cost) for x in x_vals]

    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=x_vals,
        y=revenue_line,
        name="Total Revenue"
    ))

    fig.add_trace(go.Scatter(
        x=x_vals,
        y=operating_cost_line,
        name="Operating Cost Line"
    ))

    fig.add_vline(
        x=operating_bep,
        line_dash="dash",
        annotation_text="Operating BEP"
    )

    fig.add_vline(
        x=survival_bep,
        line_dash="dot",
        annotation_text="Survival BEP"
    )

    fig.update_layout(
        title="Break-Even Structure",
        xaxis_title="Units",
        yaxis_title="Euros"
    )

    st.plotly_chart(fig, use_container_width=True)

    # =====================================================
    # NAVIGATION
    # =====================================================
    nav1, nav2 = st.columns(2)

    with nav1:
        if st.button("⬅️ Back to Calibration"):
            st.session_state.flow_step = 0
            st.rerun()

    with nav2:
        if st.button("Proceed to Stage 2 ➡️", type="primary"):
            st.session_state.flow_step = 2
            st.rerun()
