import streamlit as st
import pandas as pd
from datetime import datetime

def run_home():
    s = st.session_state
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
        if s.get("flow_step") == "home":
            
            st.subheader("⚙️ Business Baseline")
            st.text_input("Scenario Name", value=s.get("scenario_name", "Baseline Scenario"), key="scenario_name")

            with st.expander("📊 Core Business Model", expanded=True):

                st.number_input("Unit Price ($)", value=float(s.get("price", 150.0)), key="price")

                vc_val = st.number_input("Variable Cost ($)", value=float(s.get("variable_cost", 90.0)))
                s.variable_cost = vc_val

                st.number_input("Annual Volume", value=int(s.get("volume", 15000)), key="volume")

            fc_val = st.number_input("Annual Fixed Costs ($)", value=float(s.get("fixed_cost", 450000.0)))
            s.fixed_cost = fc_val

            st.number_input("Net Fixed Assets ($)", value=float(s.get("fixed_assets", 800000.0)), key="fixed_assets")
            st.number_input("Annual Depreciation ($)", value=float(s.get("depreciation", 50000.0)), key="depreciation")
            st.number_input("Target Profit ($)", value=float(s.get("target_profit_goal", 200000.0)), key="target_profit_goal")

            st.divider()

            # --------------------------------------------------
            # SNAPSHOT (ΜΕΤΑ ΤΑ INPUTS - ΣΩΣΤΗ ΘΕΣΗ)
            # --------------------------------------------------
            st.subheader("📊 Executive Simulation Snapshot")

            c1, c2, c3, c4 = st.columns(4)

            c1.metric("ROIC", f"{m.get('roic', 0)*100:.1f}%")
            c2.metric("Break-Even", f"{m.get('bep_units', 0):,.0f} units")
            c3.metric("Margin of Safety", f"{m.get('margin_of_safety', 0)*100:.1f}%")
            c4.metric("Net Cash Position", f"${m.get('net_cash_position', 0):,.0f}")

            st.divider()

            # --------------------------------------------------
            # LOCK / SAVE
            # --------------------------------------------------
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
                st.success("Scenario saved!")

    with col_right:
        st.subheader("🧠 Business Strategy Modules")

        if not s.get("baseline_locked"):
            st.info("Lock baseline to activate modules.")
        else:
            st.write("Modules go here")
