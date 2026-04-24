import streamlit as st

def run_home():
    s = st.session_state
    m = s.get("metrics", {})

    if "saved_scenarios" not in s:
        s.saved_scenarios = {}

    # ---------------- DEFAULTS ----------------
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
        "scenario_name": "Baseline Scenario",
    }

    for k, v in defaults.items():
        if k not in s:
            s[k] = v

    # ---------------- HERO ----------------
    st.markdown("""
    <div style='text-align:center; padding: 10px 0;'>
        <div style='font-size:26px; font-weight:700;'>
            Your business looks profitable.
        </div>
        <div style='font-size:22px; font-weight:600; color:#DC2626;'>
            But it may be running out of cash.
        </div>
        <div style='font-size:14px; color:#6B7280; margin-top:6px;'>
            Change one assumption. See what breaks.
        </div>
    </div>
    """, unsafe_allow_html=True)

    col_left, col_right = st.columns([0.4, 0.6])

    # ================= LEFT =================
    with col_left:

        st.subheader("⚙️ Start with a real scenario")
        st.caption("Start simple. Then stress the system.")

        st.text_input("Scenario Name", key="scenario_name")

        # -------- CORE MODEL --------
        with st.expander("📊 Core Business Model", expanded=True):

            st.number_input("Unit Price ($)", key="price", min_value=0.0)
            st.number_input("Variable Cost ($)", key="variable_cost", min_value=0.0)
            st.number_input("Annual Volume", key="volume", min_value=0)

        # -------- FIXED COST --------
        st.number_input("Annual Fixed Costs ($)", key="fixed_cost", min_value=0.0)

        # -------- WORKING CAPITAL --------
        with st.expander("🔄 Working Capital"):

            st.number_input("Opening Cash ($)", key="opening_cash")
            st.number_input("A/R Days", key="ar_days")
            st.number_input("Inventory Days", key="inv_days")
            st.number_input("A/P Days", key="ap_days")

        # ================= CORE SIGNAL =================
        st.divider()

        cash_flag = m.get("net_cash_position", 0)

        if cash_flag < 0:
            st.error("⚠️ Cash turns negative — even though the business looks profitable.")
            st.markdown("💥 This business will need external financing.")
        else:
            st.success("✔ Looks stable. Now change one number and try to break it.")

        # ================= AUTO DEMO =================
        if st.button("Test: What if costs increase 10%?", use_container_width=True):
            s.variable_cost = s.get("variable_cost", 0) * 1.10
            st.rerun()

        # ================= ACTION =================
        if st.button("▶ Test My Business", type="primary", use_container_width=True):
            s.baseline_locked = True
            st.rerun()

        if st.button("💾 Save Scenario", use_container_width=True):
            s.saved_scenarios[s.scenario_name] = dict(s)
            st.success(f"Saved: {s.scenario_name}")

    # ================= RIGHT =================
    with col_right:

        st.subheader("What this tests")

        st.markdown("""
        - Pricing vs cost pressure  
        - Cash timing (receivables vs payables)  
        - Inventory drag  
        - Contribution margin  
        """)

        st.info("👉 Change one number on the left")

        st.markdown("**Try this:** Increase cost by 10% 👈")

    # ================= METRICS =================
    st.divider()
    st.subheader("📊 What happens under pressure")

    c1, c2, c3, c4 = st.columns(4)

    c1.metric("ROIC", f"{m.get('roic', 0)*100:.1f}%")
    c2.metric("Break-Even", f"{m.get('bep_units', 0):,.0f}")
    c3.metric("Margin of Safety", f"{m.get('margin_of_safety', 0)*100:.1f}%")
    c4.metric("Net Cash", f"${m.get('net_cash_position', 0):,.0f}")
