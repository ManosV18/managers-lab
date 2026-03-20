import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime
from core.engine import calculate_metrics

def _safe_get(key, default=0.0):
    """Safe session_state getter with float casting."""
    try:
        val = st.session_state.get(key, default)
        return float(val) if val is not None else float(default)
    except Exception:
        return float(default)

def show_control_tower():
    s = st.session_state
    
    # --- 1. LIVE ENGINE SYNC (Από το Executive Dashboard) ---
    # Διασφαλίζουμε ότι τα metrics είναι πάντα φρέσκα βάσει των inputs του Home
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
    st.session_state.metrics = m # Ενημέρωση καθολικού state

    # --- 2. HEADER & SCENARIO INFO (Από το Decision Report) ---
    st.title("🕹️ Mission Control: Enterprise Tower")
    scenario_name = s.get("scenario_name", "Baseline Scenario")
    current_date = datetime.now().strftime("%d/%m/%Y %H:%M")
    
    st.markdown(f"""
    <div style="background-color:#1e293b; padding:15px; border-radius:10px; border-left:5px solid #3b82f6; margin-bottom:20px;">
        <p style="margin:0; color:#94a3b8; font-size:12px;">SCENARIO STATUS</p>
        <h4 style="margin:0; color:white;">{scenario_name}</h4>
        <p style="margin:0; color:#64748b; font-size:12px;">Last Update: {current_date}</p>
    </div>
    """, unsafe_allow_html=True)

    # --- 3. TOP LEVEL METRICS (Single Source of Truth) ---
    revenue = m.get("revenue", 0.0)
    net_profit = m.get("net_profit", 0.0)
    roic = m.get("roic", 0.0)
    invested_cap = m.get("invested_capital", 0.0)
    bep = m.get("bep_units", 0.0)
    ccc = m.get("ccc", 0.0)
    locked_wacc = s.get('wacc_locked', 15.0)

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Annual Revenue", f"${revenue:,.0f}")
    c2.metric("Net Profit", f"${net_profit:,.0f}", 
              delta=f"{(net_profit/revenue*100 if revenue > 0 else 0):.1f}% Margin")
    c3.metric("Invested Capital", f"${invested_cap:,.0f}")
    c4.metric("WACC (Hurdle)", f"{locked_wacc:.2f}%")

    st.divider()

    # --- 4. STRATEGIC QUADRANTS (Combined Visuals) ---
    q1, q2 = st.columns(2)
    q3, q4 = st.columns(2)

    with q1: # QUADRANT 1: PROFITABILITY & BREAK-EVEN CURVE
        st.subheader("🎯 Profitability & BEP")
        # Εδώ βάλαμε το γράφημα από το Executive Dashboard
        p, v, vc, fc = _safe_get('price'), _safe_get('volume'), _safe_get('variable_cost'), _safe_get('fixed_cost')
        v_range = list(range(0, int(v * 2), int(max(1, v/10))))
        df_be = pd.DataFrame({
            "Volume": v_range,
            "Revenue": [vol * p for vol in v_range],
            "Costs": [fc + (vol * vc) for vol in v_range]
        })
        fig_be = px.line(df_be, x="Volume", y=["Revenue", "Costs"], template="plotly_dark", 
                         color_discrete_map={"Revenue": "#10b981", "Costs": "#ef4444"})
        fig_be.update_layout(height=280, margin=dict(l=10, r=10, t=30, b=10))
        st.plotly_chart(fig_be, use_container_width=True)

    with q2: # QUADRANT 2: LIQUIDITY (CCC Bar)
        st.subheader("💧 Working Capital Velocity")
        st.write(f"**CCC:** {ccc:.0f} Days")
        ar, inv, ap = s.get("ar_days", 30), s.get("inv_days", 60), s.get("ap_days", 45)
        fig_ccc = go.Figure(go.Bar(y=['Receivables', 'Inventory', 'Payables'], x=[ar, inv, -ap], 
                                 orientation='h', marker_color=['#3b82f6', '#f59e0b', '#ef4444']))
        fig_ccc.update_layout(height=280, template="plotly_dark", margin=dict(l=10, r=10, t=10, b=10))
        st.plotly_chart(fig_ccc, use_container_width=True)

    with q3: # QUADRANT 3: VALUE CREATION (ROIC vs WACC)
        st.subheader("🚀 Value Creation Spread")
        roic_pct = roic * 100
        spread = roic_pct - locked_wacc
        st.metric("ROIC", f"{roic_pct:.2f}%", delta=f"{spread:.2f}% vs WACC")
        if spread > 0: st.success(f"Value Creation Mode")
        else: st.error(f"Value Destruction Mode")
        
        # Προσθήκη Margin of Safety (από Executive Dashboard)
        mos = m.get('margin_of_safety', 0) * 100
        st.write(f"**Margin of Safety:** {mos:.1f}%")
        st.progress(min(max(mos/100, 0.0), 1.0))

    with q4: # QUADRANT 4: CASH & RUNWAY
        st.subheader("🛡️ Liquidity Buffer")
        net_cash = m.get('net_cash_position', 0.0)
        st.metric("Net Cash Position", f"${net_cash:,.0f}")
        # Προσθήκη Liquidty % (από Decision Report)
        liq_buffer = m.get('liquidity_buffer', 0.0)
        st.write(f"**Liquidity Buffer:** {liq_buffer:.1f}%")
        st.progress(min(liq_buffer/100, 1.0))

    # --- 5. STRATEGIC TOOL SUITE (Navigation Buttons) ---
    st.divider()
    st.subheader("🛠️ Strategic Tool Suite")
    c_b1, c_b2, c_b3, c_b4 = st.columns(4)
    if c_b1.button("🛡️ Stress Test", use_container_width=True): s.selected_tool = "stress_test_tool"; s.flow_step = "tool"; st.rerun()
    if c_b2.button("📦 Inventory", use_container_width=True): s.selected_tool = "inventory_manager"; s.flow_step = "tool"; st.rerun()
    if c_b3.button("👥 CLV Simulator", use_container_width=True): s.selected_tool = "clv_calculator"; s.flow_step = "tool"; st.rerun()
    if c_b4.button("📉 WACC Opt.", use_container_width=True): s.selected_tool = "wacc_optimizer"; s.flow_step = "tool"; st.rerun()

    c_b5, c_b6, c_b7, c_b8 = st.columns(4)
    if c_b5.button("📉 Loss Threshold", use_container_width=True): s.selected_tool = "loss_threshold"; s.flow_step = "tool"; st.rerun()
    if c_b6.button("📊 Unit Cost Audit", use_container_width=True): s.selected_tool = "unit_cost_app"; s.flow_step = "tool"; st.rerun()
    # Εδώ μπορείς να προσθέσεις κι άλλα αν θες

    # --- 6. REPORT EXPORT (Από το Decision Report) ---
    st.divider()
    with st.expander("📄 Export Decision Data"):
        export_df = pd.DataFrame({
            "Metric": ["ROIC", "WACC", "Net Cash", "Break-Even", "CCC"],
            "Value": [f"{roic*100:.1f}%", f"{locked_wacc:.1f}%", f"${net_cash:,.0f}", f"{bep:,.0f} units", f"{ccc:.0f} days"]
        })
        st.table(export_df)
        st.download_button("Download Executive CSV", export_df.to_csv(index=False), 
                         file_name=f"report_{scenario_name.replace(' ','_')}.csv", mime="text/csv")

    # Back to Home
    if st.button("⬅️ Return to Global Baseline (Home)", use_container_width=True):
        s.flow_step = "home"
        st.rerun()
