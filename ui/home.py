import streamlit as st
import pandas as pd
from datetime import datetime
from fpdf import FPDF
from io import BytesIO


# --------------------------------------------------
# DECISION REPORT
# --------------------------------------------------

def show_decision_report():

    st.title("📄 Executive Decision Report")

    metrics = st.session_state.get("metrics", {})
    scenario_name = st.session_state.get("scenario_name", "Baseline Scenario")
    current_date = datetime.now().strftime("%d/%m/%Y %H:%M")

    report = {
        "ROIC": f"{metrics.get('roic',0)*100:.1f}%",
        "Break Even": f"{metrics.get('bep_units',0):,.0f} units",
        "Net Cash": f"€{metrics.get('net_cash_position',0):,.2f}",
        "Liquidity Buffer": f"{metrics.get('liquidity_buffer',0):,.1f}%"
    }

    st.subheader("Managers Lab | Strategic Simulation Report")
    st.caption(f"Scenario: {scenario_name} | Date: {current_date}")

    df = pd.DataFrame(report.items(), columns=["Metric","Value"])
    st.table(df)

    col1,col2 = st.columns(2)

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

        pdf.set_font("Arial","B",16)
        pdf.cell(200,10,"Managers Lab",ln=True)

        pdf.set_font("Arial","B",12)
        pdf.cell(200,10,"Strategic Simulation Report",ln=True)

        pdf.set_font("Arial",size=10)
        pdf.cell(200,10,f"Scenario: {scenario_name}",ln=True)
        pdf.cell(200,10,f"Date: {current_date}",ln=True)

        pdf.ln(10)

        pdf.set_font("Arial","B",12)
        pdf.cell(100,10,"Metric",border=1)
        pdf.cell(80,10,"Value",border=1,ln=True)

        pdf.set_font("Arial",size=12)

        for metric,value in report.items():

            pdf.cell(100,10,str(metric),border=1)
            pdf.cell(80,10,str(value),border=1,ln=True)

        buffer = BytesIO()
        pdf.output(buffer)

        st.download_button(
            "📄 Download PDF",
            buffer.getvalue(),
            file_name=f"{scenario_name}_report.pdf",
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

    for name,data in scenarios.items():

        rows.append({
            "Scenario": name,
            "Price": data.get("price",0),
            "Volume": data.get("volume",0),
            "ROIC": data.get("metrics",{}).get("roic",0),
            "Break Even": data.get("metrics",{}).get("bep_units",0),
            "Net Cash": data.get("metrics",{}).get("net_cash_position",0)
        })

    df = pd.DataFrame(rows)

    st.dataframe(df,use_container_width=True)

    st.divider()

    st.subheader("🗑 Delete Scenario")

    scenario_to_delete = st.selectbox(
        "Select Scenario",
        list(scenarios.keys())
    )

    if st.button("Delete Scenario",use_container_width=True):

        del st.session_state.saved_scenarios[scenario_to_delete]

        st.success(f"Scenario '{scenario_to_delete}' deleted.")

        st.rerun()


# --------------------------------------------------
# HOME
# --------------------------------------------------

def run_home():

    s = st.session_state
    m = s.get("metrics",{})

    p = s.get("price",100.0)
    vc = s.get("variable_cost",60.0)
    v = s.get("volume",1000)
    fc = s.get("fixed_cost",20000.0)

    margin = p - vc

    # --------------------------------------------------
    # SAVE SCENARIO
    # --------------------------------------------------

    st.subheader("💾 Scenario Management")

    if "saved_scenarios" not in st.session_state:
        st.session_state.saved_scenarios = {}

    scenario_name = st.text_input(
        "Scenario Name",
        value=st.session_state.get("scenario_name","Baseline")
    )

    if st.button("Save Scenario"):

        st.session_state.saved_scenarios[scenario_name] = {

            "price": s.get("price"),
            "volume": s.get("volume"),
            "variable_cost": s.get("variable_cost"),
            "fixed_cost": s.get("fixed_cost"),

            "metrics": s.get("metrics",{})
        }

        st.success(f"Scenario '{scenario_name}' saved.")

    st.divider()

    # --------------------------------------------------
    # HERO
    # --------------------------------------------------

    st.markdown("""
    # Managers Lab

    Business Strategy Simulator

    Test pricing, financing and operational decisions before implementing them.
    """)

    st.divider()

    # --------------------------------------------------
    # BASELINE INPUT
    # --------------------------------------------------

    st.subheader("⚙️ Business Baseline")

    st.number_input("Unit Price (€)",value=float(p),key="price")
    st.number_input("Variable Cost (€)",value=float(vc),key="variable_cost")
    st.number_input("Annual Volume",value=int(v),key="volume")
    st.number_input("Annual Fixed Costs (€)",value=float(fc),key="fixed_cost")

    if st.button("🔒 Lock Baseline & Activate Simulation"):

        st.session_state.baseline_locked = True
        st.rerun()

    st.divider()

    # --------------------------------------------------
    # NAVIGATION
    # --------------------------------------------------

    st.subheader("🧠 Strategy Simulation Modules")

    if st.button("📄 Executive Decision Report",use_container_width=True):

        s.selected_tool = "decision_report"
        s.flow_step = "tool"
        st.rerun()

    if st.button("📊 Scenario Comparison",use_container_width=True):

        s.selected_tool = "scenario_comparison"
        s.flow_step = "tool"
        st.rerun()
