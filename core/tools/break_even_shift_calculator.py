import streamlit as st
import plotly.graph_objects as go

def show_break_even_shift_calculator():
    s = st.session_state
    
    st.header("🛡️ Survival Simulator")
    st.info("Adjust all business levers to see how the Break-Even point shifts in real-time.")

    # 1. DATA INITIALIZATION (Ensuring all are floats to avoid type errors)
    # [2026-02-18] 365-day basis calculation
    b_price = float(s.get('input_price', 100.0))
    b_vc = float(s.get('input_vc', 60.0))
    b_volume = float(s.get('input_volume', 1000.0))
    b_fc = float(s.get('input_fc', 20000.0))
    b_debt = float(s.get('input_ads', 0.0))
    b_profit = float(s.get('target_profit_goal', 0.0))

    # 2. SCENARIO SLIDERS (Explicit float casting for min/max/value)
    st.subheader("🕹️ Simulation Controls")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("**Core Pricing**")
        sim_price = st.slider("Unit Price (€)", float(b_price * 0.5), float(b_price * 2.0), float(b_price), step=1.0)
        sim_vc = st.slider("Variable Cost (€)", float(b_vc * 0.5), float(b_vc * 2.0), float(b_vc), step=1.0)
        
    with col2:
        st.markdown("**Fixed & Obligations**")
        sim_fc = st.slider("Fixed Costs (€)", float(b_fc * 0.5), float(b_fc * 2.5), float(b_fc), step=100.0)
        sim_debt = st.slider("Loan / Leasing Service (€)", 0.0, float((b_debt + 5000) * 3), float(b_debt), step=50.0)

    with col3:
        st.markdown("**Targets & Growth**")
        sim_volume = st.slider("Current Sales Volume", float(b_volume * 0.1), float(b_volume * 3.0), float(b_volume), step=10.0)
        sim_profit = st.slider("Target Profit Goal (€)", 0.0, float((b_profit + 10000) * 3), float(b_profit), step=100.0)

    # 3. CALCULATIONS (Cold Analytical Logic)
    total_burden = sim_fc + sim_debt + sim_profit
    unit_margin = sim_price - sim_vc
    
    # New Break Even Units
    new_bep = total_burden / unit_margin if unit_margin > 0 else 0.0
    safety_margin = sim_volume - new_bep

    # 4. RESULTS DASHBOARD
    st.divider()
    res1, res2, res3 = st.columns(3)
    
    res1.metric("Survival Break-Even", f"{new_bep:,.0f} units")
    res2.metric("Total Cash Burden", f"€{total_burden:,.0f}")
    res3.metric("Volume Surplus/Deficit", f"{safety_margin:,.0f} units", 
               delta=f"{safety_margin:,.0f}", delta_color="normal" if safety_margin >= 0 else "inverse")

    # 5. VISUALIZATION (Comparison Bar Chart)
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        name="Units Needed (BEP)",
        x=["Scenario"],
        y=[new_bep],
        marker_color='#ef4444', # Red
        text=[f"{new_bep:,.0f}"],
        textposition='auto',
    ))
    
    fig.add_trace(go.Bar(
        name="Current Sales Volume",
        x=["Scenario"],
        y=[sim_volume],
        marker_color='#1E3A8A', # Blue
        text=[f"{sim_volume:,.0f}"],
        textposition='auto',
    ))

    fig.update_layout(
        title="Survival Threshold vs. Simulated Volume",
        barmode='group',
        template="plotly_white",
        height=400
    )
    
    st.plotly_chart(fig, use_container_width=True)

    # Verdict
    if unit_margin <= 0:
        st.error("🚨 UNIT MARGIN ERROR: Variable costs exceed price. No survival possible.")
    elif safety_margin < 0:
        st.error(f"⚠️ DANGER: You are {abs(safety_margin):,.0f} units below survival point.")
    else:
        st.success(f"✅ SAFE: Operating {safety_margin:,.0f} units above survival threshold.")

    # 6. NAVIGATION
    if st.button("⬅ Back to Hub", use_container_width=True):
        st.session_state.selected_tool = None
        st.rerun()
