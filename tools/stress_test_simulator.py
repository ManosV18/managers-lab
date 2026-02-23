import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from core.engine import compute_core_metrics

def show_stress_test_simulator():
    st.header("🛡️ Cash Flow Stress Test & Scenario Planning")
    st.info("Analytical simulation of financial resilience under adverse market conditions.")

    # 1. FETCH BASELINE DATA
    metrics = compute_core_metrics()
    s = st.session_state
    
    base_rev = metrics['revenue']
    base_profit = metrics['net_profit']
    base_dso = s.get('ar_days', 45)
    base_cash = s.get('debt', 20000.0) # Χρησιμοποιούμε το debt ως proxy για τις ανάγκες ρευστότητας ή ταμειακό απόθεμα

    # 2. SCENARIO INPUTS (SHOCKS)
    st.subheader("⚠️ Scenario Parameters (The Shock)")
    c1, c2, c3 = st.columns(3)
    
    rev_shock = c1.slider("Revenue Change (%)", -50, 20, -20) / 100
    dso_shock = c2.slider("DSO Delay (Extra Days)", 0, 90, 15)
    cost_shock = c3.slider("Fixed Cost Increase (%)", 0, 30, 5) / 100

    # 3. IMPACT CALCULATIONS
    new_rev = base_rev * (1 + rev_shock)
    new_dso = base_dso + dso_shock
    
    # Calculate Liquidity Gap (The "Drain")
    # Κάθε μέρα καθυστέρησης στο DSO δεσμεύει: (Revenue / 365) * Days
    liquidity_impact = (new_rev / 365) * dso_shock
    new_profit = (new_rev * (metrics['unit_contribution'] / s.get('price', 1))) - (s.get('fixed_cost', 0) * (1 + cost_shock))
    
    st.divider()

    # 4. RESULTS DASHBOARD
    st.subheader("📊 Financial Impact Analysis")
    m1, m2, m3 = st.columns(3)
    m1.metric("New Annual Revenue", f"€ {new_rev:,.0f}", delta=f"{rev_shock:.0%}")
    m2.metric("Net Profit Shift", f"€ {new_profit:,.0f}", delta=f"{new_profit - base_profit:,.0f}", delta_color="inverse")
    m3.metric("Cash Liquidity Drain", f"€ {liquidity_impact:,.0f}", delta="Immediate Gap", delta_color="inverse")

    # 5. RESILIENCE VISUALIZATION
    # Gauge for "Survival Index"
    survival_score = 100 + (rev_shock * 100) - (dso_shock / 2)
    survival_score = max(0, min(100, survival_score))
    
    fig = go.Figure(go.Indicator(
        mode = "gauge+number",
        value = survival_score,
        title = {'text': "System Resilience Score"},
        gauge = {
            'axis': {'range': [0, 100]},
            'bar': {'color': "darkblue"},
            'steps': [
                {'range': [0, 30], 'color': "red"},
                {'range': [30, 70], 'color': "orange"},
                {'range': [70, 100], 'color': "green"}]
        }
    ))
    st.plotly_chart(fig, use_container_width=True)

    # 6. ANALYST'S VERDICT
    st.subheader("🧠 Cold Analysis & Recommendations")
    if survival_score < 40:
        st.error(f"**CRITICAL VULNERABILITY:** Under this scenario, the business faces a liquidity gap of €{liquidity_impact:,.2f}. The shock absorption capacity is exhausted.")
        st.write("👉 **Action:** Immediate reduction of Payables Days or emergency credit line activation required.")
    elif survival_score < 70:
        st.warning(f"**MODERATE STRESS:** Significant margin erosion. Cash flow is negative but manageable through working capital optimization.")
    else:
        st.success("**HIGH RESILIENCE:** The current structure can absorb this shock without structural damage.")
