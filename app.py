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

    # Strategy & Pricing
    "control_tower": ("control_tower", "show_control_tower"),
    "pricing_strategy": ("pricing_strategy", "show_pricing_strategy_tool"),
    "pricing_radar": ("pricing_radar", "show_pricing_radar"),
    "loss_threshold": ("loss_threshold", "show_loss_threshold_before_price_cut"),
    "qspm_analyzer": ("qspm_analyzer", "show_qspm_tool"),

    # Survival
    "break_even_shift": ("break_even_shift_calculator", "show_break_even_shift_calculator"),

    # Finance
    "wacc_optimizer": ("wacc_optimizer", "show_wacc_optimizer_ui"),
    "loan_vs_leasing": ("loan_vs_leasing", "loan_vs_leasing_ui"),
    "growth_funding": ("growth_funding", "show_growth_funding_needed"),

    # Operations
    "unit_cost_analyzer": ("unit_cost_analyzer", "show_unit_cost_app"),
    "inventory_manager": ("inventory_manager", "show_inventory_manager"),
    "receivables_npv": ("receivables_npv", "show_receivables_analyzer_ui"),
    "cash_cycle": ("cash_cycle", "run_cash_cycle_app"),
    "payables_manager": ("payables_manager", "show_payables_manager"),
    "wc_optimizer": ("working_capital_optimizer", "show_wc_optimizer"),

    # Risk
    "executive_dashboard": ("executive_dashboard", "show_executive_dashboard"),
    "cash_fragility": ("cash_fragility_index", "show_cash_fragility_index"),
    "resilience_map": ("financial_resilience_app", "show_resilience_map"),
    "stress_test": ("stress_test_simulator", "show_stress_test_tool"),
    "clv_calculator": ("clv_calculator", "show_clv_calculator"),
    "shock_simulator": ("company_shock_simulator", "show_company_shock_simulator")

}


# --------------------------------------------------
# STATE INITIALIZATION
# --------------------------------------------------

if "baseline_locked" not in st.session_state:
    st.session_state.baseline_locked = False

if "flow_step" not in st.session_state:
    st.session_state.flow_step = "home"

if "metrics" not in st.session_state:
    st.session_state.metrics = {}

if "selected_tool" not in st.session_state:
    st.session_state.selected_tool = None

# μικρό SaaS touch
st.session_state.setdefault("scenario_name", "Baseline Scenario")


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

        ar_days=float(s.get("ar_days", 45)),
        inv_days=float(s.get("inv_days", 60)),
        ap_days=float(s.get("ap_days", 30)),

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

    # reset tool selection όταν επιστρέφεις στο hub
    st.session_state.selected_tool = None
    run_home()

elif step == "tool":

    tool_key = st.session_state.get("selected_tool")

    if tool_key in TOOL_MAP:

        mod_name, func_name = TOOL_MAP[tool_key]

        col_title, col_back = st.columns([0.8, 0.2])

        col_title.caption(
            f"Strategy Room > {tool_key.replace('_',' ').title()}"
        )

        if col_back.button("⬅ Back to Hub", use_container_width=True):

            st.session_state.flow_step = "home"
            st.rerun()

        st.divider()

        try:

            module = importlib.import_module(f"core.tools.{mod_name}")
            func = getattr(module, func_name)

            func()

        except Exception as e:

            st.error(f"Error loading module: {e}")

