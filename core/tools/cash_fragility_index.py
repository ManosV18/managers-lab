import streamlit as st
import plotly.graph_objects as go

def show_cash_fragility_index():
    s = st.session_state
    
    st.header("🛡️ Cash Fragility & Survival Analysis")
    st.info("Critical Link: Comparing Cash Runway against the Operational Cash Conversion Cycle (CCC).")

    # 1. FETCH & CALCULATE DATA (User Instruction [2026-02-18]: 365-day basis)
    volume = float(s.get('volume', 0))
    variable_cost = float(s.get('variable_cost', 0.0))
    fixed_costs = float(s.get('fixed_cost', 0.0)) 
    debt_service = float(s.get('annual_debt_service', 0.0)) 
    
    # Annual cash outflow includes OpEx and Debt Obligations
    annual_outflows = (volume * variable_cost) + fixed_costs + debt_service
    # Analytical safeguard: ensure daily_burn is never zero to avoid crashes
    daily_burn_rate = annual_outflows / 365 if annual_outflows > 0 else 0.00001
    
    # Working Capital Components (Synced with Home keys)
    ar_days = float(s.get('ar_days', 45.0))
    inv_days = float(s.get('inv_days', 60.0)) 
    ap_days = float(s.get('ap_days', 30.0))            
    ccc_days = ar_days + inv_days - ap_days

    # 2. LIQUIDITY POSITION
    st.subheader("1. Real-Time Liquidity Position")
    col1, col2 = st.columns(2)
    
    default_cash = s.get('opening_cash', 0.0)
    cash_on_hand = col1.number_input("Current Cash & Equivalents (€)", value=float(default_cash), step=1000.0)
    unused_credit = col2.number_input("Available Credit Lines (€)", value=0.0, step=1000.0)
    
    total_liquidity = cash_on_hand + unused_credit

    # 3. FRAGILITY CALCULATIONS (Analytical Approach)
    cash_runway = total_liquidity / daily_burn_rate
    # Fragility Index: If > 1, cash depletes before a business cycle completes.
    fragility_score = (ccc_days / cash_runway) if cash_runway > 0 else 99.0

    st.divider()

    # 4. DASHBOARD METRICS
    m1, m2, m3 = st.columns(3)
    m1.metric("Cash Runway", f"{cash_runway:.1f} Days", help="Survival window based on 365-day burn rate.")
    m2.metric("Cash Cycle (CCC)", f"{ccc_days:.1f} Days", delta="Funding Gap", delta_color="inverse")
    
    if cash_runway == 0 or total_liquidity <= 0: 
        status = "NO RUNWAY"
    elif fragility_score > 1.0: 
        status = "CRITICAL"
    elif fragility_score > 0.7: 
        status = "VULNERABLE"
    else: 
        status = "IMMUNE"
        
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
                {'range': [0, ccc_days], 'color': "#FF4B4B"}, # Dangerous: Burn exceeds cycle
                {'range': [ccc_days, ccc_days * 1.5], 'color': "#FFA500"}, # Warning: Tight buffer
                {'range': [ccc_days * 1.5, 1000], 'color': "#00CC96"}], # Safe: Robust buffer
            'threshold': {
                'line': {'color': "white", 'width': 4},
                'thickness': 0.75,
                'value': ccc_days}
        }
    ))
    fig.update_layout(height=350, template="plotly_dark", margin=dict(l=20, r=20, t=50, b=20))
    st.plotly_chart(fig, use_container_width=True)

    # 6. ANALYST'S VERDICT (Cold & Direct)
    st.subheader("2. Strategic Analytical Verdict")
    if fragility_score > 1:
        st.error(f"**Structural Deficit:** Your Runway ({cash_runway:.1f} days) is shorter than your CCC ({ccc_days:.1f} days).")
        st.write("🚨 **Insight:** The system will require external financing before it can collect cash from its own customers. Bankruptcy risk is high during rapid growth.")
    else:
        st.success(f"**Structural Buffer:** The system is anti-fragile.")
        st.write(f"✅ **Insight:** You possess a safety margin of {(cash_runway - ccc_days):.1f} days after completing the operational cycle.")

    # 7. NAVIGATION
    st.divider()
    if st.button("⬅️ Back to Control Tower", use_container_width=True):
        st.session_state.flow_step = "home"
        st.session_state.selected_tool = None
        st.rerun()
