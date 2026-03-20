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
        <div style='text-align:center; padding: 10px 0 30px 0;'>
            <h1 style='font-size:64px; font-weight:900; color:#1E3A8A;'>
            Managers Lab<span style='color:#ef4444;'>.</span>
            </h1>
            <div style='font-size:26px; font-weight:700; margin-top:10px;'>
            Business Strategy Simulator
            </div>
            <div style='font-size:18px; color:#475569; max-width:750px; margin:auto; margin-top:10px;'>
            Test pricing, financing and operational decisions before implementing them in the real world.
            </div>
            <div style='font-size:14px; color:#94a3b8; margin-top:10px;'>
            Financial Stress Testing & Strategy Simulation Platform
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    # --------------------------------------------------
    # STRATEGY EXPLANATION
    # --------------------------------------------------
    colA, colB = st.columns(2)
    with colA:
        st.markdown("""
        ### ⚙️ Financial Simulation Engine
        All modules run on a unified **financial engine** that converts business assumptions into real-time metrics.
        """)
    with colB:
        st.markdown("""
        ### 🔁 Strategy Simulation Loop
        1️⃣ Define Baseline ➡️ 2️⃣ Run Diagnostics ➡️ 3️⃣ Simulate Decisions ➡️ 4️⃣ Optimize
        """)

    st.divider()

    # --------------------------------------------------
    # SNAPSHOT METRICS
    # --------------------------------------------------
    st.subheader("📊 Executive Simulation Snapshot")
    c1, c2, c3, c4 = st.columns(4)
    
    c1.metric("ROIC", f"{m.get('roic', 0)*100:.1f}%")
    c2.metric("Break-Even", f"{m.get('bep_units', 0):,.0f} units")
    c3.metric("Margin of Safety", f"{m.get('margin_of_safety', 0)*100:.1f}%")
    c4.metric("Net Cash Position", f"${m.get('net_cash_position', 0):,.0f}")
    
    st.divider()

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
                
                # --- Variable Cost Section με Audit Popover ---
                col_vc_input, col_vc_pop = st.columns([0.7, 0.3])
                with col_vc_input:
                    st.number_input("Variable Cost ($)", value=float(s.get("variable_cost", 90.0)), key="variable_cost")
                with col_vc_pop:
                    st.write("") # Alignment padding
                    with st.popover("🔍 Audit VC"):
                        st.caption("Variable Cost Breakdown")
                        v1 = st.number_input("Raw Materials/Unit", value=0.0)
                        v2 = st.number_input("Logistics/Shipping", value=0.0)
                        v3 = st.number_input("Commissions/Other", value=0.0)
                        v_total = v1 + v2 + v3
                        st.info(f"Total: ${v_total:.2f}")
                        if st.button("Apply Total VC"):
                            s.variable_cost = v_total
                            st.rerun()

                st.number_input("Annual Volume", value=int(s.get("volume", 15000)), key="volume")
                
                # --- Fixed Cost Section με Audit Popover ---
                col_fc_input, col_fc_pop = st.columns([0.7, 0.3])
                with col_fc_input:
                    st.number_input("Annual Fixed Costs ($)", value=float(s.get("fixed_cost", 450000.0)), key="fixed_cost")
                with col_fc_pop:
                    st.write("") # Alignment padding
                    with st.popover("🔍 Audit FC"):
                        st.caption("Fixed Cost Breakdown")
                        f1 = st.number_input("Monthly Rent", value=0.0) * 12
                        f2 = st.number_input("Annual Salaries", value=0.0)
                        f3 = st.number_input("Admin & Utilities", value=0.0)
                        f_total = f1 + f2 + f3
                        st.info(f"Annual Total: ${f_total:,.0f}")
                        if st.button("Apply Total FC"):
                            s.fixed_cost = f_total
                            st.rerun()

                st.number_input("Net Fixed Assets ($)", value=float(s.get("fixed_assets", 800000.0)), key="fixed_assets")
                st.number_input("Annual Depreciation ($)", value=float(s.get("depreciation", 50000.0)), key="depreciation")
                st.number_input("Target Profit ($)", value=float(s.get("target_profit_goal", 200000.0)), key="target_profit_goal")

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
            
            if st.button("🔒 Lock & Activate Simulation", type="primary", use_container_width=True):
                s.baseline_locked = True
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
        st.subheader("🧠 Strategy Simulation Modules")
        
        if not s.get("baseline_locked"):
            st.info("🔒 Lock the baseline to activate the simulation modules.")
        else:
            t1, t2, t3, t4 = st.tabs(["Strategy", "Finance", "Operations", "Risk & Reports"])
            
            with t1:
                if st.button("🕹️ Mission Control", use_container_width=True, type="primary"): s.selected_tool="control_tower"; s.flow_step="tool"; st.rerun()
                if st.button("🎯 Pricing Strategy", use_container_width=True): s.selected_tool="pricing_strategy"; s.flow_step="tool"; st.rerun()
                if st.button("📡 Pricing Radar", use_container_width=True): s.selected_tool="pricing_radar"; s.flow_step="tool"; st.rerun()
                if st.button("📉 Loss Threshold", use_container_width=True): s.selected_tool="loss_threshold"; s.flow_step="tool"; st.rerun()
                if st.button("🧭 QSPM Strategy Matrix", use_container_width=True): s.selected_tool="qspm_analyzer"; s.flow_step="tool"; st.rerun()
                if st.button("⚖️ Cash Survival Simulator", use_container_width=True): s.selected_tool="break_even_shift"; s.flow_step="tool"; st.rerun()
                if st.button("👥 Customer Lifetime Value (CLV)", use_container_width=True): s.selected_tool="clv_calculator"; s.flow_step="tool"; st.rerun()

            with t2:
                if st.button("📈 Growth Funding (AFN)", use_container_width=True): s.selected_tool="growth_funding"; s.flow_step="tool"; st.rerun()
                if st.button("📉 WACC Optimizer", use_container_width=True): s.selected_tool="wacc_optimizer"; s.flow_step="tool"; st.rerun()
                if st.button("⚖️ Loan vs Leasing", use_container_width=True): s.selected_tool="loan_vs_leasing"; s.flow_step="tool"; st.rerun()

            with t3:
                # Εδώ μπορείς να αλλάξεις το όνομα του κουμπιού αν θες
                if st.button("🔢 Unit Cost Analyzer", use_container_width=True): s.selected_tool="unit_cost_analyzer"; s.flow_step="tool"; st.rerun()
                if st.button("📦 Inventory Optimizer", use_container_width=True): s.selected_tool="inventory_manager"; s.flow_step="tool"; st.rerun()
                if st.button("📊 NPV Receivables Analyzer", use_container_width=True): s.selected_tool="receivables_npv"; s.flow_step="tool"; st.rerun()
                if st.button("🔄 Cash Conversion Cycle", use_container_width=True): s.selected_tool="cash_cycle"; s.flow_step="tool"; st.rerun()
                if st.button("🤝 Payables Manager", use_container_width=True): s.selected_tool="payables_manager"; s.flow_step="tool"; st.rerun()
                if st.button("💰 Working Capital Engine", use_container_width=True): s.selected_tool="wc_optimizer"; s.flow_step="tool"; st.rerun()

            with t4:
                if st.button("🚨 Cash Fragility Index", use_container_width=True): s.selected_tool="cash_fragility"; s.flow_step="tool"; st.rerun()
                if st.button("🗺️ Resilience Map", use_container_width=True): s.selected_tool="resilience_map"; s.flow_step="tool"; st.rerun()
                if st.button("📉 Stress Test Simulator", use_container_width=True): s.selected_tool="stress_test"; s.flow_step="tool"; st.rerun()
                st.divider()
                # Τα παρακάτω μπορούν να καταργηθούν αφού έχουμε το Mission Control
                if st.button("🏁 Executive Dashboard", use_container_width=True): s.selected_tool="executive_dashboard"; s.flow_step="tool"; st.rerun()
                if st.button("📄 Executive Decision Report", use_container_width=True): s.selected_tool="decision_report"; s.flow_step="tool"; st.rerun()
                if st.button("📊 Scenario Comparison", use_container_width=True): s.selected_tool="scenario_comparison"; s.flow_step="tool"; st.rerun()

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
