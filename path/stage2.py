import streamlit as st
from core.engine import compute_core_metrics

def run_stage2():
    st.header("📉 Stage 2: Volume Shock Simulation")
    st.caption("Stress testing survival against market volatility and revenue collapse.")

    # 1. Shock Input
    st.subheader("Simulate Market Crisis")
    shock_pct = st.slider("Simulated Volume Drop (%)", 0, 80, 25, help="How much sales volume is lost?")
    
    # 2. Recompute for the Shock
    original_vol = st.session_state.volume
    st.session_state.volume = original_vol * (1 - shock_pct/100)
    
    metrics = compute_core_metrics()
    fcf = metrics.get('fcf', 0.0)
    
    # 3. Display Impact
    st.divider()
    c1, c2 = st.columns(2)
    c1.metric("Stressed Volume", f"{st.session_state.volume:,.0f} Units")
    
    status_color = "normal" if fcf >= 0 else "inverse"
    c2.metric("Stressed Annual FCF", f"{fcf:,.0f} €", delta="CRITICAL" if fcf < 0 else "STABLE", delta_color=status_color)

    # 4. Elasticity of Survival
    st.subheader("⚠️ Elasticity Analysis")
    if fcf < 0:
        st.error(f"💀 **Collapse Point:** At a {shock_pct}% drop, the system enters a death spiral (Negative FCF).")
    else:
        st.success(f"🛡️ **Resilience:** The system absorbs a {shock_pct}% shock and remains cash-flow positive.")

    # Επαναφορά Baseline
    st.session_state.volume = original_vol

    st.divider()
    nav1, nav2 = st.columns(2)
    with nav1:
        if st.button("⬅️ Back to Stage 1"):
            st.session_state.flow_step = 1
            st.rerun()
    with nav2:
        if st.button("Next: Stage 3 (Liquidity Timeline) 🫁", type="primary"):
            st.session_state.flow_step = 3
            st.rerun()
