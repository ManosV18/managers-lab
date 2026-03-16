import streamlit as st
import pandas as pd
from datetime import datetime
from fpdf import FPDF
from io import BytesIO

# --------------------------------------------------
# 1. REPORT FUNCTION
# --------------------------------------------------
def show_decision_report():
    st.title("📄 Executive Decision Report")

    metrics = st.session_state.get("metrics", {})
    scenario_name = st.session_state.get("scenario_name", "Baseline Scenario")
    current_date = datetime.now().strftime("%d/%m/%Y %H:%M")

    report = {
        "ROIC": f"{metrics.get('roic', 0)*100:.1f}%",
        "Break Even": f"{metrics.get('bep_units', 0):,.0f} units",
        "Net Cash": f"€{metrics.get('net_cash_position', 0):,.2f}",
        "Liquidity Buffer": f"{metrics.get('liquidity_buffer', 0):,.1f}%"
    }

    st.markdown(f"""
    <div style="background-color:#f1f5f9; padding:20px; border-radius:10px; border-left:5px solid #1E3A8A;">
        <h3 style="margin:0;color:#1E3A8A;">Managers Lab</h3>
        <p style="margin:0;font-weight:bold;">Strategic Simulation Report</p>
        <hr>
        <b>Scenario:</b> {scenario_name}<br>
        <b>Date:</b> {current_date}
    </div>
    """, unsafe_allow_html=True)

    df = pd.DataFrame(report.items(), columns=["Metric", "Value"])
    st.table(df)

    col1, col2 = st.columns(2)
    with col1:
        st.download_button("Download CSV", df.to_csv(index=False), file_name="decision_report.csv", mime="text/csv", use_container_width=True)

    with col2:
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", "B", 16)
        pdf.cell(200, 10, "Managers Lab", ln=True)
        pdf.set_font("Arial", "B", 12)
        pdf.cell(200, 10, "Strategic Simulation Report", ln=True)
        pdf.ln(10)
        pdf.set_font("Arial", "B", 12)
        pdf.cell(100, 10, "Metric", border=1)
        pdf.cell(80, 10, "Value", border=1, ln=True)
        pdf.set_font("Arial", size=12)
        for metric, value in report.items():
            pdf.cell(100, 10, str(metric), border=1)
            pdf.cell(80, 10, str(value), border=1, ln=True)
        
        pdf_output = pdf.output(dest='S').encode('latin-1')
        st.download_button("📄 Download PDF", pdf_output, file_name=f"Report_{scenario_name}.pdf", mime="application/pdf", use_container_width=True)

# --------------------------------------------------
# 2. COMPARISON FUNCTION
# --------------------------------------------------
def show_scenario_comparison():
    st.title("📊 Scenario Comparison")
    scenarios = st.session_state.get("saved_scenarios", {})

    if not scenarios:
        st.info("No saved scenarios yet.")
        return

    rows = []
    for name, data in scenarios.items():
        rows.append({
            "Scenario": name,
            "Price": data.get("price", 0),
            "Volume": data.get("volume", 0),
            "ROIC": data.get("metrics", {}).get("roic", 0),
            "Break Even": data.get("metrics", {}).get("bep_units", 0),
            "Net Cash": data.get("metrics", {}).get("net_cash_position", 0)
        })

    df = pd.DataFrame(rows)
    st.dataframe(df, use_container_width=True)
    
    st.divider()
    st.subheader("🗑 Delete Scenario")
    to_delete = st.selectbox("Select Scenario", list(scenarios.keys()))
    if st.button("Delete Scenario", use_container_width=True):
        del st.session_state.saved_scenarios[to_delete]
        st.rerun()

