import streamlit as st
# Do NOT import from core.sync if the file isn't ready. 
# But since we need them, ensure the path is correct:
try:
    from core.sync import lock_baseline, sync_global_state
except ImportError:
    st.error("Critical Error: core/sync.py is missing or corrupted.")

def show_sidebar():
    with st.sidebar:
        st.title("⚙️ Global Controls")
        
        # --- SYSTEM INTEGRITY MONITOR ---
        st.subheader("🛡️ System Integrity")
        if st.session_state.get('baseline_locked', False):
            st.success("✅ Baseline: LOCKED")
        else:
            st.warning("🔓 Baseline: OPEN (Setup Phase)")
            
        if st.session_state.get('wacc_locked', False):
            st.info(f"🎯 WACC: {st.session_state.wacc:.2%} (Optimized)")
        else:
            st.caption("Using manual WACC estimate")
        st.divider()

        # 1. NAVIGATION & BASE PARAMETERS
        st.info(f"**Current Stage:** {st.session_state.get('flow_step', 'N/A')}")
        st.session_state.price = st.number_input("Unit Price (€)", value=float(st.session_state.get('price', 100.0)))
        st.session_state.variable_cost = st.number_input("Variable Cost (€)", value=float(st.session_state.get('variable_cost', 60.0)))
        st.session_state.volume = st.number_input("Annual Volume", value=int(st.session_state.get('volume', 1000)))
        st.session_state.fixed_cost = st.number_input("Annual Fixed Costs", value=float(st.session_state.get('fixed_cost', 20000.0)))
        st.divider()
        st.subheader("💳 Financials & WC")
        st.session_state.annual_debt_service = st.number_input("Annual Debt Service (€)", value=float(st.session_state.get('annual_debt_service', 0.0)))
        st.session_state.tax_rate = st.number_input("Tax Rate (%)", value=float(st.session_state.get('tax_rate', 0.22)) * 100) / 100

        st.subheader("⏳ Operating Cycle (Days)")
        st.session_state.ar_days = st.number_input("AR Days (Collection)", value=float(st.session_state.get('ar_days', 45.0)))
        st.session_state.inventory_days = st.number_input("Inventory Days", value=float(st.session_state.get('inventory_days', 60.0)))
        st.session_state.ap_days = st.number_input("AP Days (Payment)", value=float(st.session_state.get('ap_days', 30.0)))

        # 2. WACC & BASELINE LOCK
        st.divider()
        if not st.session_state.get('baseline_locked', False):
            if st.button("🔒 Lock Baseline for Analysis", use_container_width=True):
                lock_baseline()
                st.rerun()
        
        if st.button("🔄 Reset All Data", type="secondary", use_container_width=True):
            st.session_state.clear()
            st.rerun()
