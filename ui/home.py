# -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd
from datetime import datetime
from fpdf import FPDF
import plotly.express as px
from core.pdf_report import generate_professional_pdf  # Εισαγωγή του νέου εργαλείου

# --------------------------------------------------
# REPORTING & DASHBOARD FUNCTIONS
# --------------------------------------------------
def show_decision_report():
    st.title("📄 Executive Decision Report")
    metrics = st.session_state.get("metrics", {})
    scenario_name = st.session_state.get("scenario_name", "Baseline Scenario")
    current_date = datetime.now().strftime("%d/%m/%Y %H:%M")
    
    report = {
        "ROIC": f"{metrics.get('roic',0)*100:.1f}%",
        "Break Even": f"{metrics.get('bep_units',0):,.0f} units",
        "Net Cash": f"EUR{metrics.get('net_cash_position',0):,.0f}",
        "Margin of Safety": f"{metrics.get('margin_of_safety', 0)*100:.1f}%"
    }
    
    st.markdown(f"**Managers Lab – Strategic Simulation Report**\n\nScenario: **{scenario_name}**\n\nDate: **{current_date}**")
    df = pd.DataFrame(report.items(), columns=["Metric", "Value"])
    st.table(df)
    
    col1, col2 = st.columns(2)
    with col1:
        st.download_button("Download CSV", df.to_csv(index=False).encode("utf-8"), file_name="decision_report.csv", mime="text/csv", use_container_width=True)

def show_scenario_comparison():
    st.title("📊 Scenario Comparison")
    scenarios = st.session_state.get("saved_scenarios", {})
    if not scenarios:
        st.info("No saved scenarios yet.")
        return
    rows = []
    for name, data in scenarios.items():
        m = data.get("metrics", {})
        rows.append({
            "Scenario": name, 
            "Price": data.get("price"),
            "Volume": data.get("volume"),
            "ROIC %": f"{m.get('roic', 0)*100:.1f}%", 
            "Break Even": f"{m.get('bep_units', 0):,.0f}"
        })
    st.dataframe(pd.DataFrame(rows), use_container_width=True)

def show_executive_dashboard():
    st.title("🏁 Executive Dashboard")
    m = st.session_state.get("metrics", {})

    c1, c2, c3, c4 = st.columns(4)

    c1.metric("ROIC", f"{m.get('roic', 0)*100:.1f}%")
    c2.metric("Break-Even", f"{m.get('bep_units', 0):,.0f} units")
    c3.metric("Net Cash", f"EUR{m.get('net_cash_position', 0):,.0f}")
    c4.metric("Margin of Safety", f"{m.get('margin_of_safety', 0)*100:.1f}%")

    st.divider()

    c5, c6 = st.columns(2)
    c5.metric("Revenue", f"EUR{m.get('revenue', 0):,.0f}")
    c6.metric("Total Costs", f"EUR{m.get('total_costs', 0):,.0f}")

