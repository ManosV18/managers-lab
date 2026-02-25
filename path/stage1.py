import streamlit as st
from core.sync import sync_global_state

def run_stage1():
    st.header("⚖️ Stage 1: Operating Leverage & Break-Even Analysis")
    
    # 1. FETCH DATA
    m = sync_global_state()
    s = st.session_state

    st.caption("Analyzing the structural sensitivity of EBIT relative to volume fluctuations.")
    st.divider()

    # 2. KPIs
    c1, c2, c3 = st.columns(3)
    
    bep = m.get('survival_bep', 0.0)
    ebit = m.get('ebit', 0.0)
    vol = s.get('volume', 0)
    
    c1.metric("Survival BEP", f"{bep:,.0f} Units", help="Volume required to cover all fixed costs and debt.")
    
    safety_margin = ((vol - bep) / vol) if vol > 0 else 0
    c2.metric("Margin of Safety", f"{safety_margin:.1%}", 
              delta="Secure" if safety_margin > 0.2 else "Risk",
              delta_color="normal" if safety_margin > 0.2 else "inverse")
    
    c3.metric("Annual EBIT", f"{ebit:,.0f} €")

    # 3. LEVERAGE INSIGHTS
    st.subheader("Leverage Metrics")
    c_margin = m.get('contribution_margin', 0.0)
    dol = (c_margin / ebit) if ebit > 0 else 0
    
    st.write(f"**Degree of Operating Leverage (DOL):** {dol:.2f}")
    st.info(f"Analytical Mandate: A 1% change in sales will result in a {dol:.2f}% change in EBIT.")

    

    # 4. NAVIGATION
    st.divider()
    col_prev, col_next = st.columns(2)
    with col_prev:
        if st.button("⬅️ Back to Stage 0"):
            st.session_state.flow_step = "stage0"
            st.rerun()
    with col_next:
        if st.button("Proceed to Stage 2 ➡️"):
            st.session_state.flow_step = "stage1" # Safety: ensuring string format
            st.session_state.flow_step = "stage2"
            st.rerun()
