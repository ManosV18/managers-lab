import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from core.engine import calculate_metrics

def _safe_get(key, default=0.0):
    """Safe session_state getter with float casting."""
    try:
        # Κοιτάμε πρώτα το input_ key, μετά το σκέτο key
        val = st.session_state.get(f"input_{key}", st.session_state.get(key, default))
        return float(val) if val is not None else float(default)
    except Exception:
        return float(default)

def show_executive_dashboard():
    st.title("🏁 Executive Dashboard")
    s = st.session_state

    # Τραβάμε τα Metrics (αν δεν υπάρχουν, τα υπολογίζουμε επιτόπου)
    m = s.get("metrics", {})
    
    # -------------------------------
    # KPIs
    # -------------------------------
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("ROIC", f"{m.get('roic', 0)*100:.1f}%")
    c2.metric("Break-Even", f"{m.get('bep_units', 0):,.0f} units")
    c3.metric("Net Cash", f"€{m.get('net_cash_position', 0):,.0f}")
    c4.metric("Liquidity Buffer", f"{m.get('liquidity_buffer', 0):,.1f}%")

    st.divider()

    # -------------------------------
    # BREAK-EVEN CURVE (Με τα σωστά Keys)
    # -------------------------------
    st.subheader("📉 Break-Even Analysis")

    price = _safe_get("price", 100.0)
    vc = _safe_get("vc", 60.0)
    fc = _safe_get("fc", 20000.0)
    current_v = int(_safe_get("volume", 1000))

    volumes = list(range(0, current_v * 2, 50))
    revenue_line = [v * price for v in volumes]
    costs_line = [fc + v * vc for v in volumes]

    df_be = pd.DataFrame({
        "Volume": volumes,
        "Revenue": revenue_line,
        "Total Cost": costs_line
    })

    fig2 = px.line(df_be, x="Volume", y=["Revenue", "Total Cost"], 
                   title="Break-Even Curve",
                   color_discrete_map={"Revenue": "#1E3A8A", "Total Cost": "#ef4444"})
    st.plotly_chart(fig2, use_container_width=True)

    

    # -------------------------------
    # STRATEGY OPTIMIZATION (Scenario)
    # -------------------------------
    st.divider()
    st.subheader("🚀 Strategy Optimization Scenario")
    
    curr_ar = _safe_get("ar", 45.0)
    curr_inv = _safe_get("inv", 60.0)
    curr_ap = _safe_get("ap", 30.0)
    wacc_pct = _safe_get("wacc", 15.0)

    with st.expander("Adjust Optimization Targets", expanded=True):
        c1, c2, c3 = st.columns(3)
        opt_ar = c1.slider("Target AR Days", 0, 150, value=int(curr_ar * 0.8))
        opt_inv = c2.slider("Target Inv. Days", 0, 150, value=int(curr_inv * 0.8))
        opt_ap = c3.slider("Target AP Days", 0, 150, value=int(curr_ap * 1.2))

    # Υπολογισμός Optimized Metrics
    optimized_results = calculate_metrics(
        price, current_v, vc, fc, 
        0.22, # Tax
        opt_ar, opt_inv, opt_ap,
        _safe_get('ads', 0.0),
        _safe_get('cash', 10000.0)
    )

    cash_released = float(m.get('wc_requirement', 0)) - float(optimized_results.get('wc_requirement', 0))
    
    # Comparison Display
    res_col1, res_col2 = st.columns(2)
    with res_col1:
        st.write("**Current State**")
        st.metric("Capital Tied Up", f"€ {float(m.get('wc_requirement', 0)):,.0f}")
    with res_col2:
        st.write("**Optimized State**")
        st.metric("Capital Required", f"€ {float(optimized_results.get('wc_requirement', 0)):,.0f}", 
                  delta=f"€ {-cash_released:,.0f}", delta_color="inverse")

    # -------------------------------
    # VERDICT & SYNC
    # -------------------------------
    if st.button("Finalize Strategy & Update Global Dials", use_container_width=True, type="primary"):
        st.session_state.input_ar = opt_ar
        st.session_state.input_inv = opt_inv
        st.session_state.input_ap = opt_ap
        st.success("Global model updated!")
        st.rerun()

    if st.button("⬅️ Back to Control Tower", use_container_width=True):
        st.session_state.flow_step = "home"
        st.session_state.selected_tool = None
        st.rerun()
