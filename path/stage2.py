import streamlit as st
from core.engine import compute_core_metrics

def run_stage2():
    st.header("📉 Stage 2: Volume Shock Simulation")
    st.caption("Sensitivity Analysis: Assessing how sales volatility impacts Free Cash Flow.")
    st.divider()

    # 1. BASELINE CAPTURE
    # Παίρνουμε τα metrics πριν την αλλαγή για σύγκριση
    baseline_metrics = compute_core_metrics()
    baseline_fcf = baseline_metrics['fcf']
    original_vol = st.session_state.volume

    # 2. STRESS TEST CONTROL
    st.subheader("Apply Market Shock")
    st.write("Simulate a drop in sales volume (e.g., due to competition or market downturn).")
    shock_pct = st.slider("Simulated Volume Drop (%)", 0, 80, 25)
    
    # Προσωρινή εφαρμογή του σοκ στο state
    st.session_state.volume = original_vol * (1 - shock_pct/100)
    
    # Επανυπολογισμός μέσω Orchestrator
    stressed_metrics = compute_core_metrics()
    fcf_shocked = stressed_metrics['fcf']

    # 3. IMPACT ANALYSIS
    # Υπολογισμός της ελαστικότητας του FCF σε σχέση με το Volume
    delta_pct = (fcf_shocked - baseline_fcf) / abs(baseline_fcf) if baseline_fcf != 0 else 0.0

    # 4. RESULTS DISPLAY (Layout Consistency)
    st.divider()
    c1, c2 = st.columns(2)
    
    c1.metric("Original Annual FCF", f"{baseline_fcf:,.0f} €")
    c2.metric(
        label="Stressed Annual FCF", 
        value=f"{fcf_shocked:,.0f} €", 
        delta=f"{delta_pct:.1%} vs Baseline", 
        delta_color="inverse" # Κόκκινο αν πέφτει, πράσινο αν ανεβαίνει
    )

    # 5. MANAGER'S COLD INSIGHT
    st.subheader("🔬 Fragility Assessment")
    if fcf_shocked < 0:
        st.error(f"🚨 **Terminal Shock:** At a -{shock_pct}% volume drop, the enterprise enters a deficit state (Burn Rate: {abs(fcf_shocked/12):,.0f}€/mo).")
    else:
        st.success(f"✅ **Resilience Confirmed:** The system remains FCF-positive even with a -{shock_pct}% reduction in sales.")

    # 6. STATE RECOVERY (Critical!)
    # Επαναφέρουμε τον όγκο στην αρχική του τιμή για να μην επηρεαστούν τα επόμενα stages
    st.session_state.volume = original_vol

    # 7. NAVIGATION
    st.divider()
    col_prev, col_next = st.columns(2)
    
    with col_prev:
        if st.button("⬅️ Back to Stage 1", use_container_width=True):
            st.session_state.flow_step = 1
            st.rerun()
            
    with col_next:
        if st.button("Next: Liquidity Collapse (Stage 3) 🫁", type="primary", use_container_width=True):
            st.session_state.flow_step = 3
            st.rerun()
