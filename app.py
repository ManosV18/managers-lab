import streamlit as st
import importlib
from ui.sidebar import show_sidebar
from ui.home import run_home
from core.engine import calculate_metrics

st.set_page_config(
    page_title="Managers Lab | Strategy OS",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Εδώ προσθέτουμε ΟΛΑ τα εργαλεία στο TOOL_MAP για να αναγνωρίζονται
TOOL_MAP = {
    "control_tower": ("ui.tools", "run_control_tower"),
    "pricing_strategy": ("ui.tools", "run_pricing_strategy"),
    "pricing_radar": ("ui.tools", "run_pricing_radar"),
    "loss_threshold": ("ui.tools", "run_loss_threshold"),
    "qspm_analyzer": ("ui.tools", "run_qspm_analyzer"),
    "break_even_shift": ("ui.tools", "run_break_even_shift"),
    "clv_calculator": ("ui.tools", "run_clv_calculator"),
    "growth_funding": ("ui.tools", "run_growth_funding"),
    "wacc_optimizer": ("ui.tools", "run_wacc_optimizer"),
    "loan_vs_leasing": ("ui.tools", "run_loan_vs_leasing"),
    "receivables_npv": ("ui.tools", "run_receivables_npv"),
    "cash_cycle": ("ui.tools", "run_cash_cycle"),
    "unit_cost_analyzer": ("ui.tools", "run_unit_cost_analyzer"),
    "inventory_manager": ("ui.tools", "run_inventory_manager"),
    "payables_manager": ("ui.tools", "run_payables_manager"),
    "wc_optimizer": ("ui.tools", "run_wc_optimizer"),
    "shock_simulator": ("ui.tools", "run_shock_simulator"),
    "cash_fragility": ("ui.tools", "run_cash_fragility"),
    "resilience_map": ("ui.tools", "run_resilience_map"),
    "stress_test": ("ui.tools", "run_stress_test"),
    "executive_dashboard": ("ui.home", "show_executive_dashboard"),
    "decision_report": ("ui.home", "show_decision_report"),
    "scenario_comparison": ("ui.home", "show_scenario_comparison")
}

if "baseline_locked" not in st.session_state: st.session_state.baseline_locked = False
if "flow_step" not in st.session_state: st.session_state.flow_step = "home"
if "metrics" not in st.session_state: st.session_state.metrics = {}
if "selected_tool" not in st.session_state: st.session_state.selected_tool = None

show_sidebar()

step = st.session_state.get("flow_step", "home")

if step == "home":
    st.session_state.selected_tool = None
    run_home()
elif step == "tool":
    tool_key = st.session_state.get("selected_tool")
    if tool_key in TOOL_MAP:
        mod_name, func_name = TOOL_MAP[tool_key]
        col_title, col_back = st.columns([0.8, 0.2])
        col_title.caption(f"Strategy Room > {tool_key.replace('_',' ').title()}")
        if col_back.button("⬅ Back to Hub", use_container_width=True):
            st.session_state.flow_step = "home"
            st.rerun()
        st.divider()
        module = importlib.import_module(mod_name)
        getattr(module, func_name)()

# ΥΠΟΛΟΓΙΣΜΟΣ ΣΤΟ ΤΕΛΟΣ ΓΙΑ ΑΠΟΦΥΓΗ ΣΦΑΛΜΑΤΟΣ
if st.session_state.baseline_locked:
    s = st.session_state
    st.session_state.metrics = calculate_metrics(
        price=float(s.get("price", 100.0)),
        volume=float(s.get("volume", 1000.0)),
        variable_cost=float(s.get("variable_cost", 60.0)),
        fixed_cost=float(s.get("fixed_cost", 20000.0)),
        opening_cash=float(s.get("opening_cash", 10000.0))
    )
