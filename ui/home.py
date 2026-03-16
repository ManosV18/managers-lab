import streamlit as st
import pandas as pd
from datetime import datetime
from fpdf import FPDF

# --- REPORTING FUNCTIONS (From 2nd version) ---
def show_decision_report():
    st.title("📄 Executive Decision Report")
    metrics = st.session_state.get("metrics", {})
    scenario_name = st.session_state.get("scenario_name", "Baseline Scenario")
    current_date = datetime.now().strftime("%d/%m/%Y %H:%M")
    report = {
        "ROIC": f"{metrics.get('roic',0)*100:.1f}%",
        "Break Even": f"{metrics.get('bep_units',0):,.0f} units",
        "Net Cash": f"€{metrics.get('net_cash_position',0):,.0f}",
        "Liquidity Buffer": f"{metrics.get('liquidity_buffer',0):,.1f}%"
    }
    st.markdown(f"**Managers Lab – Strategic Simulation Report**\n\nScenario: **{scenario_name}**\n\nDate: **{current_date}**")
    df = pd.DataFrame(report.items(), columns=["Metric","Value"])
    st.table(df)
    col1, col2 = st.columns(2)
    with col1:
        st.download_button("Download CSV", df.to_csv(index=False).encode("utf-8"), file_name="decision_report.csv", mime="text/csv", use_container_width=True)
    with col2:
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial","B",16)
        pdf.cell(200,10,"Managers Lab",ln=True)
        pdf_output = pdf.output(dest="S").encode("latin-1")
        st.download_button("📄 Download PDF", pdf_output, file_name=f"report_{scenario_name}.pdf", mime="application/pdf", use_container_width=True)

def show_scenario_comparison():
    st.title("📊 Scenario Comparison")
    scenarios = st.session_state.get("saved_scenarios",{})
    if not scenarios:
        st.info("No saved scenarios yet.")
        return
    rows = []
    for name,data in scenarios.items():
        rows.append({"Scenario":name, "ROIC":data.get("metrics",{}).get("roic",0), "Break Even":data.get("metrics",{}).get("bep_units",0)})
    st.dataframe(pd.DataFrame(rows), use_container_width=True)

def show_executive_dashboard():
    st.title("🏁 Executive Dashboard")
    metrics = st.session_state.get("metrics",{})
    st.metric("ROIC", f"{metrics.get('roic',0)*100:.1f}%")

# --- MAIN HOME ---
def run_home():
    s = st.session_state
    m = s.get("metrics", {})
    if "saved_scenarios" not in s:
        s.saved_scenarios = {}

    # --------------------------------------------------
    # HERO SECTION (From 1st version)
    # --------------------------------------------------
    st.markdown("""
        <div style='text-align:center; padding: 10px 0 30px 0;'>
        <h1 style='font-size:64px; font-weight:900; color:#1E3A8A;'>Managers Lab<span style='color:#ef4444;'>.</span></h1>
        <div style='font-size:26px; font-weight:700; margin-top:10px;'>Business Strategy Simulator</div>
        </div>
        """, unsafe_allow_html=True)

    # --------------------------------------------------
    # SNAPSHOT (From 1st version)
    # --------------------------------------------------
    st.subheader("📊 Executive Simulation Snapshot")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Unit Price", f"€{s.get('price', 100.0)}")
    c2.metric("Break-Even", f"{m.get('bep_units', 0):,.0f}")
    c3.metric("ROIC", f"{m.get('roic', 0)*100:.1f}%")
    c4.metric("Net Cash", f"€{m.get('net_cash_position', 0):,.0f}")
    st.divider()

    col_left, col_right = st.columns([0.4, 0.6], gap="large")

    with col_left:
        st.subheader("⚙️ Business Baseline")
        st.text_input("Scenario Name", value=s.get("scenario_name", "Baseline Scenario"), key="scenario_name")
        st.number_input("Unit Price (€)", value=float(s.get("price", 100.0)), key="price")
        st.number_input("Variable Cost (€)", value=float(s.get("variable_cost", 60.0)), key="variable_cost")
        st.number_input("Annual Volume", value=int(s.get("volume", 1000)), key="volume")
        st.number_input("Annual Fixed Costs (€)", value=float(s.get("fixed_cost", 20000.0)), key="fixed_cost")
        st.number_input("Opening Cash (€)", value=float(s.get("opening_cash", 10000.0)), key="opening_cash")
        
        with st.expander("Working Capital & Debt"):
            st.number_input("AR Days", value=float(s.get("ar_days", 45.0)), key="ar_days")
            st.number_input("Inventory Days", value=float(s.get("inv_days", 60.0)), key="inv_days")
            st.number_input("AP Days", value=float(s.get("ap_days", 30.0)), key="ap_days")

        if st.button("🔒 Lock & Activate Simulation", type="primary", use_container_width=True):
            s.baseline_locked = True
            st.rerun()
            
        if st.button("💾 Save Scenario", use_container_width=True):
            s.saved_scenarios[s.scenario_name] = {
                "price": s.get("price"),
                "volume": s.get("volume"),
                "metrics": s.get("metrics")
            }
            st.success(f"Scenario '{s.scenario_name}' saved!")

    with col_right:
        st.subheader("🧠 Strategy Modules")
        if not s.get("baseline_locked"):
            st.info("Please lock the baseline to activate strategy tools.")
        else:
            t1, t2, t3, t4 = st.tabs(["Strategy", "Finance", "Operations", "Risk & Reports"])
            
            with t1:
                if st.button("🕹️ Mission Control", use_container_width=True): s.selected_tool="control_tower"; s.flow_step="tool"; st.rerun()
                if st.button("🎯 Pricing Strategy", use_container_width=True): s.selected_tool="pricing_strategy"; s.flow_step="tool"; st.rerun()
                if st.button("⚖️ Cash Survival Simulator", use_container_width=True): s.selected_tool="break_even_shift"; s.flow_step="tool"; st.rerun()
                if st.button("📡 Pricing Radar", use_container_width=True): s.selected_tool="pricing_radar"; s.flow_step="tool"; st.rerun()

            with t2:
                if st.button("📈 Growth Funding (AFN)", use_container_width=True): s.selected_tool="growth_funding"; s.flow_step="tool"; st.rerun()
                if st.button("📉 WACC Optimizer", use_container_width=True): s.selected_tool="wacc_optimizer"; s.flow_step="tool"; st.rerun()

            with t3:
                if st.button("🔄 Cash Conversion Cycle", use_container_width=True): s.selected_tool="cash_cycle"; s.flow_step="tool"; st.rerun()
                if st.button("💰 Working Capital Engine", use_container_width=True): s.selected_tool="wc_optimizer"; s.flow_step="tool"; st.rerun()

            with t4:
                if st.button("🛡️ Strategic Shock Simulator", use_container_width=True): s.selected_tool="shock_simulator"; s.flow_step="tool"; st.rerun()
                st.divider()
                if st.button("🏁 Executive Dashboard", use_container_width=True): s.selected_tool="executive_dashboard"; s.flow_step="tool"; st.rerun()
                if st.button("📄 Executive Decision Report", use_container_width=True): s.selected_tool="decision_report"; s.flow_step="tool"; st.rerun()
                if st.button("📊 Scenario Comparison", use_container_width=True): s.selected_tool="scenario_comparison"; s.flow_step="tool"; st.rerun()
