import streamlit as st
from core.sync import sync_global_state

def run_stage4():
    st.header("🌪️ Stage 4: Strategic Stress Testing")
    
    # 1. FETCH DATA (Secure Bridge)
    m = sync_global_state()
    s = st.session_state

    if not m:
        st.warning("⚠️ Please lock the baseline in Stage 0 to perform stress testing.")
        return

    st.caption("Evaluating structural resilience against multi-factor exogenous shocks.")
    st.divider()

    # 2. SHOCK PARAMETERS (UI Sliders)
    st.subheader("Shock Parameters")
    c_sh1, c_sh2 = st.columns(2)
    
    with c_sh1:
        vol_shock = st.slider("Volume Contraction (%)", 0, 100, 20, help="Reduction in units sold.")
        price_shock = st.slider("Price Erosion (%)", 0, 50, 10, help="Decrease in unit selling price.")
        
    with c_sh2:
        cost_vc_shock = st.slider("VC Inflation (%)", 0, 50, 15, help="Increase in Variable Costs (Materials, Labor).")
        cost_fc_shock = st.slider("Fixed Cost Increase (%)", 0, 50, 10, help="Increase in Fixed Costs (Rent, Energy, Admin).")

    # 3. SIMULATION LOGIC (Cold Analytical Calculation)
    # Baseline Values
    b_price = float(s.get('price', 0.0))
    b_vol = float(s.get('volume', 0.0))
    b_vc = float(s.get('variable_cost', 0.0))
    b_fc = float(s.get('fixed_cost', 0.0))
    b_ebit = float(m.get('ebit', 0.0))

    # Simulated Values
    sim_price = b_price * (1 - price_shock/100)
    sim_vol = b_vol * (1 - vol_shock/100)
    sim_vc = b_vc * (1 + cost_vc_shock/100)
    sim_fc = b_fc * (1 + cost_fc_shock/100)

    # Formula: (Sim Price - Sim VC) * Sim Volume - Sim Fixed Costs
    sim_ebit = ((sim_price - sim_vc) * sim_vol) - sim_fc
    delta_ebit = sim_ebit - b_ebit

    # 4. SIMULATION RESULTS UI
    st.divider()
    st.subheader("Simulation Results")
    
    res1, res2, res3 = st.columns(3)
    
    # EBIT Impact
    res1.metric("Simulated EBIT", f"€ {sim_ebit:,.0f}", delta=f"€ {delta_ebit:,.0f}", delta_color="inverse")
    
    # Margin Impact
    sim_margin = (sim_price - sim_vc) / sim_price if sim_price > 0 else 0
    base_margin = (b_price - b_vc) / b_price if b_price > 0 else 0
    res2.metric("Simulated Margin", f"{sim_margin:.1%}", delta=f"{(sim_margin - base_margin):.1%}", delta_color="inverse")
    
    # Resilience Status
    status = "RESILIENT" if sim_ebit > 0 else "VULNERABLE"
    color = "green" if status == "RESILIENT" else "red"
    res3.markdown(f"**System Status under Stress:**\n### :{color}[{status}]")

    # 5. VISUAL ANALYSIS (Progress to Cash Wall)
    st.write("**EBIT Erosion Analysis:**")
    # Πόσο % του αρχικού EBIT χάθηκε;
    erosion_pct = abs(delta_ebit / b_ebit) if b_ebit != 0 else 1.0
    st.progress(min(max(erosion_pct, 0.0), 1.0))
    st.caption(f"The simulation indicates a {erosion_pct:.1%} erosion of baseline EBIT.")

    # 6. NAVIGATION
    st.divider()
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("⬅️ Back to Stage 3", use_container_width=True):
            st.session_state.flow_step = "stage3"
            st.rerun()
            
    with col2:
        if st.button("Proceed to Stage 5 ➡️", use_container_width=True, type="primary"):
            st.session_state.flow_step = "stage5"
            st.rerun()
