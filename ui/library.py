import streamlit as st
import importlib

def show_library():
    st.title("🏛️ Strategic Tool Library")
    
    # Tabs για οργάνωση
    tab1, tab2, tab3, tab4 = st.tabs(["🚀 Strategy", "💰 Finance", "⚙️ Ops", "📉 Risk"])

    if st.session_state.get('selected_tool') is None:
        # ΕΔΩ ΘΑ ΠΡΟΣΘΕΤΟΥΜΕ ΤΑ ΚΟΥΜΠΙΑ ΕΝΑ-ΕΝΑ ΚΑΘΩΣ ΤΑ ΦΤΙΑΧΝΟΥΜΕ
        with tab1:
            # Παράδειγμα:
            # if st.button("⚖️ BEP Shift"): st.session_state.selected_tool = ("break_even_shift_calculator", "show_break_even_shift_calculator")
            pass
        
        if st.session_state.get('selected_tool'):
            st.rerun()
    else:
        # ΕΔΩ ΕΚΤΕΛΕΙΤΑΙ ΤΟ ΕΡΓΑΛΕΪΟ
        if st.button("⬅️ Πίσω στη Βιβλιοθήκη"):
            st.session_state.selected_tool = None
            st.rerun()
        
        mod_name, func_name = st.session_state.selected_tool
        module = importlib.import_module(f"tools.{mod_name}")
        func = getattr(module, func_name)
        func()
