import streamlit as st
import importlib

def show_library():
    # 1. Sidebar navigation
    if st.sidebar.button("🏠 Exit Library"):
        st.session_state.mode = "path"
        st.session_state.flow_step = "home"
        st.session_state.selected_tool = None
        st.rerun()

    st.title("🏛️ Strategic Tool Library")

    # 2. Tool Routing
    if st.session_state.get('selected_tool') is None:
        # Δημιουργία των Tabs
        t1, t2, t3, t4 = st.tabs(["🚀 Strategy", "💰 Finance", "⚙️ Ops", "📉 Risk"])
        
        with t1:
            st.subheader("Strategy & Growth")
            if st.button("⚖️ BEP Shift Analysis", use_container_width=True):
                st.session_state.selected_tool = ("break_even_shift_calculator", "show_break_even_shift_calculator")
                st.rerun()
            if st.button("👥 CLV Simulator", use_container_width=True):
                st.session_state.selected_tool = ("clv_calculator", "show_clv_calculator")
                st.rerun()
        
        with t2:
            st.subheader("Finance & Capital")
            if st.button("📉 WACC Optimizer", use_container_width=True):
                st.session_state.selected_tool = ("wacc_optimizer", "show_wacc_optimizer")
                st.rerun()
            # ΔΙΟΡΘΩΣΗ: Αφαίρεση του col_t2b που προκαλούσε το error
            if st.button("📈 Growth Funding (AFN)", use_container_width=True):
                st.session_state.selected_tool = ("growth_funding", "show_growth_funding_needed")
                st.rerun()

        with t3:
            st.subheader("Operations & Efficiency")
            if st.button("🔄 Cash Conversion Cycle", use_container_width=True):
                st.session_state.selected_tool = ("cash_cycle", "run_cash_cycle_app")
                st.rerun()
            
            # ΣΥΝΔΕΣΗ ΤΟΥ INVENTORY MANAGER
            if st.button("📦 Inventory Analyzer", use_container_width=True):
                st.session_state.selected_tool = ("inventory_manager", "show_inventory_manager")
                st.rerun()

        with t4:
            st.subheader("Risk & Command Center")
            if st.button("🛡️ Resilience & Shock Map", use_container_width=True):
                st.session_state.selected_tool = ("resilience_map", "show_resilience_map")
                st.rerun()
            if st.button("🚨 Cash Fragility Index", use_container_width=True):
                st.session_state.selected_tool = ("cash_fragility_index", "show_cash_fragility_index")
                st.rerun()
            if st.button("🏁 Executive Command Center", use_container_width=True):
                st.session_state.selected_tool = ("executive_dashboard", "show_executive_dashboard")
                st.rerun()

    else:
        # 3. Tool Execution Mode
        if st.button("⬅️ Back to Library Hub"):
            st.session_state.selected_tool = None
            st.rerun()
        
        st.divider()
        mod_name, func_name = st.session_state.selected_tool
        try:
            # Δυναμική φόρτωση από το φάκελο tools/
            module = importlib.import_module(f"tools.{mod_name}")
            tool_func = getattr(module, func_name)
            tool_func()
        except Exception as e:
            st.error(f"❌ Σφάλμα φόρτωσης εργαλείου '{mod_name}': {e}")
            if st.button("Reset Selection"):
                st.session_state.selected_tool = None
                st.rerun()
