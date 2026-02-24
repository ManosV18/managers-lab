import streamlit as st
from core.engine import compute_core_metrics

def run_stage2():
    st.header("📉 Stage 2: Volume Shock Simulation")
    st.caption("Sensitivity Analysis: Assessing how sales volatility impacts Free Cash Flow.")

    # 1. Baseline Capture
    baseline_metrics = compute_core_metrics()
    baseline_fcf = baseline_metrics['fcf']
    original_vol = st.session_state.volume

    # 2. Stress Test Control
    st.subheader("Apply Stress Test")
    shock_pct = st.slider("Simulated Volume Drop (%)", 0, 80, 25)
    
    # Apply temporary shock
    st.session_state.volume = original_vol * (1 - shock_pct/100)
    stressed_metrics = compute_core_metrics()
    fcf_shocked = stressed_metrics['fcf']

    # 3. Elasticity Calculation
    delta_pct = (fcf_shocked - baseline_fcf) / abs(baseline_fcf) if baseline_fcf != 0 else 0.0

    # 4. Results Display (Layout Consistency)
    st.divider()
    c1, c2 = st.columns(2)
    
    c1.metric("Original Annual FCF", f"{baseline_fcf:,.0f} €")
    c2.metric(
        label="Stressed Annual FCF", 
        value=f"{fcf_shocked:,.0f} €", 
        delta=f"{delta_pct:.1%} vs Baseline", 
        delta_color="inverse"
    )

    

    # 5. Manager Insight
    if fcf_shocked < 0:
        st.error(f"🚨 **Terminal Shock:** Burn rate of {abs(fcf_shocked):,.0f}€ detected at -{shock_pct}% volume.")
    else:
        st.success(f"✅ **Resilient:** Positive FCF maintained at {fcf_shocked:,.0f}€.")

    # 6. State Recovery
    st.session_state.volume = original_vol

    st.divider()
    if st.button("Next: Liquidity Collapse (Stage 3) 🫁", type="primary", use_container_width=True):
        st.session_state.flow_step = 3
        st.rerun()
