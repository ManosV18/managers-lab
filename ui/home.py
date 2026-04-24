import streamlit as st
import pandas as pd

def run_home():
    s = st.session_state
    m = s.get("metrics", {})

    # Διασφάλιση βασικών μεταβλητών πλοήγησης
    if "flow_step" not in s:
        s.flow_step = "home"
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
        "baseline_locked": False
    }
    for k, v in defaults.items():
        if k not in s:
            s[k] = v

    # ---------------- HERO SECTION ----------------
    st.markdown("""
        <div style='text-align:center; padding: 10px 0;'>
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

    col_left, col_right = st.columns([0.45, 0.55], gap="large")

    # ================= LEFT COLUMN =================
    with col_left:
        st.subheader("⚙️ Business Baseline")
        st.caption("Set your baseline — then test the interactions.")
        
        st.text_input("Scenario Name", key="scenario_name")

        # --- CORE MODEL EXPANDER ---
        with st.expander("📊 Core Business Model", expanded=True):
            st.number_input("Unit Price ($)", key="price", step=1.0)
            
            # Variable Cost Logic
            vc_val = st.number_input("Variable Cost ($)", value=float(s.variable_cost), step=1.0)
            s.variable_cost = vc_val
            
            with st.expander("🔍 Audit VC Breakdown"):
                v1 = st.number_input("Materials", value=0.0, key="audit_v1")
                v2 = st.number_input("Logistics", value=0.0, key="audit_v2")
                if st.button("Apply Breakdown"):
                    s.variable_cost = v1 + v2
                    st.rerun()
            
            st.number_input("Annual Volume", key="volume", step=100)

        # --- FIXED COSTS ---
        with st.expander("🏢 Fixed Costs & Assets"):
            fc_val = st.number_input("Annual Fixed Costs ($)", value=float(s.fixed_cost), step=1000.0)
            s.fixed_cost = fc_val
            st.number_input("Net Fixed Assets ($)", key="fixed_assets", step=1000.0)

        # --- WORKING CAPITAL ---
        with st.expander("🔄 Working Capital & Debt"):
            st.number_input("Opening Cash ($)", key="opening_cash", step=1000.0)
            st.number_input("A/R Days", key="ar_days", step=1)
            st.number_input("Inventory Days", key="inv_days", step=1)
            st.number_input("A/P Days", key="ap_days", step=1)
            st.number_input("Total Debt ($)", key="total_debt", step=1000.0)

        st.divider()

        # --- SIGNALS & ACTIONS ---
        cash_flag = m.get("net_cash_position", 0)
        if cash_flag < 0:
            st.error(f"⚠️ Cash turns negative: ${cash_flag:,.0f}")
        else:
            st.success("✔ Business looks stable.")

        if st.button("Test: What if costs increase 10%?", use_container_width=True):
            s.variable_cost = float(s.variable_cost) * 1.10
            st.rerun()

        if not s.baseline_locked:
            if st.button("▶ LOCK BASELINE & TEST", type="primary", use_container_width=True):
                s.baseline_locked = True
                st.rerun()
        else:
            if st.button("🔓 UNLOCK TO EDIT", use_container_width=True):
                s.baseline_locked = False
                st.rerun()

    # ================= RIGHT COLUMN =================
    with col_right:
        st.subheader("🧠 The Simulation Logic")
        
        if not s.baseline_locked:
            st.warning("👈 Set and Lock your baseline to enable strategic tools.")
            st.info("The system needs a starting point to calculate how variables interact.")
        else:
            st.success("✅ Baseline Locked. Simulation Active.")
            
        st.markdown("""
        **What you are testing here:**
        - **Timing:** How payables/receivables gap eats your cash.
        - **Pressure:** How margin contraction destroys ROIC.
        - **Interaction:** How small changes in inventory collide with fixed costs.
        """)
        
        st.info("👉 Change a number on the left and watch the Dashboard below update instantly.")

    # ================= BOTTOM: METRICS =================
    st.divider()
    st.subheader("📊 Tactical Dashboard")
    
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("ROIC", f"{m.get('roic', 0)*100:.1f}%")
    c2.metric("Break-Even", f"{m.get('bep_units', 0):,.0f} units")
    c3.metric("Safety Margin", f"{m.get('margin_of_safety', 0)*100:.1f}%")
    c4.metric("Net Cash", f"${m.get('net_cash_position', 0):,.0f}")
