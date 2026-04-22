import streamlit as st
import pandas as pd
from datetime import datetime


# --------------------------------------------------
# STATE INIT (NO CRASH VERSION)
# --------------------------------------------------
def init_state():
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
        if k not in st.session_state:
            st.session_state[k] = v


# --------------------------------------------------
# MAIN APP
# --------------------------------------------------
def run_home():

    init_state()

    s = st.session_state
    m = s.get("metrics", {})

    if "saved_scenarios" not in s:
        s.saved_scenarios = {}

    # --------------------------------------------------
    # HERO
    # --------------------------------------------------
    st.markdown(
        """
        <div style='text-align:center; padding: 10px 0;'>
            <div style='font-size:22px; font-weight:600; color:#1E3A8A;'>
            Test your decisions before they impact your business
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    # --------------------------------------------------
    # LAYOUT
    # --------------------------------------------------
    col_left, col_right = st.columns([0.4, 0.6], gap="large")

    # ==================================================
    # LEFT SIDE (INPUTS)
    # ==================================================
    with col_left:

        if s["flow_step"] == "home":

            st.subheader("⚙️ Business Baseline")

            st.text_input(
                "Scenario Name",
                key="scenario_name"
            )

            with st.expander("📊 Core Business Model", expanded=True):

                st.number_input("Unit Price ($)", key="price")

                st.number_input("Variable Cost ($)", key="variable_cost")

                with st.expander("🔍 Variable Cost Breakdown"):
                    v1 = st.number_input("Raw Materials/Unit", value=0.0)
                    v2 = st.number_input("Logistics/Shipping", value=0.0)
                    v3 = st.number_input("Commissions/Other", value=0.0)

                    total = v1 + v2 + v3
                    st.write(f"Calculated Total: **${total:.2f}**")

                    if st.button("Apply Breakdown"):
                        s["variable_cost"] = total
                        st.rerun()

                st.number_input("Annual Volume", key="volume")

                st.number_input("Annual Fixed Costs ($)", key="fixed_cost")

            with st.expander("🔍 Fixed Cost Breakdown"):
                f1 = st.number_input("Rent", value=0.0)
                f2 = st.number_input("Salaries", value=0.0)
                f3 = st.number_input("Admin & Utilities", value=0.0)

                total_f = f1 + f2 + f3
                st.info(f"Total Fixed Cost: ${total_f:,.0f}")

                if st.button("Apply Fixed Costs"):
                    s["fixed_cost"] = total_f
                    st.rerun()

            st.number_input("Net Fixed Assets ($)", key="fixed_assets")
            st.number_input("Depreciation ($)", key="depreciation")
            st.number_input("Target Profit ($)", key="target_profit_goal")

            with st.expander("🔄 Working Capital"):
                st.number_input("Opening Cash ($)", key="opening_cash")
                st.number_input("Equity ($)", key="equity")
                st.number_input("Debt ($)", key="total_debt")
                st.number_input("Interest ($)", key="annual_interest_only")
                st.number_input("Tax Rate (%)", key="tax_rate")

            # --------------------------------------------------
            # LOCK
            # --------------------------------------------------
            if not s["baseline_locked"]:
                if st.button("🔒 Lock & Activate", type="primary"):
                    s["baseline_locked"] = True
                    s["flow_step"] = "control_tower"
                    st.rerun()
            else:
                col1, col2 = st.columns(2)

                with col1:
                    if st.button("🕹️ Tower"):
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

    # ==================================================
    # RIGHT SIDE (MODULES)
    # ==================================================
    with col_right:

        st.subheader("🧠 Strategy Modules")

        if not s["baseline_locked"]:
            st.warning("Lock baseline first.")
        else:
            st.write("Modules active...")

    # ==================================================
    # SNAPSHOT
    # ==================================================
    st.divider()
    st.subheader("📊 Snapshot")

    c1, c2, c3, c4 = st.columns(4)

    c1.metric("ROIC", f"{m.get('roic', 0)*100:.1f}%")
    c2.metric("Break-Even", f"{m.get('bep_units', 0):,.0f}")
    c3.metric("Margin", f"{m.get('margin_of_safety', 0)*100:.1f}%")
    c4.metric("Cash", f"${m.get('net_cash_position', 0):,.0f}")
