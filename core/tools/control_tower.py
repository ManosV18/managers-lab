import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime

def show_control_tower():
    # --- 1. SETUP & DATA ---
    st.title("🕹️ Mission Control: Enterprise Tower")
    s = st.session_state
    m = s.get("metrics", {})
    
    # Live Sync Check
    revenue = m.get("revenue", 0.0)
    net_profit = m.get("net_profit", 0.0)
    roic = m.get("roic", 0.0)
    bep = m.get("bep_units", 0.0)
    ccc = m.get("ccc", 0.0)
    wacc = s.get('wacc_locked', 15.0)

    # --- 2. TOP LEVEL KPIs (High Level Summary) ---
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Annual Revenue", f"${revenue:,.0f}")
    c2.metric("Net Profit", f"${net_profit:,.0f}", delta=f"{(net_profit/revenue*100 if revenue > 0 else 0):.1f}% Margin")
    c3.metric("ROIC", f"{roic*100:.2f}%", delta=f"{(roic*100 - wacc):.2f}% Spread")
    c4.metric("WACC", f"{wacc:.2f}%")

    st.divider()

    # --- 3. ANALYTICAL QUADRANTS ---
    q1, q2 = st.columns(2)
    
    with q1: # Break-Even Graph (Από το Executive Dashboard)
        st.subheader("📉 Profitability Curve")
        p, v, vc, fc = s.get('price', 0), s.get('volume', 0), s.get('variable_cost', 0), s.get('fixed_cost', 0)
        v_range = list(range(0, int(v * 2), int(max(1, v/10))))
        df_be = pd.DataFrame({
            "Volume": v_range,
            "Revenue": [vol * p for vol in v_range],
            "Costs": [fc + (vol * vc) for vol in v_range]
        })
        fig_be = px.line(df_be, x="Volume", y=["Revenue", "Costs"], template="plotly_dark")
        st.plotly_chart(fig_be, use_container_width=True)

    with q2: # Liquidity Bridge (Από το αρχικό Control Tower)
        st.subheader("💧 Working Capital (CCC)")
        ar, inv, ap = s.get("ar_days", 30), s.get("inv_days", 60), s.get("ap_days", 45)
        fig_ccc = go.Figure(go.Bar(y=['Receivables', 'Inventory', 'Payables'], x=[ar, inv, -ap], orientation='h', marker_color=['#3b82f6', '#f59e0b', '#ef4444']))
        fig_ccc.update_layout(height=300, template="plotly_dark", margin=dict(l=20, r=20, t=10, b=10))
        st.plotly_chart(fig_ccc, use_container_width=True)

    # --- 4. STRATEGIC TOOLS (The Buttons) ---
    st.subheader("🛠️ Strategic Tool Suite")
    t1, t2, t3, t4 = st.columns(4)
    if t1.button("🛡️ Stress Test", use_container_width=True): s.selected_tool = "stress_test_tool"; s.flow_step = "tool"; st.rerun()
    if t2.button("📦 Inventory", use_container_width=True): s.selected_tool = "inventory_manager"; s.flow_step = "tool"; st.rerun()
    if t3.button("👥 CLV Simulator", use_container_width=True): s.selected_tool = "clv_calculator"; s.flow_step = "tool"; st.rerun()
    if t4.button("📉 WACC Opt.", use_container_width=True): s.selected_tool = "wacc_optimizer"; s.flow_step = "tool"; st.rerun()

    # --- 5. REPORTING & EXPORT (Από το Decision Report) ---
    st.divider()
    with st.expander("📄 Export Executive Summary"):
        report_df = pd.DataFrame({
            "Metric": ["ROIC", "WACC", "Net Profit", "Break-Even"],
            "Value": [f"{roic*100:.1f}%", f"{wacc:.1f}%", f"${net_profit:,.0f}", f"{bep:,.0f} units"]
        })
        st.table(report_df)
        st.download_button("Download Report (CSV)", report_df.to_csv(index=False), "executive_report.csv", "text/csv")

    if st.button("⬅️ Return to Home", use_container_width=True):
        s.flow_step = "home"
        st.rerun()
