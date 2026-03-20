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
    
    if not s.get("baseline_locked"):
        st.warning("⚠️ Baseline not locked. Showing real-time simulation.")

    # --- 2. FETCH DATA ---
    revenue = m.get("revenue", 0.0)
    net_profit = m.get("net_profit", 0.0)
    roic = m.get("roic", 0.0)
    invested_cap = m.get("invested_capital", 0.0)
    bep = m.get("bep_units", 0.0)
    ccc = m.get("ccc", 0.0)
    
    # TOP LEVEL METRICS
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Annual Revenue", f"${revenue:,.0f}")
    c2.metric("Net Profit", f"${net_profit:,.0f}", 
              delta=f"{(net_profit/revenue*100 if revenue > 0 else 0):.1f}% Margin")
    c3.metric("Invested Capital", f"${invested_cap:,.0f}")
    
    wacc_input = s.get('wacc_locked', 15.0) 
    c4.metric("WACC Target", f"{wacc_input:.2f}%")

    st.divider()

    # --- 3. QUADRANTS ---
    q1, q2 = st.columns(2)
    q3, q4 = st.columns(2)

    with q1: # QUADRANT 1: PROFITABILITY (Break-Even Curve)
        st.subheader("🎯 Profitability Hub")
        p, v, vc, fc = _safe_get('price'), _safe_get('volume'), _safe_get('variable_cost'), _safe_get('fixed_cost')
        v_range = list(range(0, int(v * 2), int(max(1, v/10))))
        df_be = pd.DataFrame({
            "Volume": v_range,
            "Revenue": [vol * p for vol in v_range],
            "Costs": [fc + (vol * vc) for vol in v_range]
        })
        fig_be = px.line(df_be, x="Volume", y=["Revenue", "Costs"])
        fig_be.update_layout(height=250, margin=dict(l=10, r=10, t=30, b=10), template="plotly_dark")
        st.plotly_chart(fig_be, use_container_width=True)

    with q2: # QUADRANT 2: LIQUIDITY ENGINE
        st.subheader("💧 Liquidity Engine")
        st.write(f"**CCC:** {ccc:.0f} Days")
        ar, inv, ap = s.get("ar_days", 30), s.get("inv_days", 60), s.get("ap_days", 45)
        fig_ccc = go.Figure(go.Bar(y=['Receivables', 'Inventory', 'Payables'], x=[ar, inv, -ap], 
                                 orientation='h', marker_color=['#3b82f6', '#10b981', '#ef4444']))
        fig_ccc.update_layout(height=200, margin=dict(l=10, r=10, t=10, b=10), template="plotly_dark")
        st.plotly_chart(fig_ccc, use_container_width=True)

    with q3: # QUADRANT 3: RISK RADAR
        st.subheader("🛡️ Risk Radar")
        prob_fail = m.get("insolvency_prob", 0.0)
        runway = m.get("runway_months", 0.0)
        col_r1, col_r2 = st.columns(2)
        col_r1.metric("Insolvency Prob.", f"{prob_fail:.1f}%")
        if runway == float('inf'): col_r2.metric("Runway", "∞ (Cash Positive)")
        else: col_r2.metric("Runway", f"{runway:.1f} Months")
        st.progress(min(prob_fail / 100, 1.0), text="Insolvency Risk Level")

    with q4: # QUADRANT 4: VALUE CREATION
        st.subheader("🚀 Value Creation")
        st.write(f"**Implied ROIC:** {roic:.1%}")
        if (roic * 100) > wacc_input: 
            st.success(f"✅ ROIC > WACC (Value Creation)")
        else: 
            st.error(f"🚨 ROIC < WACC (Value Destruction)")
        
        # Προσθήκη Margin of Safety
        mos = m.get('margin_of_safety', 0.0) * 100
        st.write(f"**Margin of Safety:** {mos:.1f}%")

    st.divider()
    
    # --- 4. BACK NAVIGATION ONLY ---
    if st.button("⬅️ Return to Global Baseline (Home)", use_container_width=True):
        s.flow_step = "home"
        st.rerun()
