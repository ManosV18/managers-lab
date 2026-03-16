import streamlit as st
import pandas as pd
from datetime import datetime
from fpdf import FPDF

# --------------------------------------------------
# EXECUTIVE DECISION REPORT
# --------------------------------------------------

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

    st.markdown(f"""
**Managers Lab – Strategic Simulation Report**

Scenario: **{scenario_name}**

Date: **{current_date}**
""")

    df = pd.DataFrame(report.items(), columns=["Metric","Value"])

    st.table(df)

    col1,col2 = st.columns(2)

    with col1:

        st.download_button(
            "Download CSV",
            df.to_csv(index=False).encode("utf-8"),
            file_name="decision_report.csv",
            mime="text/csv",
            use_container_width=True
        )

    with col2:

        pdf = FPDF()
        pdf.add_page()

        pdf.set_font("Arial","B",16)
        pdf.cell(200,10,"Managers Lab",ln=True)

        pdf.set_font("Arial","",12)
        pdf.cell(200,10,"Strategic Simulation Report",ln=True)

        pdf.ln(10)

        pdf.set_font("Arial","B",12)
        pdf.cell(100,10,"Metric",border=1)
        pdf.cell(80,10,"Value",border=1,ln=True)

        pdf.set_font("Arial","",12)

        for metric,value in report.items():

            pdf.cell(100,10,str(metric),border=1)
            pdf.cell(80,10,str(value),border=1,ln=True)

        pdf_output = pdf.output(dest="S").encode("latin-1")

        st.download_button(
            "📄 Download PDF",
            pdf_output,
            file_name=f"report_{scenario_name}.pdf",
            mime="application/pdf",
            use_container_width=True
        )


# --------------------------------------------------
# SCENARIO COMPARISON
# --------------------------------------------------

def show_scenario_comparison():

    st.title("📊 Scenario Comparison")

    scenarios = st.session_state.get("saved_scenarios",{})

    if not scenarios:

        st.info("No saved scenarios yet.")
        return

    rows = []

    for name,data in scenarios.items():

        rows.append({
            "Scenario":name,
            "Price":data.get("price",0),
            "Volume":data.get("volume",0),
            "ROIC":data.get("metrics",{}).get("roic",0),
            "Break Even":data.get("metrics",{}).get("bep_units",0),
            "Net Cash":data.get("metrics",{}).get("net_cash_position",0)
        })

    df = pd.DataFrame(rows)

    st.dataframe(df,use_container_width=True)

    st.divider()

    st.subheader("🗑 Delete Scenario")

    to_delete = st.selectbox("Select Scenario",list(scenarios.keys()))

    if st.button("Delete Scenario",use_container_width=True):

        del st.session_state.saved_scenarios[to_delete]

        st.success("Scenario deleted")

        st.rerun()

# --------------------------------------------------
# EXECUTIVE DASHBOARD
# --------------------------------------------------

def show_executive_dashboard():

    st.title("🏁 Executive Dashboard")

    metrics = st.session_state.get("metrics",{})

    roic = metrics.get("roic",0)
    bep = metrics.get("bep_units",0)
    cash = metrics.get("net_cash_position",0)

    st.subheader("🧠 Strategic Insight")

    if roic > 0.15:

        st.success("High return strategy. Capital allocation efficient.")

    elif roic > 0.05:

        st.warning("Moderate performance. Improvements possible.")

    else:

        st.error("Low ROIC. Review pricing or cost structure.")

    st.write(
        f"""
Return on invested capital: **{roic*100:.1f}%**

Break-even level: **{bep:,.0f} units**

Net cash position: **€{cash:,.0f}**
"""
    )

    scenarios = st.session_state.get("saved_scenarios",{})

    if scenarios:

        st.subheader("📊 Scenario Visual Comparison")

        rows=[]

        for name,data in scenarios.items():

            rows.append({
                "Scenario":name,
                "ROIC":data.get("metrics",{}).get("roic",0),
                "BreakEven":data.get("metrics",{}).get("bep_units",0),
                "NetCash":data.get("metrics",{}).get("net_cash_position",0)
            })

        df = pd.DataFrame(rows)

        st.bar_chart(df.set_index("Scenario")[["ROIC"]])
        st.bar_chart(df.set_index("Scenario")[["

        st.subheader("📊 Scenario Visual Comparison")

        rows = []

        for name, data in scenarios.items():

            rows.append({
                "Scenario": name,
                "ROIC": data.get("metrics", {}).get("roic", 0),
                "BreakEven": data.get("metrics", {}).get("bep_units", 0),
                "NetCash": data.get("metrics", {}).get("net_cash_position", 0)
            })

        df = pd.DataFrame(rows)

        st.bar_chart(df.set_index("Scenario")[["ROIC"]])
        st.bar_chart(df.set_index("Scenario")[["BreakEven"]])
        st.bar_chart(df.set_index("Scenario")[["NetCash"]])

    else:

        st.info("Save scenarios to see comparisons on the dashboard.")
