import streamlit as st
import pandas as pd
from datetime import datetime
from fpdf import FPDF
from io import BytesIO


def show_decision_report():

    st.title("📄 Executive Decision Report")

    metrics = st.session_state.get("metrics", {})
    scenario_name = st.session_state.get("scenario_name", "Baseline Scenario")
    current_date = datetime.now().strftime("%d/%m/%Y %H:%M")

    report = {
        "ROIC": f"{metrics.get('roic', 0)*100:.1f}%",
        "Break Even": f"{metrics.get('bep_units', 0):,.0f} units",
        "Net Cash": f"EUR{metrics.get('net_cash_position', 0):,.2f}",
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

    # CSV
    with col1:

        st.download_button(
            "Download CSV",
            df.to_csv(index=False),
            file_name="decision_report.csv",
            mime="text/csv",
            use_container_width=True
        )
