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
        
        with t1:
            if st.button("⚖️ BEP Shift Analysis", use_container_width=True):
                st.session_state.selected_tool = ("break_even_shift_calculator", "show_break_even_shift_calculator")
                st.rerun()
        
        with t2: st.info("Finance tools pending...")
    else:
        # Εκτέλεση του επιλεγμένου εργαλείου
        if st.button("⬅️ Back to Library"):
            st.session_state.selected_tool = None
            st.rerun()
        
        mod_name, func_name = st.session_state.selected_tool
        try:
            module = importlib.import_module(f"tools.{mod_name}")
            getattr(module, func_name)()
        except Exception as e:
            st.error(f"Error: {e}")
