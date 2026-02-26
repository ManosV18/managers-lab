import streamlit as st
from core.sync import lock_baseline

def show_sidebar():
    # 1. Defaults
    if "flow_step" not in st.session_state:
        st.session_state.flow_step = "home"

    with st.sidebar:
        st.title("🚀 War Room Command")
        
        # 2. Navigation Logic
        nav_options = {
            "🏠 Home": "home",
            "🏗️ Stage 0: Setup": "stage0",
            "📊 Stage 1: Survival & BEP": "stage1",
            "🏁 Stage 2: Dashboard": "stage2",
            "💧 Stage 3: Liquidity Physics": "stage3",
            "🌪️ Stage 4: Stress Testing": "stage4",
            "⚖️ Stage 5: Strategic Decision": "stage5",
            "📚 Tools Library": "library"
        }
               
        current_step = st.session_state.flow_step
        options_list = list(nav_options.keys())
        values_list = list(nav_options.values())
        
        try:
            default_idx = values_list.index(current_step)
        except ValueError:
            default_idx = 0

        selection = st.selectbox("Tool Selection:", options_list, index=default_idx)
        
        # Αν αλλάξει η επιλογή, αλλάζουμε ΜΟΝΟ το flow_step
        if nav_options[selection] != current_step:
            st.session_state.flow_step = nav_options[selection]
            st.rerun()

        st.divider()
        
        # --- Baseline Status Indicator ---
        if st.session_state.get('baseline_locked', False):
            st.success("✅ Baseline: LOCKED")
        else:
            st.warning("🔓 Baseline: OPEN")
            
        st.divider()
        # (Εδώ συνεχίζουν τα number_inputs για Price, Volume κλπ όπως τα είχες)

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
            
        )

        st.session_state.variable_cost = st.number_input(
            "Variable Cost (€)",
            value=float(st.session_state.get('variable_cost', 60.0)),
            
        )

        st.session_state.volume = st.number_input(
            "Annual Volume",
            value=int(st.session_state.get('volume', 1000)),
            
        )

        st.session_state.fixed_cost = st.number_input(
            "Annual Fixed Costs",
            value=float(st.session_state.get('fixed_cost', 20000.0)),
            
        )

        # =====================================================
        # 3. FINANCIALS & WC
        # =====================================================
        st.subheader("💳 Financials & WC")

        st.session_state.annual_debt_service = st.number_input(
            "Annual Debt Service (€)",
            value=float(st.session_state.get('annual_debt_service', 0.0)),
            
        )

        st.session_state.opening_cash = st.number_input(
            "Opening Cash (€)",
            value=float(st.session_state.get('opening_cash', 10000.0)),
            
        )

        tax_percent = st.number_input(
            "Tax Rate (%)",
            value=float(st.session_state.get('tax_rate', 0.22)) * 100,
            
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
            
        )

        st.session_state.inventory_days = st.number_input(
            "Inventory Days",
            value=float(st.session_state.get('inventory_days', 60.0)),
            
        )

        st.session_state.ap_days = st.number_input(
            "AP Days (Payment)",
            value=float(st.session_state.get('ap_days', 30.0)),
            
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
