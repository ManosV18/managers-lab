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
        "_name": "Baseline Scenario",
    }
    for k, v in defaults.items():
        if k not in s:
            s[k] = v

    # --------------------------------------------------
    # HERO SECTION
    # --------------------------------------------------
    st.markdown("""
<div style='text-align:center; padding: 10px 0 5px 0;'>
    <div style='font-size:26px; font-weight:700; color:#111;'>
        Your business looks profitable.
    </div>
    <div style='font-size:22px; font-weight:600; color:#DC2626;'>
        But it may be running out of cash.
    </div>
    <div style='font-size:14px; color:#6B7280; margin-top:8px;'>
        Change one assumption. See what breaks.
    </div>
</div>
""", unsafe_allow_html=True)
    
    # --------------------------------------------------
    # MAIN LAYOUT
    # --------------------------------------------------
    col_left, col_right = st.columns([0.4, 0.6], gap="large")

    with col_left:
        if s.get("flow_step") == "home":
            st.subheader("⚙️ Start with a real scenario")
            st.caption("**Start simple. Then stress the system.**")

            with st.expander("📊 Core Business Model", expanded=False):
                st.number_input("Unit Price ($)", key="price", min_value=0.0, step=1.0)

                # Variable Cost — χειροκίνητο state γιατί έχει audit breakdown
                vc_val = st.number_input("Variable Cost ($)", value=float(s.get("variable_cost", 100.0)))
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
                if st.button("▶ Test My Business", type="primary", use_container_width=True):
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
        st.subheader("🧠 Test a Decision")

        is_disabled = not s.get("baseline_locked")
        if is_disabled:
            st.warning("Set your baseline first — then test decisions.")

        st.subheader("What this tests")

        st.markdown("""
        - Pricing vs cost pressure  
        - Cash timing (receivables vs payables)  
        - Inventory drag  
        - Contribution margin  

        **Change one input → the system reacts**
        """)

        st.info("👉 Start on the left. Change one number and watch what happens.")
        
        

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

