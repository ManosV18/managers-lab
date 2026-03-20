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

    # --- 2. TOP LEVEL METRICS ---
    revenue = m.get("revenue", 0.0)
    net_profit = m.get("net_profit", 0.0)
    invested_cap = m.get("invested_capital", 0.0)
    wacc_locked = s.get('wacc_locked', 15.0)
    
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Annual Revenue", f"${revenue:,.0f}")
    c2.metric("Net Profit", f"${net_profit:,.0f}")
    c3.metric("Invested Capital", f"${invested_cap:,.0f}")
    c4.metric("WACC Target", f"{wacc_locked:.2f}%")

    st.divider()

    # --- 3. QUADRANTS ---
    q1, q2 = st.columns(2)
    q3, q4 = st.columns(2)

    with q1: # QUADRANT 1: BREAK-EVEN CHART (ΕΠΑΝΑΦΟΡΑ)
        st.subheader("🎯 Profitability Hub")
        p, v, vc, fc = _safe_get('price'), _safe_get('volume'), _safe_get('variable_cost'), _safe_get('fixed_cost')
        
        # Δημιουργία εύρους για το γράφημα (από 0 έως 2x το τρέχον volume)
        v_range = list(range(0, int(v * 2) + 1, int(max(1, v/10))))
        df_be = pd.DataFrame({
            "Volume": v_range,
            "Revenue": [vol * p for vol in v_range],
            "Total Costs": [fc + (vol * vc) for vol in v_range]
        })
        
        fig_be = px.line(df_be, x="Volume", y=["Revenue", "Total Costs"], 
                         color_discrete_map={"Revenue": "#10b981", "Total Costs": "#ef4444"})
        fig_be.update_layout(height=300, margin=dict(l=10, r=10, t=30, b=10), template="plotly_dark", legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1))
        st.plotly_chart(fig_be, use_container_width=True)

    with q2: # QUADRANT 2: LIQUIDITY (CCC)
        st.subheader("💧 Working Capital Velocity")
        ccc = m.get("ccc", 0.0)
        st.write(f"**CCC:** {ccc:.0f} Days")
        ar, inv, ap = s.get("ar_days", 30), s.get("inv_days", 60), s.get("ap_days", 45)
        fig_ccc = go.Figure(go.Bar(y=['Receivables', 'Inventory', 'Payables'], x=[ar, inv, -ap], 
                                 orientation='h', marker_color=['#3b82f6', '#f59e0b', '#ef4444']))
        fig_ccc.update_layout(height=250, margin=dict(l=10, r=10, t=10, b=10), template="plotly_dark")
        st.plotly_chart(fig_ccc, use_container_width=True)

    with q3: # QUADRANT 3: RISK RADAR (ΑΠΛΟΠΟΙΗΜΕΝΟ)
        st.subheader("🛡️ Risk Radar")
        # Υπολογισμός ημερών επιβίωσης: (Διαθέσιμα Μετρητά / Ημερήσια Έξοδα)
        cash = m.get('net_cash_position', 0.0)
        daily_burn = (fc + (v * vc)) / 365 # [2026-02-18] 365 days
        survival_days = cash / daily_burn if daily_burn > 0 else float('inf')
        
        st.metric("Survival (Zero Income)", f"{survival_days:.0f} Days", 
                  help="How many days the business survives with current cash if revenue drops to zero.")
        
        # Οπτική ένδειξη κινδύνου
        if survival_days < 30:
            st.error("🚨 Critical Cash Position (< 30 days)")
        elif survival_days < 90:
            st.warning("⚠️ Tight Liquidity (30-90 days)")
        else:
            st.success("✅ Safe Runway (> 90 days)")

    with q4: # QUADRANT 4: VALUE CREATION
        st.subheader("🚀 Value Creation")
        roic = m.get("roic", 0.0) * 100
        spread = roic - wacc_locked
        st.metric("ROIC", f"{roic:.2f}%", delta=f"{spread:.2f}% vs WACC")
        
        if spread > 0:
            st.success("Value Creation Mode")
        else:
            st.error("Value Destruction Mode")

    st.divider()
    
    # NAVIGATION
    if st.button("⬅️ Return to Global Baseline (Home)", use_container_width=True):
        s.flow_step = "home"
        st.rerun()
