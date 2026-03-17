import streamlit as st
import importlib

from ui.sidebar import show_sidebar
from ui.home import run_home
from core.engine import calculate_metrics

# --------------------------------------------------
# PAGE CONFIG
# --------------------------------------------------

st.set_page_config(
    page_title="Managers Lab | Strategy OS",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --------------------------------------------------
# TOOL MAP
# --------------------------------------------------

TOOL_MAP = {
    # Strategy
    "control_tower": ("core.tools.control_tower", "show_control_tower"),
    "pricing_strategy": ("core.tools.pricing_strategy", "show_pricing_strategy_tool"),
    "pricing_radar": ("core.tools.pricing_radar", "show_pricing_radar"),
    "loss_threshold": ("core.tools.loss_threshold", "show_loss_threshold_before_price_cut"),
    "qspm_analyzer": ("core.tools.qspm_analyzer", "show_qspm_tool"),

    # Survival
    "break_even_shift": ("core.tools.break_even_shift_calculator", "show_break_even_shift_calculator"),

    # Finance
    "wacc_optimizer": ("core.tools.wacc_optimizer", "show_wacc_optimizer_ui"),
    "loan_vs_leasing": ("core.tools.loan_vs_leasing", "loan_vs_leasing_ui"),
    "growth_funding": ("core.tools.growth_funding", "show_growth_funding_needed"),

    # Operations
    "unit_cost_analyzer": ("core.tools.unit_cost_analyzer", "show_unit_cost_app"),
    "inventory_manager": ("core.tools.inventory_manager", "show_inventory_manager"),
    "receivables_npv": ("core.tools.receivables_npv", "show_receivables_analyzer_ui"),
    "cash_cycle": ("core.tools.cash_cycle", "run_cash_cycle_app"),
    "payables_manager": ("core.tools.payables_manager", "show_payables_manager"),
    "wc_optimizer": ("core.tools.working_capital_optimizer", "show_wc_optimizer"),

    # Risk
    "executive_dashboard": ("ui.home", "show_executive_dashboard"),
    "cash_fragility": ("core.tools.cash_fragility_index", "show_cash_fragility_index"),
    "resilience_map": ("core.tools.financial_resilience_app", "show_resilience_map"),
    "stress_test": ("core.tools.stress_test_simulator", "show_stress_test_tool"),
    "clv_calculator": ("core.tools.clv_calculator", "show_clv_calculator"),
    "shock_simulator": ("core.tools.company_shock_simulator", "show_company_shock_simulator"),

    # Reports
    "decision_report": ("ui.home", "show_decision_report"),
    "scenario_comparison": ("ui.home", "show_scenario_comparison")
}

# --------------------------------------------------
# STATE INITIALIZATION
# --------------------------------------------------

if "baseline_locked" not in st.session_state:
    st.session_state.baseline_locked = False

if "flow_step" not in st.session_state:
    st.session_state.flow_step = "home"

if "metrics" not in st.session_state or st.session_state.metrics is None:
    st.session_state.metrics = {}

if "selected_tool" not in st.session_state:
    st.session_state.selected_tool = None

if "scenario_name" not in st.session_state:
    st.session_state.scenario_name = "Baseline Scenario"

# --------------------------------------------------
# RUN FINANCIAL ENGINE
# --------------------------------------------------

if st.session_state.baseline_locked:
    s = st.session_state
    st.session_state.metrics = calculate_metrics(
        price=float(s.get("price", 100)),
        volume=float(s.get("volume", 1000)),
        variable_cost=float(s.get("variable_cost", 60)),
        fixed_cost=float(s.get("fixed_cost", 20000)),
        ar_days=int(s.get("ar_days", 45)),
        inv_days=int(s.get("inv_days", 60)),
        ap_days=int(s.get("ap_days", 30)),
        annual_debt_service=float(s.get("annual_debt_service", 0)),
        opening_cash=float(s.get("opening_cash", 10000)),
        target_profit=float(s.get("target_profit_goal", 0))
    )

# --------------------------------------------------
# SIDEBAR
# --------------------------------------------------

show_sidebar()

# --------------------------------------------------
# ROUTING
# --------------------------------------------------

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
        try:
            module = importlib.import_module(mod_name)
            func = getattr(module, func_name)
            func()
        except Exception as e:
            st.error(f"Error loading module: {e}")
