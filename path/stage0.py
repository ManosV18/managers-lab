import streamlit as st
from core.sync import lock_baseline

def run_stage0():
    st.header("🏗️ Stage 0: Strategic Baseline Setup")
    st.divider()

    # SECTION 1: REVENUE
    st.subheader("📊 Sales Parameters")
    c1, c2 = st.columns(2)
    st.session_state.price = c1.number_input("Unit Price (€)", value=float(st.session_state.get('price', 100.0)))
    st.session_state.volume = c2.number_input("Annual Volume", value=int(st.session_state.get('volume', 1000)))

    # SECTION 2: COSTS
    st.subheader("💰 Cost Structure Analyzer")
    col_a, col_b = st.columns(2)
    
    with col_a:
        st.markdown("**Variable Costs**")
        v1 = st.number_input("Materials (€/unit)", value=30.0, key='in_mat', format="%.2f")
        v2 = st.number_input("Labor (€/unit)", value=15.0, key='in_lab', format="%.2f")
        st.session_state.variable_cost = v1 + v2
        st.info(f"Total VC: €{st.session_state.variable_cost:,.2f}")

    with col_b:
        st.markdown("**Fixed Costs (Annual)**")
        f1 = st.number_input("Annual Rent & Utilities (€)", value=12000.0, key='in_rent', format="%.2f")
        f2 = st.number_input("Annual Salaries & Admin (€)", value=8000.0, key='in_sal', format="%.2f")
        st.session_state.fixed_cost = f1 + f2
        st.info(f"Total Fixed: €{st.session_state.fixed_cost:,.2f}")
    
    st.divider()
    
    # SECTION 3: FINANCIAL & RISK (Hidden but Important)
    with st.expander("⚙️ Advanced Financial Settings"):
        c1, c2, c3 = st.columns(3)
        st.session_state.wacc = c1.number_input("Cost of Capital (WACC %)", value=float(s.get('wacc', 0.15)), format="%.2f")
        st.session_state.tax_rate = c2.number_input("Tax Rate (%)", value=float(s.get('tax_rate', 0.22)), format="%.2f")
        st.session_state.annual_debt_service = c3.number_input("Annual Debt Service (€)", value=float(s.get('annual_debt_service', 0.0)))

        st.markdown("**Working Capital Assumptions (Days)**")
        d1, d2, d3 = st.columns(3)
        st.session_state.ar_days = d1.number_input("AR Days", value=45)
        st.session_state.inventory_days = d2.number_input("Inv Days", value=60)
        st.session_state.ap_days = d3.number_input("AP Days", value=30)
    
    # LOCK LOGIC
    if st.button("🔒 Lock Baseline & Initialize Engine", use_container_width=True):
        if st.session_state.price > st.session_state.variable_cost:
            lock_baseline()
            st.session_state.flow_step = "stage1"
            st.rerun()
        else:
            st.error("Check Margin (Price > VC required)")
