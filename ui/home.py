import streamlit as st
from core.sync import lock_baseline

def run_home():

    s = st.session_state

    # --- HERO SECTION ---
    st.markdown(
        """
        <div style="text-align:center; padding: 30px 0;">
            <h1 style="font-size:48px;">🛡️ Strategic Decision Room</h1>
            <h2 style="font-size:28px; font-weight:600; margin-top:10px;">
                See the real impact on your cash and survival before committing
            </h2>
            <h3 style="font-size:20px; font-weight:normal; color:#555; margin-top:10px;">
                Change prices, costs, or volumes and instantly see the effect on profit, break-even, and cash survival.
            </h3>
            <p style="font-size:18px; color:#777; margin-top:15px;">
                Know the outcome before you spend a euro.
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )
    st.divider()

    # --- MAIN LAYOUT ---
    col_input, col_nav = st.columns([0.45, 0.55], gap="large")

    # LEFT COLUMN: Global Parameters
    with col_input:
        st.subheader("⚙️ Global Parameters")
        with st.expander("Business Baseline", expanded=True):
            s.price = st.number_input("Unit Price (€)", value=float(s.get('price', 100.0)))
            s.variable_cost = st.number_input("Variable Cost (€)", value=float(s.get('variable_cost', 60.0)))
            s.volume = st.number_input("Annual Volume", value=int(s.get('volume', 1000)))
            s.fixed_cost = st.number_input("Annual Fixed Costs (€)", value=float(s.get('fixed_cost', 20000.0)))
        
        with st.expander("Financials & Working Capital"):
            s.opening_cash = st.number_input("Opening Cash (€)", value=float(s.get('opening_cash', 10000.0)))
            s.annual_debt_service = st.number_input("Annual Debt Service (€)", value=float(s.get('annual_debt_service', 0.0)))
            s.ar_days = st.number_input("AR Days (Collection)", value=float(s.get('ar_days', 45.0)))
            s.inventory_days = st.number_input("Inventory Days", value=float(s.get('inventory_days', 60.0)))
            s.ap_days = st.number_input("AP Days (Payment)", value=float(s.get('ap_days', 30.0)))

        if st.button("🔄 Reset All Data (Zero-Base)", type="secondary", use_container_width=True):
            st.session_state.clear()
            s.flow_step = "home"
            st.rerun()

    # RIGHT COLUMN: All 18 Tools Categorized
    with col_nav:
        st.subheader("📊 Strategic Tool Library")
        t1, t2, t3, t4 = st.tabs(["🚀 Strategy", "💰 Finance", "⚙️ Ops", "🛡️ Risk"])

        with t1: # Strategy & Pricing (6 Tools)
            if st.button("🎯 Pricing Strategy", use_container_width=True):
                s.selected_tool = ("pricing_strategy", "show_pricing_strategy_tool"); s.flow_step = "library"; st.rerun()
            st.caption("Which pricing strategy will maximize my profit?")

            if st.button("⚖️ BEP Shift Analysis", use_container_width=True):
                s.selected_tool = ("break_even_shift_calculator", "show_break_even_shift_calculator"); s.flow_step = "library"; st.rerun()
            st.caption("If I change the price or costs increase, how many units do I need to sell to cover my expenses?")

            if st.button("📡 Pricing Radar", use_container_width=True):
                s.selected_tool = ("pricing_radar", "show_pricing_radar"); s.flow_step = "library"; st.rerun()
            st.caption("How do price changes affect competition and sales?")

            if st.button("📉 Loss Threshold", use_container_width=True):
                s.selected_tool = ("loss_threshold", "show_loss_threshold_before_price_cut"); s.flow_step = "library"; st.rerun()
            st.caption("How much price reduction can I withstand before the business is at risk?")

            if st.button("🧭 QSPM Strategy Matrix", use_container_width=True):
                s.selected_tool = ("qspm_analyzer", "show_qspm_tool"); s.flow_step = "library"; st.rerun()
            st.caption("What is the optimal strategic plan based on critical factors?")

            if st.button("👥 CLV Simulator", use_container_width=True):
                s.selected_tool = ("clv_calculator", "show_clv_calculator"); s.flow_step = "library"; st.rerun()
            st.caption("What is the total value of my customers over the entire relationship?")

        with t2: # Capital & Finance (4 Tools)
            if st.button("📈 Growth Funding (AFN)", use_container_width=True):
                s.selected_tool = ("growth_funding", "show_growth_funding_needed"); s.flow_step = "library"; st.rerun()
            st.caption("How can I fund growth and calculate my capital needs?")

            if st.button("📉 WACC Optimizer", use_container_width=True):
                s.selected_tool = ("wacc_optimizer", "show_wacc_optimizer"); s.flow_step = "library"; st.rerun()
            st.caption("How can I find the optimal cost of capital for my investments?")

            if st.button("⚖️ Loan vs Leasing", use_container_width=True):
                s.selected_tool = ("loan_vs_leasing", "loan_vs_leasing_ui"); s.flow_step = "library"; st.rerun()
            st.caption("Which is better: a loan or leasing for my equipment?")

        with t3: # Operations & CCC (4 Tools)
            if st.button("🔄 Cash Conversion Cycle", use_container_width=True):
                s.selected_tool = ("cash_cycle", "run_cash_cycle_app"); s.flow_step = "library"; st.rerun()
            st.caption("How fast do my sales convert into cash?")

            if st.button("🔢 Unit Cost Analyzer", use_container_width=True):
                s.selected_tool = ("unit_cost_analyzer", "show_unit_cost_app"); s.flow_step = "library"; st.rerun()
            st.caption("What is the actual cost to produce each unit of product?")

            if st.button("📦 Inventory Optimizer", use_container_width=True):
                s.selected_tool = ("inventory_manager", "show_inventory_manager"); s.flow_step = "library"; st.rerun()
            st.caption("How much inventory do I need to meet demand without waste?")

            if st.button("🤝 Payables Manager", use_container_width=True):
                s.selected_tool = ("INTERNAL", "show_payables_manager_internal"); s.flow_step = "library"; st.rerun()
            st.caption("How can I manage my supplier payments to maintain liquidity?")

        with t4: # Risk & Executive (4 Tools)
            if st.button("🏁 Executive Dashboard", use_container_width=True):
                s.selected_tool = ("executive_dashboard", "show_executive_dashboard"); s.flow_step = "library"; st.rerun()
            st.caption("I want to see my business’s key metrics in a single dashboard.")

            if st.button("🚨 Cash Fragility Index", use_container_width=True):
                s.selected_tool = ("cash_fragility_index", "show_cash_fragility_index"); s.flow_step = "library"; st.rerun()
            st.caption("If revenue stopped today, how long could my business survive?")

            if st.button("🛡️ Resilience & Shock Map", use_container_width=True):
                s.selected_tool = ("financial_resilience_app", "show_resilience_map"); s.flow_step = "library"; st.rerun()
            st.caption("How resilient is my business under unforeseen pressures?")

            if st.button("📉 Stress Test Simulator", use_container_width=True):
                s.selected_tool = ("stress_test_simulator", "show_stress_test_tool"); s.flow_step = "library"; st.rerun()
            st.caption("How will my business withstand extreme financial conditions?")

    # --- FOOTER NAVIGATION ---
    st.divider()
    st.subheader("🏁 Full Sequential Stages")
    cols = st.columns(5)
    for i in range(1, 6):
        if cols[i-1].button(f"Go to Stage {i}", use_container_width=True):
            if s.get('price', 0) > 0:
                s.flow_step = f"stage{i}"
                st.rerun()
            else:
                st.error("Please set Price first.")
