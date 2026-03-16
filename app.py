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

TOOL_MAP = {

    "executive_dashboard": ("ui.home", "show_executive_dashboard"),
    "decision_report": ("ui.home", "show_decision_report"),
    "scenario_comparison": ("ui.home", "show_scenario_comparison")
}

if "baseline_locked" not in st.session_state:
    st.session_state.baseline_locked = False

if "flow_step" not in st.session_state:
    st.session_state.flow_step = "home"

if "metrics" not in st.session_state:
    st.session_state.metrics = {}

if "selected_tool" not in st.session_state:
    st.session_state.selected_tool = None

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

        col_title.caption(
            f"Strategy Room > {tool_key.replace('_',' ').title()}"
        )

        if col_back.button("⬅ Back to Hub", use_container_width=True):

            st.session_state.flow_step = "home"
            st.rerun()

        st.divider()

        module = importlib.import_module(mod_name)

        func = getattr(module, func_name)

        func()
