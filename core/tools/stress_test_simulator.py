import streamlit as st
import pandas as pd
import plotly.graph_objects as go

def show_stress_test_tool():  # Renamed to match the registry exactly
    st.header("🛡️ Cash Flow Stress Test & Scenario Planning")
    st.info("Simulate shocks to revenue, costs, and collection cycles to test your business resilience.")
    
    # 1. FETCH DATA DIRECTLY FROM SESSION STATE (Analytical Approach)
    s = st.session_state
    
    # Base metrics from Stage 0 or defaults
    price = float(s.get('price', 100.0))
    vc = float(s.get('variable_cost', 60.0))
    unit_contribution = price - vc
    volume = float(s.get('volume', 10000))
    
    base_rev = price * volume
    base_fixed_costs = float(s.get('fixed_cost', 200000.0))
    base_ebitda = (unit_contribution * volume) - base_fixed_costs
    base_tax = max(0, base_ebitda * 0.22)
    base_loan = float(s.get('annual_debt_service', 50000.0))
    base_profit = base_ebitda - base_tax - base_loan
    
    # 2. SCENARIO INPUTS (SHOCKS)
    st.subheader("⚠️ Scenario Parameters (The Shock)")
    c1, c2, c3 = st.columns(3)
    
    rev_shock = c1.slider("Revenue Change (%)", -50, 20, -20) / 100
    dso_shock = c2.slider("DSO Delay (Extra Days)", 0, 90, 15)
    cost_shock = c3.slider("Fixed Cost Increase (%)", 0, 30, 5) / 100

    # 3. IMPACT CALCULATIONS
    new_rev = base_rev * (1 + rev_shock)
    new_volume = volume * (1 + rev_shock)
    
    # Liquidity Drain due to DSO delay: (Revenue/365) * extra days
    liquidity_impact = (new_rev / 365) * dso_shock
    
    # New Profit impact
    new_ebitda = (unit_contribution * new_volume) - (base_fixed_costs * (1 + cost_shock))
    new_tax = max(0, new_ebitda * 0.22)
    new_profit = new_ebitda - new_tax - base_loan
    
    total_cash_gap = liquidity_impact + (base_profit - new_profit)

    st.divider()

    # 4. RESULTS DASHBOARD
    m1, m2, m3 = st.columns(3)
    m1.metric("New Annual Revenue", f"€ {new_rev:,.0f}", delta=f"{rev_shock:.0%}")
    m2.metric("Projected FCF", f"€ {new_profit:,.0f}", delta=f"{new_profit - base_profit:,.0f}", delta_color="inverse")
    m3.metric("Total Liquidity Gap", f"€ {total_cash_gap:,.0f}", delta="Immediate Risk", delta_color="inverse")

    # 5. AUTOMATIC MITIGATION LOGIC
    st.subheader("🛠️ Mitigation Strategy")
    if total_cash_gap > 0:
        req_dso_reduction = (total_cash_gap * 365) / new_rev if new_rev > 0 else 0
        
        col_a, col_b = st.columns(2)
        with col_a:
            st.warning(f"**Option A: DSO Tightening**\nYou need to reduce collection time by **{req_dso_reduction:.1f} days** to offset the gap.")
        with col_b:
            approx_cogs = new_volume * vc
            req_inv_reduction = (total_cash_gap / approx_cogs * 100) if approx_cogs > 0 else 0
            st.warning(f"**Option B: Inventory Lean**\nYou need a **{req_inv_reduction:.1f}%** reduction in average stock levels.")
    else:
        st.success("🟢 The system is self-sustaining under this scenario. No emergency mitigation required.")

    # 6. SURVIVAL GAUGE
    resilience_score = 100
    if new_profit < 0: resilience_score -= 40
    if total_cash_gap > (base_rev * 0.1): resilience_score -= 40
    resilience_score = max(0, min(100, resilience_score + (rev_shock * 50)))
    
    
    
    fig = go.Figure(go.Indicator(
        mode = "gauge+number",
        value = resilience_score,
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
    fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', font={'color': "gray"})
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("🧠 Analyst's Verdict")
    if total_cash_gap > (base_rev * 0.15): 
        st.error("🚨 **STRUCTURAL DANGER:** The shock is too deep. Internal optimization is mathematically insufficient. Capital injection required.")
    else:
        st.info("ℹ️ **MANAGEABLE STRESS:** Operational levers (DSO/Inventory) can bridge this gap.")

    if st.button("⬅️ Back to Library Hub", use_container_width=True):
        st.session_state.selected_tool = None
        st.rerun()
