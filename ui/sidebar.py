import streamlit as st
from core.sync import lock_baseline

def show_sidebar():
    # --- Defaults ---
    if "wacc" not in st.session_state:
        st.session_state.wacc = 0.15  # Default 15%
    if "flow_step" not in st.session_state:
        st.session_state.flow_step = "home"
    if "baseline_locked" not in st.session_state:
        st.session_state.baseline_locked = False
    if "selected_tool" not in st.session_state:
        st.session_state.selected_tool = None

    with st.sidebar:
        st.title("💧 Cash Survival OS")

        st.divider()
        
        # --- SYSTEM INTEGRITY ---
        st.subheader("🛡️ System Status")
        if st.session_state.baseline_locked:
            st.success("✅ Baseline Locked")
        else:
            st.warning("🔓 Baseline OPEN (Setup Stage)")

        st.divider()

        # --- GLOBAL PARAMETERS INPUT ---
        st.subheader("⚙️ Input Basic Numbers")
        st.session_state.price = st.number_input(
            "Unit Price (€)", value=float(st.session_state.get("price", 100.0))
        )
        st.session_state.variable_cost = st.number_input(
            "Variable Cost (€)", value=float(st.session_state.get("variable_cost", 60.0))
        )
        st.session_state.volume = st.number_input(
            "Annual Volume", value=int(st.session_state.get("volume", 1000))
        )
        st.session_state.fixed_cost = st.number_input(
            "Annual Fixed Costs (€)", value=float(st.session_state.get("fixed_cost", 20000.0))
        )

        st.divider()

        # --- ACTIONS ---
        if not st.session_state.baseline_locked:
            if st.button("🔒 Lock Baseline & Start", use_container_width=True):
                lock_baseline()
                st.session_state.flow_step = "stage1"
                st.rerun()

        if st.button("🔄 Reset All Data", use_container_width=True, type="secondary"):
            st.session_state.clear()
            st.session_state.flow_step = "home"
            st.session_state.wacc = 0.15
            st.session_state.baseline_locked = False
            st.session_state.selected_tool = None
            st.rerun()

        st.divider()

        # --- TOOLS SELECTION ---
        st.subheader("🛠️ Select Tool")
        tools_mapping = {
            "Break-Even Calculator": ("break_even", "show_break_even_tool"),
            "CLV Simulator": ("clv_calculator", "show_clv_calculator"),
            "Cash Conversion Cycle (CCC)": ("cash_cycle", "run_cash_cycle_app"),
            "Receivables Analyzer": ("receivables_analyzer", "show_receivables_analyzer_ui"),
            "Inventory Optimizer (EOQ)": ("inventory_manager", "show_inventory_manager"),
            "Payables Manager": ("INTERNAL", "show_payables_manager_internal"),
            "Unit Cost Analyzer": ("unit_cost_analyzer", "show_unit_cost_app"),
            "Executive Dashboard": ("executive_dashboard", "show_executive_dashboard"),
            "Cash Fragility Index": ("cash_fragility_index", "show_cash_fragility_index"),
            "Stress Test Simulator": ("stress_test_simulator", "show_stress_test_tool")
        }

        # Δημιουργία κουμπιών για κάθε εργαλείο
        for t_name, tool_tuple in tools_mapping.items():
            if st.button(t_name, key=f"tool_{t_name}", use_container_width=True):
                st.session_state.selected_tool = tool_tuple
                st.session_state.flow_step = "library"
                st.rerun()
