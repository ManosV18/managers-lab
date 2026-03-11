import streamlit as st
import plotly.graph_objects as go
from core.sync import sync_global_state

def show_break_even_shift_calculator():
    metrics = sync_global_state()
    s = st.session_state
    
    st.header("🛡️ Cash-Flow Survival Simulator")
    
    # 1. PARAMETERS FROM ENGINE
    base_fixed = float(s.get('fixed_cost', 0.0))
    base_debt = float(s.get('annual_debt_service', 0.0))
    base_profit = float(s.get('target_profit_goal', 0.0))
    current_price = float(s.get('price', 0.0))
    current_vc = float(s.get('variable_cost', 0.0))
    current_unit_cm = current_price - current_vc

    # 2. SCENARIO SLIDERS
    st.subheader("🕹️ Scenario Sliders")
    c1, c2 = st.columns(2)
    with c1:
        add_debt = st.slider("Additional Debt/Leasing Service (€)", 0, 50000, 0)
        target_profit_slider = st.slider("Adjust Target Profit Goal (€)", 0, 100000, int(base_profit))
    with c2:
        price_shift = st.slider("Price Adjustment (%)", -20, 20, 0)
        fc_shift = st.slider("Fixed Costs Shift (%)", -20, 20, 0)

    # 3. NEW CALCULATIONS
    new_price = current_price * (1 + price_shift / 100)
    new_fixed = (base_fixed * (1 + fc_shift / 100)) + base_debt + add_debt + target_profit_slider
    new_unit_cm = new_price - current_vc
    
    new_bep = new_fixed / new_unit_cm if new_unit_cm > 0 else 0

    # 4. RESULTS
    st.divider()
    res1, res2 = st.columns(2)
    res1.metric("New Cash Break-Even", f"{new_bep:,.0f} units")
    res2.metric("Total Cash Burden", f"€{new_fixed:,.0f}", help="Fixed + Debt + Target Profit")

    # 5. VISUALIZATION
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=[0, new_bep * 1.5], y=[new_fixed, new_fixed], name="Total Cash Burden", line=dict(color='red', dash='dash')))
    st.plotly_chart(fig)

    if st.button("⬅ Back to Hub"):
        st.session_state.selected_tool = None
        st.rerun()
