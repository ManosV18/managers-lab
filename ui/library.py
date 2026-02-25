import streamlit as st
import importlib

def show_library():
    # Sidebar back button
    if st.sidebar.button("🏠 Exit Library"):
        st.session_state.mode = "path"
        st.session_state.flow_step = "home"
        st.session_state.selected_tool = None
        st.rerun()

    st.title("🏛️ Strategic Tool Library")

    # Έλεγχος αν υπάρχει επιλεγμένο εργαλείο
    if st.session_state.get('selected_tool') is None:
        # Ορισμός των Tabs
        t1, t2, t3, t4 = st.tabs(["🚀 Strategy", "💰 Finance", "⚙️ Ops", "📉 Risk"])
        
        with t1:
            st.subheader("Strategy & Growth")
            col_t1a, col_t1b = st.columns(2)
            
            with col_t1a:
                if st.button("⚖️ BEP Shift Analysis", use_container_width=True):
                    st.session_state.selected_tool = ("break_even_shift_calculator", "show_break_even_shift_calculator")
                    st.rerun()
            
            with col_t1b:
                # ΣΥΝΔΕΣΗ ΤΟΥ CLV SIMULATOR
                if st.button("👥 CLV Simulator", use_container_width=True):
                    st.session_state.selected_tool = ("clv_calculator", "show_clv_calculator")
                    st.rerun()
        with t2:
            st.subheader("Finance & Capital")
            # Σωστή κλήση του t2 (όχι tab2)
            if st.button("📉 WACC Optimizer", use_container_width=True):
                st.session_state.selected_tool = ("wacc_optimizer", "show_wacc_optimizer")
                st.rerun()
            with col_t2b:
                # ΣΥΝΔΕΣΗ ΤΟΥ AFN CALCULATOR
                if st.button("📈 Growth Funding (AFN)", use_container_width=True):
                    st.session_state.selected_tool = ("growth_funding", "show_growth_funding_needed")
                    st.rerun()
            st.info("Additional finance tools pending...")

        with t3:
            st.subheader("Operations & Efficiency")
            # ΣΥΝΔΕΣΗ ΤΟΥ CASH CYCLE
            if st.button("🔄 Cash Conversion Cycle", use_container_width=True):
                st.session_state.selected_tool = ("cash_cycle", "run_cash_cycle_app")
                st.rerun()
            
            st.info("Additional operations tools pending...")

        
        with t4:
            st.subheader("Risk & Vulnerability")
            # ΣΥΝΔΕΣΗ ΤΟΥ RESILIENCE MAP
            if st.button("🛡️ Resilience & Shock Map", use_container_width=True):
                st.session_state.selected_tool = ("resilience_map", "show_resilience_map")
                st.rerun()
            # ΣΥΝΔΕΣΗ ΤΟΥ CASH FRAGILITY INDEX
            if st.button("🛡️ Cash Fragility Index", use_container_width=True):
                st.session_state.selected_tool = ("cash_fragility_index", "show_cash_fragility_index")
                st.rerun()
           # ΣΥΝΔΕΣΗ ΤΟΥ EXECUTIVE DASHBOARD
            if st.button("🏁 Executive Liquidity Command", use_container_width=True):
                st.session_state.selected_tool = ("executive_dashboard", "show_executive_dashboard")
                st.rerun()
            st.info("Additional risk assessment tools pending...")
      

    else:
        # Εκτέλεση του επιλεγμένου εργαλείου
        if st.button("⬅️ Back to Library Hub"):
            st.session_state.selected_tool = None
            st.rerun()
        
        st.divider()
        
        mod_name, func_name = st.session_state.selected_tool
        try:
            # Δυναμικό import
            module = importlib.import_module(f"tools.{mod_name}")
            tool_func = getattr(module, func_name)
            tool_func()
        except Exception as e:
            st.error(f"❌ Σφάλμα κατά τη φόρτωση του εργαλείου '{mod_name}': {e}")
            if st.button("Reset Selection"):
                st.session_state.selected_tool = None
                st.rerun()
