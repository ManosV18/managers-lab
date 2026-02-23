import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from core.engine import compute_core_metrics

def show_stress_test_simulator():
    st.header("🛡️ Cash Flow Stress Test & Scenario Planning")
    st.info("Simulation of financial resilience with automatic mitigation logic.")

    # 1. FETCH BASELINE DATA
    metrics = compute_core_metrics()
    s = st.session_state
    
    base_rev = metrics['revenue']
    base_profit = metrics['net_profit']
    base_dso = s.get('ar_days', 45)
    
    # 2. SCENARIO INPUTS (SHOCKS)
    st.subheader("⚠️ Scenario Parameters (The Shock)")
    c1, c2, c3 = st.columns(3)
    
    rev_shock = c1.slider("Revenue Change (%)", -50, 20, -20) / 100
    dso_shock = c2.slider("DSO Delay (Extra Days)", 0, 90, 15)
    cost_shock = c3.slider("Fixed Cost Increase (%)", 0, 30, 5) / 100

    # 3. IMPACT CALCULATIONS
    new_rev = base_rev * (1 + rev_shock)
    # Liquidity Drain due to DSO delay
    liquidity_impact = (new_rev / 365) * dso_shock
    # Profit impact calculation
    new_profit = (new_rev * (metrics['unit_contribution'] / s.get('price', 1))) - (s.get('fixed_cost', 0) * (1 + cost_shock))
    
    total_cash_gap = liquidity_impact + (base_profit - new_profit)

    st.divider()

    # 4. RESULTS DASHBOARD
    m1, m2, m3 = st.columns(3)
    m1.metric("New Annual Revenue", f"€ {new_rev:,.0f}", delta=f"{rev_shock:.0%}")
    m2.metric("Net Profit Shift", f"€ {new_profit:,.0f}", delta=f"{new_profit - base_profit:,.0f}", delta_color="inverse")
    m3.metric("Total Liquidity Gap", f"€ {total_cash_gap:,.0f}", delta="Immediate Risk", delta_color="inverse")

    # 5. AUTOMATIC MITIGATION LOGIC
    st.subheader("🛠️ Automatic Mitigation Strategy")
    st.write("How to close the liquidity gap through Working Capital optimization:")
    
    # Calculate required reduction in Inventory or DSO to cover the gap
    # Formula: Gap = (Annual Revenue / 365) * Days_Reduction
    if total_cash_gap > 0:
        req_dso_reduction = (total_cash_gap * 365) / new_rev if new_rev > 0 else 0
        
        col_a, col_b = st.columns(2)
        with col_a:
            st.warning(f"**Option A: DSO Tightening**\nYou need to reduce collection time by **{req_dso_reduction:.1f} days** to offset the gap.")
        with col_b:
            # Mitigation via Inventory (assuming COGS is 60% of Revenue for the math)
            approx_cogs = new_rev * 0.6
            req_inv_reduction = (total_cash_gap / approx_cogs * 100) if approx_cogs > 0 else 0
            st.warning(f"**Option B: Inventory Lean**\nYou need a **{req_inv_reduction:.1f}%** reduction in average stock levels.")
    else:
        st.success("The system is self-sustaining under this scenario. No emergency mitigation required.")

    # 6. SURVIVAL GAUGE
    survival_score = max(0, min(100, 100 + (rev_shock * 150) - (dso_shock)))
    
    fig = go.Figure(go.Indicator(
        mode = "gauge+number",
        value = survival_score,
        title = {'text': "Survival Resilience Index"},
        gauge = {
            'axis': {'range': [0, 100]},
            'bar': {'color': "white"},
            'steps': [
                {'range': [0, 40], 'color': "#8b0000"},
                {'range': [40, 75], 'color': "#ffa500"},
                {'range': [75, 100], 'color': "#228b22"}]
        }
    ))
    fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', font={'color': "white"})
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("🧠 Analyst's Verdict")
    if total_cash_gap > (base_rev * 0.1): # If gap > 10% of Revenue
        st.error("🚨 **STRUCTURAL DANGER:** The cash drain is too aggressive. Traditional working capital optimization might not be enough. Consider capital injection or drastic cost-cutting.")
    else:
        st.info("ℹ️ **MANAGEABLE STRESS:** The liquidity gap can be absorbed by optimizing internal operations (DSO & Inventory).")
