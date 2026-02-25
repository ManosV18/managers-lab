import streamlit as st
import importlib

def show_library():
    # 1. Βασικά Metrics (Χωρίς βαριά imports)
    from core.sync import sync_global_state
    metrics = sync_global_state()
    
    st.title("🏛️ Strategic Tool Library")
    
    # 2. Tabs για οργάνωση (Πιο ελαφρύ από Columns)
    tab1, tab2, tab3, tab4 = st.tabs(["🚀 Growth", "💰 Finance", "⚙️ Ops", "📉 Risk"])

    # Συνάρτηση-εκτελεστής
    def run_tool(module_name, func_name):
        try:
            module = importlib.import_module(f"tools.{module_name}")
            func = getattr(module, func_name)
            func()
        except Exception as e:
            st.error(f"Error loading {module_name}: {e}")

    if st.session_state.get('selected_tool') is None:
        with tab1:
            if st.button("⚖️ BEP Shift Analysis"): st.session_state.selected_tool = ("break_even_shift_calculator", "show_break_even_shift_calculator")
            if st.button("👥 CLV Simulator"): st.session_state.selected_tool = ("clv_calculator", "show_clv_calculator")
        with tab2:
            if st.button("🛡️ Cash Fragility"): st.session_state.selected_tool = ("cash_fragility_index", "show_cash_fragility_index")
            if st.button("📉 WACC Optimizer"): st.session_state.selected_tool = ("wacc_optimizer", "show_wacc_optimizer")
        # Πρόσθεσε τα υπόλοιπα με τον ίδιο τρόπο σταδιακά
        
        if st.session_state.get('selected_tool'):
            st.rerun()
    else:
        if st.button("⬅️ Back to Categories"):
            st.session_state.selected_tool = None
            st.rerun()
        
        # Εκτέλεση του επιλεγμένου εργαλείου
        module_n, func_n = st.session_state.selected_tool
        run_tool(module_n, func_n)
