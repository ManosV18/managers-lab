import streamlit as st
import pandas as pd
import plotly.graph_objects as go

def show_control_tower():
    st.title("🕹️ Mission Control: Enterprise Tower")
    st.caption("Integrated Strategic & Financial Oversight")
    
    s = st.session_state
    m = s.get("metrics", {})
    
    if not s.get("baseline_locked"):
        st.warning("⚠️ Baseline not locked. Using session parameters.")

    # --- FETCH FROM ENGINE (Cold Logic: Single Source of Truth) ---
    revenue = m.get("revenue", 0.0)
    ebit = m.get("ebit", 0.0)
    net_profit = m.get("net_profit", 0.0)
    roic = m.get("roic", 0.0)
    invested_cap = m.get("invested_capital", 0.0)
    bep = m.get("bep_units", 0.0)
    ccc = m.get("ccc", 0.0)  # Correct key from our updated engine
    
    # TOP LEVEL METRICS
    c1, c2, c3, c4 = st.columns(4)
    
    c1.metric("Annual Revenue", f"€{revenue:,.0f}")
    c2.metric("Net Profit (After Tax)", f"€{net_profit:,.0f}", 
              delta=f"{(net_profit/revenue*100 if revenue > 0 else 0):.1f}% Margin")
    c3.metric("Invested Capital", f"€{invested_cap:,.0f}")
    
    # WACC Logic (Assuming a default or locked value)
    wacc_input = s.get('wacc_optimizer_value', 15.0) # Look for optimizer value or default
    wacc = wacc_input / 100
    c4.metric("WACC Target", f"{wacc:.1%}")

    st.divider()

    q1, q2 = st.columns(2)
    q3, q4 = st.columns(2)

    with q1: # QUADRANT 1: PROFITABILITY
        st.subheader("🎯 Profitability Hub")
        volume = float(s.get("volume", 0))
        axis_max = max(volume, bep, 1) * 1.2
        
        fig_be = go.Figure(go.Indicator(
            mode = "gauge+number", value = volume,
            title = {'text': "Volume vs BEP"},
            gauge = {'axis': {'range': [0, axis_max]},
                     'threshold': {'line': {'color': "red", 'width': 4}, 'value': bep},
                     'bar': {'color': "green" if volume >= bep else "red"}}
        ))
        fig_be.update_layout(height=250, margin=dict(l=20, r=20, t=40, b=20), template="plotly_dark")
        st.plotly_chart(fig_be, use_container_width=True)

    with q2: # QUADRANT 2: LIQUIDITY ENGINE
        st.subheader("💧 Liquidity Engine")
        st.write(f"**Cash Conversion Cycle (CCC):** {ccc:.0f} Days")
        
        # Pulling actual days from state to show the components
        ar = s.get("ar_days", 0)
        inv = s.get("inv_days", 0)
        ap = s.get("ap_days", 0)
        
        fig_ccc = go.Figure(go.Bar(
            y=['Receivables', 'Inventory', 'Payables'], 
            x=[ar, inv, -ap], 
            orientation='h', 
            marker_color=['#3b82f6', '#10b981', '#ef4444']
        ))
        fig_ccc.update_layout(height=200, margin=dict(l=20, r=20, t=10, b=10), template="plotly_dark")
        st.plotly_chart(fig_ccc, use_container_width=True)

    with q3: # QUADRANT 3: RISK RADAR
        st.subheader("🛡️ Risk Radar")
        # Pulling from engine/simulation state
        prob_fail = m.get("insolvency_prob", 0.0) # Should be updated by shock simulator
        runway = m.get("runway_months", 0.0)
        
        col_r1, col_r2 = st.columns(2)
        col_r1.metric("Insolvency Prob.", f"{prob_fail:.1f}%")
        
        if runway == float('inf'):
            col_r2.metric("Runway", "∞ (Cash Positive)")
        else:
            col_r2.metric("Runway", f"{runway:.1f} Months")
        
        st.progress(min(prob_fail / 100, 1.0), text="Stochastic Risk Level")

    with q4: # QUADRANT 4: GROWTH & VALUE
        st.subheader("🚀 Value Creation")
        st.write(f"**Implied ROIC:** {roic:.1%}")
        
        # Cold Logic Comparison
        if roic > wacc: 
            st.success(f"✅ Value Creation (ROIC {roic:.1%} > WACC {wacc:.1%})")
        else: 
            st.warning(f"🚨 Value Destruction (ROIC {roic:.1%} < WACC {wacc:.1%})")
            st.info("💡 Strategic Advice: Optimization of Working Capital or Price Increase required to bridge the gap.")

    st.divider()
    col_b1, col_b2, col_b3 = st.columns(3)
    if col_b1.button("🔬 Shock Simulator", use_container_width=True): s.selected_tool = "shock_simulator"; s.flow_step = "tool"; st.rerun()
    if col_b2.button("🔄 Working Capital", use_container_width=True): s.selected_tool = "wc_optimizer"; s.flow_step = "tool"; st.rerun()
    if col_b3.button("🎯 Pricing", use_container_width=True): s.selected_tool = "pricing_strategy"; s.flow_step = "tool"; st.rerun()
