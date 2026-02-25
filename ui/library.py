import streamlit as st
import importlib
from core.sync import sync_global_state

# --- 1. ΔΥΝΑΜΙΚΟΣ ΜΗΧΑΝΙΣΜΟΣ IMPORT ---
def get_tool_function(module_name, function_name):
    try:
        module = importlib.import_module(f"tools.{module_name}")
        return getattr(module, function_name)
    except (ImportError, AttributeError):
        return None

def show_library():
    metrics = sync_global_state()
    s = st.session_state

    # 2. HEADER & METRICS
    st.title("🏛️ Strategic Tool Library")
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("WACC", f"{s.get('wacc', 0.15):.2%}")
    m2.metric("Unit Margin", f"{metrics.get('unit_contribution', 0.0):,.2f} €")
    m3.metric("Survival BEP", f"{metrics.get('survival_bep', 0):,.0f} u")
    m4.metric("Net Profit", f"{metrics.get('net_profit', 0):,.2f} €")
    st.divider()

    # 3. TOOL DEFINITIONS (Mapping: Key -> [Module_Name, Function_Name, Button_Label])
    tools_config = {
        "dash": ["executive_dashboard", "show_executive_dashboard", "📊 Executive Dashboard"],
        "price_strat": ["pricing_strategy", "show_pricing_strategy", "🎯 Pricing Strategy"],
        "price_radar": ["pricing_power_radar", "show_pricing_power_radar", "📡 Pricing Power Radar"],
        "bep": ["break_even_shift_calculator", "show_break_even_shift_calculator", "⚖️ BEP Shift Analysis"],
        "clv": ["clv_calculator", "show_clv_calculator", "👥 CLV Simulator"],
        "funding": ["growth_funding_needed", "show_growth_funding", "📈 Growth Funding"],
        "wacc": ["wacc_optimizer", "show_wacc_optimizer", "📉 WACC Optimizer"],
        "loan": ["loan_vs_leasing_calculator", "show_loan_leasing", "🏦 Loan vs Leasing"],
        "fragility": ["cash_fragility_index", "show_cash_fragility_index", "🛡️ Cash Fragility"],
        "resilience": ["financial_resilience_app", "show_financial_resilience", "💎 Financial Resilience"],
        "loss": ["loss_threshold", "show_loss_threshold", "🛑 Loss Threshold"],
        "ccc": ["cash_cycle", "run_cash_cycle_app", "🔄 Cash Cycle (CCC)"],
        "inv": ["inventory_manager", "show_inventory_manager", "📦 Inventory Manager"],
        "ar": ["receivables_analyzer", "show_receivables_analyzer", "💳 Receivables Analyzer"],
        "ap": ["payables_manager", "show_payables_manager", "💸 Payables Manager"],
        "unit": ["unit_cost_app", "show_unit_cost_analyzer", "🧪 Unit Cost Analyzer"],
        "stress": ["stress_test_simulator", "show_stress_test", "🌪️ Stress Test Sim"],
        "qspm": ["qspm_two_strategies", "show_qspm", "📋 QSPM Analysis"]
    }

    # 4. ROUTER LOGIC
    if s.get('selected_tool') is None:
        c1, c2, c3, c4 = st.columns(4)
        
        # Κατανομή εργαλείων στις στήλες
        for i, (key, cfg) in enumerate(tools_config.items()):
            col = [c1, c2, c3, c4][i % 4]
            if col.button(cfg[2], key=key, use_container_width=True):
                s.selected_tool = key
                st.rerun()
    else:
        # ΕΜΦΑΝΙΣΗ ΕΡΓΑΛΕΙΟΥ
        if st.button("⬅️ Back to Categories", type="primary"):
            s.selected_tool = None
            st.rerun()
        
        st.divider()
        
        cfg = tools_config.get(s.selected_tool)
        if cfg:
            tool_func = get_tool_function(cfg[0], cfg[1])
            if tool_func:
                tool_func()
            else:
                st.error(f"🚫 **Tool Connection Error**")
                st.warning(f"Το αρχείο `tools/{cfg[0]}.py` βρέθηκε, αλλά η συνάρτηση `{cfg[1]}` λείπει ή έχει σφάλμα.")
                st.info("Άνοιξε το αρχείο και βεβαιώσου ότι η συνάρτηση ονομάζεται ακριβώς έτσι.")

    # 5. SIDEBAR
    st.sidebar.divider()
    if st.sidebar.button("🚀 Exit Library"):
        s.selected_tool = None
        s.mode = "path"
        st.rerun()
