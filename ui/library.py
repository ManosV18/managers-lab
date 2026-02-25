import streamlit as st
import importlib

def show_library():
    st.title("🏛️ Strategic Tool Library")
    
    # 1. Metric Bar
    m1, m2 = st.columns(2)
    m1.metric("WACC", f"{st.session_state.get('wacc', 0.15):.2%}")
    m2.metric("Flow Step", st.session_state.get('flow_step', 'N/A'))

    # 2. ROUTER LOGIC
    if st.session_state.get('selected_tool') is None:
        # Εμφάνιση των Tabs μόνο όταν δεν τρέχει εργαλείο
        tab1, tab2, tab3, tab4 = st.tabs(["🚀 Strategy", "💰 Finance", "⚙️ Ops", "📉 Risk"])

        with tab1:
            st.subheader("Strategy & Growth")
            if st.button("⚖️ BEP Shift"): st.session_state.selected_tool = ("break_even_shift_calculator", "show_break_even_shift_calculator")
            if st.button("👥 CLV Simulator"): st.session_state.selected_tool = ("clv_calculator", "show_clv_calculator")
            if st.button("🎯 Pricing Radar"): st.session_state.selected_tool = ("pricing_power_radar", "show_pricing_power_radar")
            if st.button("📊 Executive Dashboard"): st.session_state.selected_tool = ("executive_dashboard", "show_executive_dashboard")

        with tab2:
            st.subheader("Finance & Capital")
            if st.button("📉 WACC Optimizer"): st.session_state.selected_tool = ("wacc_optimizer", "show_wacc_optimizer")
            if st.button("🛡️ Cash Fragility"): st.session_state.selected_tool = ("cash_fragility_index", "show_cash_fragility_index")
            if st.button("🏦 Loan vs Leasing"): st.session_state.selected_tool = ("loan_vs_leasing_calculator", "show_loan_leasing")
            if st.button("🛑 Loss Threshold"): st.session_state.selected_tool = ("loss_threshold", "show_loss_threshold")

        with tab3:
            st.subheader("Operations & Efficiency")
            if st.button("🔄 Cash Cycle (CCC)"): st.session_state.selected_tool = ("cash_cycle", "run_cash_cycle_app")
            if st.button("📦 Inventory Manager"): st.session_state.selected_tool = ("inventory_manager", "show_inventory_manager")
            if st.button("💳 Receivables"): st.session_state.selected_tool = ("receivables_analyzer", "show_receivables_analyzer")
            if st.button("🧪 Unit Cost"): st.session_state.selected_tool = ("unit_cost_app", "show_unit_cost_analyzer")

        with tab4:
            st.subheader("Risk & Decision")
            if st.button("🌪️ Stress Test"): st.session_state.selected_tool = ("stress_test_simulator", "show_stress_test")
            if st.button("📋 QSPM Analysis"): st.session_state.selected_tool = ("qspm_two_strategies", "show_qspm")

        if st.session_state.get('selected_tool'):
            st.rerun()

    else:
        # 3. ΕΚΤΕΛΕΣΗ ΕΡΓΑΛΕΙΟΥ
        if st.button("⬅️ Back to Library Hub", type="primary"):
            st.session_state.selected_tool = None
            st.rerun()
        
        st.divider()
        
        module_name, func_name = st.session_state.selected_tool
        try:
            # Δυναμικό import μόνο του επιλεγμένου module
            module = importlib.import_module(f"tools.{module_name}")
            tool_func = getattr(module, func_name)
            tool_func()
        except Exception as e:
            st.error(f"⚠️ Error in tool '{module_name}': {e}")
            if st.button("Reset Tool Selection"):
                st.session_state.selected_tool = None
                st.rerun()
