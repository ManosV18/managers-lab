import streamlit as st
import importlib

def show_library():
    st.title("🏛️ Strategic Tool Library")
    
    # 1. Metric Bar
    m1, m2 = st.columns(2)
    m1.metric("WACC", f"{st.session_state.get('wacc', 0.15):.2%}")
    m2.metric("Step", st.session_state.get('flow_step', 'N/A'))

    if st.session_state.get('selected_tool') is None:
        tab1, tab2, tab3, tab4 = st.tabs(["🚀 Strategy", "💰 Finance", "⚙️ Ops", "📉 Risk"])

        with tab1:
            if st.button("⚖️ BEP Shift"): st.session_state.selected_tool = ("break_even_shift_calculator", "show_break_even_shift_calculator")
            if st.button("👥 CLV Simulator"): st.session_state.selected_tool = ("clv_calculator", "show_clv_calculator")
            if st.button("📊 Dashboard"): st.session_state.selected_tool = ("executive_dashboard", "show_executive_dashboard")

        with tab2:
            if st.button("📉 WACC Optimizer"): st.session_state.selected_tool = ("wacc_optimizer", "show_wacc_optimizer")
            if st.button("🛡️ Cash Fragility"): st.session_state.selected_tool = ("cash_fragility_index", "show_cash_fragility_index")
            if st.button("🛑 Loss Threshold"): st.session_state.selected_tool = ("loss_threshold", "show_loss_threshold")

        with tab3:
            if st.button("🔄 Cash Cycle"): st.session_state.selected_tool = ("cash_cycle", "run_cash_cycle_app")
            if st.button("📦 Inventory"): st.session_state.selected_tool = ("inventory_manager", "show_inventory_manager")

        with tab4:
            if st.button("🌪️ Stress Test"): st.session_state.selected_tool = ("stress_test_simulator", "show_stress_test")

        if st.session_state.get('selected_tool'):
            st.rerun()

    else:
        if st.button("⬅️ Back to Library"):
            st.session_state.selected_tool = None
            st.rerun()
        
        st.divider()
        mod_name, func_name = st.session_state.selected_tool
        
        try:
            # ΔΥΝΑΜΙΚΟ ΦΟΡΤΩΜΑ
            module = importlib.import_module(f"tools.{mod_name}")
            
            # Δοκιμάζει το όνομα που δώσαμε, αν αποτύχει δοκιμάζει 'main', αν αποτύχει δοκιμάζει 'run'
            tool_func = getattr(module, func_name, None) or getattr(module, "main", None) or getattr(module, "run", None)
            
            if tool_func:
                tool_func()
            else:
                st.error(f"🚫 Σφάλμα: Δεν βρέθηκε συνάρτηση εκκίνησης στο αρχείο tools/{mod_name}.py")
                st.info("Βεβαιώσου ότι η συνάρτηση ονομάζεται είτε '" + func_name + "' είτε 'main'.")
        except Exception as e:
            st.error(f"💥 Κρίσιμο Σφάλμα στο εργαλείο: {e}")
