import streamlit as st
import plotly.graph_objects as go

def show_stress_test_tool():
    st.header("🛡️ Cash Flow Stress Test")
    st.info("Simulate shocks to revenue, costs, and collection cycles.")
    
    s = st.session_state
    
    # 1. FETCH DATA (Linked to Home Parameters)
    price = float(s.get('price', 100.0))
    vc = float(s.get('variable_cost', 60.0))
    volume = float(s.get('volume', 1000))
    fixed_costs = float(s.get('fixed_cost', 20000.0))
    debt_service = float(s.get('annual_debt_service', 0.0)) # Διόρθωση ονόματος
    
    base_rev = price * volume
    unit_contribution = price - vc
    base_ebitda = (unit_contribution * volume) - fixed_costs
    base_tax = max(0, base_ebitda * 0.22)
    base_profit = base_ebitda - base_tax - debt_service
    
    # 2. SCENARIO INPUTS
    st.subheader("⚠️ Scenario Parameters (The Shock)")
    c1, c2, c3 = st.columns(3)
    
    rev_shock = c1.slider("Revenue Change (%)", -50, 20, -20) / 100
    dso_shock = c2.slider("DSO Delay (Extra Days)", 0, 90, 15)
    cost_shock = c3.slider("Fixed Cost Increase (%)", 0, 30, 5) / 100

    # 3. IMPACT CALCULATIONS
    new_rev = base_rev * (1 + rev_shock)
    new_volume = volume * (1 + rev_shock)
    
    # Liquidity Drain (DSO delay) on 365-day basis
    liquidity_impact = (new_rev / 365) * dso_shock
    
    new_ebitda = (unit_contribution * new_volume) - (fixed_costs * (1 + cost_shock))
    new_tax = max(0, new_ebitda * 0.22)
    new_profit = new_ebitda - new_tax - debt_service
    
    total_cash_gap = liquidity_impact + (base_profit - new_profit)

    # 4. RESULTS DASHBOARD
    st.divider()
    m1, m2, m3 = st.columns(3)
    m1.metric("New Annual Revenue", f"€ {new_rev:,.0f}", delta=f"{rev_shock:.0%}")
    m2.metric("Projected Cash Flow", f"€ {new_profit:,.0f}", delta=f"{new_profit - base_profit:,.0f}", delta_color="inverse")
    m3.metric("Total Liquidity Gap", f"€ {total_cash_gap:,.0f}", delta="Immediate Risk", delta_color="inverse")

    # 5. SURVIVAL GAUGE
    resilience_score = 100
    if new_profit < 0: resilience_score -= 40
    if total_cash_gap > (base_rev * 0.1): resilience_score -= 40
    resilience_score = max(0, min(100, resilience_score + (rev_shock * 50)))
    
    fig = go.Figure(go.Indicator(
        mode = "gauge+number",
        value = resilience_score,
        title = {'text': "Survival Resilience Index"},
        gauge = {'axis': {'range': [0, 100]},
                 'bar': {'color': "white"},
                 'steps': [
                     {'range': [0, 40], 'color': "#8b0000"},
                     {'range': [40, 75], 'color': "#ffa500"},
                     {'range': [75, 100], 'color': "#228b22"}]
                }
    ))
    fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', font={'color': "gray"}, height=300)
    st.plotly_chart(fig, use_container_width=True)

    if st.button("⬅️ Back to Library Hub", use_container_width=True):
        st.session_state.selected_tool = None
        st.rerun()
