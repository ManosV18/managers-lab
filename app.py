import streamlit as st
import importlib

from ui.sidebar import show_sidebar
from ui.home import run_home
from ui.about import show_about  # Εισαγωγή της νέας οθόνης
from core.engine import calculate_metrics

# 1. PAGE CONFIG
st.set_page_config(
    page_title="Managers Lab | Strategy OS",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --------------------------------------------------
# TOOL MAP (Updated: Removing redundant tools)
# --------------------------------------------------
TOOL_MAP = {
    # Strategy & Analysis
    "control_tower": ("core.tools.control_tower", "show_control_tower"),
    "pricing_strategy": ("core.tools.pricing_strategy", "show_pricing_strategy_tool"),
    "pricing_radar": ("core.tools.pricing_radar", "show_pricing_radar"),
    "loss_threshold": ("core.tools.loss_threshold", "show_loss_threshold_before_price_cut"),
    "qspm_analyzer": ("core.tools.qspm_analyzer", "show_qspm_tool"),
    "break_even_shift": ("core.tools.break_even_shift_calculator", "show_break_even_shift_calculator"),

    # Finance
    "wacc_optimizer": ("core.tools.wacc_optimizer", "show_wacc_optimizer_ui"),
    "loan_vs_leasing": ("core.tools.loan_vs_leasing", "loan_vs_leasing_ui"),
    "growth_funding": ("core.tools.growth_funding", "show_growth_funding_needed"),

    # Operations
    "inventory_manager": ("core.tools.inventory_manager", "show_inventory_manager"),
    "receivables_npv": ("core.tools.receivables_npv", "show_receivables_analyzer_ui"),
    "cash_cycle": ("core.tools.cash_cycle", "run_cash_cycle_app"),
    "payables_manager": ("core.tools.payables_manager", "show_payables_manager"),
    "wc_optimizer": ("core.tools.working_capital_optimizer", "show_wc_optimizer"),

    # Risk
    "cash_fragility": ("core.tools.cash_fragility_index", "show_cash_fragility_index"),
    "resilience_map": ("core.tools.financial_resilience_app", "show_resilience_map"),
    "stress_test": ("core.tools.stress_test_simulator", "show_stress_test_tool"),
    "clv_calculator": ("core.tools.clv_calculator", "show_clv_calculator"),
    "shock_simulator": ("core.tools.company_shock_simulator", "show_company_shock_simulator"),
}

# 3. STATE INITIALIZATION & DEFAULTS
s = st.session_state

defaults = {
    "baseline_locked": False,
    "flow_step": "home",
    "selected_tool": None,
    "scenario_name": "Baseline Scenario",
    "price": 150.0,
    "variable_cost": 90.0,
    "volume": 15000,
    "fixed_cost": 450000.0,
    "fixed_assets": 800000.0,
    "depreciation": 50000.0,
    "target_profit_goal": 200000.0,
    "opening_cash": 150000.0,
    "equity": 500000.0,
    "total_debt": 500000.0,
    "annual_interest_only": 0.0,
    "tax_rate": 22.0,
    "ar_days": 60,
    "inv_days": 45,
    "ap_days": 30,
    "annual_debt_service": 70000.0
}

for key, val in defaults.items():
    if key not in s:
        s[key] = val

# 4. RUN FINANCIAL ENGINE
s.metrics = calculate_metrics(
    price=float(s.price),
    volume=float(s.volume),
    variable_cost=float(s.variable_cost),
    fixed_cost=float(s.fixed_cost),
    ar_days=int(s.ar_days),
    inv_days=int(s.inv_days),
    ap_days=int(s.ap_days),
    annual_debt_service=float(s.annual_debt_service),
    opening_cash=float(s.opening_cash),
    total_debt=float(s.total_debt),
    fixed_assets=float(s.fixed_assets),
    target_profit=float(s.target_profit_goal),
    tax_rate=float(s.tax_rate),
    annual_interest=float(s.annual_interest_only),
    equity=float(s.equity),
    depreciation=float(s.depreciation)
)

# ... (προηγούμενος κώδικας 1, 2, 3, 4 παραμένει ίδιος) ...

# 5. SIDEBAR & ROUTING
show_sidebar()
step = s.flow_step

if step == "home":
    s.selected_tool = None
    run_home()
    st.stop()

elif step == "about":
    show_about()
    st.stop()

# --- ΝΕΟ STEP: ΑΠΕΥΘΕΙΑΣ ΣΤΟ CONTROL TOWER ---
elif step == "control_tower":
    # Φορτώνουμε το Control Tower αυτόματα
    mod_name, func_name = TOOL_MAP["control_tower"]
    try:
        module = importlib.import_module(mod_name)
        func = getattr(module, func_name)
        
        # Προσθέτουμε ένα κουμπί επιστροφής στο Home αν θέλει ο χρήστης
        if st.sidebar.button("🏠 Back to Strategy Hub", use_container_width=True):
            s.flow_step = "home"
            st.rerun()
            
        func() # Εκτέλεση του Control Tower
    except Exception as e:
        st.error(f"Error loading Mission Control: {e}")
    st.stop()

elif step == "tool":
    tool_key = s.selected_tool
    if tool_key in TOOL_MAP:
        mod_name, func_name = TOOL_MAP[tool_key]
        
        col_title, col_back = st.columns([0.8, 0.2])
        col_title.caption(f"Strategy Room > {tool_key.replace('_',' ').title()}")
        if col_back.button("⬅ Back to Hub", use_container_width=True):
            # Αν είναι το control tower, ίσως θέλουμε να γυρίζει στο home
            s.flow_step = "home"
            st.rerun()
            
        st.divider()
        
        try:
            module = importlib.import_module(mod_name)
            func = getattr(module, func_name)
            func()
        except Exception as e:
            st.error(f"Error loading module: {e}")


# 5. SIDEBAR & ROUTING
show_sidebar()
step = s.flow_step

if step == "home":
    s.selected_tool = None
    run_home()
    st.stop()

elif step == "about":
    show_about()
    st.stop()

elif step == "tool":
    tool_key = s.selected_tool
    if tool_key in TOOL_MAP:
        mod_name, func_name = TOOL_MAP[tool_key]
        
        col_title, col_back = st.columns([0.8, 0.2])
        col_title.caption(f"Strategy Room > {tool_key.replace('_',' ').title()}")
        if col_back.button("⬅ Back to Hub", use_container_width=True):
            s.flow_step = "home"
            st.rerun()
            
        st.divider()
        
        try:
            module = importlib.import_module(mod_name)
            func = getattr(module, func_name)
            func()
        except Exception as e:
            st.error(f"Error loading module: {e}")
