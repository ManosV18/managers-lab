import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import numpy as np

def show_company_shock_simulator():
    st.title("🛡️ Strategic Survival & Risk Lab")
    st.markdown("---")

    # 1. SHARED UNIVERSE
    price = float(st.session_state.get("price", 100.0))
    volume = float(st.session_state.get("volume", 1000.0))
    variable_cost = float(st.session_state.get("variable_cost", 60.0))
    fixed_cost = float(st.session_state.get("fixed_cost", 20000.0)) 
    current_cash = float(st.session_state.get("opening_cash", 10000.0))

    # 2. RAPID SCENARIO BUTTONS
    st.subheader("⚡ Rapid Stress Scenarios")
    c1, c2, c3, c4 = st.columns(4)
    if 'd_shock' not in st.session_state: st.session_state.d_shock = 0
    if 'c_shock' not in st.session_state: st.session_state.c_shock = 0
    if 'ar_shock' not in st.session_state: st.session_state.ar_shock = 0

    if c1.button("📉 Demand Crisis"):
        st.session_state.d_shock, st.session_state.c_shock, st.session_state.ar_shock = -25, 5, 20
        st.rerun()
    if c2.button("📦 Supply Shock"):
        st.session_state.d_shock, st.session_state.c_shock, st.session_state.ar_shock = -10, 15, 5
        st.rerun()
    if c3.button("💳 Credit Crunch"):
        st.session_state.ar_shock = 45
        st.rerun()
    if c4.button("🏦 Full Crisis"):
        st.session_state.d_shock, st.session_state.c_shock, st.session_state.ar_shock = -30, 20, 30
        st.rerun()

    # 3. SHOCK CONTROLS
    col1, col2 = st.columns(2)
    with col1:
        demand_shock = st.slider("Demand Shock %", -50, 20, st.session_state.d_shock)
        cost_shock = st.slider("Cost Shock %", 0, 50, st.session_state.c_shock)
    with col2:
        ar_delay = st.slider("Receivables Delay (extra days)", 0, 90, st.session_state.ar_shock)

    # 4. CORE ENGINE & LIQUIDITY LOGIC
    shocked_volume = volume * (1 + demand_shock / 100)
    shocked_cost = variable_cost * (1 + cost_shock / 100)
    shock_margin = price - shocked_cost
    shock_rev = shocked_volume * price
    shock_net_cash_monthly = (shocked_volume * shock_margin - fixed_cost) / 12
    
    cash_delay_impact = (shock_rev / 365) * ar_delay
    effective_cash = current_cash - cash_delay_impact
    
    months_range = list(range(25))
    shock_path = [effective_cash + (shock_net_cash_monthly * m) for m in months_range]
    
    # Precise Survival Calculation
    survival_idx = next((i for i, x in enumerate(shock_path) if x < 0), None)
    survival_display = f"{survival_idx} Mo" if survival_idx is not None else "∞"
    st.session_state["survival_months"] = survival_display

    # 5. MONTE CARLO SIMULATION
    iterations = 1000
    mc_results = []
    for _ in range(iterations):
        mc_v = shocked_volume * np.random.normal(1, 0.10)
        mc_c = shocked_cost * np.random.normal(1, 0.05)
        mc_cf = (mc_v * (price - mc_c) - fixed_cost) / 12
        
        # BUG FIX 1: Protection against negative effective cash
        if mc_cf < 0:
            res = max(0, min(24, effective_cash / abs(mc_cf)))
        else:
            res = 24
        mc_results.append(res)
    
    prob_failure = (sum(1 for res in mc_results if res < 12) / iterations) * 100
    st.session_state["mc_prob_fail"] = prob_failure

    # 6. EXECUTIVE DASHBOARD
    st.subheader("🏁 Executive Decision Panel")
    m1, m2, m3, m4, m5 = st.columns(5)
    cm_ratio = shock_margin / price if price != 0 else 0
    liq_gap = min(shock_path)
    
    m1.metric("Survival Threshold", survival_display)
    m2.metric("Monthly Net CF", f"€{int(shock_net_cash_monthly):,}")
    m3.metric("Funding Required", f"€{int(abs(min(0, liq_gap))):,}")
    m4.metric("CM Ratio", f"{cm_ratio:.1%}")
    m5.metric("Liquidity Gap", f"€{int(liq_gap):,}")

    # 7. RISK ANALYSIS & CHARTS
    st.divider()
    col_g, col_h = st.columns([1, 2])
    
    with col_g:
        fig_gauge = go.Figure(go.Indicator(
            mode = "gauge+number", value = prob_failure,
            title = {'text': "Failure Prob. (12 Mo)"},
            gauge = {'axis': {'range': [0, 100]}, 'bar': {'color': "black"},
                     'steps': [{'range': [0, 20], 'color': "green"}, {'range': [20, 50], 'color': "yellow"}, {'range': [50, 100], 'color': "red"}]}
        ))
        st.plotly_chart(fig_gauge, use_container_width=True)
    
    with col_h:
        st.subheader("Monte Carlo Survival Distribution")
        fig_hist = go.Figure()
        fig_hist.add_histogram(x=mc_results, nbinsx=24, marker_color='#ef4444')
        fig_hist.update_layout(xaxis_title="Months of Survival", template="plotly_dark", height=350)
        st.plotly_chart(fig_hist, use_container_width=True)

    # SURVIVAL PATH CHART
    st.subheader("📉 Cash Survival Path")
    fig_path = go.Figure()
    fig_path.add_trace(go.Scatter(x=months_range, y=shock_path, mode="lines+markers", line=dict(color="#FF4B4B", width=3)))
    fig_path.add_hline(y=0, line_dash="dash", line_color="white")
    st.plotly_chart(fig_path, use_container_width=True)

    if st.button("⬅️ Reset Simulator"):
        st.session_state.d_shock, st.session_state.c_shock, st.session_state.ar_shock = 0, 0, 0
        st.rerun()
