import streamlit as st
from core.sync import lock_baseline

def run_home():
    s = st.session_state

    # --- HERO SECTION ---
    st.markdown(
        f"""
        <div style="text-align:center; padding: 20px 0 30px 0;">
            <h1 style="font-size:72px; font-weight:900; color:#1E3A8A; margin-bottom:0px; letter-spacing:-1px; line-height:1;">Managers Lab<span style="color:#ef4444;">.</span></h1>
            <div style="font-size:22px; font-weight:400; color:#64748b; letter-spacing:3px; text-transform:uppercase; margin-top:10px; margin-bottom:30px;">🛡️ Strategic Decision Room</div>
            <div style="max-width:850px; margin: 0 auto; border-top: 2px solid #f1f5f9; padding-top: 25px;">
                <h2 style="font-size:28px; font-weight:600; color:#1e293b; line-height:1.2; margin-bottom:10px;">Analyze the outcome before the execution.</h2>
                <p style="font-size:19px; color:#475569; line-height:1.5;">A cold, analytical simulator for evaluating price shifts, cost structures, and cash resilience based on a <b>365-day</b> fiscal cycle.</p>
            </div>
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

        if s.get('baseline_locked', False):
            st.success("✅ Baseline is currently LOCKED")
        else:
            st.warning("🔓 Baseline is OPEN (Adjust values below)")

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

        col_btn1, col_btn2 = st.columns(2)
        with col_btn1:
            if st.button("🔒 Lock Baseline", use_container_width=True, type="primary"):
                lock_baseline()
                st.rerun()
        with col_btn2:
            if st.button("🔄 Reset All Data", type="secondary", use_container_width=True):
                st.session_state.clear()
                st.session_state.flow_step = "home"
                st.rerun()

    # RIGHT COLUMN: Tool Tabs
    with col_nav:
        st.subheader("📊 Strategic Tool Library")
        t1, t2, t3, t4 = st.tabs(["🚀 Strategy", "💰 Finance", "⚙️ Ops", "🛡️ Risk"])

        with t1:
            if st.button("🎯 Pricing Strategy", use_container_width=True):
                s.selected_tool = ("pricing_strategy", "show_pricing_strategy_tool"); s.flow_step = "library"; st.rerun()
            if st.button("⚖️ BEP Shift Analysis", use_container_width=True):
                s.selected_tool = ("break_even_shift_calculator", "show_break_even_shift_calculator"); s.flow_step = "library"; st.rerun()
            if st.button("📡 Pricing Radar", use_container_width=True):
                s.selected_tool = ("pricing_radar", "show_pricing_radar"); s.flow_step = "library"; st.rerun()
            if st.button("📉 Loss Threshold", use_container_width=True):
                s.selected_tool = ("loss_threshold", "show_loss_threshold_before_price_cut"); s.flow_step = "library"; st.rerun()
            if st.button("🧭 QSPM Strategy Matrix", use_container_width=True):
                s.selected_tool = ("qspm_analyzer", "show_qspm_tool"); s.flow_step = "library"; st.rerun()
            if st.button("👥 CLV Simulator", use_container_width=True):
                s.selected_tool = ("clv_calculator", "show_clv_calculator"); s.flow_step = "library"; st.rerun()

        with t2:
            if st.button("📈 Growth Funding (AFN)", use_container_width=True):
                s.selected_tool = ("growth_funding", "show_growth_funding_needed"); s.flow_step = "library"; st.rerun()
            if st.button("📉 WACC Optimizer", use_container_width=True):
                s.selected_tool = ("wacc_optimizer", "show_wacc_optimizer"); s.flow_step = "library"; st.rerun()
            if st.button("⚖️ Loan vs Leasing", use_container_width=True):
                s.selected_tool = ("loan_vs_leasing", "loan_vs_leasing_ui"); s.flow_step = "library"; st.rerun()

        with t3:
            if st.button("🔄 Cash Conversion Cycle", use_container_width=True):
                s.selected_tool = ("cash_cycle", "run_cash_cycle_app"); s.flow_step = "library"; st.rerun()
            if st.button("🔢 Unit Cost Analyzer", use_container_width=True):
                s.selected_tool = ("unit_cost_analyzer", "show_unit_cost_app"); s.flow_step = "library"; st.rerun()
            if st.button("📦 Inventory Optimizer", use_container_width=True):
                s.selected_tool = ("inventory_manager", "show_inventory_manager"); s.flow_step = "library"; st.rerun()
            if st.button("🤝 Payables Manager", use_container_width=True):
                s.selected_tool = ("INTERNAL", "show_payables_manager_internal"); s.flow_step = "library"; st.rerun()

        with t4:
            if st.button("🏁 Executive Dashboard", use_container_width=True):
                s.selected_tool = ("executive_dashboard", "show_executive_dashboard"); s.flow_step = "library"; st.rerun()
            if st.button("🚨 Cash Fragility Index", use_container_width=True):
                s.selected_tool = ("cash_fragility_index", "show_cash_fragility_index"); s.flow_step = "library"; st.rerun()
            if st.button("🛡️ Resilience & Shock Map", use_container_width=True):
                s.selected_tool = ("financial_resilience_app", "show_resilience_map"); s.flow_step = "library"; st.rerun()
            if st.button("📉 Stress Test Simulator", use_container_width=True):
                s.selected_tool = ("stress_test_simulator", "show_stress_test_tool"); s.flow_step = "library"; st.rerun()

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
