import streamlit as st

# Do NOT import from core.sync if the file isn't ready. 
try:
    from core.sync import lock_baseline, sync_global_state
except ImportError:
    st.error("Critical Error: core/sync.py is missing or corrupted.")


def show_sidebar():

    # =====================================================
    # SAFE INITIALIZATION (Cold Start Protection)
    # =====================================================
    if "wacc" not in st.session_state:
        st.session_state.wacc = 0.15  # Default 15%

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

        # =====================================================
        # 1. BASE PARAMETERS
        # =====================================================
        st.info(f"**Current Stage:** {st.session_state.get('flow_step', 'N/A')}")

        st.session_state.price = st.number_input(
            "Unit Price (€)",
            value=float(st.session_state.get('price', 100.0)),
            on_change=st.rerun
        )

        st.session_state.variable_cost = st.number_input(
            "Variable Cost (€)",
            value=float(st.session_state.get('variable_cost', 60.0)),
            on_change=st.rerun
        )

        st.session_state.volume = st.number_input(
            "Annual Volume",
            value=int(st.session_state.get('volume', 1000)),
            on_change=st.rerun
        )

        st.session_state.fixed_cost = st.number_input(
            "Annual Fixed Costs",
            value=float(st.session_state.get('fixed_cost', 20000.0)),
            on_change=st.rerun
        )

        st.divider()

        # =====================================================
        # 2. FINANCIALS & WC
        # =====================================================
        st.subheader("💳 Financials & WC")

        st.session_state.annual_debt_service = st.number_input(
            "Annual Debt Service (€)",
            value=float(st.session_state.get('annual_debt_service', 0.0)),
            on_change=st.rerun
        )

        st.session_state.opening_cash = st.number_input(
            "Opening Cash (€)",
            value=float(st.session_state.get('opening_cash', 10000.0)),
            on_change=st.rerun
        )

        tax_percent = st.number_input(
            "Tax Rate (%)",
            value=float(st.session_state.get('tax_rate', 0.22)) * 100,
            on_change=st.rerun
        )
        st.session_state.tax_rate = tax_percent / 100

        # =====================================================
        # 3. WACC INPUT
        # =====================================================
        st.subheader("📊 Cost of Capital")

        if not st.session_state.get('wacc_locked', False):
            wacc_percent = st.number_input(
                "WACC (%)",
                min_value=0.0,
                max_value=100.0,
                value=st.session_state.wacc * 100,
                step=0.1,
                on_change=st.rerun
            )
            st.session_state.wacc = wacc_percent / 100
        else:
            st.info(f"WACC Locked at {st.session_state.wacc:.2%}")

        # =====================================================
        # 4. OPERATING CYCLE
        # =====================================================
        st.subheader("⏳ Operating Cycle (Days)")

        st.session_state.ar_days = st.number_input(
            "AR Days (Collection)",
            value=float(st.session_state.get('ar_days', 45.0)),
            on_change=st.rerun
        )

        st.session_state.inventory_days = st.number_input(
            "Inventory Days",
            value=float(st.session_state.get('inventory_days', 60.0)),
            on_change=st.rerun
        )

        st.session_state.ap_days = st.number_input(
            "AP Days (Payment)",
            value=float(st.session_state.get('ap_days', 30.0)),
            on_change=st.rerun
        )

        # =====================================================
        # 5. BASELINE LOCK
        # =====================================================
        st.divider()

        if not st.session_state.get('baseline_locked', False):
            if st.button("🔒 Lock Baseline for Analysis", use_container_width=True):
                lock_baseline()
                st.rerun()
        
        if st.button("🔄 Reset All Data", type="secondary", use_container_width=True):
            st.session_state.clear()
            st.rerun()
