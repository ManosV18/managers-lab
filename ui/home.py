import streamlit as st
import pandas as pd
from datetime import datetime


# --------------------------------------------------
# STATE INITIALIZER (PRODUCTION SAFE)
# --------------------------------------------------
def init_state(s):
    defaults = {
        "scenario_name": "Baseline Scenario",
        "price": 150.0,
        "variable_cost": 100.0,
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
        "flow_step": "home"
    }

    for k, v in defaults.items():
        if k not in s:
            s[k] = v


# --------------------------------------------------
# MAIN MODULE
# --------------------------------------------------
def run_home():
    s = st.session_state
    init_state(s)
    m = s.get("metrics", {})

    if "saved_scenarios" not in s:
        s.saved_scenarios = {}

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

    with col_left:

        if s["flow_step"] == "home":

            st.subheader("⚙️ Business Baseline")

            st.text_input(
                "Scenario Name",
                value=s["scenario_name"],
                key="scenario_name"
            )

            with st.expander("📊 Core Business Model", expanded=True):

                st.number_input(
                    "Unit Price ($)",
                    value=s["price"],
                    key="price"
                )

                s["variable_cost"] = st.number_input(
                    "Variable Cost ($)",
                    value=s["variable_cost"],
                    key="variable_cost"
                )

                with st.expander("🔍 Audit Variable Cost Breakdown"):
                    v1 = st.number_input("Raw Materials/Unit", value=0.0)
                    v2 = st.number_input("Logistics/Shipping", value=0.0)
                    v3 = st.number_input("Commissions/Other", value=0.0)

                    v_total = v1 + v2 + v3
                    st.write(f"Calculated Total: **${v_total:.2f}**")

                    if st.button("Apply to Variable Cost"):
                        s["variable_cost"] = v_total
                        st.rerun()

                s["volume"] = st.number_input(
                    "Annual Volume",
                    value=s["volume"],
                    key="volume"
                )

                s["fixed_cost"] = st.number_input(
                    "Annual Fixed Costs ($)",
                    value=s["fixed_cost"],
                    key="fixed_cost"
                )

            with st.expander("🔍 Audit Fixed Cost Breakdown"):
                f1 = st.number_input("Rent", value=0.0)
                f2 = st.number_input("Salaries", value=0.0)
                f3 = st.number_input("Admin & Utilities", value=0.0)

                f_total = f1 + f2 + f3
                st.info(f"Total Fixed Cost: ${f_total:,.0f}")

                if st.button("Apply to Fixed Costs"):
                    s["fixed_cost"] = f_total
                    st.rerun()

            st.number_input("Net Fixed Assets ($)", value=s["fixed_assets"], key="fixed_assets")
            st.number_input("Depreciation ($)", value=s["depreciation"], key="depreciation")
            st.number_input("Target Profit ($)", value=s["target_profit_goal"], key="target_profit_goal")

            with st.expander("🔄 Working Capital"):
                st.number_input("Opening Cash ($)", value=s["opening_cash"], key="opening_cash")
                st.number_input("Equity ($)", value=s["equity"], key="equity")
                st.number_input("Debt ($)", value=s["total_debt"], key="total_debt")
                st.number_input("Interest ($)", value=s["annual_interest_only"], key="annual_interest_only")
                st.number_input("Tax Rate (%)", value=s["tax_rate"], key="tax_rate")

            # --------------------------------------------------
            # LOCK SYSTEM
            # --------------------------------------------------
            if not s["baseline_locked"]:
                if st.button("🔒 Lock & Activate Simulation", type="primary"):
                    s["baseline_locked"] = True
                    s["flow_step"] = "control_tower"
                    st.rerun()
            else:
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("🕹️ Go to Tower"):
                        s["flow_step"] = "control_tower"
                        st.rerun()
                with col2:
                    if st.button("🔓 Unlock"):
                        s["baseline_locked"] = False
                        st.rerun()

            if st.button("💾 Save Scenario"):
                s.saved_scenarios[s["scenario_name"]] = {
                    "price": s["price"],
                    "volume": s["volume"],
                    "metrics": dict(m)
                }
                st.success("Saved!")

        else:
            st.info(f"Active: {s['scenario_name']}")
            st.write(f"Price: {s['price']}")
            st.write(f"Volume: {s['volume']}")

    # --------------------------------------------------
    # RIGHT SIDE (UNCHANGED STRUCTURE)
    # --------------------------------------------------
    with col_right:
        st.subheader("🧠 Strategy Modules")

        if not s["baseline_locked"]:
            st.warning("Lock baseline first.")
        else:
            st.write("Modules active...")

    # --------------------------------------------------
    # SNAPSHOT (BOTTOM)
    # --------------------------------------------------
    st.divider()
    st.subheader("📊 Snapshot")

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("ROIC", f"{m.get('roic', 0)*100:.1f}%")
    c2.metric("BEP", f"{m.get('bep_units', 0):,.0f}")
    c3.metric("MOS", f"{m.get('margin_of_safety', 0)*100:.1f}%")
    c4.metric("Cash", f"${m.get('net_cash_position', 0):,.0f}")
