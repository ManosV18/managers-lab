import streamlit as st
import pandas as pd
from datetime import datetime
from fpdf import FPDF
from io import BytesIO


# --------------------------------------------------
# EXECUTIVE DECISION REPORT
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
    <div style="background-color:#f1f5f9;padding:20px;border-radius:10px;border-left:5px solid #1E3A8A;">
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

    # CSV
    with col1:

        st.download_button(
            "Download CSV",
            df.to_csv(index=False),
            file_name="decision_report.csv",
            mime="text/csv",
            use_container_width=True
        )

    # PDF
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

        pdf_buffer = BytesIO()
        pdf.output(pdf_buffer)

        st.download_button(
            "📄 Download PDF",
            pdf_buffer.getvalue(),
            file_name=f"ManagersLab_{scenario_name}.pdf",
            mime="application/pdf",
            use_container_width=True
        )


# --------------------------------------------------
# SCENARIO COMPARISON
# --------------------------------------------------

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
            "Price": data.get("price", 0),
            "Volume": data.get("volume", 0),
            "ROIC": data.get("metrics", {}).get("roic", 0),
            "Break Even": data.get("metrics", {}).get("bep_units", 0),
            "Net Cash": data.get("metrics", {}).get("net_cash_position", 0)
        })

    df = pd.DataFrame(rows)

    st.dataframe(df, use_container_width=True)

    st.caption("Compare financial resilience across scenarios.")

    st.divider()

    # DELETE
    st.subheader("🗑 Delete Scenario")

    scenario_to_delete = st.selectbox(
        "Select Scenario to Delete",
        list(scenarios.keys())
    )

    if st.button("Delete Scenario", use_container_width=True):

        del st.session_state.saved_scenarios[scenario_to_delete]

        st.success(f"Scenario '{scenario_to_delete}' deleted.")

        st.rerun()


# --------------------------------------------------
# HOME PAGE
# --------------------------------------------------

def run_home():

    s = st.session_state
    m = s.get("metrics", {})

    p = s.get("price", 100.0)
    vc = s.get("variable_cost", 60.0)
    v = s.get("volume", 1000)
    fc = s.get("fixed_cost", 20000.0)

    margin = p - vc
    bep_units = m.get("bep_units", 0)

    # --------------------------------------------------
    # SCENARIO SAVE
    # --------------------------------------------------

    st.subheader("💾 Scenario Management")

    if "saved_scenarios" not in st.session_state:
        st.session_state.saved_scenarios = {}

    scenario_name = st.text_input(
        "Scenario Name",
        value=st.session_state.get("scenario_name", "Baseline")
    )

    if st.button("Save Scenario"):

        st.session_state.saved_scenarios[scenario_name] = {

            "price": st.session_state.get("price"),
            "volume": st.session_state.get("volume"),
            "variable_cost": st.session_state.get("variable_cost"),
            "fixed_cost": st.session_state.get("fixed_cost"),
            "metrics": st.session_state.get("metrics", {})
        }

        st.success(f"Scenario '{scenario_name}' saved.")

    st.divider()

    st.title("Managers Lab")
    st.caption("Business Strategy Simulator")

    if margin > 0 and bep_units:

        margin_of_safety = v - bep_units

        st.metric(
            "Cash Break-Even",
            f"{bep_units:,.0f} units",
            delta=f"{margin_of_safety:,.0f}"
        )

    else:

        st.metric("Cash Break-Even", "N/A")
