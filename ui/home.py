import streamlit as st
import pandas as pd
from datetime import datetime


# --------------------------------------------------
# QUICK START
# --------------------------------------------------
def render_quickstart(s):

    if s.get("baseline_locked"):
        return

    if not s.get("show_quickstart"):
        st.markdown("<div style='text-align:center; margin: 10px 0 20px 0;'>", unsafe_allow_html=True)
        if st.button("Start with your numbers", type="primary", key="btn_open_qs"):
            s.show_quickstart = True
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)
        return

    st.markdown("""
    <div style='text-align:center; padding:10px 0;'>
        <div style='font-size:18px; font-weight:700;'>Quick Start</div>
        <div style='font-size:13px; color:#64748b;'>4 numbers. Instant simulation.</div>
    </div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns(2)

    with col1:
        price_qs = st.number_input("Unit Price ($)", value=float(s.get("price", 0.0)), key="qs_price")
        vc_qs = st.number_input("Variable Cost ($)", value=float(s.get("variable_cost", 0.0)), key="qs_vc")

    with col2:
        volume_qs = st.number_input(
            "Monthly Units",
            value=int(s.get("volume", 0) // 12) if s.get("volume") else 0,
            key="qs_vol"
        )
        fc_qs = st.number_input(
            "Monthly Fixed Costs ($)",
            value=float(s.get("fixed_cost", 0.0) / 12) if s.get("fixed_cost") else 0.0,
            key="qs_fc"
        )

    # ---------------- LIVE PREVIEW ----------------
    if price_qs > 0 and vc_qs >= 0 and volume_qs > 0 and fc_qs > 0:

        margin = price_qs - vc_qs
        monthly_profit = (margin * volume_qs) - fc_qs
        bep = fc_qs / margin if margin > 0 else 0

        st.markdown("---")

        if monthly_profit > 0:
            st.success(f"You are profitable, but you need {int(bep):,} units/month to break even.")
        else:
            st.error("At this level, your business is losing money each month.")

        c1, c2, c3 = st.columns(3)
        c1.metric("Margin", f"${margin:.2f}")
        c2.metric("Profit", f"${monthly_profit:,.0f}")
        c3.metric("Break-even", f"{bep:,.0f}")

    # ---------------- ACTION ----------------
    if st.button("Run Full Simulation", type="primary", use_container_width=True):

        if price_qs > 0 and volume_qs > 0:

            s.price = price_qs
            s.variable_cost = vc_qs
            s.volume = volume_qs * 12
            s.fixed_cost = fc_qs * 12

            s.baseline_locked = True
            s.flow_step = "control_tower"
            s.show_quickstart = False

            st.rerun()
        else:
            st.warning("Enter at least price and volume.")


# --------------------------------------------------
# MAIN APP
# --------------------------------------------------
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
        <div style='text-align:center; padding: 20px 0 10px 0;'>
            <div style='font-size:32px; font-weight:700; color:#1E3A8A; max-width:750px; margin:auto;'>
            Test your pricing and see if your business actually makes money.
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    # QUICK START ENTRY
    render_quickstart(s)

    st.divider()

    # --------------------------------------------------
    # STRATEGY EXPLANATION
    # --------------------------------------------------
    colA, colB = st.columns(2)

    with colA:
        st.markdown("### Financial Simulation Engine\nTurns assumptions into real-time metrics.")

    with colB:
        st.markdown("### Strategy Loop\nBaseline → Test → Simulate → Optimize")

    st.divider()

    # --------------------------------------------------
    # SNAPSHOT
    # --------------------------------------------------
    st.subheader("📊 Executive Snapshot")

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("ROIC", f"{m.get('roic', 0)*100:.1f}%")
    c2.metric("Break-Even", f"{m.get('bep_units', 0):,.0f}")
    c3.metric("MOS", f"{m.get('margin_of_safety', 0)*100:.1f}%")
    c4.metric("Cash", f"${m.get('net_cash_position', 0):,.0f}")

    st.divider()

    # --------------------------------------------------
    # REST OF APP
    # --------------------------------------------------
    col_left, col_right = st.columns([0.4, 0.6], gap="large")

    with col_left:
        st.info(f"Active Scenario: {s.get('scenario_name','Baseline')}")

    with col_right:

        st.subheader("🧠 Business Modules")
        st.caption("Choose one area to test your assumptions")

        if not s.get("baseline_locked"):
            st.info("Lock your baseline to activate modules.")
        else:

            t1, t2, t3, t4 = st.tabs(["Strategy", "Finance", "Ops", "Risk"])

            with t1:
                st.markdown("**Pricing & demand decisions**")
                if st.button("Price & Profit Planner", use_container_width=True):
                    s.selected_tool = "pricing_strategy"
                    s.flow_step = "tool"
                    st.rerun()

                if st.button("Break-even Shift", use_container_width=True):
                    s.selected_tool = "break_even_shift"
                    s.flow_step = "tool"
                    st.rerun()

            with t2:
                st.markdown("**Funding & capital decisions**")
                if st.button("Cash & Funding View", use_container_width=True):
                    s.selected_tool = "growth_funding"
                    s.flow_step = "tool"
                    st.rerun()

                if st.button("Cost of Capital (WACC)", use_container_width=True):
                    s.selected_tool = "wacc_optimizer"
                    s.flow_step = "tool"
                    st.rerun()

            with t3:
                st.markdown("**Cash flow & operations**")
                if st.button("Cash Conversion Cycle", use_container_width=True):
                    s.selected_tool = "cash_cycle"
                    s.flow_step = "tool"
                    st.rerun()

                if st.button("Working Capital Unlock", use_container_width=True):
                    s.selected_tool = "wc_optimizer"
                    s.flow_step = "tool"
                    st.rerun()

            with t4:
                st.markdown("**Risk & stress testing**")
                if st.button("Cash Runway Risk", use_container_width=True):
                    s.selected_tool = "cash_fragility"
                    s.flow_step = "tool"
                    st.rerun()

                if st.button("Worst Case Scenario", use_container_width=True):
                    s.selected_tool = "stress_test"
                    s.flow_step = "tool"
                    st.rerun()

