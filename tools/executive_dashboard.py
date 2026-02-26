import streamlit as st
import plotly.graph_objects as go
from core.sync import sync_global_state
from core.engine import calculate_metrics

def show_executive_dashboard():
    st.header("🏁 Executive Liquidity Command Center")
    st.info("Compare your Current Operations with an Optimized Strategic Scenario.")

    # 1. FETCH DATA
    metrics = sync_global_state()
    s = st.session_state

    curr_ar = s.get('ar_days', 60.0)
    curr_inv = s.get('inventory_days', 45.0)
    curr_ap = s.get('ap_days', 30.0)

    wacc = s.get('wacc', 0.15)

    # 2. SCENARIO BUILDER
    st.subheader("🚀 Strategy Optimization Scenario")
    with st.expander("Adjust Optimization Targets", expanded=True):
        c1, c2, c3 = st.columns(3)
        opt_ar = c1.slider("Target AR Days", 0, 150, int(curr_ar * 0.8))
        opt_inv = c2.slider("Target Inv. Days", 0, 150, int(curr_inv * 0.8))
        opt_ap = c3.slider("Target AP Days", 0, 150, int(curr_ap * 1.2))

    # 3. CALCULATIONS

    curr_ccc = curr_ar + curr_inv - curr_ap
    opt_ccc = opt_ar + opt_inv - opt_ap

    # Current WC from engine
    curr_gap = metrics.get('wc_requirement', 0.0)

    # Optimized WC via temporary engine recalculation
    optimized_metrics = calculate_metrics(
        s.price,
        s.volume,
        s.variable_cost,
        s.fixed_cost,
        s.wacc,
        s.tax_rate,
        opt_ar,
        opt_inv,
        opt_ap,
        s.annual_debt_service,
        s.get('opening_cash', 10000.0)
    )

    opt_gap = optimized_metrics.get('wc_requirement', 0.0)

    cash_released = curr_gap - opt_gap
    annual_savings = cash_released * wacc

    # 4. COMPARISON DASHBOARD
    st.divider()
    st.subheader("📈 Scenario Comparison")

    res_col1, res_col2 = st.columns(2)

    with res_col1:
        st.write("**Current State**")
        st.metric("Cash Cycle", f"{curr_ccc:.1f} Days")
        st.metric("Capital Tied Up", f"€ {curr_gap:,.0f}")

    with res_col2:
        st.write("**Optimized State**")
        st.metric(
            "Cash Cycle",
            f"{opt_ccc:.1f} Days",
            delta=f"{opt_ccc - curr_ccc:.1f} Days",
            delta_color="inverse"
        )
        st.metric(
            "Capital Required",
            f"€ {opt_gap:,.0f}",
            delta=f"€ {-cash_released:,.0f}",
            delta_color="inverse"
        )

    # 5. FINANCIAL UPSIDE
    st.subheader("💰 Financial Upside of Optimization")
    m1, m2 = st.columns(2)
    m1.metric("Potential Cash Release", f"€ {cash_released:,.2f}")
    m2.metric("Annual WACC Savings", f"€ {annual_savings:,.2f}")

    # 6. VISUAL GAP ANALYSIS
    fig = go.Figure()
    fig.add_trace(go.Bar(
        name='Current',
        x=['Inv', 'Rec', 'Pay'],
        y=[curr_inv, curr_ar, -curr_ap],
        marker_color='#636EFA'
    ))
    fig.add_trace(go.Bar(
        name='Optimized',
        x=['Inv', 'Rec', 'Pay'],
        y=[opt_inv, opt_ar, -opt_ap],
        marker_color='#00CC96'
    ))

    fig.update_layout(
        barmode='group',
        template="plotly_dark",
        height=350,
        margin=dict(l=20, r=20, t=40, b=20)
    )

    st.plotly_chart(fig, use_container_width=True)

    # 7. VERDICT & SYNC
    st.subheader("💡 Cold Analytical Verdict")

    if cash_released > 0:
        st.success(
            f"Execution liberates € {cash_released:,.2f}. "
            f"WACC gain: € {annual_savings:,.2f}/yr."
        )

    if st.button("Finalize Strategy & Update Global Dials", use_container_width=True, type="primary"):
        st.session_state.ar_days = opt_ar
        st.session_state.inventory_days = opt_inv
        st.session_state.ap_days = opt_ap
        st.success("Global model updated.")
        st.rerun()
