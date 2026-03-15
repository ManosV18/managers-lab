import streamlit as st
import pandas as pd

def show_decision_report():

    st.title("📄 Executive Decision Report")

    metrics = st.session_state.get("metrics",{})

    report = {
        "ROIC": metrics.get("roic",0),
        "Break Even": metrics.get("bep_units",0),
        "Net Cash": metrics.get("net_cash_position",0),
        "Liquidity Buffer": metrics.get("liquidity_buffer",0)
    }

    df = pd.DataFrame(report.items(), columns=["Metric","Value"])

    st.table(df)

    st.download_button(
        "Download Report (CSV)",
        df.to_csv(index=False),
        "decision_report.csv",
        "text/csv"
    )
