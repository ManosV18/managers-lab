import streamlit as st
import importlib
from ui.sidebar import show_sidebar
from ui.home import run_home
from core.engine import calculate_metrics

st.set_page_config(page_title="Managers Lab", layout="wide")

# Mapping: UI Key -> (Module Name, Function Name)
TOOL_MAP = {
    "survival_simulator": ("survival", "show_survival_tool"),
    "pricing_impact": ("pricing", "show_pricing_tool"),
    "clv_analyzer": ("clv", "show_clv_tool")
}

# 1. State Initialization
if 'baseline_locked' not in st.session_state:
    st.session_state.baseline_locked = False
if 'flow_step' not in st.session_state:
    st.session_state.flow_step = "home"

# 2. RUN ENGINE (Always update metrics if locked)
if st.session_state.baseline_locked:
    s = st.session_state
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
            module = importlib.import_module(f"core.tools.{mod_name}")
            func = getattr(module, func_name)
            
            if st.button("⬅ Back to Dashboard"):
                st.session_state.flow_step = "home"
                st.session_state.selected_tool = None
                st.rerun()
                
            st.divider()
            func()
            
        except Exception as e:
            st.error(f"❌ Error loading tool: {e}")
            if st.button("Return Home"):
                st.session_state.flow_step = "home"
                st.rerun()
