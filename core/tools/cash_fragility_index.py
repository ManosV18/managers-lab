import streamlit as st
import plotly.graph_objects as go
from core.sync import sync_global_state 

def show_cash_fragility_index():
    st.header("🛡️ Cash Fragility & Survival Analysis")
    st.info("Critical Link: Comparing Cash Runway against the Operational Cash Conversion Cycle (CCC).")

    # 1. FETCH & CALCULATE DATA FROM BASELINE
    metrics = sync_global_state()
    s = st.session_state
    
    # Financial extraction
    volume = float(s.get('volume', 0))
    variable_cost = float(s.get('variable_cost', 0.0))
    fixed_costs = float(s.get('fixed_cost', 0.0)) 
    
    annual_costs = (volume * variable_cost) + fixed_costs
    daily_burn_rate = annual_costs / 365 if annual_costs > 0 else 0.1
    
    # Sync CCC components
    ar_days = float(s.get('ar_days', 60.0))
    inv_days = float(s.get('inventory_days', 45.0)) 
    ap_days = float(s.get('ap_days', 30.0))          
    ccc_days = ar_days + inv_days - ap_days

    # 2. LIQUIDITY POSITION
    st.subheader("1. Real-Time Liquidity Position")
    col1, col2 = st.columns(2)
    
    # Source cash from session state (Stage 0 Cash)
    default_cash = s.get('opening_cash', annual_costs * 0.1)
    cash_on_hand = col1.number_input("Current Cash & Equivalents (€)", value=float(default_cash), step=5000.0)
    unused_credit = col2.number_input("Available Credit Lines / Overdraft (€)", value=0.0, step=5000.0)
    
    total_liquidity = cash_on_hand + unused_credit

    # 3. FRAGILITY CALCULATIONS
    cash_runway = total_liquidity / daily_burn_rate if daily_burn_rate > 0 else 0
    # Fragility Index: If > 1, the company burns cash faster than it collects it.
    fragility_score = (ccc_days / cash_runway) if cash_runway > 0 else 99.0

    st.divider()

    # 4. DASHBOARD METRICS
    m1, m2, m3 = st.columns(3)
    m1.metric("Cash Runway", f"{cash_runway:.1f} Days", help="Survival window if revenue drops to zero.")
    m2.metric("Cash Cycle (CCC)", f"{ccc_days:.1f} Days", delta="Funding Gap", delta_color="inverse")
    
    if cash_runway == 0:
        status, color = "NO RUNWAY", "red"
    elif fragility_score > 1.0:
        status, color = "CRITICAL", "red"
    elif fragility_score > 0.7:
        status, color = "VULNERABLE", "orange"
    else:
        status, color = "IMMUNE", "green"
        
    m3.metric("Fragility Status", status, delta=f"Index: {fragility_score:.2f}", delta_color="inverse" if fragility_score > 1 else "normal")

    # 5. SURVIVAL GAUGE
    
    fig = go.Figure(go.Indicator(
        mode = "gauge+number",
        value = cash_runway,
        title = {'text': "Survival Window (Days)"},
        gauge = {
            'axis': {'range': [None, max(180, ccc_days * 2)]},
            'bar': {'color': "white"},
            'steps': [
                {'range': [0, ccc_days], 'color': "#FF4B4B"}, # Red zone: Burning faster than collecting
                {'range': [ccc_days, ccc_days * 1.5], 'color': "#FFA500"}, # Warning zone
                {'range': [ccc_days * 1.5, 1000], 'color': "#00CC96"}], # Safe zone
            'threshold': {
                'line': {'color': "yellow", 'width': 5},
                'value': ccc_days}
        }
    ))
    fig.update_layout(template="plotly_dark", height=350, margin=dict(l=20, r=20, t=50, b=20))
    st.plotly_chart(fig, use_container_width=True)

    # 6. ANALYTICAL VERDICT
    st.subheader("2. Strategic Analytical Verdict")
    if fragility_score > 1:
        st.error(f"**Structural Deficit:** Your Runway ({cash_runway:.1f} days) is shorter than your CCC ({ccc_days:.1f} days). The system is mathematically guaranteed to hit a liquidity wall unless external financing is secured.")
    else:
        st.success(f"**Structural Buffer:** The system is anti-fragile. You can self-finance a full operational cycle with a safety margin of {(cash_runway - ccc_days):.1f} days.")

    # 7. RESILIENCE STRESS TEST
    st.divider()
    st.subheader("3. Operating Stress Test")
    cost_surge = st.slider("Scenario: Sudden Fixed/Variable Cost Spike (%)", 0, 50, 20)
    stressed_runway = total_liquidity / (daily_burn_rate * (1 + cost_surge/100))
    
    st.warning(f"In a {cost_surge}% spike scenario, your survival window collapses to **{stressed_runway:.1f} days**.")

    if st.button("⬅️ Back to Library"):
        st.session_state.selected_tool = None
        st.rerun()
