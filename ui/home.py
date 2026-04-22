import streamlit as st
import pandas as pd
from datetime import datetime

def run_home():
    s = st.session_state
    m = s.get("metrics", {})

    if "saved_scenarios" not in s:
        s.saved_scenarios = {}

    # ---------------- DEFAULT STATE (IMPORTANT FIX) ----------------
    defaults = {
        "scenario_name": "Baseline Scenario",
        "price": 150.0,
        "variable_cost": 90.0,
        "volume": 10000,
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
        "baseline_locked": False,
        "flow_step": "home",
    }

    for k, v in defaults.items():
        if k not in s:
            s[k] = v

    # --------------------------------------------------
    # HERO
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

    # ================= LEFT =================
    with col_left:

        st.subheader("⚙️ Business Baseline")

        st.text_input("Scenario Name", key="scenario_name")

        with st.expander("📊 Core Business Model", expanded=True):

            st.number_input("Unit Price ($)", key="price")

            st.number_input("Variable Cost ($)", key="variable_cost")

            st.number_input("Annual Volume", key="volume")

            st.number_input("Annual Fixed Costs ($)", key="fixed_cost")

            st.number_input("Net Fixed Assets ($)", key="fixed_assets")

            st.number_input("Annual Depreciation ($)", key="depreciation")

            st.number_input("Target Profit ($)", key="target_profit_goal")

        with st.expander("🔍 Audit Variable Cost Breakdown"):

            v1 = st.number_input("Raw Materials/Unit", value=0.0, key="audit_v1")
            v2 = st.number_input("Logistics/Shipping", value=0.0, key="audit_v2")
            v3 = st.number_input("Commissions/Other", value=0.0, key="audit_v3")

            v_total = v1 + v2 + v3

            st.write(f"Calculated Total: **${v_total:.2f}**")

            if st.button("Apply to Variable Cost", key="btn_vc"):
                s.variable_cost = v_total
                st.rerun()

        with st.expander("🔄 Working Capital & Liquidity"):

            st.number_input("Opening Cash ($)", key="opening_cash")
            st.number_input("Total Equity ($)", key="equity")
            st.number_input("Total Debt ($)", key="total_debt")

            col_fin1, col_fin2 = st.columns(2)

            col_fin1.number_input("Annual Interest Costs ($)", key="annual_interest_only")
            col_fin2.number_input("Corporate Tax Rate (%)", key="tax_rate")

            st.number_input("A/R Days", key="ar_days")
            st.number_input("Inventory Days", key="inv_days")
            st.number_input("A/P Days", key="ap_days")
            st.number_input("Annual Debt Service ($)", key="annual_debt_service")

        # ---------------- LOCK ----------------
        if not s.baseline_locked:
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

        # ---------------- SAVE ----------------
        if st.button("💾 Save Current Scenario", use_container_width=True):
            s.saved_scenarios[s.scenario_name] = {
                "price": s.get("price"),
                "volume": s.get("volume"),
                "metrics": dict(s.get("metrics", {}))
            }
            st.success(f"Scenario '{s.scenario_name}' saved!")

    # ================= RIGHT =================
    with col_right:

        st.subheader("🧠 Business Strategy Modules")

        if not s.baseline_locked:
            st.info("🔒 Lock the baseline to activate modules.")
        else:

            t1, t2, t3, t4 = st.tabs(["Strategy", "Finance", "Operations", "Risk"])

            with t1:
                if st.button("🎯 Price & Profit Planner", use_container_width=True):
                    s.selected_tool = "pricing_strategy"
                    st.rerun()

                if st.button("📉 Sales Safety Margin", use_container_width=True):
                    s.selected_tool = "loss_threshold"
                    st.rerun()

            with t2:
                if st.button("📈 Funding Growth", use_container_width=True):
                    s.selected_tool = "growth_funding"
                    st.rerun()

                if st.button("📉 WACC", use_container_width=True):
                    s.selected_tool = "wacc_optimizer"
                    st.rerun()

            with t3:
                if st.button("🔄 Cash Cycle", use_container_width=True):
                    s.selected_tool = "cash_cycle"
                    st.rerun()

                if st.button("💰 Working Capital", use_container_width=True):
                    s.selected_tool = "wc_optimizer"
                    st.rerun()

            with t4:
                if st.button("🚨 Cash Risk", use_container_width=True):
                    s.selected_tool = "cash_fragility"
                    st.rerun()

                if st.button("📉 Stress Test", use_container_width=True):
                    s.selected_tool = "stress_test"
                    st.rerun()

    # --------------------------------------------------
    # SNAPSHOT (BOTTOM - όπως ζήτησες)
    # --------------------------------------------------
    st.divider()

    st.subheader("📊 Executive Simulation Snapshot")

    c1, c2, c3, c4 = st.columns(4)

    c1.metric("ROIC", f"{m.get('roic', 0)*100:.1f}%")
    c2.metric("Break-Even", f"{m.get('bep_units', 0):,.0f}")
    c3.metric("Margin of Safety", f"{m.get('margin_of_safety', 0)*100:.1f}%")
    c4.metric("Net Cash Position", f"${m.get('net_cash_position', 0):,.0f}")
