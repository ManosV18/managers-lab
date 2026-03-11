import streamlit as st
import importlib
from ui.sidebar import show_sidebar
from ui.home import run_home
from core.engine import calculate_metrics

# 1. Page Configuration
st.set_page_config(
    page_title="Managers Lab | Strategy OS",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 2. TOOL_MAP: Η Πλήρης Καλωδίωση για όλα τα αρχεία σου
TOOL_MAP = {
    # --- Strategy & Pricing ---
    "pricing_strategy": ("pricing_strategy", "show_pricing_strategy_tool"),
    "pricing_radar": ("pricing_radar", "show_pricing_radar"),
    "loss_threshold": ("loss_threshold", "show_loss_threshold_before_price_cut"),
    "qspm_analyzer": ("qspm_analyzer", "show_qspm_tool"),
    
    # --- Survival & Break-Even ---
    "break_even_shift": ("break_even_shift_calculator", "show_break_even_shift_calculator"),
    
    # --- Finance & Debt ---
    "wacc_optimizer": ("wacc_optimizer", "show_wacc_optimizer_ui"),
    "loan_vs_leasing": ("loan_vs_leasing", "loan_vs_leasing_ui"),
    "growth_funding": ("growth_funding", "show_growth_funding_needed"),
    
    # --- Operations & Cash Cycle ---
    "unit_cost_analyzer": ("unit_cost_analyzer", "show_unit_cost_app"),
    "inventory_manager": ("inventory_manager", "show_inventory_manager"),
    "receivables_npv": ("receivables_npv", "show_receivables_analyzer_ui"),
    "cash_cycle": ("cash_cycle", "run_cash_cycle_app"),
    "payables_manager": ("payables_manager", "show_payables_manager"),
    
    # --- Risk & Dashboards ---
    "executive_dashboard": ("executive_dashboard", "show_executive_dashboard"),
    "cash_fragility": ("cash_fragility_index", "show_cash_fragility_index"),
    "resilience_map": ("financial_resilience_app", "show_resilience_map"),
    "stress_test": ("stress_test_simulator", "show_stress_test_tool"),
    "clv_calculator": ("clv_calculator", "show_clv_calculator") # Αν η συνάρτηση λέγεται έτσι
}

# 3. State Initialization (The Global Notebook)
if 'baseline_locked' not in st.session_state:
    st.session_state.baseline_locked = False
if 'flow_step' not in st.session_state:
    st.session_state.flow_step = "home"
if 'metrics' not in st.session_state:
    st.session_state.metrics = {}
if 'selected_tool' not in st.session_state:
    st.session_state.selected_tool = None

# 4. RUN ENGINE (Calculates the "Shock Absorption" metrics)
# User Instruction [2026-02-18]: Υπολογισμός με 365 ημέρες
if st.session_state.baseline_locked:
    s = st.session_state
    try:
        st.session_state.metrics = calculate_metrics(
            price=float(s.get("price", 100)),
            volume=float(s.get("volume", 1000)),
            variable_cost=float(s.get("variable_cost", 60)),
            fixed_cost=float(s.get("fixed_cost", 20000)),
            ar_days=float(s.get("ar_days", 45)),
            inv_days=float(s.get("inv_days", 60)), # Χρήση inv_days για συνέπεια
            ap_days=float(s.get("ap_days", 30)),
            annual_debt_service=float(s.get("annual_debt_service", 0)),
            opening_cash=float(s.get("opening_cash", 10000)),
            target_profit=float(s.get("target_profit_goal", 0))
        )
    except Exception as e:
        st.warning("Engine Calculation Pending: Ensure all numeric inputs are valid.")

# 5. UI Layout: Sidebar
show_sidebar()

# 6. Routing Logic (The Dispatcher)
step = st.session_state.get("flow_step", "home")

if step == "home":
    run_home()

elif step == "tool":
    tool_key = st.session_state.get("selected_tool")
    
    if tool_key in TOOL_MAP:
        mod_name, func_name = TOOL_MAP[tool_key]
        
        # UI Header for the Tool view
        col_title, col_back = st.columns([0.8, 0.2])
        friendly_name = tool_key.replace('_', ' ').title()
        col_title.caption(f"Strategy Room > {friendly_name}")
        
        if col_back.button("⬅ Back to Hub", use_container_width=True, key="global_back_btn"):
            st.session_state.flow_step = "home"
            st.session_state.selected_tool = None
            st.rerun()
            
        st.divider()

        try:
            # Δυναμικό Import από τον φάκελο core.tools
            module = importlib.import_module(f"core.tools.{mod_name}")
            func = getattr(module, func_name)
            
            # ΕΚΤΕΛΕΣΗ ΤΟΥ ΕΡΓΑΛΕΙΟΥ
            func()
            
        except ModuleNotFoundError:
            st.error(f"❌ Σφάλμα: Το αρχείο `core/tools/{mod_name}.py` δεν βρέθηκε.")
        except AttributeError:
            st.error(f"❌ Σφάλμα: Η συνάρτηση `{func_name}` δεν υπάρχει στο αρχείο `{mod_name}.py`.")
        except Exception as e:
            st.error(f"❌ Λειτουργικό Σφάλμα: {e}")
            if st.button("Emergency Return Home"):
                st.session_state.flow_step = "home"
                st.rerun()
    else:
        st.error(f"Unknown Tool Selected: {tool_key}")
        if st.button("Return Home"):
            st.session_state.flow_step = "home"
            st.rerun()
