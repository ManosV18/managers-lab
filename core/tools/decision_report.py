import streamlit as st
import pandas as pd
from fpdf import FPDF
from datetime import datetime

def show_decision_report():
    st.title("📄 Executive Decision Report")

    metrics = st.session_state.get("metrics", {})
    scenario_name = st.session_state.get("scenario_name", "Baseline Scenario")
    current_date = datetime.now().strftime("%d/%m/%Y %H:%M")

    # Metrics Mapping
    report = {
        "ROIC": f"{metrics.get('roic', 0)*100:.1f}%",
        "Break Even": f"{metrics.get('bep_units', 0):,.0f} units",
        "Net Cash": f"€{metrics.get('net_cash_position', 0):,.2f}",
        "Liquidity Buffer": f"{metrics.get('liquidity_buffer', 0):,.1f}%"
    }

    # Enterprise Header display in UI
    st.markdown(f"""
    <div style="background-color:#f1f5f9; padding:20px; border-radius:10px; border-left: 5px solid #1E3A8A; margin-bottom:20px;">
        <h3 style="margin:0; color:#1E3A8A;">Managers Lab</h3>
        <p style="margin:0; font-weight:bold;">Strategic Simulation Report</p>
        <hr style="margin:10px 0;">
        <span style="font-size:14px;"><b>Scenario:</b> {scenario_name}</span><br>
        <span style="font-size:14px;"><b>Date:</b> {current_date}</span>
    </div>
    """, unsafe_allow_html=True)

    # Data Table
    df = pd.DataFrame(report.items(), columns=["Metric", "Value"])
    st.table(df)

    # Export Buttons
    col1, col2 = st.columns(2)

    with col1:
        st.download_button(
            "Download Report (CSV)",
            df.to_csv(index=False),
            "decision_report.csv",
            "text/csv",
            use_container_width=True
        )

    with col2:
        if st.button("Generate PDF Report", use_container_width=True):
            pdf = FPDF()
            pdf.add_page()
            
            # Enterprise Header in PDF
            pdf.set_font("Arial", 'B', 16)
            pdf.cell(200, 10, txt="Managers Lab", ln=True)
            pdf.set_font("Arial", 'B', 12)
            pdf.cell(200, 10, txt="Strategic Simulation Report", ln=True)
            pdf.set_font("Arial", size=10)
            pdf.cell(200, 10, txt=f"Scenario: {scenario_name}", ln=True)
            pdf.cell(200, 10, txt=f"Date: {current_date}", ln=True)
            pdf.ln(10) # Line break
            
            # Content
            pdf.set_font("Arial", 'B', 12)
            pdf.cell(100, 10, txt="Metric", border=1)
            pdf.cell(80, 10, txt="Value", border=1, ln=True)
            
            pdf.set_font("Arial", size=12)
            for metric, value in report.items():
                pdf.cell(100, 10, txt=str(metric), border=1)
                pdf.cell(80, 10, txt=str(value), border=1, ln=True)

            pdf_file = "decision_report.pdf"
            pdf.output(pdf_file)

            with open(pdf_file, "rb") as f:
                st.download_button(
                    "📥 Click to Download PDF",
                    f,
                    file_name=f"Report_{scenario_name}.pdf",
                    mime="application/pdf",
                    use_container_width=True
                )

# Διόρθωση ομοιομορφίας (Syncing saved_scenarios)
if "saved_scenarios" not in st.session_state:
    st.session_state.saved_scenarios = {}
