import streamlit as st
from core.sync import sync_global_state

def run_stage2():
    st.header("💳 Stage 2: Capital Structure & Debt Sustainability")
    
    # 1. FETCH DATA
    m = sync_global_state()
    s = st.session_state

    st.caption("Evaluating the cost of capital and the system's ability to service financial obligations.")
    st.divider()

    # 2. FINANCIAL DATA
    c1, c2, c3 = st.columns(3)
    
    # Secure access using .get()
    wacc = s.get('wacc', 0.15)
    debt_service = s.get('annual_loan_payment', 0.0)
    ebit = m.get('ebit', 0.0)
    
    c1.metric("WACC", f"{wacc:.1%}", help="Weighted Average Cost of Capital")
    c2.metric("Annual Debt Load", f"{debt_service:,.0f} €")
    
    dscr = (ebit / debt_service) if debt_service > 0 else 5.0
    c3.metric("DSCR", f"{dscr:.2f}x", 
              delta="Optimal" if dscr > 1.25 else "Distressed",
              delta_color="normal" if dscr > 1.25 else "inverse")

    # 3. ANALYSIS
    st.subheader("Solvency Assessment")
    if dscr < 1.0:
        st.error("🚨 **CRITICAL FAIL:** Operating profit is insufficient to cover debt. System is insolvent without external funding.")
    elif dscr < 1.25:
        st.warning("⚠️ **VULNERABILITY:** Minimal cushion for error. Cash flow volatility may lead to default.")
    else:
        st.success("✅ **STABLE STRUCTURE:** Debt service is well-covered by operating performance.")

    # 4. NAVIGATION
    st.divider()
    col_prev, col_next = st.columns(2)
    with col_prev:
        if st.button("⬅️ Back to Stage 1"):
            st.session_state.flow_step = "stage1"
            st.rerun()
    with col_next:
        if st.button("Proceed to Stage 3 ➡️"):
            st.session_state.flow_step = "stage3"
            st.rerun()
