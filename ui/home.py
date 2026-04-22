import streamlit as st
import pandas as pd
from datetime import datetime


def _render_quickstart(s):
    """Quick Start block - εμφανίζεται μόνο αν δεν έχει γίνει lock το baseline."""

    if s.get("baseline_locked"):
        return

    if not s.get("show_quickstart"):
        # Απλό CTA κουμπί κάτω από το hero
        col_c1, col_c2, col_c3 = st.columns([1, 2, 1])
        with col_c2:
            if st.button("→ Start with your numbers", type="primary", use_container_width=True, key="btn_open_qs"):
                s.show_quickstart = True
                st.rerun()
        st.markdown("<br>", unsafe_allow_html=True)
        return

    # --------------------------------------------------
    # QUICK START FORM
    # --------------------------------------------------
    st.markdown("""
    <div style='background:#f8fafc; border:1px solid #e2e8f0; border-radius:12px;
                padding:24px 28px; max-width:640px; margin:0 auto 24px auto;'>
        <div style='font-size:20px; font-weight:700; color:#1E3A8A; margin-bottom:4px;'>
            Quick Start
        </div>
        <div style='font-size:14px; color:#64748b;'>
            4 numbers. That's all you need to begin.
        </div>
    </div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns(2)

    with col1:
        price_qs = st.number_input(
            "Unit Price ($)",
            min_value=0.0,
            value=float(s.get("price", 0.0)),
            step=1.0,
            key="qs_price",
            help="What do you charge per unit or service?"
        )
        vc_qs = st.number_input(
            "Variable Cost per Unit ($)",
            min_value=0.0,
            value=float(s.get("variable_cost", 0.0)),
            step=1.0,
            key="qs_vc",
            help="Direct cost to deliver one unit (materials, shipping, etc.)"
        )

    with col2:
        volume_qs = st.number_input(
            "Monthly Units Sold",
            min_value=0,
            value=int(s.get("volume", 0) // 12) if s.get("volume") else 0,
            step=10,
            key="qs_volume",
            help="How many units do you sell per month on average?"
        )
        fc_qs = st.number_input(
            "Monthly Fixed Costs ($)",
            min_value=0.0,
            value=float(s.get("fixed_cost", 0.0) / 12) if s.get("fixed_cost") else 0.0,
            step=100.0,
            key="qs_fc",
            help="Rent, salaries, utilities — costs that don't change with volume"
        )

    # Live preview — εμφανίζεται μόνο αν έχουν μπει αριθμοί
    margin = price_qs - vc_qs
    if price_qs > 0 and margin > 0 and volume_qs > 0 and fc_qs > 0:
        monthly_profit = (margin * volume_qs) - fc_qs
        bep = fc_qs / margin

        st.markdown("---")
        col_p1, col_p2, col_p3 = st.columns(3)
        col_p1.metric("Contribution Margin", f"${margin:.2f} / unit")
        col_p2.metric(
            "Monthly Profit Est.",
            f"${monthly_profit:,.0f}",
            delta="profitable" if monthly_profit > 0 else "loss",
            delta_color="normal" if monthly_profit > 0 else "inverse"
        )
        col_p3.metric("Break-Even (units/mo)", f"{bep:,.0f}")
        st.markdown("")

    # Buttons
    col_btn1, col_btn2 = st.columns([3, 1])
    with col_btn1:
        if st.button("→ Run Full Simulation", type="primary", use_container_width=True, key="btn_qs_go"):
            if price_qs > 0 and volume_qs > 0:
                s.price = price_qs
                s.variable_cost = vc_qs
                s.volume = volume_qs * 12      # το υπόλοιπο app δουλεύει με annual
                s.fixed_cost = fc_qs * 12      # annual
                s.baseline_locked = True
                s.flow_step = "control_tower"
                s.show_quickstart = False
                st.rerun()
            else:
                st.warning("Fill in at least Price and Volume to continue.")
    with col_btn2:
        if st.button("Cancel", use_container_width=True, key="btn_qs_cancel"):
            s.show_quickstart = False
            st.rerun()

    st.divider()


def run_home():
    s = st.session_state
    m = s.get("metrics", {})

    if "saved_scenarios" not in s:
        s.saved_scenarios = {}

    # --------------------------------------------------
    # HERO SECTION
    # --------------------------------------------------
    st.markdown(
        """
        <div style='text-align:center; padding: 8px 0 10px 0;'>
            <div style='font-size:22px; font-weight:600; color:#1E3A8A;'>
            Test your pricing before you make the decision
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    # --------------------------------------------------
    # QUICK START  ← νέο
    # --------------------------------------------------
    _render_quickstart(s)

    # --------------------------------------------------
    # STRATEGY EXPLANATION  (εμφανίζεται μόνο αν ΔΕΝ είναι ανοιχτό το quick start)
    # --------------------------------------------------
    if not s.get("show_quickstart"):
        colA, colB = st.columns([0.6, 0.4])
        with colA:
            st.markdown("### Engine")
        with colB:
            st.markdown("### Loop")

        st.divider()

        # --------------------------------------------------
        # SNAPSHOT METRICS
        # --------------------------------------------------
        st.subheader("📊 Executive Simulation Snapshot")
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("ROIC", f"{m.get('roic', 0)*100:.1f}%")
        c2.metric("Break-Even", f"{m.get('bep_units', 0):,.0f} units")
        c3.metric("Margin of Safety", f"{m.get('margin_of_safety', 0)*100:.1f}%")
        c4.metric("Net Cash Position", f"${m.get('net_cash_position', 0):,.0f}")

        st.divider()

        # --------------------------------------------------
        # MAIN LAYOUT
        # --------------------------------------------------
        col_left, col_right = st.columns([0.4, 0.6], gap="large")

        with col_left:
            if s.get("flow_step") == "home":
                st.subheader("⚙️ Business Baseline")
                st.text_input("Scenario Name", value=s.get("scenario_name", "Baseline Scenario"), key="scenario_name")

                with st.expander("📊 Core Business Model", expanded=True):
                    st.number_input("Unit Price ($)", value=float(s.get("price", 150.0)), key="price")

                    vc_val = st.number_input("Variable Cost ($)", value=float(s.get("variable_cost", 90.0)))
                    s.variable_cost = vc_val

                    with st.expander("🔍 Audit Variable Cost Breakdown"):
                        v1 = st.number_input("Raw Materials/Unit", value=0.0, key="audit_v1")
                        v2 = st.number_input("Logistics/Shipping", value=0.0, key="audit_v2")
                        v3 = st.number_input("Commissions/Other", value=0.0, key="audit_v3")
                        v_total = float(v1 + v2 + v3)
                        st.write(f"Calculated Total: **${v_total:.2f}**")
                        if st.button("Apply to Variable Cost", key="btn_vc"):
                            s.variable_cost = v_total
                            st.rerun()

                    st.number_input("Annual Volume", value=int(s.get("volume", 15000)), key="volume")

                fc_val = st.number_input("Annual Fixed Costs ($)", value=float(s.get("fixed_cost", 450000.0)))
                s.fixed_cost = fc_val

                with st.expander("🔍 Audit Fixed Cost Breakdown"):
                    f1 = st.number_input("Annual Rent", value=0.0, key="audit_f1", help="Το συνολικό ετήσιο κόστος ενοικίων.")
                    f2 = st.number_input("Annual Salaries", value=0.0, key="audit_f2", help="Μικτά + Εργοδοτικές εισφορές (ετήσια).")
                    f3 = st.number_input("Annual Admin & Utilities", value=0.0, key="audit_f3", help="Λειτουργικά έξοδα, συνδρομές κτλ (ετήσια).")
                    f_total = float(f1 + f2 + f3)
                    st.info(f"Total Annual Fixed Cost: **${f_total:,.0f}**")
                    if st.button("Apply to Fixed Costs", key="btn_fc"):
                        s.fixed_cost = f_total
                        st.rerun()

                    st.number_input("Net Fixed Assets ($)", value=float(s.get("fixed_assets", 800000.0)), key="fixed_assets")
                    st.number_input("Annual Depreciation ($)", value=float(s.get("depreciation", 50000.0)), key="depreciation")
                    st.number_input("Target Profit ($)", value=float(s.get("target_profit_goal", 200000.0)), key="target_profit_goal")

                with st.expander("🔄 Working Capital & Liquidity"):
                    st.number_input("Opening Cash ($)", value=float(s.get("opening_cash", 150000.0)), key="opening_cash")
                    st.number_input("Total Equity ($)", value=float(s.get("equity", 500000.0)), key="equity")
                    st.number_input("Total Debt ($)", value=float(s.get("total_debt", 500000.0)), key="total_debt")

                    col_fin1, col_fin2 = st.columns(2)
                    col_fin1.number_input("Annual Interest Costs ($)", value=float(s.get("annual_interest_only", 0.0)), key="annual_interest_only")
                    col_fin2.number_input("Corporate Tax Rate (%)", value=float(s.get("tax_rate", 22.0)), key="tax_rate")

                    st.number_input("A/R Days", value=int(s.get("ar_days", 60)), key="ar_days")
                    st.number_input("Inventory Days", value=int(s.get("inv_days", 45)), key="inv_days")
                    st.number_input("A/P Days", value=int(s.get("ap_days", 30)), key="ap_days")
                    st.number_input("Annual Debt Service ($)", value=float(s.get("annual_debt_service", 70000.0)), key="annual_debt_service")

                if not s.get("baseline_locked"):
                    if st.button("🔒 Lock & Activate Simulation", type="primary", use_container_width=True):
                        s.baseline_locked = True
                        s.flow_step = "control_tower"
                        st.rerun()
                else:
                    col_nav1, col_nav2 = st.columns(2)
                    with col_nav1:
                        if st.button("🕹️ Go to Tower", type="primary", use_container_width=True):
                            s.flow_step = "control_tower"
                            st.rerun()
                    with col_nav2:
                        if st.button("🔓 Unlock", use_container_width=True):
                            s.baseline_locked = False
                            st.rerun()

                if st.button("💾 Save Current Scenario", use_container_width=True):
                    s.saved_scenarios[s.scenario_name] = {
                        "price": s.get("price"),
                        "volume": s.get("volume"),
                        "metrics": dict(s.get("metrics", {}))
                    }
                    st.success(f"Scenario '{s.scenario_name}' saved!")

            else:
                st.info(f"💡 Active Scenario: **{s.get('scenario_name')}**")
                st.write(f"Price: ${s.get('price')}")
                st.write(f"Volume: {s.get('volume')}")

        with col_right:
            st.subheader("🧠 Business Strategy Modules")

            if not s.get("baseline_locked"):
                st.info("🔒 Lock the baseline to activate the simulation modules.")
            else:
                t1, t2, t3, t4 = st.tabs(["Strategy", "Finance", "Operations", "Risk"])

                with t1:
                    if st.button("🎯 Price & Profit Planner", use_container_width=True): s.selected_tool="pricing_strategy"; s.flow_step="tool"; st.rerun()
                    if st.button("📡 Competitor Price Radar", use_container_width=True): s.selected_tool="pricing_radar"; s.flow_step="tool"; st.rerun()
                    if st.button("📉 Sales Safety Margin", use_container_width=True): s.selected_tool="loss_threshold"; s.flow_step="tool"; st.rerun()
                    if st.button("⚖️ Cash Survival Goal (BEP)", use_container_width=True): s.selected_tool="break_even_shift"; s.flow_step="tool"; st.rerun()
                    if st.button("🧭 Strategy Decision Matrix", use_container_width=True): s.selected_tool="qspm_analyzer"; s.flow_step="tool"; st.rerun()
                    if st.button("👥 Customer Value (CLV)", use_container_width=True): s.selected_tool="clv_calculator"; s.flow_step="tool"; st.rerun()

                with t2:
                    if st.button("📈 Funding for Growth", use_container_width=True): s.selected_tool="growth_funding"; s.flow_step="tool"; st.rerun()
                    if st.button("📉 Cost of Capital (WACC)", use_container_width=True): s.selected_tool="wacc_optimizer"; s.flow_step="tool"; st.rerun()
                    if st.button("⚖️ Buy vs Lease Finder", use_container_width=True): s.selected_tool="loan_vs_leasing"; s.flow_step="tool"; st.rerun()

                with t3:
                    if st.button("🕵️ Deal & Cash Gap Auditor", use_container_width=True): s.selected_tool="deal_auditor"; s.flow_step="tool"; st.rerun()
                    if st.button("🔄 Cash Speed (Cycle)", use_container_width=True): s.selected_tool="cash_cycle"; s.flow_step="tool"; st.rerun()
                    if st.button("💰 Cash Unlocker (Working Cap)", use_container_width=True): s.selected_tool="wc_optimizer"; s.flow_step="tool"; st.rerun()
                    if st.button("📦 Stock & Inventory Lab", use_container_width=True): s.selected_tool="inventory_manager"; s.flow_step="tool"; st.rerun()
                    if st.button("📊 Customer Credit NPV", use_container_width=True): s.selected_tool="receivables_npv"; s.flow_step="tool"; st.rerun()
                    if st.button("🤝 Supplier Payment Mgr", use_container_width=True): s.selected_tool="payables_manager"; s.flow_step="tool"; st.rerun()

                with t4:
                    if st.button("🚨 When do I run out of Cash?", use_container_width=True): s.selected_tool="cash_fragility"; s.flow_step="tool"; st.rerun()
                    if st.button("📉 Worst-Case Scenario", use_container_width=True): s.selected_tool="stress_test"; s.flow_step="tool"; st.rerun()
                    if st.button("🗺️ Business Resilience Map", use_container_width=True): s.selected_tool="resilience_map"; s.flow_step="tool"; st.rerun()

                st.divider()
                with st.expander("🔍 Capital Structure Analysis", expanded=True):
                    ca1, ca2 = st.columns(2)
                    ca1.write(f"**Total Debt:** ${s.get('total_debt', 0):,.0f}")
                    ca1.write(f"**Total Equity:** ${s.get('equity', 0):,.0f}")
                    ca1.write(f"**Fixed Assets:** ${s.get('fixed_assets', 0):,.0f}")

                    net_debt_val = s.get('total_debt', 0) - s.get('opening_cash', 0)
                    color = "red" if net_debt_val > 0 else "green"
                    ca2.markdown(f"**Net Debt:** <span style='color:{color}'>${net_debt_val:,.0f}</span>", unsafe_allow_html=True)
                    ca2.write(f"**Invested Capital:** ${m.get('invested_capital', 0):,.0f}")
