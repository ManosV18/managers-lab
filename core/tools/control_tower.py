import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import numpy as np

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
    c4.metric("WACC (Locked)", f"{s.get('wacc_locked', 15.0):.1%}")

    st.divider()

    q1, q2 = st.columns(2)
    q3, q4 = st.columns(2)

    with q1: # PROFITABILITY
        st.subheader("🎯 Profitability Hub")
        bep = m.get("bep_units", 0)
        fig_be = go.Figure(go.Indicator(
            mode = "gauge+number", value = volume,
            title = {'text': "Volume vs Break-even"},
            gauge = {
                'axis': {'range': [0, max(volume, bep) * 1.2]},
                'threshold': {'line': {'color': "red", 'width': 4}, 'thickness': 0.75, 'value': bep},
                'bar': {'color': "green" if volume >= bep else "red"}
            }
        ))
        fig_be.update_layout(height=250, margin=dict(l=20, r=20, t=40, b=20))
        st.plotly_chart(fig_be, use_container_width=True)

    with q2: # LIQUIDITY
        st.subheader("💧 Liquidity Engine")
        ccc = m.get("cash_conversion_cycle", 0)
        st.write(f"**Cash Conversion Cycle:** {ccc:.0f} Days")
        
        ar = s.get("ar_days", 45)
        inv = s.get("inv_days", 60)
        ap = s.get("ap_days", 30)
        
        fig_ccc = go.Figure(go.Bar(
            y=['Receivables', 'Inventory', 'Payables'],
            x=[ar, inv, -ap],
            orientation='h',
            marker_color=['#3b82f6', '#10b981', '#ef4444']
        ))
        fig_ccc.update_layout(height=200, margin=dict(l=20, r=20, t=10, b=10))
        st.plotly_chart(fig_ccc, use_container_width=True)

    with q3: # RISK
        st.subheader("🛡️ Risk Radar")
        # Τραβάμε το real value από το Shock Simulator
        prob_fail = s.get("mc_prob_fail", 0)
        
        st.metric("Bankruptcy Probability", f"{prob_fail:.1f}%")
        st.progress(prob_fail / 100, text="Stochastic Risk Level")
        
        if prob_fail > 50:
            st.error("🚨 Critical Risk: Run Stress Tests immediately.")
        elif prob_fail > 20:
            st.warning("⚠️ Elevated Risk: Review liquidity buffers.")
        else:
            st.success("✅ Risk under control based on current shock models.")

    with q4: # GROWTH
        st.subheader("🚀 Growth Strategy")
        roe = (net_profit / s.get('opening_cash', 1)) * 100
        st.write(f"**Implied ROE:** {roe:.1%}")
        wacc = s.get('wacc_locked', 15.0)
        
        if roe > wacc:
            st.success(f"✅ Value Creation (ROE {roe:.1%} > WACC {wacc:.1%})")
        else:
            st.warning(f"⚠️ Value Destruction (ROE {roe:.1%} < WACC {wacc:.1%})")

    st.divider()
    st.subheader("🛠️ Deep Dive Tools")
    col_btn1, col_btn2, col_btn3 = st.columns(3)
    if col_btn1.button("🔬 Shock Simulator", use_container_width=True): 
        s.selected_tool = "shock_simulator"; s.flow_step = "tool"; st.rerun()
    if col_btn2.button("🔄 Cash Conversion Cycle", use_container_width=True): 
        s.selected_tool = "cash_cycle"; s.flow_step = "tool"; st.rerun()
    if col_btn3.button("🎯 Pricing Strategy", use_container_width=True): 
        s.selected_tool = "pricing_strategy"; s.flow_step = "tool"; st.rerun()
