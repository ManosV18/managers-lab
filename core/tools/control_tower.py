import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from core.engine import calculate_metrics

def _safe_get(key, default=0.0):
    """Safe session_state getter with float casting."""
    try:
        val = st.session_state.get(key, default)
        return float(val) if val is not None else float(default)
    except Exception:
        return float(default)

def show_control_tower():
    st.title("🕹️ Mission Control: Enterprise Tower")
    st.caption("Integrated Strategic & Financial Oversight")
    
    s = st.session_state
    
    # --- 1. LIVE SYNC ---
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
    s.metrics = m

    # --- 1.1 BASELINE CALCULATION ---
    if 'baseline_nwc' not in s:
        b = calculate_metrics(
            price=150.0, volume=15000.0, variable_cost=90.0, fixed_cost=450000.0,
            ar_days=60, inv_days=45, ap_days=30,
            annual_debt_service=70000.0, opening_cash=150000.0
        )
        s.baseline_nwc = (b.get('ar_value', 0.0) + b.get('inv_value', 0.0)) - b.get('ap_value', 0.0)
    
    # --- 2. TOP LEVEL METRICS ---
    revenue = m.get("revenue", 0.0)
    net_profit = m.get("net_profit", 0.0)
    depreciation = _safe_get('depreciation', 0.0)
    debt_service = _safe_get('annual_debt_service', 0.0)
    
    current_nwc = (m.get('ar_value', 0.0) + m.get('inv_value', 0.0)) - m.get('ap_value', 0.0)
    wc_cash_impact = current_nwc - s.baseline_nwc 
    fcf = net_profit + depreciation - debt_service - wc_cash_impact
    
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Annual Revenue", f"${revenue:,.0f}")
    c2.metric("Net Profit (P&L)", f"${net_profit:,.0f}")
    fcf_color = "normal" if fcf > 0 else "inverse"
    c3.metric("Free Cash Flow", f"${fcf:,.0f}", delta=f"{fcf-net_profit:,.0f} vs Profit", delta_color=fcf_color)
    wacc_locked = s.get('wacc_locked', 15.0)
    c4.metric("WACC Target", f"{wacc_locked:.2f}%")
    
    st.divider()

    # --- 3. QUADRANTS ---
    q1, q2 = st.columns(2)
    q3, q4 = st.columns(2)

    with q1:
        st.subheader("🎯 Profitability Hub")
        v_range = list(range(0, int(_safe_get('volume', 15000.0)*2) + 1000, 2000))
        df_be = pd.DataFrame({
            "Units": v_range,
            "Revenue": [vol * _safe_get('price', 150.0) for vol in v_range],
            "Total Costs": [_safe_get('fixed_cost', 450000.0) + (vol * _safe_get('variable_cost', 90.0)) for vol in v_range]
        })
        fig_be = go.Figure()
        fig_be.add_trace(go.Scatter(x=df_be["Units"], y=df_be["Revenue"], name="Revenue", line=dict(color='#10b981', width=3)))
        fig_be.add_trace(go.Scatter(x=df_be["Units"], y=df_be["Total Costs"], name="Total Costs", line=dict(color='#ef4444', width=3)))
        fig_be.update_layout(height=300, template="plotly_dark", margin=dict(l=10, r=10, t=30, b=10))
        st.plotly_chart(fig_be, use_container_width=True)

    with q2:
        st.subheader("💧 Working Capital Velocity")
        fig_ccc = go.Figure(go.Bar(
            y=['Receivables', 'Inventory', 'Payables'], 
            x=[m.get('ar_days',0), m.get('inv_days',0), -m.get('ap_days',0)], 
            orientation='h', marker_color=['#3b82f6', '#f59e0b', '#ef4444']
        ))
        fig_ccc.update_layout(height=250, template="plotly_dark")
        st.plotly_chart(fig_ccc, use_container_width=True)

    with q3:
        st.subheader("🛡️ Risk Radar")
        daily_burn = (m['fixed_cost'] + (m['volume'] * m['variable_cost'])) / 365 
        survival_days = int(m['net_cash_position'] / daily_burn) if daily_burn > 0 else 0
        st.metric("Survival (Zero Income)", f"{survival_days} Days")
        if survival_days < 30: st.error("🚨 Critical Runway")
        else: st.success("✅ Safe Runway")

    with q4:
        st.subheader("🚀 Value Creation")
        roic = m.get("roic", 0.0) * 100
        st.metric("ROIC", f"{roic:.2f}%", delta=f"{roic - wacc_locked:.2f}% vs WACC")

    st.divider()

    # --- 4. STRATEGIC GAP ANALYSIS (FIXED INDENTATION) ---
    st.subheader(f"🛠️ Strategic Gap Analysis: How to fix the ${abs(wc_cash_impact):,.0f} hole")
    
    daily_cogs = (m['variable_cost'] * m['volume']) / 365
    # Πόσες ημέρες χρειαζόμαστε για να καλύψουμε το impact
    required_days = wc_cash_impact / daily_cogs if daily_cogs > 0 else 0

    col1, col2 = st.columns(2)

    with col1:
        st.write("#### Option 1: Pressure Suppliers")
        st.warning(f"To offset this, you must increase Payables by **{required_days:.1f} days**.")
        st.caption(f"Target AP Days: {m['ap_days'] + required_days:.0f} Days")

    with col2:
        st.write("#### Option 2: Lean Operations")
        if required_days > m['inv_days']:
            st.error(f"IMPOSSIBLE: You need to cut **{required_days:.1f} days** of stock, but you only have {m['inv_days']}.")
        else:
            st.success(f"Reduce Inventory by **{required_days:.1f} days** to break even on cash.")

    st.divider()
    if st.button("⬅️ Return to Global Baseline (Home)", use_container_width=True):
        s.flow_step = "home"
        st.rerun()
