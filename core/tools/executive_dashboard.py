import streamlit as st
import pandas as pd
import plotly.express as px
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
    st.title("🏁 Executive Dashboard")

    m = st.session_state.get("metrics", {})

    # -------------------------------
    # 1. KPIs
    # -------------------------------
    c1, c2, c3, c4 = st.columns(4)

    c1.metric("ROIC", f"{m.get('roic', 0)*100:.1f}%")
    c2.metric("Break-Even", f"{m.get('bep_units', 0):,.0f} units")
    c3.metric("Net Cash", f"€{m.get('net_cash_position', 0):,.0f}")
    
    # Διόρθωση Margin of Safety: Πολλαπλασιασμός * 100 και σωστό κλειδί
    mos_val = m.get('margin_of_safety', 0) * 100
    c4.metric("Margin of Safety", f"{mos_val:.1f}%")

    st.divider()

    # -------------------------------
    # 2. VISUALS (Core & Break-Even)
    # -------------------------------
    col_chart1, col_chart2 = st.columns(2)

    with col_chart1:
        st.subheader("📊 Core Performance")
        df = pd.DataFrame({
            "Metric": ["Revenue", "Costs", "Cash"],
            "Value": [m.get("revenue", 0), m.get("total_costs", 0), m.get("net_cash_position", 0)]
        })
        fig = px.bar(df, x="Metric", y="Value", title="Financial Overview", template="plotly_dark")
        st.plotly_chart(fig, use_container_width=True)

    with col_chart2:
        st.subheader("📉 Break-Even Curve")
        price = _safe_get("price", 150.0)
        vc = _safe_get("variable_cost", 90.0)
        fc = _safe_get("fixed_cost", 450000.0)
        vol_limit = int(_safe_get("volume", 15000))
        
        volumes = list(range(0, vol_limit * 2, int(max(1, vol_limit/20))))
        rev_curve = [v * price for v in volumes]
        cost_curve = [fc + v * vc for v in volumes]
        
        df_be = pd.DataFrame({"Volume": volumes, "Revenue": rev_curve, "Total Cost": cost_curve})
        fig2 = px.line(df_be, x="Volume", y=["Revenue", "Total Cost"], title="Operational Safety Zone")
        st.plotly_chart(fig2, use_container_width=True)

    # -------------------------------
    # 3. STRATEGY OPTIMIZATION (Scenario Builder)
    # -------------------------------
    st.divider()
    st.subheader("🚀 Strategy Optimization Scenario")
    
    curr_ar = _safe_get("ar_days", 60)
    curr_inv = _safe_get("inv_days", 45)
    curr_ap = _safe_get("ap_days", 30)
    wacc_pct = _safe_get("wacc", 10.0)

    with st.expander("Adjust Optimization Targets", expanded=True):
        c_opt1, c_opt2, c_opt3 = st.columns(3)
        opt_ar = c_opt1.slider("Target AR Days", 0, 150, value=int(curr_ar * 0.8))
        opt_inv = c_opt2.slider("Target Inv. Days", 0, 150, value=int(curr_inv * 0.8))
        opt_ap = c_opt3.slider("Target AP Days", 0, 150, value=int(curr_ap * 1.2))

    # --- CRITICAL: ENGINE CALL FIRST ---
    optimized_results = calculate_metrics(
        price=_safe_get('price', 150.0),
        volume=_safe_get('volume', 15000.0),
        variable_cost=_safe_get('variable_cost', 90.0),
        fixed_cost=_safe_get('fixed_cost', 450000.0),
        ar_days=opt_ar,
        inv_days=opt_inv,
        ap_days=opt_ap,
        annual_debt_service=_safe_get('annual_debt_service', 70000.0),
        opening_cash=_safe_get('opening_cash', 150000.0),
        total_debt=_safe_get('total_debt', 500000.0),
        fixed_assets=_safe_get('fixed_assets', 800000.0)
    )

    # --- NOW CALCULATE GAPS ---
    curr_ccc = curr_ar + curr_inv - curr_ap
    opt_ccc = opt_ar + opt_inv - opt_ap
    
    curr_gap = float(m.get('net_working_capital', 0.0))
    opt_gap = float(optimized_results.get('net_working_capital', 0.0))
    
    cash_released = curr_gap - opt_gap
    annual_savings = cash_released * (wacc_pct / 100)

    # -------------------------------
    # 4. COMPARISON RESULTS
    # -------------------------------
    res_col1, res_col2 = st.columns(2)
    with res_col1:
        st.write("**Current State**")
        st.metric("Cash Cycle", f"{curr_ccc:.1f} Days")
        st.metric("Capital Tied Up", f"€ {curr_gap:,.0f}")

    with res_col2:
        st.write("**Optimized State**")
        st.metric("Cash Cycle", f"{opt_ccc:.1f} Days", delta=f"{opt_ccc - curr_ccc:.1f} Days", delta_color="inverse")
        st.metric("Capital Required", f"€ {opt_gap:,.0f}", delta=f"€ {-cash_released:,.0f}", delta_color="inverse")

    st.subheader("💰 Financial Upside")
    m1, m2 = st.columns(2)
    m1.metric("Potential Cash Release", f"€ {cash_released:,.2f}")
    m2.metric("Annual WACC Savings", f"€ {annual_savings:,.2f}")

    # Visual Bar Comparison
    fig_opt = go.Figure()
    fig_opt.add_trace(go.Bar(name='Current', x=['Inventory', 'Receivables', 'Payables'], y=[curr_inv, curr_ar, -curr_ap], marker_color='#64748b'))
    fig_opt.add_trace(go.Bar(name='Optimized', x=['Inventory', 'Receivables', 'Payables'], y=[opt_inv, opt_ar, -opt_ap], marker_color='#1E3A8A'))
    fig_opt.update_layout(barmode='group', template="plotly_dark", height=300)
    st.plotly_chart(fig_opt, use_container_width=True)

    if st.button("Finalize Strategy & Update Global Dials", use_container_width=True, type="primary"):
        st.session_state.ar_days = opt_ar
        st.session_state.inv_days = opt_inv
        st.session_state.ap_days = opt_ap
        st.success("Global model updated with optimized targets.")
        st.rerun()

    if st.button("⬅️ Back to Control Tower", use_container_width=True):
        st.session_state.flow_step = "home"
        st.session_state.selected_tool = None
        st.rerun()
