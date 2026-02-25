import streamlit as st
import importlib

def show_library():
    # Αρχικοποίηση state αν λείπει
    if "selected_tool" not in st.session_state:
        st.session_state.selected_tool = None

    # Αν έχει επιλεγεί εργαλείο, προσπάθησε να το φορτώσεις δυναμικά
    if st.session_state.selected_tool:
        module_name, function_name = st.session_state.selected_tool
        try:
            # Δυναμικό import για να μην κρασάρει η app.py αν το εργαλείο έχει λάθος
            module = importlib.import_module(f"tools.{module_name}")
            func = getattr(module, function_name)
            func()
        except Exception as e:
            st.error(f"❌ Σφάλμα στο εργαλείο '{module_name}': {e}")
            if st.button("Επιστροφή στη Βιβλιοθήκη"):
                st.session_state.selected_tool = None
                st.rerun()
        return

    # Κύριο UI Βιβλιοθήκης
    st.title("📚 Strategy & Operations Library")
    st.info("Επιλέξτε ένα αναλυτικό εργαλείο για να τροφοδοτήσετε το κεντρικό μοντέλο.")
    
    tabs = st.tabs(["🎯 Strategy", "📈 Sales", "⚙️ Operations"])

    with tabs[0]: # Strategy
        if st.button("🧭 QSPM Strategy Comparison", use_container_width=True):
            st.session_state.selected_tool = ("qspm_analyzer", "show_qspm_tool")
            st.rerun()

    with tabs[2]: # Operations
        if st.button("📊 Receivables NPV Analyzer", use_container_width=True):
            st.session_state.selected_tool = ("receivables_analyzer", "show_receivables_analyzer_ui")
            st.rerun()
