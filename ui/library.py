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
            if st.button("⚖️ BEP Shift Analysis", use_container_width=True):
                st.session_state.selected_tool = ("break_even_shift_calculator", "show_break_even_shift_calculator")
                st.rerun()
        
        with t2:
            st.subheader("Finance & Capital")
            # Σωστή κλήση του t2 (όχι tab2)
            if st.button("📉 WACC Optimizer", use_container_width=True):
                st.session_state.selected_tool = ("wacc_optimizer", "show_wacc_optimizer")
                st.rerun()
            st.info("Additional finance tools pending...")

        with t3:
            st.subheader("Operations & Efficiency")
            st.info("Operations tools pending...")

        with t4:
            st.subheader("Risk & Vulnerability")
            st.info("Risk tools pending...")

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
