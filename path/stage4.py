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

    st.caption("Multi-factor sensitivity analysis for structural resilience.")
    st.divider()

    # 2. SHOCK PARAMETERS (Εδώ είναι τα νέα μέτρα που ζήτησες)
    st.subheader("Shock Parameters")
    c_sh1, c_sh2 = st.columns(2)
    
    with c_sh1:
        # Μέτρο 1: Ποσότητα
        vol_shock = st.slider("Volume Contraction (%)", 0, 100, 20)
        # Μέτρο 2: Τιμή
        price_shock = st.slider("Price Erosion (%)", 0, 50, 10)
        
    with c_sh2:
        # Μέτρο 3: Μεταβλητά Έξοδα
        vc_shock = st.slider("VC Inflation (%)", 0, 50, 15)
        # Μέτρο 4: Σταθερά Έξοδα
        fc_shock = st.slider("Fixed Cost Increase (%)", 0, 50, 10)

    # 3. DETERMINISTIC CALCULATION (Cold Analysis)
    # Παίρνουμε τις καθαρές τιμές από το session_state
    b_price = float(s.get('price', 100.0))
    b_vol = float(s.get('volume', 1000.0))
    b_vc = float(s.get('variable_cost', 60.0))
    b_fc = float(s.get('fixed_cost', 20000.0))
    b_ebit = float(m.get('ebit', 0.0))

    # Εφαρμογή των Shocks
    sim_price = b_price * (1 - price_shock/100)
    sim_vol = b_vol * (1 - vol_shock/100)
    sim_vc = b_vc * (1 + vc_shock/100)
    sim_fc = b_fc * (1 + fc_shock/100)

    # Υπολογισμός νέου EBIT
    sim_ebit = ((sim_price - sim_vc) * sim_vol) - sim_fc
    delta_ebit = sim_ebit - b_ebit

    # 4. RESULTS UI
    st.divider()
    st.subheader("Simulation Results")
    res1, res2, res3 = st.columns(3)
    
    res1.metric("Simulated EBIT", f"€ {sim_ebit:,.0f}", delta=f"€ {delta_ebit:,.0f}", delta_color="inverse")
    
    sim_margin = (sim_price - sim_vc) / sim_price if sim_price > 0 else 0
    res2.metric("Simulated Margin", f"{sim_margin:.1%}")
    
    status = "RESILIENT" if sim_ebit > 0 else "VULNERABLE"
    color = "green" if status == "RESILIENT" else "red"
    res3.markdown(f"**Status:**\n### :{color}[{status}]")

    # 5. NAVIGATION
    st.divider()
    c_nav1, c_nav2 = st.columns(2)
    if c_nav1.button("⬅️ Back to Stage 3", use_container_width=True):
        st.session_state.flow_step = "stage3"
        st.rerun()
    if c_nav2.button("Proceed to Stage 5 ➡️", use_container_width=True, type="primary"):
        st.session_state.flow_step = "stage5"
        st.rerun()
