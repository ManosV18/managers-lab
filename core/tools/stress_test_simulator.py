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
    
    # --- ΠΡΟΣΘΗΚΗ: ΤΟ ΤΑΜΕΙΟ ΣΟΥ ---
    current_cash = float(s.get('opening_cash', 0.0))
    
    base_rev = price * volume
    unit_contribution = price - vc
    base_ebitda = (unit_contribution * volume) - fixed_costs
    base_tax = max(0, base_ebitda * 0.22)
    base_profit = base_ebitda - base_tax - debt_service
    
    # 2. SCENARIO INPUTS (The Shock)
    st.subheader("⚠️ Scenario Parameters")
    c1, c2, c3 = st.columns(3)
    
    rev_shock = c1.slider("Revenue Change (%)", -60, 20, -25) / 100
    dso_shock = c2.slider("Collection Delay (Days)", 0, 120, 30)
    cost_shock = c3.slider("Fixed Cost Spike (%)", 0, 50, 10) / 100

    # 3. IMPACT CALCULATIONS
    new_rev = base_rev * (1 + rev_shock)
    new_volume = volume * (1 + rev_shock)
    
    # Liquidity Drain (Compliance [2026-02-18]: 365 days)
    liquidity_impact = (new_rev / 365) * dso_shock
    
    new_ebitda = (unit_contribution * new_volume) - (fixed_costs * (1 + cost_shock))
    new_tax = max(0, new_ebitda * 0.22)
    new_profit = new_ebitda - new_tax - debt_service
    
    # --- ΠΡΟΣΘΗΚΗ: ΝΕΟ ΤΑΜΕΙΟ ---
    # Το ταμείο μετά το σοκ της καθυστέρησης πληρωμών και της απώλειας κερδοφορίας
    remaining_liquidity = current_cash - liquidity_impact + (new_profit / 12) # Μηνιαία επίδραση κέρδους
    
    # 4. RESULTS DASHBOARD
    st.divider()
    m1, m2, m3, m4 = st.columns(4) # Αυξήσαμε τις στήλες σε 4
    m1.metric("New Revenue", f"$ {new_rev:,.0f}")
    m2.metric("New Profit", f"$ {new_profit:,.0f}")
    m3.metric("Liquidity Drain", f"$ {liquidity_impact:,.0f}", delta_color="inverse")
    
    # Το Ταμείο με χρώμα ανάλογα με το αποτέλεσμα
    m4.metric("Post-Shock Cash", f"$ {remaining_liquidity:,.0f}", 
              delta=f"{remaining_liquidity - current_cash:,.0f}",
              delta_color="normal" if remaining_liquidity > 0 else "inverse")

    # 5. RESILIENCE GAUGE & ALERTS
    st.subheader("🧭 Survival Analysis")
    
    if remaining_liquidity < 0:
        st.error(f"🚨 **LIQUIDITY CRUNCH:** Το ταμείο αδυνατεί να απορροφήσει το σοκ. Απαιτούνται $ {abs(remaining_liquidity):,.0f} για επιβίωση.")
    
    # Heuristic scoring
    resilience_score = 100
    if new_profit < 0: resilience_score -= 40
    if remaining_liquidity < 0: resilience_score -= 50
    if dso_shock > 45: resilience_score -= 10
    
    resilience_score = max(0, min(100, resilience_score))
    
    fig = go.Figure(go.Indicator(
        mode = "gauge+number",
        value = resilience_score,
        gauge = {'axis': {'range': [0, 100]},
                 'bar': {'color': "white"},
                 'steps': [
                     {'range': [0, 35], 'color': "#8B0000"},
                     {'range': [35, 70], 'color': "#FFA500"},
                     {'range': [70, 100], 'color': "#228B22"}]}
    ))
    fig.update_layout(height=280, margin=dict(t=0, b=0, l=40, r=40), paper_bgcolor='rgba(0,0,0,0)', font={'color': "gray"})
    st.plotly_chart(fig, use_container_width=True)

    st.divider()
    if st.button("⬅️ Back to Control Tower", use_container_width=True):
        st.session_state.flow_step = "home"
        st.session_state.selected_tool = None
        st.rerun()
