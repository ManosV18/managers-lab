import streamlit as st
import plotly.graph_objects as go
from core.sync import sync_global_state

def show_break_even_shift_calculator():
    # 1. FETCH DATA
    metrics = sync_global_state()
    s = st.session_state
    
    st.header("🛡️ Business Survival Simulator")
    st.info("Simulate how changes in costs, pricing, and volume shift your survival threshold (Fixed Costs + Debt Service).")

    # 2. BASELINE VALUES (Analytical Logic)
    # Προσθέτουμε το Debt Service στα Fixed Costs για να βρούμε το Survival Point
    current_fixed = float(s.get('fixed_cost', 0.0)) + float(s.get('annual_debt_service', 0.0))
    current_price = float(s.get('price', 0.0))
    current_vc = float(s.get('variable_cost', 0.0))
    current_unit_cm = current_price - current_vc
    current_volume = float(s.get('volume', 0.0))
    
    # Υπολογισμός του Baseline Survival BEP (για να συγκρίνουμε όμοια πράγματα)
    current_bep = current_fixed / current_unit_cm if current_unit_cm > 0 else 0.0

    if current_unit_cm <= 0:
        st.error("🚨 Unit Margin is zero or negative. Survival point cannot be calculated.")
        return

    # 3. SHIFT PARAMETERS
    st.subheader("🛠️ Stress Scenario Sliders")
    col1, col2 = st.columns(2)
    
    with col1:
        fixed_change_pct = st.slider("Fixed Costs & Debt Change (%)", -50, 50, 0, key="be_fixed_shift")
        price_change_pct = st.slider("Price Change (%)", -30, 30, 0, key="be_price_shift")
    
    with col2:
        vc_change_pct = st.slider("Variable Cost Change (%)", -30, 30, 0, key="be_vc_shift")
        vol_change_pct = st.slider("Sales Volume Change (%)", -50, 50, 0, key="be_vol_shift")

    # 4. CALCULATIONS
    new_fixed = current_fixed * (1 + fixed_change_pct / 100)
    new_price = current_price * (1 + price_change_pct / 100)
    new_vc = current_vc * (1 + vc_change_pct / 100)
    new_unit_cm = new_price - new_vc
    new_volume = current_volume * (1 + vol_change_pct / 100)
    
    # New Survival Point
    new_bep = new_fixed / new_unit_cm if new_unit_cm > 0 else 0.0
    
    # Safety Margin
    safety_margin_units = new_volume - new_bep
    safety_margin_pct = (safety_margin_units / new_volume * 100) if new_volume > 0 else 0.0

    # 5. RESULTS DASHBOARD
    st.divider()
    m1, m2, m3 = st.columns(3)
    
    m1.metric("Survival BEP (Units)", f"{new_bep:,.0f}", 
              delta=f"{new_bep - current_bep:+.0f} units", 
              delta_color="inverse")
    
    m2.metric("Simulated Volume", f"{new_volume:,.0f}", 
              delta=f"{new_volume - current_volume:+.0f} units")
    
    m3.metric("Survival Buffer", f"{safety_margin_pct:.1f}%", 
              delta="Risk Headroom")

    # 6. VISUALIZATION
    st.subheader("📈 Survival Threshold vs. Actual Volume")
    
    fig = go.Figure()
    fig.add_trace(go.Bar(
        name="Survival Point (Units)",
        x=['Baseline', 'Simulated'],
        y=[current_bep, new_bep],
        marker_color='#EF553B'
    ))
    fig.add_trace(go.Bar(
        name="Sales Volume",
        x=['Baseline', 'Simulated'],
        y=[current_volume, new_volume],
        marker_color='#636EFA'
    ))

    fig.update_layout(
        barmode='group',
        yaxis_title="Units",
        template="plotly_dark",
        height=400,
        margin=dict(l=20, r=20, t=40, b=20)
    )
    st.plotly_chart(fig, use_container_width=True)

    # 7. ANALYST'S VERDICT
    st.subheader("🧠 Analyst's Verdict")
    if new_volume < new_bep:
        st.error(f"🚨 **NEGATIVE MARGIN:** Business cannot cover operations and debt. You are **{abs(safety_margin_units):,.0f} units** short.")
    elif safety_margin_pct < 10:
        st.warning(f"⚠️ **HIGH RISK:** Survival buffer is thin ({safety_margin_pct:.1f}%). Minor shocks will trigger cash shortfall.")
    else:
        st.success(f"✅ **RESILIENT:** Buffer at {safety_margin_pct:.1f}%. The business can absorb market shocks.")

    # 8. NAVIGATION
    st.divider()
    if st.button("Back to Library Hub", use_container_width=True):
        st.session_state.selected_tool = None
        st.rerun()
