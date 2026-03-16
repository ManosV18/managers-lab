import streamlit as st
import pandas as pd
from datetime import datetime
from fpdf import FPDF

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

        pdf_output = pdf.output(dest="S").encode("latin-1")

        st.download_button(
            "📄 Download PDF",
            pdf_output,
            file_name=f"Report_{scenario_name}.pdf",
            mime="application/pdf",
            use_container_width=True
        )


# --------------------------------------------------
# 2. SCENARIO COMPARISON
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

    to_delete = st.selectbox(
        "Select Scenario",
        list(scenarios.keys())
    )

    if st.button("Delete Scenario", use_container_width=True):

        del st.session_state.saved_scenarios[to_delete]

        st.success("Scenario deleted")

        st.rerun()


# --------------------------------------------------
# 3. EXECUTIVE DASHBOARD
# --------------------------------------------------

def show_executive_dashboard():

    st.title("🏁 Executive Dashboard")

    metrics = st.session_state.get("metrics", {})

    roic = metrics.get("roic", 0)
    bep = metrics.get("bep_units", 0)
    cash = metrics.get("net_cash_position", 0)

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

    scenarios = st.session_state.get("saved_scenarios", {})

    if scenarios:

        st.subheader("📊 Scenario Comparison")

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


# --------------------------------------------------
# 4. HOME SCREEN
# --------------------------------------------------

def run_home():

    s = st.session_state
    m = s.get("metrics", {})

    p = s.get("price", 100.0)
    vc = s.get("variable_cost", 60.0)
    v = s.get("volume", 1000)
    fc = s.get("fixed_cost", 20000.0)
    cash = s.get("opening_cash", 10000.0)

    margin = p - vc
    bep = m.get("bep_units", 0)
    roic = m.get("roic", 0)
    net_cash = m.get("net_cash_position", 0)

    st.markdown(
        "<h1 style='text-align:center;color:#1E3A8A;'>Managers Lab</h1>",
        unsafe_allow_html=True
    )

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

        scen_name = st.text_input(
            "Scenario Name",
            value=s.get("scenario_name", "Baseline"),
            key="scenario_name_input"
        )

        if st.button("Save Scenario", use_container_width=True):

            if "saved_scenarios" not in s:
                s.saved_scenarios = {}

            s.saved_scenarios[scen_name] = {
                "price": s.price,
                "volume": s.volume,
                "variable_cost": s.variable_cost,
                "fixed_cost": s.fixed_cost,
                "metrics": m
            }

            st.success(f"Scenario '{scen_name}' saved")

    with col_right:

        st.subheader("🧠 Strategy Modules")

        if not s.get("baseline_locked"):

            st.info("Lock the baseline to activate the tools.")

        else:

            t1, t2, t3, t4 = st.tabs(
                ["Strategy", "Finance", "Operations", "Risk & Reports"]
            )

            with t4:

                if st.button("🏁 Executive Dashboard", use_container_width=True):

                    s.selected_tool = "executive_dashboard"
                    s.flow_step = "tool"
                    st.rerun()

                if st.button("📄 Executive Decision Report", use_container_width=True):

                    s.selected_tool = "decision_report"
                    s.flow_step = "tool"
                    st.rerun()

                if st.button("📊 Scenario Comparison", use_container_width=True):

                    s.selected_tool = "scenario_comparison"
                    s.flow_step = "tool"
                    st.rerun()
