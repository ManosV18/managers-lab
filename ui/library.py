import streamlit as st
import importlib

# --- INTERNAL TOOL: PAYABLES MANAGER ---
def show_payables_manager_internal():
    st.header("🤝 Payables Manager: Supplier Credit Analysis")
    st.info("Evaluate cash discounts vs. supplier credit terms (365-day basis).")
    
    col1, col2 = st.columns(2)
    with col1:
        cred_days = st.number_input("Supplier Credit Period (Days)", value=60, key="int_cred_days")
        disc_prc = st.number_input("Cash Discount Offered (%)", value=2.0, key="int_disc_prc") / 100
        cash_take = st.number_input("% of Purchases for Discount", value=50.0, key="int_cash_prc") / 100
    with col2:
        annual_purch = st.number_input("Annual Purchase Volume (€)", value=1000000, key="int_ann_purch")
        wacc = st.number_input("Cost of Capital / Interest (%)", value=10.0, key="int_wacc") / 100

    # Calculation based on instruction [2026-02-18] (365 days)
    disc_gain = annual_purch * disc_prc * cash_take
    opp_cost = (annual_purch * cash_take * (cred_days / 365)) * wacc
    net_benefit = disc_gain - opp_cost

    st.divider()
    c1, c2, c3 = st.columns(3)
    c1.metric("Discount Gain", f"€{disc_gain:,.0f}")
    c2.metric("Credit Opp. Cost", f"-€{opp_cost:,.0f}")
    c3.metric("Net Benefit", f"€{net_benefit:,.0f}", delta=f"{net_benefit:,.0f}")

    if st.button("⬅️ Back to Library Hub", key="back_from_internal"):
        st.session_state.selected_tool = None
        st.rerun()

# --- MAIN LIBRARY FUNCTION ---
def show_library():
    # 1. Sidebar navigation
    if st.sidebar.button("🏠 Exit Library", key="exit_lib"):
        st.session_state.mode = "path"
        st.session_state.flow_step = "home"
        st.session_state.selected_tool = None
        st.rerun()

    st.title("🏛️ Strategic Tool Library")

    # 2. Tool Routing
    if st.session_state.get('selected_tool') is None:
        t1, t2, t3, t4 = st.tabs(["🚀 Strategy & Pricing", "💰 Capital & Finance", "⚙️ Operations & CCC", "🛡️ Risk & Control"])
        
        with t1:
            st.subheader("Core Strategy & Growth")
            if st.button("🎯 Pricing Strategy & Elasticity", use_container_width=True, key="btn_pricing"):
                st.session_state.selected_tool = ("pricing_strategy", "show_pricing_strategy_tool")
                st.rerun()
            if st.button("📉 Loss Threshold (Price Cut)", use_container_width=True, key="btn_loss"):
                st.session_state.selected_tool = ("loss_threshold", "show_loss_threshold_before_price_cut")
                st.rerun()
            if st.button("⚖️ BEP Shift Analysis", use_container_width=True, key="btn_bep"):
                st.session_state.selected_tool = ("break_even_shift_calculator", "show_break_even_shift_calculator")
                st.rerun()
            if st.button("🧭 QSPM Strategy Matrix", use_container_width=True, key="btn_qspm"):
                st.session_state.selected_tool = ("qspm_analyzer", "show_qspm_tool")
                st.rerun()
            if st.button("👥 CLV Simulator", use_container_width=True, key="btn_clv"):
                st.session_state.selected_tool = ("clv_calculator", "show_clv_calculator")
                st.rerun()
        
        with t2:
            st.subheader("Financial Engineering")
            if st.button("📉 WACC Optimizer", use_container_width=True, key="btn_wacc"):
                st.session_state.selected_tool = ("wacc_optimizer", "show_wacc_optimizer")
                st.rerun()
            if st.button("📈 Growth Funding (AFN)", use_container_width=True, key="btn_afn"):
                st.session_state.selected_tool = ("growth_funding", "show_growth_funding_needed")
                st.rerun()
            if st.button("⚖️ Loan vs Leasing Analyzer", use_container_width=True, key="btn_lvl"):
                st.session_state.selected_tool = ("loan_vs_leasing", "loan_vs_leasing_ui")
                st.rerun()

        with t3:
            st.subheader("Tactical Execution")
            if st.button("🔄 Cash Conversion Cycle (CCC)", use_container_width=True, key="btn_ccc"):
                st.session_state.selected_tool = ("cash_cycle", "run_cash_cycle_app")
                st.rerun()
            if st.button("📊 Receivables Analyzer (NPV)", use_container_width=True, key="btn_receivables"):
                st.session_state.selected_tool = ("receivables_analyzer", "show_receivables_analyzer_ui")
                st.rerun()
            if st.button("📦 Inventory Optimizer (EOQ)", use_container_width=True, key="btn_inv"):
                st.session_state.selected_tool = ("inventory_manager", "show_inventory_manager")
                st.rerun()
            if st.button("🤝 Payables Manager", use_container_width=True, key="btn_payables"):
                st.session_state.selected_tool = ("INTERNAL", "show_payables_manager_internal")
                st.rerun()
            if st.button("🔢 Unit Cost Analyzer", use_container_width=True, key="btn_uc"):
                st.session_state.selected_tool = ("unit_cost_analyzer", "show_unit_cost_app")
                st.rerun()

        with t4:
            st.subheader("Executive Command & Risk")
            if st.button("🏁 Executive Command Center", use_container_width=True, key="btn_exec"):
                st.session_state.selected_tool = ("executive_dashboard", "show_executive_dashboard")
                st.rerun()
            if st.button("🚨 Cash Fragility Index", use_container_width=True, key="btn_frag"):
                st.session_state.selected_tool = ("cash_fragility_index", "show_cash_fragility_index")
                st.rerun()
            if st.button("🛡️ Resilience & Shock Map", use_container_width=True, key="btn_res"):
                st.session_state.selected_tool = ("resilience_map", "show_resilience_map")
                st.rerun()

    else:
        # 3. Execution Mode
        mod_name, func_name = st.session_state.selected_tool
        
        # Back button for non-internal tools
        if mod_name != "INTERNAL":
            if st.button("⬅️ Back to Library Hub", key="global_back"):
                st.session_state.selected_tool = None
                st.rerun()
            st.divider()

        # Execute
        if mod_name == "INTERNAL":
            globals()[func_name]()
        else:
            try:
                module = importlib.import_module(f"tools.{mod_name}")
                importlib.reload(module)  # Essential for current development
                tool_func = getattr(module, func_name)
                tool_func()
            except Exception as e:
                st.error(f"❌ Error loading '{mod_name}': {e}")
                if st.button("Reset Selection", key="error_reset"):
                    st.session_state.selected_tool = None
                    st.rerun()