# --------------------------------------------------
# 3. MAIN RUN_HOME
# --------------------------------------------------
def run_home():
    s = st.session_state
    m = s.get("metrics", {})

    # State Sync
    p = s.get("price", 100.0)
    vc = s.get("variable_cost", 60.0)
    v = s.get("volume", 1000)
    fc = s.get("fixed_cost", 20000.0)
    cash = s.get("opening_cash", 10000.0)
    
    margin = p - vc
    bep = m.get("bep_units", 0)
    roic = m.get("roic", 0.0)
    net_cash = m.get("net_cash_position", cash)

    # Header
    st.markdown("<h1 style='text-align:center; color:#1E3A8A;'>Managers Lab.</h1>", unsafe_allow_html=True)
    
    # Snapshot
    st.subheader("📊 Simulation Snapshot")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Contribution", f"€{margin:,.2f}")
    c2.metric("Break-Even", f"{bep:,.0f} units")
    c3.metric("ROIC", f"{roic*100:.1f}%")
    c4.metric("Net Cash", f"€{net_cash:,.0f}")

    st.divider()

    col_left, col_right = st.columns([0.4, 0.6], gap="large")

    with col_left:
        st.subheader("⚙️ Business Baseline")
        st.number_input("Unit Price (€)", value=float(p), key="price")
        st.number_input("Variable Cost (€)", value=float(vc), key="variable_cost")
        st.number_input("Annual Volume", value=int(v), key="volume")
        st.number_input("Annual Fixed Costs (€)", value=float(fc), key="fixed_cost")
        st.number_input("Opening Cash (€)", value=float(cash), key="opening_cash")
        
        if st.button("🔒 Lock & Activate Simulation", type="primary", use_container_width=True):
            s.baseline_locked = True
            st.rerun()
            
        st.divider()
        st.subheader("💾 Save Scenario")
        scen_name = st.text_input("Name", value=s.get("scenario_name", "Baseline"))
        if st.button("Save Current State", use_container_width=True):
            if "saved_scenarios" not in s: s.saved_scenarios = {}
            s.saved_scenarios[scen_name] = {"price":p, "volume":v, "variable_cost":vc, "fixed_cost":fc, "metrics":m}
            st.success(f"Saved: {scen_name}")

    with col_right:
        st.subheader("🧠 Strategy Modules")
        if not s.get("baseline_locked"):
            st.info("Lock the baseline to see all tools.")
        else:
            t1, t2, t3, t4 = st.tabs(["Strategy", "Finance", "Operations", "Risk & Reports"])
            
            with t1:
                if st.button("🕹️ Mission Control", use_container_width=True): s.selected_tool="control_tower"; s.flow_step="tool"; st.rerun()
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
                if st.button("📊 NPV Receivables Analyzer", use_container_width=True): s.selected_tool="receivables_npv"; s.flow_step="tool"; st.rerun()
                if st.button("🔄 Cash Conversion Cycle", use_container_width=True): s.selected_tool="cash_cycle"; s.flow_step="tool"; st.rerun()
                if st.button("🔢 Unit Cost Analyzer", use_container_width=True): s.selected_tool="unit_cost_analyzer"; s.flow_step="tool"; st.rerun()
                if st.button("📦 Inventory Optimizer", use_container_width=True): s.selected_tool="inventory_manager"; s.flow_step="tool"; st.rerun()
                if st.button("🤝 Payables Manager", use_container_width=True): s.selected_tool="payables_manager"; s.flow_step="tool"; st.rerun()
                if st.button("💰 Working Capital Engine", use_container_width=True): s.selected_tool="wc_optimizer"; s.flow_step="tool"; st.rerun()

            with t4:
                if st.button("🛡️ Strategic Shock Simulator", use_container_width=True): s.selected_tool="shock_simulator"; s.flow_step="tool"; st.rerun()
                if st.button("🏁 Executive Dashboard", use_container_width=True): s.selected_tool="executive_dashboard"; s.flow_step="tool"; st.rerun()
                if st.button("🚨 Cash Fragility Index", use_container_width=True): s.selected_tool="cash_fragility"; s.flow_step="tool"; st.rerun()
                if st.button("🛡️ Resilience Map", use_container_width=True): s.selected_tool="resilience_map"; s.flow_step="tool"; st.rerun()
                if st.button("📉 Stress Test Simulator", use_container_width=True): s.selected_tool="stress_test"; s.flow_step="tool"; st.rerun()
                st.divider()
                if st.button("📄 Executive Decision Report", use_container_width=True, type="primary"): s.selected_tool="decision_report"; s.flow_step="tool"; st.rerun()
                if st.button("📊 Scenario Comparison", use_container_width=True): s.selected_tool="scenario_comparison"; s.flow_step="tool"; st.rerun()

# --------------------------------------------------
# SCENARIO VISUAL ANALYTICS
# --------------------------------------------------

def show_scenario_charts():

    st.subheader("📊 Scenario Visual Comparison")

    scenarios = st.session_state.get("saved_scenarios", {})

    if not scenarios:
        st.info("No scenarios saved yet.")
        return

    rows = []

    for name, data in scenarios.items():

        rows.append({
            "Scenario": name,
            "ROIC": data.get("metrics", {}).get("roic", 0),
            "BreakEven": data.get("metrics", {}).get("bep_units", 0),
            "NetCash": data.get("metrics", {}).get("net_cash_position", 0)
        })

    df = pd.DataFrame(rows)

    st.bar_chart(
        df.set_index("Scenario")[["ROIC"]]
    )

    st.bar_chart(
        df.set_index("Scenario")[["BreakEven"]]
    )

    st.bar_chart(
        df.set_index("Scenario")[["NetCash"]]
    )


# --------------------------------------------------
# STRATEGIC SUMMARY
# --------------------------------------------------

def show_strategy_summary():

    st.subheader("🧠 Strategic Insight")

    metrics = st.session_state.get("metrics", {})

    roic = metrics.get("roic", 0)
    bep = metrics.get("bep_units", 0)
    cash = metrics.get("net_cash_position", 0)

    if roic > 0.15:
        strategy = "High return strategy. Capital allocation is efficient."
    elif roic > 0.05:
        strategy = "Moderate performance. Strategy viable but improvements possible."
    else:
        strategy = "Low ROIC. Review pricing or cost structure."

    if cash < 0:
        liquidity = "Liquidity risk detected."
    else:
        liquidity = "Healthy liquidity buffer."

    st.success(strategy)
    st.warning(liquidity)

    st.write(f"""
**Strategic Interpretation**

• Return on invested capital: **{roic*100:.1f}%**

• Break-even level: **{bep:,.0f} units**

• Net cash position: **€{cash:,.0f}**

These metrics indicate the current strategic sustainability of the business model.
""")


# --------------------------------------------------
# EXECUTIVE DASHBOARD
# --------------------------------------------------

def show_executive_dashboard():

    st.title("🏁 Executive Dashboard")

    show_strategy_summary()

    st.divider()

    show_scenario_charts()
