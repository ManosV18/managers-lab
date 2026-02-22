import streamlit as st
import plotly.graph_objects as go
from core.engine import compute_core_metrics

def show_break_even_shift_calculator():
    st.header("⚖️ Break-Even Shift Analysis")
    st.caption("Strategic Simulation: Evaluate how structural changes shift your survival anchor.")

    # 1. FETCH SYNCED DATA
    # Αντλούμε τα δεδομένα από το κεντρικό state μέσω του engine
    metrics = compute_core_metrics()
    
    # 2. SIMULATION CONTROLS
    st.subheader("🛠️ Strategic Stress Test")
    st.info("Simulate shifts without affecting the baseline. Use the button at the bottom to commit changes.")

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("**Price & Volume**")
        # Χρησιμοποιούμε sliders για "τι θα γινόταν αν" (simulation)
        price_shift = st.slider("Simulate Price Change (%)", -30, 50, 0)
        vol_shift = st.slider("Simulate Volume Change (%)", -30, 50, 0)
        
    with col2:
        st.markdown("**Cost Structure**")
        fc_shift = st.slider("Simulate Fixed Cost Change (%)", -30, 50, 0)
        vc_shift = st.slider("Simulate Var. Cost Change (%)", -30, 50, 0)

    # 3. ANALYTICAL CALCULATIONS (Stressed Model)
    s_price = st.session_state.price * (1 + price_shift/100)
    s_vol = st.session_state.volume * (1 + vol_shift/100)
    s_fc = st.session_state.fixed_cost * (1 + fc_shift/100)
    s_vc = st.session_state.variable_cost * (1 + vc_shift/100)
    
    s_unit_cont = s_price - s_vc
    s_bep = s_fc / s_unit_cont if s_unit_cont > 0 else 0
    s_profit = (s_unit_cont * s_vol) - s_fc - st.session_state.annual_loan_payment - st.session_state.liquidity_drain_annual

    # 4. IMPACT VISUALIZATION
    st.divider()
    c1, c2, c3 = st.columns(3)
    
    # Σύγκριση με το τρέχον Profit
    c1.metric("Simulated Profit", f"{s_profit:,.2f} €", 
              delta=f"{s_profit - metrics['net_profit']:,.2f} €")
    
    # Μετατόπιση του Break-Even
    bep_delta = s_bep - metrics['survival_bep']
    c2.metric("Simulated Survival BEP", f"{s_bep:,.0f} u", 
              delta=f"{bep_delta:,.0f} u", delta_color="inverse")
    
    # Margin of Safety
    safety_margin = ((s_vol / s_bep) - 1) * 100 if s_bep > 0 else 0
    c3.metric("Survival Buffer", f"{safety_margin:.1f}%")

    # 5. BREAK-EVEN CHART
    
    
    # Οπτικοποίηση της διαφοράς
    labels = ['Baseline BEP', 'Simulated BEP']
    values = [metrics['survival_bep'], s_bep]
    
    fig = go.Figure(data=[go.Bar(x=labels, y=values, marker_color=['#636EFA', '#EF553B'])])
    fig.update_layout(title="Break-Even Threshold Shift", height=300, template="plotly_dark")
    st.plotly_chart(fig, use_container_width=True)

    # 6. ACTION BRIDGE
    st.divider()
    if st.button("🚨 Overwrite Baseline with Simulated Values", type="secondary"):
        st.session_state.price = s_price
        st.session_state.volume = s_vol
        st.session_state.fixed_cost = s_fc
        st.session_state.variable_cost = s_vc
        st.success("Global Configuration Updated. All stages have been recalibrated.")
        st.rerun()
