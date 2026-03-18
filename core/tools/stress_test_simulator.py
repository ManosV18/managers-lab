import streamlit as st
import plotly.graph_objects as go

def show_stress_test_tool():
    st.header("🛡️ Cash Flow Stress Test")
    st.info("Shock Absorption Analysis: Simulating systemic resilience under extreme conditions.")
    
    s = st.session_state
    m = s.get('metrics', {})
    
    # 1. BASELINE DATA (Linked to Global State)
    price = float(s.get('price', 100.0))
    vc = float(s.get('variable_cost', 60.0))
    volume = float(s.get('volume', 1000))
    fixed_costs = float(s.get('fixed_cost', 20000.0))
    debt_service = float(s.get('annual_debt_service', 0.0))
    
    base_rev = price * volume
    unit_contribution = price - vc
    base_ebitda = (unit_contribution * volume) - fixed_costs
    base_tax = max(0, base_ebitda * 0.22)
    base_profit = base_ebitda - base_tax - debt_service
    
    # 2. SCENARIO INPUTS (The Shock)
    st.subheader("⚠️ Scenario Parameters")
    
    c1, c2, c3 = st.columns(3)
    
    rev_shock = c1.slider("Revenue Change (%)", -60, 20, -25, help="Simulate a major drop in demand or market disruption.") / 100
    dso_shock = c2.slider("Collection Delay (Days)", 0, 120, 30, help="Extra days added to your DSO (Days Sales Outstanding).")
    cost_shock = c3.slider("Fixed Cost Spike (%)", 0, 50, 10, help="Unexpected increase in overheads (energy, rent, etc.).") / 100

    # 3. IMPACT CALCULATIONS (365-Day Basis Compliance)
    new_rev = base_rev * (1 + rev_shock)
    new_volume = volume * (1 + rev_shock)
    
    # Liquidity Drain: Cash trapped in receivables due to collection delays
    # Formula uses User Instruction [2026-02-18]: 365 days
    liquidity_impact = (new_rev / 365) * dso_shock
    
    new_ebitda = (unit_contribution * new_volume) - (fixed_costs * (1 + cost_shock))
    new_tax = max(0, new_ebitda * 0.22)
    new_profit = new_ebitda - new_tax - debt_service
    
    # Total Cash Gap combines P&L loss and Working Capital drain
    total_cash_gap = liquidity_impact + max(0, (base_profit - new_profit))

    # 4. RESULTS DASHBOARD
    st.divider()
    m1, m2, m3 = st.columns(3)
    m1.metric("New Revenue Floor", f"$ {new_rev:,.0f}", delta=f"{rev_shock:.1%}")
    m2.metric("New Profitability", f"$ {new_profit:,.0f}", delta=f"{new_profit - base_profit:,.0f}", delta_color="inverse")
    m3.metric("Critical Cash Gap", f"$ {total_cash_gap:,.0f}", delta="Liquidity Drain", delta_color="inverse")

    # 5. RESILIENCE GAUGE
    st.subheader("🧭 Survival Analysis")
    
    
    # Heuristic scoring for resilience
    resilience_score = 100
    if new_profit < 0: resilience_score -= 50 # Operating loss is a major failure
    if total_cash_gap > (base_rev * 0.15): resilience_score -= 30 # Liquidity drain > 15% of revenue
    if new_rev < (fixed_costs * 1.5): resilience_score -= 20 # Low safety margin over fixed costs
    
    resilience_score = max(0, min(100, resilience_score))
    
    fig = go.Figure(go.Indicator(
        mode = "gauge+number",
        value = resilience_score,
        gauge = {'axis': {'range': [0, 100], 'tickwidth': 1},
                 'bar': {'color': "white"},
                 'steps': [
                     {'range': [0, 35], 'color': "#8B0000"}, # Critical
                     {'range': [35, 70], 'color': "#FFA500"}, # Warning
                     {'range': [70, 100], 'color': "#228B22"}], # Resilient
                }
    ))
    fig.update_layout(height=280, margin=dict(t=0, b=0, l=40, r=40), paper_bgcolor='rgba(0,0,0,0)', font={'color': "gray"})
    st.plotly_chart(fig, use_container_width=True)

    # 6. ACTION BUTTONS & NAVIGATION
    st.divider()
    if st.button("⬅️ Back to Control Tower", use_container_width=True):
        # Ενημέρωση και των δύο μεταβλητών για απόλυτη συμβατότητα με το app.py
        st.session_state.flow_step = "home"
        st.session_state.selected_tool = None
        st.rerun()
