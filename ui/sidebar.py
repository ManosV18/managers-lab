import streamlit as st

def show_sidebar():
    with st.sidebar:
        st.title("⚙️ Global Controls")
        
        # 1. Navigation Status
        st.info(f"**Current Stage:** {st.session_state.flow_step}")
        
        # 2. Base Parameters
        st.subheader("Base Parameters")
        st.session_state.price = st.number_input("Unit Price (€)", value=float(st.session_state.price), step=1.0)
        st.session_state.variable_cost = st.number_input("Variable Cost (€)", value=float(st.session_state.variable_cost), step=1.0)
        st.session_state.volume = st.number_input("Annual Volume", value=int(st.session_state.volume), step=100)
        
        st.divider()
        
        # 3. Liquidity Settings
        with st.expander("💳 Liquidity & WC Settings"):
            st.session_state.ar_days = st.slider("AR Days", 0, 120, int(st.session_state.ar_days))
            st.session_state.inventory_days = st.slider("Inv. Days", 0, 120, int(st.session_state.inventory_days))
            st.session_state.ap_days = st.slider("AP Days", 0, 120, int(st.session_state.ap_days))
            st.session_state.opening_cash = st.number_input("Opening Cash (€)", value=float(st.session_state.opening_cash))

        # 4. Debt, Tax & Capital Cost
        with st.expander("🏛️ Fixed Obligations"):
            st.session_state.fixed_cost = st.number_input("Annual Fixed Costs", value=float(st.session_state.fixed_cost))
            st.session_state.annual_loan_payment = st.number_input("Annual Debt Service", value=float(st.session_state.annual_loan_payment))
            st.session_state.tax_rate = st.slider("Tax Rate", 0.0, 0.5, float(st.session_state.tax_rate))
            
            # ΠΡΟΣΘΗΚΗ WACC ΩΣ ΠΑΡΑΔΟΧΗ
            # Inside your Sidebar logic in app.py
            if st.session_state.get('wacc_locked', False):
                st.sidebar.info(f"WACC locked by Optimizer: {st.session_state.wacc:.2%}")
            else:
                st.session_state.wacc = st.sidebar.slider("WACC (%)", 5.0, 25.0, 15.0) / 100

        st.divider()
        
        if st.button("🔄 Reset All Data", type="secondary", use_container_width=True):
            st.session_state.clear()
            st.rerun()

        st.caption("Executive War Room v2.0 | 2026 Edition")
