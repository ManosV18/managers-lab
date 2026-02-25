import streamlit as st
import importlib

def show_library():
    # Κουμπί επιστροφής
    if st.sidebar.button("🏠 Back to Home"):
        st.session_state.mode = "path"
        st.session_state.flow_step = "home"
        st.session_state.selected_tool = None
        st.rerun()

    st.title("🏛️ Strategic Tool Library")

    if st.session_state.get('selected_tool') is None:
        tab1, tab2, tab3, tab4 = st.tabs(["🚀 Strategy", "💰 Finance", "⚙️ Ops", "📉 Risk"])

        with tab1:
            if st.button("⚖️ BEP Shift Analysis", use_container_width=True):
                st.session_state.selected_tool = ("break_even_shift_calculator", "show_break_even_shift_calculator")
                st.rerun()
        
        with tab2:
            st.info("Finance tools pending...")
    else:
        if st.button("⬅️ Back to Menu"):
            st.session_state.selected_tool = None
            st.rerun()
        
        st.divider()
        mod_name, func_name = st.session_state.selected_tool
        try:
            module = importlib.import_module(f"tools.{mod_name}")
            tool_func = getattr(module, func_name)
            tool_func()
        except Exception as e:
            st.error(f"Error: {e}")
