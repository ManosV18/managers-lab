import streamlit as st

def show_sidebar():

    if "selected_tool" not in st.session_state:
        st.session_state.selected_tool = None

    st.sidebar.title("TOOLS")

    tools = {
        "Break Even": ("break_even", "show_break_even_tool"),
        "Break Even Shift": ("break_even_shift", "show_break_even_shift"),
        "CLV Calculator": ("clv_calculator", "show_clv_calculator"),
        "Cash Conversion Cycle": ("cash_cycle", "run_cash_cycle_app"),
        "Receivables Analyzer": ("receivables_analyzer", "show_receivables_analyzer_ui"),
        "Inventory Manager": ("inventory_manager", "show_inventory_manager"),
        "Payables Manager": ("INTERNAL", "show_payables_manager_internal"),
        "Unit Cost Analyzer": ("unit_cost_analyzer", "show_unit_cost_app"),
        "Executive Dashboard": ("executive_dashboard", "show_executive_dashboard"),
        "Cash Fragility Index": ("cash_fragility_index", "show_cash_fragility_index"),
        "Stress Test": ("stress_test_simulator", "show_stress_test_tool"),
        "Loan vs Leasing": ("loan_vs_leasing", "loan_vs_leasing_ui")
    }

    for name, tool in tools.items():

        if st.sidebar.button(name, use_container_width=True):

            st.session_state.selected_tool = tool
            st.session_state.flow_step = "library"
            st.rerun()
