import streamlit as st
from core.sync import sync_global_state

def run_stage3():
    st.header("💧 Stage 3: Liquidity & Working Capital Physics")
    
    m = sync_global_state()
    s = st.session_state

    st.caption("Analyzing the cash conversion cycle and the structural liquidity of the model.")
    st.divider()

    # Secure Variable Retrieval
    opening_cash = s.get('opening_cash', 0.0)
    wc_req = m.get('wc_requirement', 0.0)
    cash_reserve = m.get('cash_reserve', 0.0)
    ccc = m.get('ccc', 0)

    # 1. Vital Metrics
    c1, c2, c3 = st.columns(3)
    c1.metric("Cash Conversion Cycle", f"{ccc} Days", help="Time between spending cash and receiving it.")
    c2.metric("WC Requirement", f"{wc_req:,.0f} €", delta=f"{wc_req:,.0f}", delta_color="inverse")
    c3.metric("Net Cash Reserve", f"{cash_reserve:,.0f} €")

    # 2. Runway Analysis
    st.subheader("Survival Runway")
    runway = m.get('runway_months', 0.0)
    
    if runway >= 100:
        st.success("✅ **STABLE:** Positive Cash Flow. Runway is effectively infinite.")
    else:
        st.warning(f"⚠️ **BURN RATE:** The system exhausts liquidity in {runway:.1f} months.")
        st.progress(min(runway/12, 1.0))

    

    # 3. Navigation
    st.divider()
    col_prev, col_next = st.columns(2)
    with col_prev:
        if st.button("⬅️ Back to Stage 2"):
            st.session_state.flow_step = "stage2"
            st.rerun()
    with col_next:
        if st.button("Proceed to Stage 4 ➡️"):
            st.session_state.flow_step = "stage4"
            st.rerun()
