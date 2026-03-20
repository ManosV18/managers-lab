import streamlit as st
import pandas as pd
import plotly.graph_objects as go

def show_control_tower():
    st.title("🕹️ Mission Control: Enterprise Tower")
    st.caption("Integrated Strategic & Financial Oversight | McKinsey-Level Analytics")
    
    s = st.session_state
    m = s.get("metrics", {})
    
    # --- FETCH FROM ENGINE (Single Source of Truth) ---
    revenue = m.get("revenue", 0.0)
    net_profit = m.get("net_profit", 0.0)
    roic = m.get("roic", 0.0)
    invested_cap = m.get("invested_capital", 0.0)
    bep = m.get("bep_units", 0.0)
    ccc = m.get("ccc", 0.0)
    
    # 1. TOP LEVEL METRICS
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Annual Revenue", f"${revenue:,.0f}")
    c2.metric("Net Profit", f"${net_profit:,.0f}", 
              delta=f"{(net_profit/revenue*100 if revenue > 0 else 0):.1f}% Margin")
    c3.metric("Invested Capital", f"${invested_cap:,.0f}")
    
    # WACC Connection (Linked to WACC Optimizer)
    locked_wacc = s.get('wacc_locked', 15.0) 
    c4.metric("WACC (Hurdle Rate)", f"{locked_wacc:.2f}%")

    st.divider()

    # 2. STRATEGIC QUADRANTS
    q1, q2 = st.columns(2)
    q3, q4 = st.columns(2)

    with q1: # QUADRANT 1: BREAK-EVEN RADAR
        st.subheader("🎯 Profitability Hub")
        volume = float(s.get("volume", 0))
        axis_max = max(volume, bep, 1) * 1.2
        
        fig_be = go.Figure(go.Indicator(
            mode = "gauge+number", value = volume,
            title = {'text': "Volume vs BEP"},
            gauge = {'axis': {'range': [0, axis_max]},
                     'threshold': {'line': {'color': "red", 'width': 4}, 'value': bep},
                     'bar': {'color': "#10b981" if volume >= bep else "#ef4444"}}
        ))
        fig_be.update_layout(height=250, margin=dict(l=20, r=20, t=40, b=20), template="plotly_dark")
        st.plotly_chart(fig_be, use_container_width=True)

    with q2: # QUADRANT 2: LIQUIDITY (CCC)
        st.subheader("💧 Working Capital Velocity")
        st.write(f"**CCC:** {ccc:.0f} Days")
        
        ar = s.get("ar_days", 30)
        inv = s.get("inv_days", 60)
        ap = s.get("ap_days", 45)
        
        fig_ccc = go.Figure(go.Bar(
            y=['Receivables', 'Inventory', 'Payables'], 
            x=[ar, inv, -ap], 
            orientation='h', 
            marker_color=['#3b82f6', '#f59e0b', '#ef4444']
        ))
        fig_ccc.update_layout(height=200, margin=dict(l=20, r=20, t=10, b=10), template="plotly_dark")
        st.plotly_chart(fig_ccc, use_container_width=True)

    with q3: # QUADRANT 3: CAPITAL EFFICIENCY (The ROIC-WACC Spread)
        st.subheader("🚀 Value Creation")
        roic_pct = roic * 100
        spread = roic_pct - locked_wacc
        
        st.metric("ROIC", f"{roic_pct:.2f}%", delta=f"{spread:.2f}% Spread vs WACC")
        
        if spread > 0:
            st.success(f"Creating Value (Spread: {spread:.2f}%)")
        else:
            st.error(f"Destroying Value (Spread: {spread:.2f}%)")

    with q4: # QUADRANT 4: UNIT ECONOMICS (CLV/CAC)
        st.subheader("👥 Customer Asset Value")
        # Εδώ θα μπορούσαμε να τραβήξουμε το κλειδωμένο CLV αν το είχαμε σώσει
        st.info("💡 Strategic Advice: Use the CLV Simulator to optimize your LTV/CAC ratio.")
        st.write("Current Unit Margin Linked:")
        st.markdown(f"**${(float(s.get('price',0)) - float(s.get('variable_cost',0))):,.2f}**")

    # 3. NAVIGATION (SYNCHRONIZED WITH OUR TOOLS)
    st.divider()
    st.subheader("🛠️ Strategic Tool Suite")
    
    

    c_b1, c_b2, c_b3, c_b4 = st.columns(4)
    
    # Προσαρμογή των ονομάτων στα εργαλεία που όντως έχουμε φτιάξει
    if c_b1.button("🛡️ Stress Test", use_container_width=True): 
        s.selected_tool = "stress_test_tool"; s.flow_step = "tool"; st.rerun()
        
    if c_b2.button("📦 Inventory Audit", use_container_width=True): 
        s.selected_tool = "inventory_manager"; s.flow_step = "tool"; st.rerun()
        
    if c_b3.button("👥 CLV Simulator", use_container_width=True): 
        s.selected_tool = "clv_calculator"; s.flow_step = "tool"; st.rerun()
        
    if c_b4.button("📉 WACC Optimizer", use_container_width=True): 
        s.selected_tool = "wacc_optimizer"; s.flow_step = "tool"; st.rerun()

    c_b5, c_b6, c_b7, c_b8 = st.columns(4)
    
    if c_b5.button("📉 Loss Threshold", use_container_width=True): 
        s.selected_tool = "loss_threshold"; s.flow_step = "tool"; st.rerun()

    if c_b6.button("📊 Unit Cost Audit", use_container_width=True): 
        s.selected_tool = "unit_cost_app"; s.flow_step = "tool"; st.rerun()

    # Επιστροφή στο Home
    st.write("---")
    if st.button("⬅️ Return to Global Baseline (Home)", use_container_width=True):
        s.flow_step = "home"
        st.rerun()
