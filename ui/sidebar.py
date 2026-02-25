import streamlit as st

def show_sidebar():
    with st.sidebar:
        st.title("⚙️ Global Controls")
        
        # --- NEW: SYSTEM INTEGRITY MONITOR ---
        st.subheader("🛡️ System Integrity")
        
        # Check Baseline Status
        if st.session_state.get('baseline_locked', False):
            st.success("✅ Baseline: LOCKED")
        else:
            st.warning("🔓 Baseline: OPEN (Setup Phase)")
            
        # Check WACC Source
        if st.session_state.get('wacc_locked', False):
            st.info(f"🎯 WACC: {st.session_state.wacc:.2%} (Optimized)")
        else:
            st.caption("Using manual WACC estimate")
            
        st.divider()
        # -------------------------------------

        # 1. Navigation Status
        st.info(f"**Current Stage:** {st.session_state.get('flow_step', 'N/A')}")
        
        # 2. Base Parameters
        st.subheader("Base Parameters")
        st.session_state.price = st.number_input("Unit Price (€)", value=float(st.session_state.get('price', 100.0)), step=1.0)
        st.session_state.variable_cost = st.number_input("Variable Cost (€)", value=float(st.session_state.get('variable_cost', 60.0)), step=1.0)
        st.session_state.volume = st.number_input("Annual Volume", value=int(st.session_state.get('volume', 1000)), step=100)
        
        st.divider()
        
        # 3. Liquidity Settings
        with st.expander("💳 Liquidity & WC Settings"):
            st.session_state.ar_days = st.slider("AR Days", 0, 120, int(st.session_state.get('ar_days', 60)))
            st.session_state.inventory_days = st.slider("Inv. Days", 0, 120, int(st.session_state.get('inventory_days', 45)))
            st.session_state.ap_days = st.slider("AP Days", 0, 120, int(st.session_state.get('ap_days', 30)))
            st.session_state.opening_cash = st.number_input("Opening Cash (€)", value=float(st.session_state.get('opening_cash', 50000.0)))

        # 4. Debt, Tax & Capital Cost
        with st.expander("🏛️ Fixed Obligations"):
            st.session_state.fixed_cost = st.number_input("Annual Fixed Costs", value=float(st.session_state.get('fixed_cost', 20000.0)))
            st.session_state.annual_loan_payment = st.number_input("Annual Debt Service", value=float(st.session_state.get('annual_loan_payment', 0.0)))
            st.session_state.tax_rate = st.slider("Tax Rate", 0.0, 0.5, float(st.session_state.get('tax_rate', 0.22)))
            
            # WACC Logic with Source Control
            if st.session_state.get('wacc_locked', False):
                st.info(f"WACC locked by Optimizer: {st.session_state.wacc:.2%}")
                if st.button("Unlock WACC"):
                    st.session_state.wacc_locked = False
                    st.rerun()
            else:
                st.session_state.wacc = st.slider("Manual WACC (%)", 5.0, 25.0, 15.0) / 100

        st.divider()
        
        # Lock Baseline Button
        # ... (μέσα στο sidebar.py, στο κουμπί του Lock)
        from core.sync import lock_baseline

        if not st.session_state.get('baseline_locked', False):
        if st.button("🔒 Lock Baseline for Analysis", use_container_width=True):
        lock_baseline() # Explicitly write the baseline once
        st.rerun()
        
        if not st.session_state.get('baseline_locked', False):
            if st.button("🔒 Lock Baseline for Analysis", use_container_width=True):
                st.session_state.baseline_locked = True
                st.rerun()
        
        if st.button("🔄 Reset All Data", type="secondary", use_container_width=True):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()

        st.caption("Executive War Room v2.0 | 2026 Edition")
