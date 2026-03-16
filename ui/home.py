import streamlit as st
import pandas as pd
from datetime import datetime
from fpdf import FPDF
from io import BytesIO

# --- REPORT FUNCTION ---
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

    # Header UI
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
        st.download_button(
            "Download CSV",
            df.to_csv(index=False),
            file_name="decision_report.csv",
            mime="text/csv",
            use_container_width=True
        )

    with col2:
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", "B", 16)
        pdf.cell(200, 10, "Managers Lab", ln=True)
        pdf.set_font("Arial", "B", 12)
        pdf.cell(200, 10, "Strategic Simulation Report", ln=True)
        pdf.set_font("Arial", size=10)
        pdf.cell(200, 10, f"Scenario: {scenario_name}", ln=True)
        pdf.cell(200, 10, f"Date: {current_date}", ln=True)
        pdf.ln(10)
        pdf.set_font("Arial", "B", 12)
        pdf.cell(100, 10, "Metric", border=1)
        pdf.cell(80, 10, "Value", border=1, ln=True)
        pdf.set_font("Arial", size=12)
        for metric, value in report.items():
            pdf.cell(100, 10, str(metric), border=1)
            pdf.cell(80, 10, str(value), border=1, ln=True)

        # Correct way for FPDF 1.7.2 to output to bytes
        pdf_output = pdf.output(dest='S').encode('latin-1')
        
        st.download_button(
            "📄 Download PDF",
            pdf_output,
            file_name=f"ManagersLab_{scenario_name}.pdf",
            mime="application/pdf",
            use_container_width=True
        )

# --- COMPARISON FUNCTION ---
def show_scenario_comparison():
    st.title("📊 Scenario Comparison")

    if "saved_scenarios" not in st.session_state:
        st.session_state.saved_scenarios = {}

    scenarios = st.session_state.saved_scenarios

    if not scenarios:
        st.info("No saved scenarios yet.")
        return

    rows = []
    for name, data in scenarios.items():
        rows.append({
            "Scenario": name,
            "Price": data.get("price",0),
            "Volume": data.get("volume",0),
            "ROIC": data.get("metrics",{}).get("roic",0),
            "Break Even": data.get("metrics",{}).get("bep_units",0),
            "Net Cash": data.get("metrics",{}).get("net_cash_position",0)
        })

    df = pd.DataFrame(rows)
    st.dataframe(df, use_container_width=True)

    st.divider()
    st.subheader("🗑 Delete Scenario")
    scenario_to_delete = st.selectbox("Select Scenario to Delete", list(scenarios.keys()))
    if st.button("Delete Scenario", use_container_width=True):
        del st.session_state.saved_scenarios[scenario_to_delete]
        st.success(f"Scenario '{scenario_to_delete}' deleted.")
        st.rerun()

# --- MAIN HOME FUNCTION ---
def run_home():
    s = st.session_state
    m = s.get("metrics", {})

    # BASELINE VALUES
    p = s.get("price", 100.0)
    vc = s.get("variable_cost", 60.0)
    v = s.get("volume", 1000)
    fc = s.get("fixed_cost", 20000.0)
    ads = s.get("annual_debt_service", 0.0)
    cash = s.get("opening_cash", 10000.0)
    tp = s.get("target_profit_goal", 0.0)
    
    margin = p - vc
    bep_units = m.get("bep_units", 0)
    roic = m.get("roic", 0.0)
    net_cash = m.get("net_cash_position", cash)

    # 1. SCENARIO MANAGEMENT (Save Button)
    st.subheader("💾 Scenario Management")
    if "saved_scenarios" not in st.session_state:
        st.session_state.saved_scenarios = {}

    col_name, col_btn = st.columns([0.7, 0.3])
    with col_name:
        scenario_name = st.text_input("Scenario Name", value=s.get("scenario_name", "Baseline"), label_visibility="collapsed")
    with col_btn:
        if st.button("Save Scenario", use_container_width=True, type="secondary"):
            st.session_state.saved_scenarios[scenario_name] = {
                "price": p,
                "volume": v,
                "variable_cost": vc,
                "fixed_cost": fc,
                "metrics": m
            }
            st.success(f"Saved: {scenario_name}")

    st.divider()

    # 2. HERO SECTION
    st.markdown("<h1 style='text-align:center; color:#1E3A8A;'>Managers Lab.</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align:center;'>Business Strategy Simulator</p>", unsafe_allow_html=True)

    # 3. METRICS SNAPSHOT
    st.subheader("📊 Executive Simulation Snapshot")
    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("Simulated Volume", f"{v:,.0f}")
    c2.metric("Unit Contribution", f"€{margin:,.2f}")
    c3.metric("Break-Even", f"{bep_units:,.0f} units")
    c4.metric("ROIC", f"{roic*100:.1f}%")
    c5.metric("Net Cash", f"€{net_cash:,.0f}")

    st.divider()

    # 4. INPUTS & NAVIGATION
    col_input, col_nav = st.columns([0.4, 0.6], gap="large")

    with col_input:
        st.subheader("⚙️ Business Baseline")
        st.number_input("Unit Price (€)", value=float(p), key="price")
        st.number_input("Variable Cost (€)", value=float(vc), key="variable_cost")
        st.number_input("Annual Volume", value=int(v), key="volume")
        st.number_input("Annual Fixed Costs (€)", value=float(fc), key="fixed_cost")
        
        if st.button("🔒 Lock & Activate", type="primary", use_container_width=True):
            st.session_state.baseline_locked = True
            st.rerun()

    with col_nav:
        st.subheader("🧠 Simulation Modules")
        if not s.get("baseline_locked"):
            st.info("🔒 Lock the baseline to activate modules.")
        else:
            t1, t2, t3, t4 = st.tabs(["Strategy", "Finance", "Ops", "Risk & Reports"])
            
            with t1: # Strategy (Ενδεικτικά μερικά κουμπιά)
                if st.button("🕹️ Mission Control", use_container_width=True):
                    s.selected_tool = "control_tower"
                    s.flow_step = "tool"
                    st.rerun()
            
            with t4: # Risk & Reports (Εδώ είναι τα κουμπιά που έψαχνες)
                st.write("### Analysis & Downloads")
                if st.button("📄 Executive Decision Report", use_container_width=True, type="primary"):
                    s.selected_tool = "decision_report"
                    s.flow_step = "tool"
                    st.rerun()
                
                if st.button("📊 Scenario Comparison", use_container_width=True):
                    s.selected_tool = "scenario_comparison"
                    s.flow_step = "tool"
                    st.rerun()
