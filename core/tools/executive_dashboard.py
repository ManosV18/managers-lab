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

    # ---------------------------------------------------------
    # 1. FORCE LIVE SYNC (Εδώ λύνεται το πρόβλημα)
    # ---------------------------------------------------------
    # Διαβάζουμε απευθείας από το session_state ό,τι έβαλε ο χρήστης στο Home
    m = calculate_metrics(
        price=_safe_get('price', 150.0),
        volume=_safe_get('volume', 15000.0),
        variable_cost=_safe_get('variable_cost', 90.0),
        fixed_cost=_safe_get('fixed_cost', 450000.0),
        ar_days=_safe_get('ar_days', 60),
        inv_days=_safe_get('inv_days', 45),
        ap_days=_safe_get('ap_days', 30),
        annual_debt_service=_safe_get('annual_debt_service', 70000.0),
        opening_cash=_safe_get('opening_cash', 150000.0),
        total_debt=_safe_get('total_debt', 500000.0),
        fixed_assets=_safe_get('fixed_assets', 800000.0)
    )
    
    # Ενημερώνουμε το καθολικό metrics για να συμφωνούν όλα τα tabs
    st.session_state.metrics = m 

    # ---------------------------------------------------------
    # 2. KPIs (Ευθυγραμμισμένα με τη σειρά του Snapshot)
    # ---------------------------------------------------------
    c1, c2, c3, c4 = st.columns(4)

    # Στήλη 1: ROIC
    c1.metric("ROIC", f"{m.get('roic', 0)*100:.1f}%")
    
    # Στήλη 2: Break-Even
    c2.metric("Break-Even", f"{m.get('bep_units', 0):,.0f} units")
    
    # Στήλη 3: Margin of Safety (Τώρα στη σωστή θέση)
    mos_val = m.get('margin_of_safety', 0) * 100
    c3.metric("Margin of Safety", f"{mos_val:.1f}%")
    
    # Στήλη 4: Net Cash Position (Τώρα στην τελευταία θέση)
    c4.metric("Net Cash Position", f"${m.get('net_cash_position', 0):,.0f}")

    st.divider()
    
    # ---------------------------------------------------------
    # 3. PERFORMANCE CHARTS
    # ---------------------------------------------------------
    col_a, col_b = st.columns(2)
    
    with col_a:
        st.subheader("📊 Core Performance")
        df_perf = pd.DataFrame({
            "Metric": ["Revenue", "Total Costs", "Net Cash"],
            "Value": [m.get("revenue", 0), m.get("total_costs", 0), m.get("net_cash_position", 0)]
        })
        fig_perf = px.bar(df_perf, x="Metric", y="Value", color="Metric", 
                          color_discrete_sequence=["#1E3A8A", "#ef4444", "#10b981"])
        st.plotly_chart(fig_perf, use_container_width=True)

    with col_b:
        st.subheader("📉 Break-Even Curve")
        p = _safe_get('price', 150.0)
        v = _safe_get('volume', 15000.0)
        vc = _safe_get('variable_cost', 90.0)
        fc = _safe_get('fixed_cost', 450000.0)
        
        # Δυναμικό range γύρω από το τρέχον volume
        v_range = list(range(0, int(v * 2), int(max(1, v/10))))
        df_be = pd.DataFrame({
            "Volume": v_range,
            "Revenue": [vol * p for vol in v_range],
            "Costs": [fc + (vol * vc) for vol in v_range]
        })
        fig_be = px.line(df_be, x="Volume", y=["Revenue", "Costs"], title="Safety Zone Analysis")
        st.plotly_chart(fig_be, use_container_width=True)

    # ---------------------------------------------------------
    # 4. BACK NAVIGATION
    # ---------------------------------------------------------
    st.divider()
    if st.button("⬅️ Back to Control Tower", use_container_width=True):
        st.session_state.flow_step = "home"
        st.session_state.selected_tool = None
        st.rerun()
