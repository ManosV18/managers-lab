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

    if st.session_state.get('selected_tool') is None:
        t1, t2, t3, t4 = st.tabs(["🚀 Strategy", "💰 Finance", "⚙️ Ops", "📉 Risk"])
        
        # --- TAB 1: STRATEGY ---
        with t1:
            st.subheader("Strategy & Growth")
            c1a, c1b = st.columns(2)
            with c1a:
                if st.button("⚖️ BEP Shift Analysis", use_container_width=True):
                    st.session_state.selected_tool = ("break_even_shift_calculator", "show_break_even_shift_calculator")
                    st.rerun()
            with c1b:
                if st.button("👥 CLV Simulator", use_container_width=True):
                    st.session_state.selected_tool = ("clv_calculator", "show_clv_calculator")
                    st.rerun()
        
        # --- TAB 2: FINANCE ---
        with t2:
            st.subheader("Finance & Capital")
            c2a, c2b = st.columns(2) # Ορισμός των columns για να μην κρασάρει
            with c2a:
                if st.button("📉 WACC Optimizer", use_container_width=True):
                    st.session_state.selected_tool = ("wacc_optimizer", "show_wacc_optimizer")
                    st.rerun()
            with c2b:
                if st.button("📈 Growth Funding (AFN)", use_container_width=True):
                    st.session_state.selected_tool = ("growth_funding", "show_growth_funding_needed")
                    st.rerun()

        # --- TAB 3: OPERATIONS ---
        with t3:
            st.subheader("Operations & Efficiency")
            if st.button("🔄 Cash Conversion Cycle", use_container_width=True):
                st.session_state.selected_tool = ("cash_cycle", "run_cash_cycle_app")
                st.rerun()

        # --- TAB 4: RISK & COMMAND ---
        with t4:
            st.subheader("Risk & Vulnerability")
            c4a, c4b = st.columns(2)
            with c4a:
                if st.button("🛡️ Resilience & Shock Map", use_container_width=True):
                    st.session_state.selected_tool = ("resilience_map", "show_resilience_map")
                    st.rerun()
                if st.button("🏁 Executive Command", use_container_width=True):
                    st.session_state.selected_tool = ("executive_dashboard", "show_executive_dashboard")
                    st.rerun()
            with c4b:
                if st.button("🚨 Cash Fragility Index", use_container_width=True):
                    st.session_state.selected_tool = ("cash_fragility_index", "show_cash_fragility_index")
                    st.rerun()

    else:
        # EXECUTION MODE
        if st.button("⬅️ Back to Library Hub"):
            st.session_state.selected_tool = None
            st.rerun()
        
        st.divider()
        mod_name, func_name = st.session_state.selected_tool
        try:
            module = importlib.import_module(f"tools.{mod_name}")
            getattr(module, func_name)()
        except Exception as e:
            st.error(f"❌ Error loading tool '{mod_name}': {e}")
            if st.button("Reset Selection"):
                st.session_state.selected_tool = None
                st.rerun()
