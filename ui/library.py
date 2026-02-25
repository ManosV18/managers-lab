import streamlit as st
import importlib

def show_library():
    st.title("🏛️ Strategic Tool Library")
    
    # 1. Metric Bar (Απευθείας από το session_state για ασφάλεια)
    m1, m2 = st.columns(2)
    m1.metric("WACC", f"{st.session_state.get('wacc', 0.15):.2%}")
    m2.metric("Flow Step", st.session_state.get('flow_step', 'N/A'))

    # 2. Tabs για τις κατηγορίες (Πολύ πιο ελαφρύ)
    tab1, tab2, tab3, tab4 = st.tabs(["🚀 Strategy", "💰 Finance", "⚙️ Ops", "📉 Risk"])

    if st.session_state.get('selected_tool') is None:
        with tab1:
            if st.button("⚖️ BEP Shift"): st.session_state.selected_tool = ("break_even_shift_calculator", "show_break_even_shift_calculator")
            if st.button("👥 CLV Simulator"): st.session_state.selected_tool = ("clv_calculator", "show_clv_calculator")
        with tab2:
            if st.button("🛡️ Cash Fragility"): st.session_state.selected_tool = ("cash_fragility_index", "show_cash_fragility_index")
        
        if st.session_state.get('selected_tool'):
            st.rerun()
    else:
        if st.button("⬅️ Back to Categories"):
            st.session_state.selected_tool = None
            st.rerun()
        
        # Το Import γίνεται ΜΟΝΟ εδώ, τη στιγμή που πατιέται το κουμπί
        module_name, func_name = st.session_state.selected_tool
        try:
            module = importlib.import_module(f"tools.{module_name}")
            tool_func = getattr(module, func_name)
            tool_func()
        except Exception as e:
            st.error(f"Δεν ήταν δυνατή η φόρτωση του εργαλείου: {e}")

        with tab2:
            if st.button("🛡️ Cash Fragility"): 
                st.session_state.selected_tool = ("cash_fragility_index", "show_cash_fragility_index")
            # ΠΡΟΣΘΗΚΗ WACC OPTIMIZER:
            if st.button("📉 WACC Optimizer"): 
                st.session_state.selected_tool = ("wacc_optimizer", "show_wacc_optimizer")
