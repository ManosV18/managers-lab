import streamlit as st
import pandas as pd
from datetime import datetime


def run_home():
    s = st.session_state
    m = s.get("metrics", {})

    if "saved_scenarios" not in s:
        s.saved_scenarios = {}

    # --------------------------------------------------
    # DEFAULTS — τρέχουν μόνο αν δεν υπάρχουν ήδη
    # --------------------------------------------------
    defaults = {
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
        "annual_debt_service": 70000.0,
        "scenario_name": "Baseline Scenario",
    }
    for k, v in defaults.items():
        if k not in s:
            s[k] = v

    # --------------------------------------------------
    # HERO SECTION
    # --------------------------------------------------
    st.markdown(
        """
        <div style='text-align:center; padding: 8px 0 10px 0;'>
            <div style='font-size:22px; font-weight:600; color:#1E3A8A;'>
            Test your decisions before they impact your business
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    # --------------------------------------------------
    # MAIN LAYOUT
    # --------------------------------------------------
    col_left, col_right = st.columns([0.4, 0.6], gap="large")

    with col_left:
        if s.get("flow_step") == "home":
            st.subheader("⚙️ Business Baseline")
            st.text_input("Scenario Name", key="scenario_name")

            with st.expander("📊 Core Business Model", expanded=True):
                st.number_input("Unit Price ($)", key="price", min_value=0.0, step=1.0)

                # Variable Cost — χειροκίνητο state γιατί έχει audit breakdown
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

                st.number_input("Annual Volume", key="volume", min_value=0, step=100)

            # Fixed Cost — χειροκίνητο state γιατί έχει audit breakdown
            fc_val = st.number_input("Annual Fixed Costs ($)", value=float(s.get("fixed_cost", 450000.0)))
            s.fixed_cost = fc_val

            with st.expander("🔍 Audit Fixed Cost Breakdown"):
                f1 = st.number_input("Annual Rent", value=0.0, key="audit_f1")
                f2 = st.number_input("Annual Salaries", value=0.0, key="audit_f2")
                f3 = st.number_input("Annual Admin & Utilities", value=0.0, key="audit_f3")
                f_total = float(f1 + f2 + f3)
                st.info(f"Total Annual Fixed Cost: **${f_total:,.0f}**")
                if st.button("Apply to Fixed Costs", key="btn_fc"):
                    s.fixed_cost = f_total
                    st.rerun()

            with st.expander("📐 Assets & Targets"):
                st.number_input("Net Fixed Assets ($)", key="fixed_assets", min_value=0.0, step=1000.0)
                st.number_input("Annual Depreciation ($)", key="depreciation", min_value=0.0, step=1000.0)
                st.number_input("Target Profit ($)", key="target_profit_goal", min_value=0.0, step=1000.0)

            with st.expander("🔄 Working Capital & Liquidity"):
                st.number_input("Opening Cash ($)", key="opening_cash", min_value=0.0, step=1000.0)
                st.number_input("Total Equity ($)", key="equity", min_value=0.0, step=1000.0)
                st.number_input("Total Debt ($)", key="total_debt", min_value=0.0, step=1000.0)

                col_fin1, col_fin2 = st.columns(2)
                with col_fin1:
                    st.number_input("Annual Interest Costs ($)", key="annual_interest_only", min_value=0.0, step=100.0)
                with col_fin2:
                    st.number_input("Corporate Tax Rate (%)", key="tax_rate", min_value=0.0, max_value=100.0, step=0.5)

                st.number_input("A/R Days", key="ar_days", min_value=0, step=1)
                st.number_input("Inventory Days", key="inv_days", min_value=0, step=1)
                st.number_input("A/P Days", key="ap_days", min_value=0, step=1)
                st.number_input("Annual Debt Service ($)", key="annual_debt_service", min_value=0.0, step=1000.0)

            # --- LOCK / UNLOCK LOGIC ---
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

        is_disabled = not s.get("baseline_locked")
        if is_disabled:
            st.warning("🔒 Please lock the baseline to enable these tools.")

        t1, t2, t3, t4 = st.tabs(["Strategy", "Finance", "Operations", "Risk"])

        with t1:
            if st.button("🎯 Price & Profit Planner", use_container_width=True, disabled=is_disabled): s.selected_tool="pricing_strategy"; s.flow_step="tool"; st.rerun()
            if st.button("📡 Competitor Price Radar", use_container_width=True, disabled=is_disabled): s.selected_tool="pricing_radar"; s.flow_step="tool"; st.rerun()
            if st.button("📉 Sales Safety Margin", use_container_width=True, disabled=is_disabled): s.selected_tool="loss_threshold"; s.flow_step="tool"; st.rerun()
            if st.button("⚖️ Cash Survival Goal (BEP)", use_container_width=True, disabled=is_disabled): s.selected_tool="break_even_shift"; s.flow_step="tool"; st.rerun()
            if st.button("🧭 Strategy Decision Matrix", use_container_width=True, disabled=is_disabled): s.selected_tool="qspm_analyzer"; s.flow_step="tool"; st.rerun()
            if st.button("👥 Customer Value (CLV)", use_container_width=True, disabled=is_disabled): s.selected_tool="clv_calculator"; s.flow_step="tool"; st.rerun()

        with t2:
            if st.button("📈 Funding for Growth", use_container_width=True, disabled=is_disabled): s.selected_tool="growth_funding"; s.flow_step="tool"; st.rerun()
            if st.button("📉 Cost of Capital (WACC)", use_container_width=True, disabled=is_disabled): s.selected_tool="wacc_optimizer"; s.flow_step="tool"; st.rerun()
            if st.button("⚖️ Buy vs Lease Finder", use_container_width=True, disabled=is_disabled): s.selected_tool="loan_vs_leasing"; s.flow_step="tool"; st.rerun()

        with t3:
            if st.button("🕵️ Deal & Cash Gap Auditor", use_container_width=True, disabled=is_disabled): s.selected_tool="deal_auditor"; s.flow_step="tool"; st.rerun()
            if st.button("🔄 Cash Speed (Cycle)", use_container_width=True, disabled=is_disabled): s.selected_tool="cash_cycle"; s.flow_step="tool"; st.rerun()
            if st.button("💰 Cash Unlocker (Working Cap)", use_container_width=True, disabled=is_disabled): s.selected_tool="wc_optimizer"; s.flow_step="tool"; st.rerun()
            if st.button("📦 Stock & Inventory Lab", use_container_width=True, disabled=is_disabled): s.selected_tool="inventory_manager"; s.flow_step="tool"; st.rerun()
            if st.button("📊 Customer Credit NPV", use_container_width=True, disabled=is_disabled): s.selected_tool="receivables_npv"; s.flow_step="tool"; st.rerun()
            if st.button("🤝 Supplier Payment Mgr", use_container_width=True, disabled=is_disabled): s.selected_tool="payables_manager"; s.flow_step="tool"; st.rerun()

        with t4:
            if st.button("🚨 When do I run out of Cash?", use_container_width=True, disabled=is_disabled): s.selected_tool="cash_fragility"; s.flow_step="tool"; st.rerun()
            if st.button("📉 Worst-Case Scenario", use_container_width=True, disabled=is_disabled): s.selected_tool="stress_test"; s.flow_step="tool"; st.rerun()
            if st.button("🗺️ Business Resilience Map", use_container_width=True, disabled=is_disabled): s.selected_tool="resilience_map"; s.flow_step="tool"; st.rerun()

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

    # --------------------------------------------------
    # SNAPSHOT METRICS
    # --------------------------------------------------
    st.divider()
    st.subheader("📊 Executive Simulation Snapshot")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("ROIC", f"{m.get('roic', 0)*100:.1f}%")
    c2.metric("Break-Even", f"{m.get('bep_units', 0):,.0f} units")
    c3.metric("Margin of Safety", f"{m.get('margin_of_safety', 0)*100:.1f}%")
    c4.metric("Net Cash Position", f"${m.get('net_cash_position', 0):,.0f}")

