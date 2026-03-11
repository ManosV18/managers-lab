import streamlit as st
import importlib
from ui.sidebar import show_sidebar
from ui.home import run_home
from core.engine import calculate_metrics

st.set_page_config(page_title="Managers Lab", layout="wide")

# ΠΛΗΡΕΣ MAPPING: UI Key -> (Module Name, Function Name)
# Προσοχή: Τα Module Names πρέπει να είναι ακριβώς τα ονόματα των .py αρχείων στο core/tools/

TOOL_MAP = {
    # Strategy
    "pricing_strategy": ("pricing_strategy", "show_pricing_strategy_tool"),
    "break_even_shift": ("break_even_shift_calculator", "show_break_even_shift_calculator"),
    "pricing_radar": ("pricing_radar", "show_pricing_radar"),
    "loss_threshold": ("loss_threshold", "show_loss_threshold_before_price_cut"),
    "qspm_analyzer": ("qspm_analyzer", "show_qspm_tool"),
    # Finance
    "growth_funding": ("growth_funding", "show_growth_funding_needed"),
    "wacc_optimizer": ("wacc_optimizer", "show_wacc_optimizer"),
    "loan_vs_leasing": ("loan_vs_leasing", "loan_vs_leasing_ui"),
    # Ops
    "receivables_npv": ("receivables_npv", "show_receivables_analyzer_ui"),
    "cash_cycle": ("cash_cycle", "run_cash_cycle_app"),
    "unit_cost_analyzer": ("unit_cost_analyzer", "show_unit_cost_app"),
    "inventory_manager": ("inventory_manager", "show_inventory_manager"),
    "payables_manager": ("payables_manager", "show_payables_manager"),
    # Risk
    "executive_dashboard": ("executive_dashboard", "show_executive_dashboard"),
    "cash_fragility": ("cash_fragility_index", "show_cash_fragility_index"),
    "resilience_map": ("financial_resilience_app", "show_resilience_map"),
    "stress_test": ("stress_test_simulator", "show_stress_test_tool")
}

# 1. State Initialization
if 'baseline_locked' not in st.session_state:
    st.session_state.baseline_locked = False
if 'flow_step' not in st.session_state:
    st.session_state.flow_step = "home"

# 2. RUN ENGINE (Always update metrics if locked)
if st.session_state.baseline_locked:
    s = st.session_state
    # Ο Engine υπολογίζει τα πάντα βασισμένος στο 365-day rule
    st.session_state.metrics = calculate_metrics(
        price=float(s.get("price", 100)),
        volume=float(s.get("volume", 1000)),
        variable_cost=float(s.get("variable_cost", 60)),
        fixed_cost=float(s.get("fixed_cost", 20000)),
        ar_days=float(s.get("ar_days", 45)),
        inv_days=float(s.get("inventory_days", 60)),
        ap_days=float(s.get("ap_days", 30)),
        annual_debt_service=float(s.get("annual_debt_service", 0)),
        opening_cash=float(s.get("opening_cash", 10000)),
        target_profit=float(s.get("target_profit_goal", 0))
    )

# 3. Sidebar Navigation
show_sidebar()

# 4. Routing Logic
step = st.session_state.get("flow_step", "home")

if step == "home":
    run_home()

elif step == "tool":
    tool_key = st.session_state.get("selected_tool")
    if tool_key in TOOL_MAP:
        mod_name, func_name = TOOL_MAP[tool_key]
        try:
            # Δυναμικό Import από τον φάκελο core.tools
            module = importlib.import_module(f"core.tools.{mod_name}")
            func = getattr(module, func_name)
            
            if st.button("⬅ Back to Control Tower"):
                st.session_state.flow_step = "home"
                st.session_state.selected_tool = None
                st.rerun()
                
            st.divider()
            func() # Εκτέλεση της συνάρτησης του εργαλείου
            
        except Exception as e:
            st.error(f"❌ Error loading tool '{mod_name}': {e}")
            if st.button("Return Home"):
                st.session_state.flow_step = "home"
                st.rerun()
