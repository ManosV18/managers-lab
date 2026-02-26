import streamlit as st
from core.sync import lock_baseline, sync_global_state

def run_stage0():
    st.header("🏗️ Stage 0: Strategic Baseline Setup")
    st.divider()

    # SECTION 1: REVENUE
    st.subheader("📊 Sales Parameters")
    c1, c2 = st.columns(2)
    st.session_state.price = c1.number_input("Unit Price (€)", value=float(st.session_state.get('price', 100.0)))
    st.session_state.volume = c2.number_input("Annual Volume", value=int(st.session_state.get('volume', 1000)))

    # SECTION 2: COSTS (The Analyzer)
    st.subheader("💰 Cost Structure Analyzer")
    col_a, col_b = st.columns(2)
    
    with col_a:
        st.markdown("**Variable Costs**")
        v1 = st.number_input("Materials (€/unit)", value=30.0, key='in_mat')
        v2 = st.number_input("Labor (€/unit)", value=15.0, key='in_lab')
        st.session_state.variable_cost = v1 + v2
        st.info(f"Total VC: €{st.session_state.variable_cost:,.2f}")

    with col_b:
        st.markdown("**Fixed Costs**")
        f1 = st.number_input("Monthly Rent (€)", value=1000.0, key='in_rent') * 12
        f2 = st.number_input("Annual Salaries (€)", value=10000.0, key='in_sal')
        st.session_state.fixed_cost = f1 + f2
        st.info(f"Total FC: €{st.session_state.fixed_cost:,.2f}")

    st.divider()
    
    # LOCK LOGIC
    if st.button("🔒 Lock Baseline & Initialize Engine", use_container_width=True):
        if st.session_state.price > st.session_state.variable_cost:
            lock_baseline()
            st.session_state.flow_step = "stage1"
            st.rerun()
        else:
            st.error("Check Margin (Price > VC required)")
