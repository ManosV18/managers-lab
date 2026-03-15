import streamlit as st


def run_home():

    s = st.session_state
    m = s.get("metrics", {})

    # --------------------------------------------------
    # BASELINE STATE
    # --------------------------------------------------

    p = s.get("price", 100.0)
    vc = s.get("variable_cost", 60.0)
    v = s.get("volume", 1000)
    fc = s.get("fixed_cost", 20000.0)
    ads = s.get("annual_debt_service", 0.0)
    cash = s.get("opening_cash", 10000.0)
    tp = s.get("target_profit_goal", 0.0)

    net_cash = m.get("net_cash_position", cash)
    bep_units = m.get("bep_units", 0)
    margin = p - vc
    roic = m.get("roic", 0.0)

    # --------------------------------------------------
    # SNAPSHOT LOGIC
    # --------------------------------------------------

    if margin > 0 and bep_units:

        margin_of_safety = v - bep_units
        buffer_pct = (margin_of_safety / v * 100) if v > 0 else 0

        bep_display = f"{bep_units:,.0f} units"

        delta_val = (
            f"{margin_of_safety:,.0f} surplus"
            if margin_of_safety >= 0
            else f"{abs(margin_of_safety):,.0f} deficit"
        )

        delta_col = "normal" if margin_of_safety >= 0 else "inverse"

    else:

        buffer_pct = -100.0
        bep_display = "N/A"
        delta_val = "⚠ Not viable"
        delta_col = "inverse"

    # --------------------------------------------------
    # HERO
    # --------------------------------------------------

    st.markdown(
        """
        <div style='text-align:center; padding: 10px 0 30px 0;'>

        <h1 style='font-size:64px; font-weight:900; color:#1E3A8A;'>
        Managers Lab<span style='color:#ef4444;'>.</span>
        </h1>

        <div style='font-size:26px; font-weight:700; margin-top:10px;'>
        Business Strategy Simulator
        </div>

        <div style='font-size:18px; color:#475569; max-width:750px; margin:auto; margin-top:10px;'>
        Test pricing, financing and operational decisions before
        implementing them in the real world.
        </div>

        <div style='font-size:14px; color:#94a3b8; margin-top:10px;'>
        Financial Stress Testing & Strategy Simulation Platform
        </div>

        </div>
        """,
        unsafe_allow_html=True
    )

    # --------------------------------------------------
    # STRATEGY EXPLANATION
    # --------------------------------------------------

    colA, colB = st.columns(2)

    with colA:

        st.markdown(
            """
### ⚙️ Financial Simulation Engine

All modules run on a unified **financial engine** that converts
business assumptions into real-time financial metrics.

The engine calculates:

• Cash Break-Even  
• Liquidity Position  
• Return on Capital (ROIC)  
• Survival Buffer
"""
        )

    with colB:

        st.markdown(
            """
### 🔁 Strategy Simulation Loop

Managers Lab follows a simple decision loop:

1️⃣ Define the **business baseline**

2️⃣ Run the **financial diagnostics**

3️⃣ Simulate **shocks or strategic decisions**

4️⃣ Adjust pricing, financing or operations
"""
        )

    st.divider()

    # --------------------------------------------------
    # SNAPSHOT
    # --------------------------------------------------

    st.subheader("📊 Executive Simulation Snapshot")

    c1, c2, c3, c4, c5 = st.columns(5)

    c1.metric("Simulated Volume", f"{v:,.0f} units")
    c2.metric("Unit Contribution", f"€{margin:,.2f}")

    c3.metric(
        "Cash Break-Even",
        bep_display,
        delta=delta_val,
        delta_color=delta_col
    )

    c4.metric("Survival Buffer", f"{buffer_pct:.1f}%")

    c5.metric(
        "ROIC",
        f"{roic*100:.1f}%",
        help="Return on Invested Capital"
    )

    if s.get("baseline_locked"):

        if net_cash < 0:
            st.error(f"🚨 Liquidity Deficit: €{net_cash:,.0f}")

        elif net_cash < (v * p * 0.05):
            st.warning("⚠ Low Liquidity Buffer")

    st.divider()

    # --------------------------------------------------
    # LAYOUT
    # --------------------------------------------------

    col_input, col_nav = st.columns([0.40, 0.60], gap="large")

    # --------------------------------------------------
    # BASELINE INPUT
    # --------------------------------------------------

    with col_input:

        st.subheader("⚙️ Business Baseline")

        with st.expander("📊 Core Business Model", expanded=True):

            st.number_input("Unit Price (€)", value=float(p), key="price")
            st.number_input("Variable Cost (€)", value=float(vc), key="variable_cost")
            st.number_input("Annual Volume", value=int(v), key="volume")
            st.number_input("Annual Fixed Costs (€)", value=float(fc), key="fixed_cost")
            st.number_input("Target Profit Goal (€)", value=float(tp), key="target_profit_goal")

        with st.expander("🔄 Working Capital Cycle"):

            st.number_input("AR Days", value=float(s.get("ar_days", 45.0)), key="ar_days")
            st.number_input("Inventory Days", value=float(s.get("inv_days", 60.0)), key="inv_days")
            st.number_input("AP Days", value=float(s.get("ap_days", 30.0)), key="ap_days")

        with st.expander("💰 Liquidity & Debt"):

            st.number_input("Opening Cash (€)", value=float(cash), key="opening_cash")
            st.number_input("Annual Debt Service (€)", value=float(ads), key="annual_debt_service")

        if st.button(
            "🔒 Lock Baseline & Activate Simulation",
            type="primary",
            use_container_width=True
        ):

            st.session_state.baseline_locked = True
            st.session_state.flow_step = "home"
            st.rerun()

        if s.get("baseline_locked"):

            if st.button(
                "🔄 Reset Baseline",
                use_container_width=True
            ):

                st.session_state.baseline_locked = False
                st.session_state.metrics = {}
                st.rerun()

    # --------------------------------------------------
    # MODULE NAVIGATION
    # --------------------------------------------------

    with col_nav:

        st.subheader("🧠 Strategy Simulation Modules")

        if not s.get("baseline_locked"):

            st.info("🔒 Lock the baseline to activate the simulation modules.")

        else:

            t1, t2, t3, t4 = st.tabs(
                [
                    "Strategic Decisions",
                    "Financial Structure",
                    "Operations & Cash Flow",
                    "Risk & Stress Tests"
                ]
            )

            # STRATEGY

            with t1:

                if st.button("🕹️ Mission Control", use_container_width=True, type="primary"):
                    s.selected_tool = "control_tower"
                    s.flow_step = "tool"
                    st.rerun()

                if st.button("🎯 Pricing Strategy", use_container_width=True):
                    s.selected_tool = "pricing_strategy"
                    s.flow_step = "tool"
                    st.rerun()

                if st.button("⚖️ Cash Survival Simulator", use_container_width=True):
                    s.selected_tool = "break_even_shift"
                    s.flow_step = "tool"
                    st.rerun()

                if st.button("👥 Customer Lifetime Value (CLV)", use_container_width=True):
                    s.selected_tool = "clv_calculator"
                    s.flow_step = "tool"
                    st.rerun()

                if st.button("📡 Pricing Radar", use_container_width=True):
                    s.selected_tool = "pricing_radar"
                    s.flow_step = "tool"
                    st.rerun()

                if st.button("📉 Loss Threshold", use_container_width=True):
                    s.selected_tool = "loss_threshold"
                    s.flow_step = "tool"
                    st.rerun()

                if st.button("🧭 QSPM Strategy Matrix", use_container_width=True):
                    s.selected_tool = "qspm_analyzer"
                    s.flow_step = "tool"
                    st.rerun()

            # FINANCE

            with t2:

                if st.button("📈 Growth Funding (AFN)", use_container_width=True):
                    s.selected_tool = "growth_funding"
                    s.flow_step = "tool"
                    st.rerun()

                if st.button("📉 WACC Optimizer", use_container_width=True):
                    s.selected_tool = "wacc_optimizer"
                    s.flow_step = "tool"
                    st.rerun()

                if st.button("⚖️ Loan vs Leasing", use_container_width=True):
                    s.selected_tool = "loan_vs_leasing"
                    s.flow_step = "tool"
                    st.rerun()

            # OPERATIONS

            with t3:

                if st.button("📊 NPV Receivables Analyzer", use_container_width=True):
                    s.selected_tool = "receivables_npv"
                    s.flow_step = "tool"
                    st.rerun()

                if st.button("🔄 Cash Conversion Cycle", use_container_width=True):
                    s.selected_tool = "cash_cycle"
                    s.flow_step = "tool"
                    st.rerun()

                if st.button("🔢 Unit Cost Analyzer", use_container_width=True):
                    s.selected_tool = "unit_cost_analyzer"
                    s.flow_step = "tool"
                    st.rerun()

                if st.button("📦 Inventory Optimizer", use_container_width=True):
                    s.selected_tool = "inventory_manager"
                    s.flow_step = "tool"
                    st.rerun()

                if st.button("🤝 Payables Manager", use_container_width=True):
                    s.selected_tool = "payables_manager"
                    s.flow_step = "tool"
                    st.rerun()

                if st.button("💰 Working Capital Engine", use_container_width=True):
                    s.selected_tool = "wc_optimizer"
                    s.flow_step = "tool"
                    st.rerun()

            # RISK

            with t4:

                if st.button("🛡️ Strategic Shock Simulator", use_container_width=True):
                    s.selected_tool = "shock_simulator"
                    s.flow_step = "tool"
                    st.rerun()

                if st.button("🏁 Executive Dashboard", use_container_width=True):
                    s.selected_tool = "executive_dashboard"
                    s.flow_step = "tool"
                    st.rerun()

                if st.button("🚨 Cash Fragility Index", use_container_width=True):
                    s.selected_tool = "cash_fragility"
                    s.flow_step = "tool"
                    st.rerun()

                if st.button("🛡️ Resilience Map", use_container_width=True):
                    s.selected_tool = "resilience_map"
                    s.flow_step = "tool"
                    st.rerun()

                if st.button("📉 Stress Test Simulator", use_container_width=True):
                    s.selected_tool = "stress_test"
                    s.flow_step = "tool"
                    st.rerun()
