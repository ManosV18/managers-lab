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
    
    if "flow_step" not in st.session_state:
        st.session_state.flow_step = "home"

    with st.sidebar:
        st.title("🚀 War Room Command")
        
        # =====================================================
        # 0. QUICK NAVIGATION
        # =====================================================
        st.subheader("📍 Navigation")
        
        nav_options = {
            "🏠 Home": "home",
            "🏗️ Stage 1: Setup & BEP": "stage1",
            "🏁 Stage 2: Liquidity Dashboard": "stage2",
            "💰 Stage 3: Capital Allocation": "stage3",
            "🌪️ Stage 4: Stress Testing": "stage4",
            "⚖️ Stage 5: Strategic QSPM": "stage5", # Το QSPM πλέον είναι το Stage 5
            "📚 Tools Library": "library"           # Η βιβλιοθήκη ως αυτόνομο Tool
        }
        
        # Syncing the selectbox with the current session state
        current_step = st.session_state.get('flow_step', 'home')
        options_list = list(nav_options.keys())
        values_list = list(nav_options.values())
        
        try:
            default_idx = values_list.index(current_step)
        except ValueError:
            default_idx = 0

        # Refined Tool Selection
        selection = st.selectbox("Tool Selection:", options_list, index=default_idx)
        
        # If user changes selection, trigger rerun to update the Router
        if nav_options[selection] != current_step:
            st.session_state.flow_step = nav_options[selection]
            # Mode management
            if nav_options[selection] == "library":
                st.session_state.mode = "library"
            else:
                st.session_state.mode = "path"
            st.rerun()

        st.divider()

        # =====================================================
        # 1. SYSTEM INTEGRITY MONITOR
        # =====================================================
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
        # 2. BASE PARAMETERS (GLOBAL CONTROLS)
        # =====================================================
        st.subheader("⚙️ Global Parameters")

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

        # =====================================================
        # 3. FINANCIALS & WC
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
        # 4. WACC INPUT
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
        # 5. OPERATING CYCLE (Days)
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

        st.divider()

        # =====================================================
        # 6. ACTIONS
        # =====================================================
        if not st.session_state.get('baseline_locked', False):
            if st.button("🔒 Lock Baseline", use_container_width=True):
                lock_baseline()
                # Auto-move to Stage 1 upon locking
                st.session_state.flow_step = "stage1"
                st.rerun()
        
        if st.button("🔄 Reset All Data", type="secondary", use_container_width=True):
            st.session_state.clear()
            st.rerun()
