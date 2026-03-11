import streamlit as st

def run_home():
    s = st.session_state

    # --- 1. DATA SYNC & INITIALIZATION ---
    # Χρήση καθαρών keys για αμφίδρομη κίνηση με όλα τα εργαλεία
    p = s.get("price", 100.0)
    vc = s.get("variable_cost", 60.0)
    v = s.get("volume", 1000)
    fc = s.get("fixed_cost", 20000.0)
    ads = s.get("annual_debt_service", 0.0) 
    cash = s.get("opening_cash", 10000.0)
    tp = s.get("target_profit_goal", 0.0)

    # Core Calculations (Βάσει 365 ημερών)
    margin = p - vc
    cash_wall = fc + ads + tp
    bep_units = cash_wall / margin if margin > 0 else 0
    margin_of_safety = v - bep_units
    buffer_pct = (margin_of_safety / v * 100) if v > 0 else 0

    # --- HERO SECTION ---
    st.markdown(
        f"""
        <div style="text-align:center; padding: 10px 0 20px 0;">
            <h1 style="font-size:62px; font-weight:900; color:#1E3A8A; margin-bottom:0px;">Managers Lab<span style="color:#ef4444;">.</span></h1>
            <div style="font-size:18px; color:#64748b; letter-spacing:2px; text-transform:uppercase;">🛡️ Strategic Decision Room</div>
        </div>
        """,
        unsafe_allow_html=True
    )

    # --- EXECUTIVE SNAPSHOT ---
    st.subheader("📊 Executive Snapshot")
    c1, c2, c3, c4, c5 = st.columns(5)
    
    c1.metric("Simulated Volume", f"{v:,.0f} units")
    c2.metric("Unit Contribution", f"€{margin:,.2f}")
    c3.metric(
        label="Cash Break-Even", 
        value=f"{bep_units:,.0f} units", 
        delta=f"{margin_of_safety:,.0f} surplus" if margin_of_safety >= 0 else f"{abs(margin_of_safety):,.0f} deficit",
        delta_color="normal" if margin_of_safety >= 0 else "inverse"
    )
    c4.metric("Survival Buffer", f"{buffer_pct:.1f}%", delta="Risk Headroom")
    c5.metric("Cash Position", f"€{cash:,.0f}")

    st.divider()

    # --- MAIN LAYOUT ---
    col_input, col_nav = st.columns([0.42, 0.58], gap="large")

    with col_input:
        st.subheader("⚙️ Global Parameters")

        with st.expander("📊 Business Baseline", expanded=True):
            st.number_input("Unit Price (€)", value=float(p), key="price")
            st.number_input("Variable Cost (€)", value=float(vc), key="variable_cost")
            st.number_input("Annual Volume", value=int(v), key="volume")
            st.number_input("Annual Fixed Costs (€)", value=float(fc), key="fixed_cost")
            st.number_input("Target Profit Goal (€)", value=float(tp), key="target_profit_goal")

        with st.expander("🔄 Working Capital Cycle", expanded=False):
            st.number_input("AR Days (Collection)", value=float(s.get('ar_days', 45.0)), key="ar_days")
            st.number_input("Inventory Days", value=float(s.get('inventory_days', 60.0)), key="inventory_days")
            st.number_input("AP Days (Payment)", value=float(s.get('ap_days', 30.0)), key="ap_days")

        with st.expander("💰 Liquidity & Obligations", expanded=False):
            st.number_input("Opening Cash (€)", value=float(cash), key="opening_cash")
            st.number_input("Annual Debt Service (€)", value=float(ads), key="annual_debt_service")

        # Κουμπιά ελέγχου και Διαγνωστικό
        st.divider()
        c_btn1, c_btn2 = st.columns(2)
        with c_btn1:
            if st.button("🔒 Lock Baseline", type="primary", use_container_width=True):
                st.session_state.baseline_locked = True
                st.rerun()
        with c_btn2:
            if st.button("🔄 Reset Data", type="secondary", use_container_width=True):
                st.session_state.clear()
                st.rerun()
        
        # ΕΣΩΤΕΡΙΚΟ ΔΙΑΓΝΩΣΤΙΚΟ ΕΡΓΑΛΕΙΟ (Redundancy)
        if st.button("🛠️ Run System Diagnostic", use_container_width=True):
            st.session_state.selected_tool = ("INTERNAL", "show_payables_manager_internal")
            st.session_state.flow_step = "library"
            st.rerun()

    with col_nav:
        st.subheader("📊 Strategic Tool Library")
        t1, t2, t3, t4 = st.tabs(["🚀 Strategy", "💰 Finance", "⚙️ Ops", "🛡️ Risk"])

        with t1:
            if st.button("🎯 Pricing Strategy", use_container_width=True):
                s.selected_tool = ("pricing_strategy", "show_pricing_strategy_tool"); s.flow_step = "library"; st.rerun()
            if st.button("⚖️ Cash Survival Simulator", use_container_width=True):
                s.selected_tool = ("break_even_shift_calculator", "show_break_even_shift_calculator"); s.flow_step = "library"; st.rerun()
            if st.button("📡 Pricing Radar", use_container_width=True):
                s.selected_tool = ("pricing_radar", "show_pricing_radar"); s.flow_step = "library"; st.rerun()
            if st.button("📉 Loss Threshold", use_container_width=True):
                s.selected_tool = ("loss_threshold", "show_loss_threshold_before_price_cut"); s.flow_step = "library"; st.rerun()
            if st.button("🧭 QSPM Strategy Matrix", use_container_width=True):
                s.selected_tool = ("qspm_analyzer", "show_qspm_tool"); s.flow_step = "library"; st.rerun()

        with t2:
            if st.button("📈 Growth Funding (AFN)", use_container_width=True):
                s.selected_tool = ("growth_funding", "show_growth_funding_needed"); s.flow_step = "library"; st.rerun()
            if st.button("📉 WACC Optimizer", use_container_width=True):
                s.selected_tool = ("wacc_optimizer", "show_wacc_optimizer"); s.flow_step = "library"; st.rerun()
            if st.button("⚖️ Loan vs Leasing", use_container_width=True):
                s.selected_tool = ("loan_vs_leasing", "loan_vs_leasing_ui"); s.flow_step = "library"; st.rerun()

        with t3:
            if st.button("📊 NPV Receivables Analyzer", use_container_width=True):
                s.selected_tool = ("receivables_npv", "show_receivables_analyzer_ui"); s.flow_step = "library"; st.rerun()
            if st.button("🔄 Cash Conversion Cycle", use_container_width=True):
                s.selected_tool = ("cash_cycle", "run_cash_cycle_app"); s.flow_step = "library"; st.rerun()
            if st.button("🔢 Unit Cost Analyzer", use_container_width=True):
                s.selected_tool = ("unit_cost_analyzer", "show_unit_cost_app"); s.flow_step = "library"; st.rerun()
            if st.button("📦 Inventory Optimizer", use_container_width=True):
                s.selected_tool = ("inventory_manager", "show_inventory_manager"); s.flow_step = "library"; st.rerun()
            if st.button("🤝 Payables Manager (External)", use_container_width=True):
                s.selected_tool = ("payables_manager", "show_payables_manager"); s.flow_step = "library"; st.rerun()

        with t4:
            if st.button("🏁 Executive Dashboard", use_container_width=True):
                s.selected_tool = ("executive_dashboard", "show_executive_dashboard"); s.flow_step = "library"; st.rerun()
            if st.button("🚨 Cash Fragility Index", use_container_width=True):
                s.selected_tool = ("cash_fragility_index", "show_cash_fragility_index"); s.flow_step = "library"; st.rerun()
            if st.button("🛡️ Resilience & Shock Map", use_container_width=True):
                s.selected_tool = ("financial_resilience_app", "show_resilience_map"); s.flow_step = "library"; st.rerun()
            if st.button("📉 Stress Test Simulator", use_container_width=True):
                s.selected_tool = ("stress_test_simulator", "show_stress_test_tool"); s.flow_step = "library"; st.rerun()

    if s.get("baseline_locked"):
        st.caption("✅ Data Engine Synchronized. All tools now use the locked parameters.")
