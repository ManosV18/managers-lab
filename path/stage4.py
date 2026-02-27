import streamlit as st
from core.sync import sync_global_state

def run_stage4():
    st.header("🌪️ Stage 4: Strategic Stress Testing")
    
    # 1. Secure Bridge
    m = sync_global_state()
    s = st.session_state

    if not m:
        st.warning("⚠️ Baseline not locked. Please return to Stage 0.")
        return

    st.caption("Analytical focus: Multi-factor sensitivity and margin volatility analysis.")
    st.divider()

    # 2. SHOCK PARAMETERS (Δυνατότητα για +/- μεταβολές)
    st.subheader("Scenario Parameters (% Change)")
    c_sh1, c_sh2 = st.columns(2)
    
    with c_sh1:
        # Μεταβολή Ποσότητας & Τιμής (+/-)
        vol_change = st.slider("Volume Change (%)", -50, 50, -20, help="Positive = Growth, Negative = Contraction")
        price_change = st.slider("Price Change (%)", -50, 50, -10, help="Positive = Premium increase, Negative = Discounting")
        
    with c_sh2:
        # Μεταβολή Variable & Fixed Cost (+/-)
        vc_change = st.slider("Variable Cost Change (%)", -50, 50, 15, help="Positive = Inflation, Negative = Efficiency gains")
        fc_change = st.slider("Fixed Cost Change (%)", -50, 50, 10, help="Positive = Expansion/Overheads, Negative = Cost cutting")

    # 3. DETERMINISTIC CALCULATION (Cold Analysis)
    # Baseline Values
    b_price = float(s.get('price', 100.0))
    b_vol = float(s.get('volume', 1000.0))
    b_vc = float(s.get('variable_cost', 60.0))
    b_fc = float(s.get('fixed_cost', 20000.0))
    b_ebit = float(m.get('ebit', 0.0))

    # Applied Changes (Simulated Values)
    sim_price = b_price * (1 + price_change/100)
    sim_vol = b_vol * (1 + vol_change/100)
    sim_vc = b_vc * (1 + vc_change/100)
    sim_fc = b_fc * (1 + fc_change/100)

    # Simulated EBIT Formula
    sim_ebit = ((sim_price - sim_vc) * sim_vol) - sim_fc
    delta_ebit = sim_ebit - b_ebit

    # 4. RESULTS UI
    st.divider()
    st.subheader("Simulation Results")
    res1, res2, res3 = st.columns(3)
    
    # EBIT Impact
    res1.metric("Simulated EBIT", f"€ {sim_ebit:,.0f}", delta=f"€ {delta_ebit:,.0f}", delta_color="normal")
    
    # Simulated Margin
    sim_margin = (sim_price - sim_vc) / sim_price if sim_price > 0 else 0
    base_margin = (b_price - b_vc) / b_price if b_price > 0 else 0
    res2.metric("Simulated Margin", f"{sim_margin:.1%}", delta=f"{(sim_margin - base_margin):.1%}")
    
    # System Status
    if sim_ebit > b_ebit:
        status, color = "OPTIMIZED", "green"
    elif sim_ebit > 0:
        status, color = "RESILIENT", "blue"
    else:
        status, color = "VULNERABLE", "red"
        
    res3.markdown(f"**System Status:**\n### :{color}[{status}]")

    # 5. VISUAL IMPACT ANALYSIS
    st.write(f"**EBIT Sensitivity Mapping:**")
    if b_ebit != 0:
        impact_pct = (delta_ebit / abs(b_ebit))
        st.progress(min(max(abs(impact_pct)/2, 0.0), 1.0)) # Normalized view
        st.caption(f"The simulated changes represent a {impact_pct:+.1%} variance from baseline EBIT.")

    # 6. NAVIGATION
    st.divider()
    c_nav1, c_nav2 = st.columns(2)
    if c_nav1.button("⬅️ Back to Stage 3", use_container_width=True):
        st.session_state.flow_step = "stage3"
        st.rerun()
    if c_nav2.button("Proceed to Stage 5 ➡️", use_container_width=True, type="primary"):
        st.session_state.flow_step = "stage5"
        st.rerun()
