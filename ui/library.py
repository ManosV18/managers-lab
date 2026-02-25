import streamlit as st
import importlib

def show_library():
    st.title("🏛️ Strategic Tool Library")
    
    # 1. Metrics Bar
    m1, m2 = st.columns(2)
    m1.metric("WACC", f"{st.session_state.get('wacc', 0.15):.2%}")
    m2.metric("Flow Step", st.session_state.get('flow_step', 'N/A'))

    # 2. ROUTER: Αν δεν έχουμε επιλέξει εργαλείο, δείξε τα Tabs
    if "selected_tool" not in st.session_state or st.session_state.selected_tool is None:
        
        tab1, tab2, tab3, tab4 = st.tabs(["🚀 Strategy", "💰 Finance", "⚙️ Ops", "📉 Risk"])

        with tab1:
            st.subheader("Strategy & Growth")
            if st.button("⚖️ BEP Shift Analysis", use_container_width=True):
                st.session_state.selected_tool = ("break_even_shift_calculator", "show_break_even_shift_calculator")
                st.rerun()

        with tab2:
            st.info("Finance tools pending...")

        with tab3:
            st.info("Operations tools pending...")

        with tab4:
            st.info("Risk tools pending...")

    # 3. ROUTER: Αν ΕΧΟΥΜΕ επιλέξει εργαλείο, δείξε το εργαλείο
    else:
        # Κουμπί επιστροφής ΠΑΝΤΑ πάνω από το εργαλείο
        if st.button("⬅️ Back to Library Hub", type="primary"):
            st.session_state.selected_tool = None
            st.rerun()
        
        st.divider()

        module_name, func_name = st.session_state.selected_tool
        
        try:
            # Φόρτωση του αρχείου
            module = importlib.import_module(f"tools.{module_name}")
            # Εύρεση της συνάρτησης
            tool_func = getattr(module, func_name)
            # Εκτέλεση
            tool_func()
        except Exception as e:
            st.error(f"⚠️ Σφάλμα στο αρχείο {module_name}: {e}")
            if st.button("Reset Library"):
                st.session_state.selected_tool = None
                st.rerun()
