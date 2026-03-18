import streamlit as st
import plotly.graph_objects as go

def show_stress_test_tool():
    """
    Strategic Stress Test Tool: Calculates liquidity impact based on 
    revenue shocks and collection delays (DSO).
    Compliance: Uses 365-day basis for daily revenue calculations.
    """
    st.header("🛡️ Cash Flow Stress Test")
    st.info("Shock Absorption Analysis: Simulating systemic resilience under extreme conditions.")
    
    s = st.session_state
    
    # 1. BASELINE DATA RETRIEVAL
    price = float(s.get('price', 100.0))
    vc = float(s.get('variable_cost', 60.0))
    volume = float(s.get('volume', 1000))
    fixed_costs = float(s.get('fixed_cost', 20000.0))
    debt_service = float(s.get('annual_debt_service', 0.0))
    
    # Initial Cash Position from Global State
    current_cash = float(s.get('opening_cash', 0.0))
    
    # Baseline Profitability (Annualized)
    base_rev = price * volume
    unit_contribution = price - vc
    base_ebitda = (unit_contribution * volume) - fixed_costs
    base_tax = max(0, base_ebitda * 0.22)
    base_profit = base_ebitda - base_tax - debt_service
    
    # 2. SCENARIO PARAMETERS (USER CONTROL)
    st.subheader("⚠️ Scenario Parameters")
    c1, c2, c3 = st.columns(3)
    
    rev_shock = c1.slider("Revenue Change (%)", -60, 20, -25) / 100
    dso_shock = c2.slider("Collection Delay (Days)", 0, 120, 30)
    cost_shock = c3.slider("Fixed Cost Spike (%)", 0, 50, 10) / 100

    # 3. IMPACT CALCULATIONS
    new_rev = base_rev * (1 + rev_shock)
    new_volume = volume * (1 + rev_shock)
    
    # Liquidity Drain Calculation (Instruction [2026-02-18]: 365 days)
    # This represents the cash 'trapped' in receivables due to the delay.
    liquidity_impact = (new_rev / 365) * dso_shock
    
    # New Profitability Under Stress
    new_ebitda = (unit_contribution * new_volume) - (fixed_costs * (1 + cost_shock))
    new_tax = max(0, new_ebitda * 0.22)
    new_profit = new_ebitda - new_tax - debt_service
    
    # Post-Shock Cash Position
    # Calculates monthly effect of new profit plus the immediate working capital drain.
    remaining_liquidity = current_cash - liquidity_impact + (new_profit / 12)
    
    # 4. EXECUTIVE DASHBOARD
    st.divider()
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("New Revenue", f"$ {new_rev:,.0f}")
    m2.metric("New Annual Profit", f"$ {new_profit:,.0f}")
    m3.metric("Liquidity Drain", f"$ {liquidity_impact:,.0f}", delta_color="inverse")
    
    # Cash metric color-coded based on survival
    cash_delta = remaining_liquidity - current_cash
    m4.metric("Post-Shock Cash", f"$ {remaining_liquidity:,.0f}", 
              delta=f"{cash_delta:,.0f}",
              delta_color="normal" if remaining_liquidity > 0 else "inverse")

    # 5. RESILIENCE GAUGE & DECISION LOGIC
    st.subheader("🧭 Survival Analysis")
    
    if remaining_liquidity < 0:
        st.error(f"🚨 **LIQUIDITY CRUNCH:** Business cannot absorb this shock. Funding gap: $ {abs(remaining_liquidity):,.0f}")
    elif new_profit < 0:
        st.warning("⚠️ **OPERATING LOSS:** Liquidity is currently holding, but business model is burning cash annually.")
    else:
        st.success("✅ **RESILIENT:** Company maintains positive liquidity under this specific scenario.")
    
    # Heuristic resilience scoring (0-100)
    resilience_score = 100
    if new_profit < 0: resilience_score -= 40
    if remaining_liquidity < 0: resilience_score -= 50
    if dso_shock > 45: resilience_score -= 10
    
    resilience_score = max(0, min(100, resilience_score))
    
    fig = go.Figure(go.Indicator(
        mode = "gauge+number",
        value = resilience_score,
        title = {'text': "Survival Score"},
        gauge = {'axis': {'range': [0, 100]},
                 'bar': {'color': "#1E3A8A"},
                 'steps': [
                     {'range': [0, 35], 'color': "#fee2e2"},   # Critical (Light Red)
                     {'range': [35, 70], 'color': "#fef3c7"},  # Warning (Light Amber)
                     {'range': [70, 100], 'color': "#dcfce7"}]} # Safe (Light Green)
    ))
    fig.update_layout(height=300, margin=dict(t=50, b=0, l=40, r=40), paper_bgcolor='rgba(0,0,0,0)')
    st.plotly_chart(fig, use_container_width=True)

    # 6. NAVIGATION
    st.divider()
    if st.button("⬅️ Return to Control Tower", use_container_width=True):
        st.session_state.flow_step = "home"
        st.session_state.selected_tool = None
        st.rerun()
