import streamlit as st
import pandas as pd
import plotly.graph_objects as go

def show_control_tower():
    st.title("🕹️ Mission Control: Enterprise Tower")
    st.caption("Integrated Strategic & Financial Oversight")
    
    s = st.session_state
    m = s.get("metrics", {})
    
    if not s.get("baseline_locked"):
        st.warning("⚠️ Baseline not locked. Showing default parameters.")

    # TOP LEVEL METRICS
    c1, c2, c3, c4 = st.columns(4)
    
    price = float(s.get("price", 100))
    volume = float(s.get("volume", 1000))
    vc = float(s.get("variable_cost", 60))
    fc = float(s.get("fixed_cost", 20000))
    margin = price - vc
    revenue = price * volume
    net_profit = (volume * margin) - fc
    
    c1.metric("Annual Revenue", f"€{revenue:,.0f}")
    c2.metric("Net Profitability", f"€{net_profit:,.0f}", delta=f"{(net_profit/revenue if revenue > 0 else 0):.1%} Margin")
    c3.metric("Cash Position", f"€{s.get('opening_cash', 0):,.0f}")
    
    # BUG FIX 2: ROE & WACC Logic
    wacc = s.get('wacc_locked', 15.0) / 100 # Μετατροπή σε decimal αν το input είναι π.χ. 15
    roe = net_profit / s.get('opening_cash', 1)
    c4.metric("WACC (Locked)", f"{wacc:.1%}")

    st.divider()

    q1, q2 = st.columns(2)
    q3, q4 = st.columns(2)

    with q1: # QUADRANT 1: PROFITABILITY
        st.subheader("🎯 Profitability Hub")
        bep = m.get("bep_units", 0)
        # BUG FIX 3: Safety for axis max
        axis_max = max(volume, bep, 1) * 1.2
        
        fig_be = go.Figure(go.Indicator(
            mode = "gauge+number", value = volume,
            title = {'text': "Volume vs BEP"},
            gauge = {'axis': {'range': [0, axis_max]},
                     'threshold': {'line': {'color': "red", 'width': 4}, 'value': bep},
                     'bar': {'color': "green" if volume >= bep else "red"}}
        ))
        fig_be.update_layout(height=250, margin=dict(l=20, r=20, t=40, b=20))
        st.plotly_chart(fig_be, use_container_width=True)

    with q2: # QUADRANT 2: LIQUIDITY
        st.subheader("💧 Liquidity Engine")
        ccc = m.get("cash_conversion_cycle", 0)
        st.write(f"**CCC:** {ccc:.0f} Days")
        fig_ccc = go.Figure(go.Bar(y=['Receivables', 'Inventory', 'Payables'], x=[s.get("ar_days", 45), s.get("inv_days", 60), -s.get("ap_days", 30)], orientation='h', marker_color=['#3b82f6', '#10b981', '#ef4444']))
        fig_ccc.update_layout(height=200, margin=dict(l=20, r=20, t=10, b=10))
        st.plotly_chart(fig_ccc, use_container_width=True)

    with q3: # QUADRANT 3: RISK RADAR
        st.subheader("🛡️ Risk Radar")
        prob_fail = s.get("mc_prob_fail", 0)
        survival = s.get("survival_months", "N/A") 
        
        col_r1, col_r2 = st.columns(2)
        col_r1.metric("Insolvency Prob.", f"{prob_fail:.1f}%")
        col_r2.metric("Liquidity Survival", survival)
        
        st.progress(prob_fail / 100, text="Stochastic Risk Level")

    with q4: # QUADRANT 4: GROWTH & VALUE
        st.subheader("🚀 Value Creation")
        st.write(f"**Implied ROE:** {roe:.1%}")
        
        if roe > wacc: 
            st.success(f"✅ Value Creation (ROE > WACC)")
        else: 
            st.warning(f"⚠️ Value Destruction (ROE < WACC)")

    st.divider()
    col_b1, col_b2, col_b3 = st.columns(3)
    if col_b1.button("🔬 Shock Simulator", use_container_width=True): s.selected_tool = "shock_simulator"; s.flow_step = "tool"; st.rerun()
    if col_b2.button("🔄 Cash Cycle", use_container_width=True): s.selected_tool = "cash_cycle"; s.flow_step = "tool"; st.rerun()
    if col_b3.button("🎯 Pricing", use_container_width=True): s.selected_tool = "pricing_strategy"; s.flow_step = "tool"; st.rerun()
