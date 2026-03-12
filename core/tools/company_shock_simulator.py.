import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import numpy as np

def show_company_shock_simulator():
    st.title("🛡️ Strategic Survival & Risk Lab")
    st.markdown("---")

    # 1. SHARED UNIVERSE: Σύνδεση με το Integrated Lab (Session State)
    # Τραβάει αυτόματα δεδομένα από τα άλλα εργαλεία αν υπάρχουν
    price = float(st.session_state.get("price", 100.0))
    volume = float(st.session_state.get("volume", 1000.0))
    variable_cost = float(st.session_state.get("variable_cost", 60.0))
    fixed_cost = float(st.session_state.get("fixed_costs", 20000.0))
    wacc = float(st.session_state.get("wacc_locked", 15.0))
    current_cash = float(st.session_state.get("cash_position", 100000.0))

    # 2. RAPID SCENARIO BUTTONS
    st.subheader("⚡ Rapid Stress Scenarios")
    c1, c2, c3, c4 = st.columns(4)

    if 'd_shock' not in st.session_state: st.session_state.d_shock = 0
    if 'c_shock' not in st.session_state: st.session_state.c_shock = 0
    if 'ar_shock' not in st.session_state: st.session_state.ar_shock = 0
    if 'wacc_shock' not in st.session_state: st.session_state.wacc_shock = 0.0

    if c1.button("📉 Demand Crisis"):
        st.session_state.d_shock, st.session_state.c_shock = -25, 5
        st.session_state.ar_shock, st.session_state.wacc_shock = 20, 2.0
        st.rerun()

    if c2.button("📦 Supply Shock"):
        st.session_state.d_shock, st.session_state.c_shock = -10, 15
        st.session_state.ar_shock, st.session_state.wacc_shock = 5, 1.0
        st.rerun()

    if c3.button("💳 Credit Crunch"):
        st.session_state.ar_shock, st.session_state.wacc_shock = 45, 4.0
        st.rerun()

    if c4.button("🏦 Full Crisis"):
        st.session_state.d_shock, st.session_state.c_shock = -30, 20
        st.session_state.ar_shock, st.session_state.wacc_shock = 30, 5.0
        st.rerun()

    # 3. SHOCK CONTROLS
    st.markdown("### Manual Adjustments")
    col1, col2 = st.columns(2)
    with col1:
        demand_shock = st.slider("Demand Shock %", -50, 20, st.session_state.d_shock)
        cost_shock = st.slider("Cost Shock %", 0, 50, st.session_state.c_shock)
    with col2:
        ar_delay = st.slider("Receivables Delay (days)", 0, 90, st.session_state.ar_shock)
        interest_shock = st.slider("Interest Rate Shock %", 0.0, 10.0, st.session_state.wacc_shock)

    # 4. CORE ENGINE & LIQUIDITY LOGIC
    shocked_volume = volume * (1 + demand_shock / 100)
    shocked_cost = variable_cost * (1 + cost_shock / 100)
    shock_margin = price - shocked_cost
    shock_rev = shocked_volume * price
    shock_net_cash_monthly = (shocked_volume * shock_margin) - fixed_cost
    
    # Liquidity Gap & Funding Need Calculation
    cash_delay_impact = (shock_rev / 365) * ar_delay
    effective_cash = current_cash - cash_delay_impact
    months = list(range(13))
    shock_path = [effective_cash + (shock_net_cash_monthly * m) for m in months]
    liq_gap = min(shock_path)
    funding_need = abs(min(0, liq_gap))

    # Survival Logic
    shock_survival = 999 if shock_net_cash_monthly >= 0 else max(0, effective_cash / abs(shock_net_cash_monthly))
    survival_display = "∞ (Cash Generative)" if shock_survival > 900 else f"{shock_survival:.1f} Mo"

    # 5. MONTE CARLO SIMULATION (Stochastic Risk)
    iterations = 1000
    mc_results = []
    for _ in range(iterations):
        mc_v = volume * (1 + demand_shock/100) * np.random.normal(1, 0.10)
        mc_c = variable_cost * (1 + cost_shock/100) * np.random.normal(1, 0.05)
        mc_cf = (mc_v * (price - mc_c)) - fixed_cost
        
        if mc_cf >= 0:
            res = 999
        else:
            res = effective_cash / abs(mc_cf) if mc_cf != 0 else 0
        mc_results.append(res)
    
    prob_failure = (sum(1 for res in mc_results if res < 12) / iterations) * 100
    median_survival = np.median(mc_results)
    worst_case = np.percentile(mc_results, 5)

    # 6. EXECUTIVE DASHBOARD
    st.subheader("🏁 Executive Decision Panel")
    cm_ratio = shock_margin / price if price != 0 else 0
    
    m1, m2, m3, m4, m5 = st.columns(5)
    m1.metric("Survival Horizon", survival_display)
    m2.metric("Monthly Net Cash", f"€{int(shock_net_cash_monthly):,}")
    m3.metric("Funding Required", f"€{int(funding_need):,}")
    m4.metric("CM Ratio", f"{cm_ratio:.1%}")
    m5.metric("Liquidity Gap", f"€{int(liq_gap):,}")

    # 7. RISK ANALYSIS & CHARTS
    st.divider()
    col_g, col_s = st.columns([2, 1])
    
    with col_g:
        fig_gauge = go.Figure(go.Indicator(
            mode = "gauge+number", value = prob_failure,
            title = {'text': "Bankruptcy Probability (12 Mo)"},
            gauge = {
                'axis': {'range': [0, 100]}, 
                'bar': {'color': "black"},
                'steps': [
                    {'range': [0, 20], 'color': "green"},
                    {'range': [20, 50], 'color': "yellow"},
                    {'range': [50, 100], 'color': "red"}
                ]
            }
        ))
        st.plotly_chart(fig_gauge, use_container_width=True)

    with col_s:
        st.write("📊 **Monte Carlo Stats**")
        st.metric("Median Survival", f"{median_survival:.1f} Mo" if median_survival < 900 else "Stable")
        st.metric("Worst Case (5%)", f"{worst_case:.1f} Mo" if worst_case < 900 else "Critical")
        st.info("The Worst Case (5%) indicates your survival limit in tail-risk events.")

    # SURVIVAL CHART
    st.subheader("📉 Cash Survival Path")
    fig_path = go.Figure()
    fig_path.add_trace(go.Scatter(x=months, y=shock_path, mode="lines+markers", name="Cash Position", line=dict(color="#FF4B4B", width=3)))
    fig_path.add_hline(y=0, line_dash="dash", line_color="white", annotation_text="Bankruptcy Threshold")
    fig_path.update_layout(xaxis_title="Months Forward", yaxis_title="Available Cash (€)", template="plotly_dark", height=400)
    st.plotly_chart(fig_path, use_container_width=True)

    # 8. DIAGNOSTIC IMPACT TABLE
    st.subheader("🔬 Diagnostic Analysis Table")
    
    base_rev = volume * price
    base_margin = price - variable_cost
    base_contribution = volume * base_margin
    base_be = fixed_cost / base_margin if base_margin > 0 else 0
    base_net_cash_monthly = base_contribution - fixed_cost

    df_comp = pd.DataFrame({
        "Metric": ["Revenue", "Total Contribution", "Unit Margin", "Monthly Net Cash", "Break-even Units"],
        "Baseline Status": [base_rev, base_contribution, base_margin, base_net_cash_monthly, base_be],
        "After Shock Status": [shock_rev, (shocked_volume * shock_margin), shock_margin, shock_net_cash_monthly, shock_be]
    })
    
    # Division by zero protection for Δ Change
    df_comp["Δ Change"] = (
        (df_comp["After Shock Status"] - df_comp["Baseline Status"]) / 
        df_comp["Baseline Status"].replace(0, 1).abs() * 100
    ).map("{:+.1f}%".format)
    
    st.table(df_comp)

    if st.button("⬅️ Reset Simulator to Baseline"):
        st.session_state.d_shock, st.session_state.c_shock = 0, 0
        st.session_state.ar_shock, st.session_state.wacc_shock = 0, 0.0
        st.rerun()
