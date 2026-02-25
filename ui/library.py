import streamlit as st
import importlib

def show_library():
    st.title("🏛️ Strategic Tool Library")
    
    # Metrics Bar
    m1, m2 = st.columns(2)
    m1.metric("WACC", f"{st.session_state.get('wacc', 0.15):.2%}")
    m2.metric("Flow Step", st.session_state.get('flow_step', 'N/A'))

    # Tabs
    tab1, tab2, tab3, tab4 = st.tabs(["🚀 Strategy", "💰 Finance", "⚙️ Ops", "📉 Risk"])

    if st.session_state.get('selected_tool') is None:
        with tab1:
            st.subheader("Strategy & Growth")
            # ΣΥΝΔΕΣΗ ΤΟΥ ΕΡΓΑΛΕΙΟΥ ΣΟΥ
            if st.button("⚖️ BEP Shift Analysis", use_container_width=True):
                st.session_state.selected_tool = ("break_even_shift_calculator", "show_break_even_shift_calculator")
                st.rerun()
        
        # Τα υπόλοιπα tabs μένουν κενά για την ώρα
        with tab2: st.info("Περιμένει το επόμενο αρχείο...")
        with tab3: st.info("Περιμένει το επόμενο αρχείο...")
        with tab4: st.info("Περιμένει το επόμενο αρχείο...")

    else:
        # ΕΚΤΕΛΕΣΗ ΕΡΓΑΛΕΙΟΥ
        module_name, func_name = st.session_state.selected_tool
        
        # Κουμπί επιστροφής
        if st.button("⬅️ Back to Library Hub", type="primary"):
            st.session_state.selected_tool = None
            st.rerun()
        
        st.divider()

        try:
            module = importlib.import_module(f"tools.{module_name}")
            tool_func = getattr(module, func_name)
            tool_func()
        except Exception as e:
            st.error(f"Σφάλμα φόρτωσης: {e}")
