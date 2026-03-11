import streamlit as st
import plotly.graph_objects as go

def show_break_even_shift_calculator():
    s = st.session_state
    
    st.header("🛡️ Survival Simulator")
    st.info("Adjust all business levers to see how the Break-Even point shifts in real-time.")

    # 1. DATA INITIALIZATION (Αποφυγή μηδενικών)
    # Παίρνουμε τις τιμές από το Global Engine ή βάζουμε defaults
    b_price = float(s.get('input_price', 100.0)) if float(s.get('input_price', 0)) > 0 else 100.0
    b_vc = float(s.get('input_vc', 60.0)) if float(s.get('input_vc', 0)) > 0 else 60.0
    b_volume = float(s.get('input_volume', 1000)) if float(s.get('input_volume', 0)) > 0 else 1000
    b_fc = float(s.get('input_fc', 20000.0))
    b_debt = float(s.get('input_ads', 0.0))
    b_profit = float(s.get('target_profit_goal', 0.0))

    # 2. SCENARIO SLIDERS (Όλες οι μπάρες που ζήτησες)
    st.subheader("🕹️ Simulation Controls")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("**Core Pricing**")
        sim_price = st.slider("Unit Price (€)", b_price * 0.5, b_price * 1.5, b_price)
        sim_vc = st.slider("Variable Cost (€)", b_vc * 0.5, b_vc * 1.5, b_vc)
        
    with col2:
        st.markdown("**Fixed & Obligations**")
        sim_fc = st.slider("Fixed Costs (€)", b_fc * 0.5, b_fc * 2.0, b_fc)
        sim_debt = st.slider("Loan / Leasing Service (€)", 0.0, (b_debt + 10000) * 2, b_debt)

    with col3:
        st.markdown("**Targets & Growth**")
        sim_volume = st.slider("Current Sales Volume", b_volume * 0.5, b_volume * 2.0, b_volume)
        sim_profit = st.slider("Target Profit Goal (€)", 0.0, (b_profit + 10000) * 2, b_profit)

    # 3. CALCULATIONS (Cold Analytical Logic)
    # Total Burden = Fixed Costs + Debt + Desired Profit
    total_burden = sim_fc + sim_debt + sim_profit
    unit_margin = sim_price - sim_vc
    
    # New Break Even Units
    if unit_margin > 0:
        new_bep = total_burden / unit_margin
    else:
        new_bep = 0 # Αποφυγή διαίρεσης με το μηδέν αν το margin είναι αρνητικό

    safety_margin = sim_volume - new_bep
    status_color = "green" if safety_margin > 0 else "red"

    # 4. RESULTS DASHBOARD
    st.divider()
    res1, res2, res3 = st.columns(3)
    
    res1.metric("Survival Break-Even", f"{new_bep:,.0f} units")
    res2.metric("Total Cash Burden", f"€{total_burden:,.0f}")
    res3.metric("Volume Surplus/Deficit", f"{safety_margin:,.0f} units", 
               delta=f"{safety_margin:,.0f}", delta_color="normal" if safety_margin > 0 else "inverse")

    # 5. VISUALIZATION (Comparison Bar Chart)
    fig = go.Figure()
    
    # Bar for Required Units vs Actual Units
    fig.add_trace(go.Bar(
        name="Units Needed (BEP)",
        x=["Comparison"],
        y=[new_bep],
        marker_color='red',
        text=[f"{new_bep:,.0f}"],
        textposition='auto',
    ))
    
    fig.add_trace(go.Bar(
        name="Current Sales Volume",
        x=["Comparison"],
        y=[sim_volume],
        marker_color='royalblue',
        text=[f"{sim_volume:,.0f}"],
        textposition='auto',
    ))

    fig.update_layout(
        title="Survival Threshold vs. Current Capacity",
        barmode='group',
        template="plotly_white",
        height=400,
        yaxis_title="Quantity (Units)"
    )
    
    st.plotly_chart(fig, use_container_width=True)

    # Verdict
    if safety_margin < 0:
        st.error(f"⚠️ **DANGER:** You need {abs(safety_margin):,.0f} more units to cover your total cash burden.")
    else:
        st.success(f"✅ **SAFE:** You are operating {safety_margin:,.0f} units above your survival threshold.")

    # 6. NAVIGATION
    if st.button("⬅ Back to Hub"):
        st.session_state.selected_tool = None
        st.rerun()