# --------------------------------------------------
# MAIN HOME RUNNER
# --------------------------------------------------
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
    # SNAPSHOT METRICS (Corrected Layout)
    # --------------------------------------------------
    st.subheader("📊 Executive Simulation Snapshot")
    c1, c2, c3, c4 = st.columns(4)
    
    # c1: Η απόδοση των χρημάτων που επενδύθηκαν
    c1.metric("ROIC", f"{m.get('roic', 0)*100:.1f}%")
    
    # c2: Το σημείο μηδενισμού (μονάδες)
    c2.metric("Break-Even", f"{m.get('bep_units', 0):,.0f} units")
    
    # c3: Πόσο "αέρα" έχουν οι πωλήσεις πριν τις ζημιές (Αντικαθιστά το Unit Price που είναι input)
    c3.metric("Margin of Safety", f"{m.get('margin_of_safety', 0)*100:.1f}%")
    
    # c4: Το πραγματικό διαθέσιμο ταμείο
    c4.metric("Net Cash Position", f"EUR{m.get('net_cash_position', 0):,.0f}")
    
    st.divider()

    # --------------------------------------------------
    # MAIN LAYOUT
    # --------------------------------------------------
    col_left, col_right = st.columns([0.4, 0.6], gap="large")

    with col_left:
        # Εμφανίζουμε τα inputs ΜΟΝΟ αν είμαστε στο home step
        # Αυτό αποτρέπει το Duplicate Key Error όταν φορτώνονται τα reports
        if s.get("flow_step") == "home":
            st.subheader("⚙️ Business Baseline")
            st.text_input("Scenario Name", value=s.get("scenario_name", "Baseline Scenario"), key="scenario_name")
            
            with st.expander("📊 Core Business Model", expanded=True):
                st.number_input("Unit Price (EUR)", value=float(s.get("price", 150.0)), key="price")
                st.number_input("Variable Cost (EUR)", value=float(s.get("variable_cost", 90.0)), key="variable_cost")
                st.number_input("Annual Volume", value=int(s.get("volume", 15000)), key="volume")
                st.number_input("Annual Fixed Costs (EUR)", value=float(s.get("fixed_cost", 450000.0)), key="fixed_cost")
                st.number_input("Net Fixed Assets (EUR)", value=float(s.get("fixed_assets", 800000.0)), key="fixed_assets")
                st.number_input("Target Profit (EUR)", value=float(s.get("target_profit_goal", 200000.0)), key="target_profit_goal")

            with st.expander("🔄 Working Capital & Liquidity"):
                st.number_input("Opening Cash (EUR)", value=float(s.get("opening_cash", 150000.0)), key="opening_cash")
                st.number_input("Total Debt (EUR)", value=float(s.get("total_debt", 500000.0)), key="total_debt", help="Total bank loans and interest-bearing liabilities.")
                st.number_input("A/R Days", value=int(s.get("ar_days", 60)), key="ar_days")
                st.number_input("Inventory Days", value=int(s.get("inv_days", 45)), key="inv_days")
                st.number_input("A/P Days", value=int(s.get("ap_days", 30)), key="ap_days")
                st.number_input("Annual Debt Service (EUR)", value=float(s.get("annual_debt_service", 70000.0)), key="annual_debt_service")

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
            # Αν είμαστε σε tool/report, δείχνουμε απλώς μια σύνοψη χωρίς widgets
            st.info(f"💡 Active Scenario: **{s.get('scenario_name')}**")
            st.write(f"Price: EUR{s.get('price')}")
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
                if st.button("🔢 Unit Cost Analyzer", use_container_width=True): s.selected_tool="unit_cost_analyzer"; s.flow_step="tool"; st.rerun()
                if st.button("📦 Inventory Optimizer", use_container_width=True): s.selected_tool="inventory_manager"; s.flow_step="tool"; st.rerun()
                if st.button("📊 NPV Receivables Analyzer", use_container_width=True): s.selected_tool="receivables_npv"; s.flow_step="tool"; st.rerun()
                if st.button("🔄 Cash Conversion Cycle", use_container_width=True): s.selected_tool="cash_cycle"; s.flow_step="tool"; st.rerun()
                if st.button("🤝 Payables Manager", use_container_width=True): s.selected_tool="payables_manager"; s.flow_step="tool"; st.rerun()
                if st.button("💰 Working Capital Engine", use_container_width=True): s.selected_tool="wc_optimizer"; s.flow_step="tool"; st.rerun()

            with t4:
                if st.button("🛡️ Strategic Shock Simulator", use_container_width=True): s.selected_tool="shock_simulator"; s.flow_step="tool"; st.rerun()
                if st.button("🚨 Cash Fragility Index", use_container_width=True): s.selected_tool="cash_fragility"; s.flow_step="tool"; st.rerun()
                if st.button("🗺️ Resilience Map", use_container_width=True): s.selected_tool="resilience_map"; s.flow_step="tool"; st.rerun()
                if st.button("📉 Stress Test Simulator", use_container_width=True): s.selected_tool="stress_test"; s.flow_step="tool"; st.rerun()
                st.divider()
                if st.button("🏁 Executive Dashboard", use_container_width=True): s.selected_tool="executive_dashboard"; s.flow_step="tool"; st.rerun()
                if st.button("📄 Executive Decision Report", use_container_width=True): s.selected_tool="decision_report"; s.flow_step="tool"; st.rerun()
                if st.button("📊 Scenario Comparison", use_container_width=True): s.selected_tool="scenario_comparison"; s.flow_step="tool"; st.rerun()

            # --- COLD LOGIC QUICK ANALYSIS ---
            st.divider()
            with st.expander("🔍 Capital Structure Analysis", expanded=True):
                ca1, ca2 = st.columns(2)
                ca1.write(f"**Total Debt:** EUR{s.get('total_debt', 0):,.0f}")
                ca1.write(f"**Fixed Assets:** EUR{s.get('fixed_assets', 0):,.0f}")
                
                # Υπολογισμός Net Debt live
                net_debt_val = s.get('total_debt', 0) - s.get('opening_cash', 0)
                color = "red" if net_debt_val > 0 else "green"
                ca2.markdown(f"**Net Debt:** <span style='color:{color}'>EUR{net_debt_val:,.0f}</span>", unsafe_allow_html=True)
                ca2.write(f"**Invested Capital:** EUR{m.get('invested_capital', 0):,.0f}")
