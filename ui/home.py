import streamlit as st
import pandas as pd
from datetime import datetime

def run_home():
    s = st.session_state
    m = s.get("metrics", {})
    
    if "saved_scenarios" not in s:
        s.saved_scenarios = {}

    # --------------------------------------------------
    # FULL HERO SECTION
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
            st.text_input("Scenario Name", value=s.get("scenario_name", "Baseline Scenario"), key="scenario_name")

            with st.expander("📊 Core Business Model", expanded=True):

                # Unit Price
                st.number_input("Unit Price ($)", value=float(s.get("price", 150.0)), key="price")

                # Variable Cost
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

                # --------------------------------------------------
                # SNAPSHOT METRICS (MOVED HERE ↓↓↓)
                # --------------------------------------------------
                st.subheader("📊 Executive Simulation Snapshot")

                c1, c2, c3, c4 = st.columns(4)

                c1.metric("ROIC", f"{m.get('roic', 0)*100:.1f}%")
                c2.metric("Break-Even", f"{m.get('bep_units', 0):,.0f} units")
                c3.metric("Margin of Safety", f"{m.get('margin_of_safety', 0)*100:.1f}%")
                c4.metric("Net Cash Position", f"${m.get('net_cash_position', 0):,.0f}")

                st.divider()

            # Fixed Costs
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

            st.number_input("Net Fixed Assets ($)", value=float(s.get("fixed_assets", 800000.0)), key="fixed_assets")
            st.number_input("Annual Depreciation ($)", value=float(s.get("depreciation", 50000.0)), key="depreciation")
            st.number_input("Target Profit ($)", value=float(s.get("target_profit_goal", 200000.0)), key="target_profit_goal")

            # Working capital
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

            # lock
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

    with col_right:

        st.subheader("🧠 Business Strategy Modules")

        if not s.get("baseline_locked"):
            st.info("🔒 Lock the baseline to activate the simulation modules.")
        else:
            t1, t2, t3, t4 = st.tabs(["Strategy", "Finance", "Operations", "Risk"])

            with t1:
                if st.button("🎯 Price & Profit Planner", use_container_width=True):
                    s.selected_tool="pricing_strategy"
                    s.flow_step="tool"
                    st.rerun()
