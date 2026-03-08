import streamlit as st

def run_home():
    st.markdown("<h1 style='text-align: center;'>🛡️ Strategic Decision Room</h1>", unsafe_allow_html=True)
    st.divider()

    # --- MAIN LAYOUT ---
    col_input, col_nav = st.columns([0.45, 0.55], gap="large")

    # LEFT COLUMN: Global Parameters (The "Engine Room")
    with col_input:
        st.subheader("⚙️ Global Parameters")
        with st.expander("Business Baseline", expanded=True):
            st.session_state.price = st.number_input("Unit Price (€)", value=float(st.session_state.get('price', 100.0)))
            st.session_state.variable_cost = st.number_input("Variable Cost (€)", value=float(st.session_state.get('variable_cost', 60.0)))
            st.session_state.volume = st.number_input("Annual Volume", value=int(st.session_state.get('volume', 1000)))
            st.session_state.fixed_cost = st.number_input("Annual Fixed Costs (€)", value=float(st.session_state.get('fixed_cost', 20000.0)))
        
        with st.expander("Financials & Working Capital"):
            st.session_state.opening_cash = st.number_input("Opening Cash (€)", value=float(st.session_state.get('opening_cash', 10000.0)))
            st.session_state.annual_debt_service = st.number_input("Annual Debt Service (€)", value=float(st.session_state.get('annual_debt_service', 0.0)))
            st.session_state.ar_days = st.number_input("AR Days (Collection)", value=float(st.session_state.get('ar_days', 45.0)))
            st.session_state.inventory_days = st.number_input("Inventory Days", value=float(st.session_state.get('inventory_days', 60.0)))
            st.session_state.ap_days = st.number_input("AP Days (Payment)", value=float(st.session_state.get('ap_days', 30.0)))

        if st.button("🔄 Reset All Data (Zero-Base)", type="secondary", use_container_width=True):
            st.session_state.clear()
            st.rerun()

    # RIGHT COLUMN: The 18 Tools Hub
    with col_nav:
        st.subheader("📊 Strategic Tool Library")
        t1, t2, t3, t4 = st.tabs(["🚀 Strategy", "💰 Finance", "⚙️ Ops", "🛡️ Risk"])

        with t1: # Strategy & Pricing (6 Tools)
            if st.button("🎯 Pricing Strategy", use_container_width=True):
                st.session_state.selected_tool = ("pricing_strategy", "show_pricing_strategy_tool"); st.session_state.flow_step = "library"; st.rerun()
            st.caption("Which pricing strategy will maximize my profit?")

            if st.button("⚖️ BEP Shift Analysis", use_container_width=True):
                st.session_state.selected_tool = ("break_even_shift_calculator", "show_break_even_shift_calculator"); st.session_state.flow_step = "library"; st.rerun()
            st.caption("If I change the price or costs increase, how many units do I need to sell?")

            if st.button("📡 Pricing Radar", use_container_width=True):
                st.session_state.selected_tool = ("pricing_radar", "show_pricing_radar"); st.session_state.flow_step = "library"; st.rerun()
            st.caption("How do price changes affect competition and sales?")

            if st.button("📉 Loss Threshold", use_container_width=True):
                st.session_state.selected_tool = ("loss_threshold", "show_loss_threshold_before_price_cut"); st.session_state.flow_step = "library"; st.rerun()
            st.caption("How much price reduction can I withstand before the business is at risk?")

            if st.button("🧭 QSPM Strategy Matrix", use_container_width=True):
                st.session_state.selected_tool = ("qspm_analyzer", "show_qspm_tool"); st.session_state.flow_step = "library"; st.rerun()
            st.caption("What is the optimal strategic plan based on critical factors?")

            if st.button("👥 CLV Simulator", use_container_width=True):
                st.session_state.selected_tool = ("clv_calculator", "show_clv_calculator"); st.session_state.flow_step = "library"; st.rerun()
            st.caption("What is the total value of my customers over the entire relationship?")

        with t2: # Capital & Finance (3 Tools)
            if st.button("📈 Growth Funding (AFN)", use_container_width=True):
                st.session_state.selected_tool = ("growth_funding", "show_growth_funding_needed"); st.session_state.flow_step = "library"; st.rerun()
            st.caption("How can I fund growth and calculate my capital needs?")

            if st.button("📉 WACC Optimizer", use_container_width=True):
                st.session_state.selected_tool = ("wacc_optimizer", "show_wacc_optimizer"); st.session_state.flow_step = "library"; st.rerun()
            st.caption("How can I find the optimal cost of capital for my investments?")

            if st.button("⚖️ Loan vs Leasing", use_container_width=True):
                st.session_state.selected_tool = ("loan_vs_leasing", "loan_vs_leasing_ui"); st.session_state.flow_step = "library"; st.rerun()
            st.caption("Which is better: a loan or leasing for my equipment?")

        with t3: # Operations & CCC (5 Tools)
            if st.button("🔄 Cash Conversion Cycle", use_container_width=True):
                st.session_state.selected_tool = ("cash_cycle", "run_cash_cycle_app"); st.session_state.flow_step = "library"; st.rerun()
            st.caption("How fast do my sales convert into cash?")

            if st.button("🔢 Unit Cost Analyzer", use_container_width=True):
                st.session_state.selected_tool = ("unit_cost_analyzer", "show_unit_cost_app"); st.session_state.flow_step = "library"; st.rerun()
            st.caption("What is the actual cost to produce each unit of product?")

            if st.button("📦 Inventory Optimizer", use_container_width=True):
                st.session_state.selected_tool = ("inventory_manager", "show_inventory_manager"); st.session_state.flow_step = "library"; st.rerun()
            st.caption("How much inventory do I need to meet demand without waste?")

            if st.button("🤝 Payables Manager", use_container_width=True):
                st.session_state.selected_tool = ("INTERNAL", "show_payables_manager_internal"); st.session_state.flow_step = "library"; st.rerun()
            st.caption("How can I manage my supplier payments to maintain liquidity?")

            if st.button("📊 Receivables Analyzer", use_container_width=True):
                st.session_state.selected_tool = ("receivables_analyzer", "show_receivables_analyzer_ui"); st.session_state.flow_step = "library"; st.rerun()
            st.caption("How can I manage receivables and reduce default risk?")

        with t4: # Risk & Executive (4 Tools)
            if st.button("🏁 Executive Dashboard", use_container_width=True):
                st.session_state.selected_tool = ("executive_dashboard", "show_executive_dashboard"); st.session_state.flow_step = "library"; st.rerun()
            st.caption("I want to see my business’s key metrics in a single dashboard.")

            if st.button("🚨 Cash Fragility Index", use_container_width=True):
                st.session_state.selected_tool = ("cash_fragility_index", "show_cash_fragility_index"); st.session_state.flow_step = "library"; st.rerun()
            st.caption("If revenue stopped today, how long could my business survive?")

            if st.button("🛡️ Resilience & Shock Map", use_container_width=True):
                st.session_state.selected_tool = ("financial_resilience_app", "show_resilience_map"); st.session_state.flow_step = "library"; st.rerun()
            st.caption("How resilient is my business under unforeseen pressures?")

            if st.button("📉 Stress Test Simulator", use_container_width=True):
                st.session_state.selected_tool = ("stress_test_simulator", "show_stress_test_tool"); st.session_state.flow_step = "library"; st.rerun()
            st.caption("How will my business withstand extreme financial conditions?")

    # --- FOOTER NAVIGATION ---
    st.divider()
    st.subheader("🏁 Full Sequential Stages")
    cols = st.columns(5)
    for i in range(1, 6):
        if cols[i-1].button(f"Go to Stage {i}", use_container_width=True):
            if st.session_state.get('price', 0) > 0:
                st.session_state.flow_step = f"stage{i}"
                st.rerun()
            else:
                st.error("Please set Price first.")
