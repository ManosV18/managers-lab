import streamlit as st
import plotly.graph_objects as go
from core.engine import compute_core_metrics

def show_cash_fragility_index():
    st.header("🛡️ Cash Fragility & Survival Analysis")
    st.info("Analyze business resilience by linking cash reserves to the Cash Conversion Cycle.")

    # 1. FETCH & CALCULATE DATA SAFELY
    metrics = compute_core_metrics()
    
    # Calculate Total Annual Costs dynamically since 'total_costs' key is missing
    volume = st.session_state.get('volume', 0)
    variable_cost = st.session_state.get('variable_cost', 0.0)
    fixed_costs = st.session_state.get('fixed_costs', 0.0)
    
    annual_costs = (volume * variable_cost) + fixed_costs
    daily_burn_rate = annual_costs / 365
    
    # Pull Cash Conversion Cycle components
    ar_days = st.session_state.get('ar_days', 60.0)
    inv_days = st.session_state.get('global_inventory_dsi', 45.0)
    ap_days = st.session_state.get('payables_days', 30.0)
    ccc_days = ar_days + inv_days - ap_days

    # 2. USER INPUTS FOR CASH RESERVES
    st.subheader("1. Liquidity Position")
    col1, col2 = st.columns(2)
    
    # Provide a sensible default for cash (e.g., 10% of annual costs)
    cash_on_hand = col1.number_input("Current Cash & Equivalents (€)", value=float(annual_costs * 0.1) if annual_costs > 0 else 50000.0, step=5000.0)
    unused_credit = col2.number_input("Unused Credit Lines / Overdraft (€)", value=0.0, step=5000.0)
    
    total_liquidity = cash_on_hand + unused_credit

    # 3. CALCULATE FRAGILITY METRICS
    cash_runway = total_liquidity / daily_burn_rate if daily_burn_rate > 0 else 0
    
    # Fragility Score: Relation between Runway and CCC
    fragility_score = (ccc_days / cash_runway) if cash_runway > 0 else 0

    st.divider()

    # 4. DASHBOARD METRICS
    m1, m2, m3 = st.columns(3)
    m1.metric("Cash Runway", f"{cash_runway:.1f} Days", help="How many days you can survive with zero inflows.")
    m2.metric("Cash Conversion Cycle", f"{ccc_days:.1f} Days", delta="Funding Gap", delta_color="inverse")
    
    # Analytical Status Logic
    if cash_runway == 0:
        status, color = "NO CASH", "red"
    elif fragility_score > 1.2:
        status, color = "CRITICAL", "red"
    elif fragility_score > 0.8:
        status, color = "WARNING", "orange"
    else:
        status, color = "SAFE", "green"
        
    m3.metric("Fragility Status", status, delta=f"Score: {fragility_score:.2f}", delta_color="inverse")

    # 5. VISUAL SURVIVAL GAUGE
    fig = go.Figure(go.Indicator(
        mode = "gauge+number",
        value = cash_runway,
        title = {'text': "Survival Days (Runway)"},
        gauge = {
            'axis': {'range': [None, max(180, ccc_days * 2)]},
            'steps': [
                {'range': [0, ccc_days], 'color': "#FF4B4B"},
                {'range': [ccc_days, ccc_days * 1.5], 'color': "#FFA500"},
                {'range': [ccc_days * 1.5, 1000], 'color': "#00CC96"}],
            'threshold': {
                'line': {'color': "white", 'width': 4},
                'value': ccc_days}
        }
    ))
    fig.update_layout(template="plotly_dark", height=350)
    st.plotly_chart(fig, use_container_width=True)

    

    # 6. STRATEGIC VERDICT
    st.subheader("2. Strategic Analytical Verdict")
    
    if fragility_score > 1:
        st.error(f"""
        **Cold Analysis:** Your Cash Runway ({cash_runway:.1f} days) is shorter than your Cash Conversion Cycle ({ccc_days:.1f} days). 
        This indicates a structural liquidity deficit. You are relying on external financing or extreme vendor stretching to stay afloat.
        """)
    else:
        st.success(f"""
        **Cold Analysis:** Your liquidity position is robust. The business can self-finance a full cash cycle and still maintain a safety buffer of {(cash_runway - ccc_days):.1f} days.
        """)

    # 7. SHOCK TEST
    st.subheader("3. Resilience Stress Test")
    cost_surge = st.slider("Scenario: Sudden Increase in Operating Costs (%)", 0, 50, 20)
    stressed_runway = total_liquidity / (daily_burn_rate * (1 + cost_surge/100)) if daily_burn_rate > 0 else 0
    
    st.warning(f"Under a {cost_surge}% cost surge, your survival window shrinks to **{stressed_runway:.1f} days**.")

if __name__ == "__main__":
    show_cash_fragility_index()
