import streamlit as st
import plotly.graph_objects as go
from core.engine import calculate_metrics

def _safe_get(key, default=0.0):
    """Safe session_state getter with float casting."""
    try:
        val = st.session_state.get(key, default)
        return float(val) if val is not None else float(default)
    except Exception:
        return float(default)

def show_executive_dashboard():
    st.header("🏁 Executive Liquidity Command Center")
    st.info("Compare your Current Operations with an Optimized Strategic Scenario.")

    # 1. FETCH DATA (Linked to Home Session State)
    s = st.session_state
    m = s.get("metrics", {})

    # Sync with Global Keys
    curr_ar = _safe_get('ar_days', 45.0)
    curr_inv = _safe_get('inv_days', 60.0) # Corrected key to match home.py
    curr_ap = _safe_get('ap_days', 30.0)
    
    # Use locked WACC if available, otherwise 15%
    wacc_pct = _safe_get('wacc_locked', 15.0)
    wacc_decimal = wacc_pct / 100

    # 2. SCENARIO BUILDER
    st.subheader("🚀 Strategy Optimization Scenario")
    st.caption("💡 Smart Target: Suggested values based on 20% efficiency improvement.")

    with st.expander("Adjust Optimization Targets", expanded=True):
        c1, c2, c3 = st.columns(3)

        opt_ar = c1.slider(
            "Target AR Days", 0, 150, 
            value=int(curr_ar * 0.8), 
            key=f"opt_ar_eval"
        )

        opt_inv = c2.slider(
            "Target Inv. Days", 0, 150, 
            value=int(curr_inv * 0.8), 
            key=f"opt_inv_eval"
        )

        opt_ap = c3.slider(
            "Target AP Days", 0, 150, 
            value=int(curr_ap * 1.2), 
            key=f"opt_ap_eval"
        )

    # 3. CALCULATIONS
    curr_ccc = curr_ar + curr_inv - curr_ap
    opt_ccc = opt_ar + opt_inv - opt_ap

    curr_gap = float(m.get('wc_requirement', 0.0))

    # 4. CORRECTED ENGINE CALL (Matching engine.py arguments)
    # Arguments: price, volume, v_cost, f_cost, tax, ar, inv, ap, debt_service, cash
    optimized_results = calculate_metrics(
        _safe_get('price', 100.0),
        _safe_get('volume', 1000.0),
        _safe_get('variable_cost', 60.0),
        _safe_get('fixed_cost', 20000.0),
        0.22, # Tax rate
        opt_ar,
        opt_inv,
        opt_ap,
        _safe_get('annual_debt_service', 0.0),
        _safe_get('opening_cash', 10000.0)
    )

    opt_gap = float(optimized_results.get('wc_requirement', 0.0))
    cash_released = curr_gap - opt_gap
    annual_savings = cash_released * wacc_decimal

    # 5. COMPARISON DASHBOARD
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

    # 6. FINANCIAL UPSIDE
    st.subheader("💰 Financial Upside of Optimization")
    m1, m2 = st.columns(2)
    m1.metric("Potential Cash Release", f"€ {cash_released:,.2f}")
    m2.metric("Annual WACC Savings", f"€ {annual_savings:,.2f}", help=f"Cost of capital saved at {wacc_pct}%.")

    # 7. VISUAL GAP ANALYSIS
    
    
    fig = go.Figure()
    fig.add_trace(go.Bar(
        name='Current',
        x=['Inventory', 'Receivables', 'Payables'],
        y=[curr_inv, curr_ar, -curr_ap],
        marker_color='#64748b'
    ))
    fig.add_trace(go.Bar(
        name='Optimized',
        x=['Inventory', 'Receivables', 'Payables'],
        y=[opt_inv, opt_ar, -opt_ap],
        marker_color='#1E3A8A'
    ))
    fig.update_layout(
        barmode='group',
        template="plotly_dark",
        height=350,
        margin=dict(l=20, r=20, t=40, b=20),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    st.plotly_chart(fig, use_container_width=True)

    # 8. VERDICT & SYNC
    st.subheader("💡 Cold Analytical Verdict")
    if cash_released > 0:
        st.success(
            f"Optimizing operations liberates **€ {cash_released:,.2f}** in stagnant liquidity. "
            f"At a {wacc_pct:.1f}% cost of capital, this adds **€ {annual_savings:,.2f}/year** to your bottom line."
        )
    else:
        st.warning("Current targets do not yield capital efficiency gains. Tighten DSO or Inventory days.")

    if st.button("Finalize Strategy & Update Global Dials", use_container_width=True, type="primary"):
        st.session_state.ar_days = opt_ar
        st.session_state.inv_days = opt_inv
        st.session_state.ap_days = opt_ap
        st.success("Global model updated with optimized targets.")
        st.rerun()

    # Navigation
    st.divider()
    if st.button("⬅️ Back to Control Tower", use_container_width=True):
        st.session_state.flow_step = "home"
        st.session_state.selected_tool = None
        st.rerun()
