import streamlit as st
import pandas as pd
from datetime import datetime
from fpdf import FPDF

# --------------------------------------------------
# REPORTING & DASHBOARD FUNCTIONS
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
    
    st.markdown(f"**Managers Lab – Strategic Simulation Report**\n\nScenario: **{scenario_name}**\n\nDate: **{current_date}**")
    df = pd.DataFrame(report.items(), columns=["Metric", "Value"])
    st.table(df)
    
    col1, col2 = st.columns(2)
    with col1:
        st.download_button("Download CSV", df.to_csv(index=False).encode("utf-8"), file_name="decision_report.csv", mime="text/csv", use_container_width=True)
    with col2:
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", "B", 16)
        pdf.cell(200, 10, "Managers Lab - Executive Report", ln=True)
        pdf_output = pdf.output(dest="S").encode("latin-1")
        st.download_button("📄 Download PDF", pdf_output, file_name=f"report_{scenario_name}.pdf", mime="application/pdf", use_container_width=True)

def show_scenario_comparison():
    st.title("📊 Scenario Comparison")
    scenarios = st.session_state.get("saved_scenarios", {})
    if not scenarios:
        st.info("No saved scenarios yet.")
        return
    rows = []
    for name, data in scenarios.items():
        m = data.get("metrics", {})
        rows.append({
            "Scenario": name, 
            "Price": data.get("price"),
            "Volume": data.get("volume"),
            "ROIC %": f"{m.get('roic', 0)*100:.1f}%", 
            "Break Even": f"{m.get('bep_units', 0):,.0f}"
        })
    st.dataframe(pd.DataFrame(rows), use_container_width=True)

def show_executive_dashboard():
    st.title("🏁 Executive Dashboard")
    m = st.session_state.get("metrics", {})
    
    c1, c2 = st.columns(2)
    c1.metric("Return on Capital (ROIC)", f"{m.get('roic', 0)*100:.1f}%")
    c2.metric("Cash Position", f"€{m.get('net_cash_position', 0):,.0f}")
    
    st.divider()
    st.subheader("Profitability Analysis")
    # Εδώ θα μπορούσε να μπει ένα γράφημα στο μέλλον

# --------------------------------------------------
# MAIN HOME RUNNER
# --------------------------------------------------
def run_home():
    s = st.session_state
    m = s.get("metrics", {})
    
    if "saved_scenarios" not in s:
        s.saved_scenarios = {}

    # Hero Section
    st.markdown("""
        <div style='text-align:center; padding: 10px 0 30px 0;'>
            <h1 style='font-size:64px; font-weight:900; color:#1E3A8A;'>Managers Lab<span style='color:#ef4444;'>.</span></h1>
            <div style='font-size:24px; font-weight:700; color:#475569;'>The Business Strategy OS</div>
        </div>
        """, unsafe_allow_html=True)

    # Snapshot Metrics
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Current Price", f"€{s.get('price', 100.0)}")
    c2.metric("Break-Even Units", f"{m.get('bep_units', 0):,.0f}")
    c3.metric("ROIC", f"{m.get('roic', 0)*100:.1f}%")
    c4.metric("Net Cash", f"€{m.get('net_cash_position', 0):,.0f}")
    
    st.divider()

    col_left, col_right = st.columns([0.35, 0.65], gap="large")

    with col_left:
        st.subheader("⚙️ Business Baseline")
        st.text_input("Scenario Name", value=s.get("scenario_name", "Baseline Scenario"), key="scenario_name")
        
        with st.expander("📈 Core P&L Inputs", expanded=True):
            st.number_input("Unit Price (€)", value=float(s.get("price", 100.0)), key="price")
            st.number_input("Variable Cost (€)", value=float(s.get("variable_cost", 60.0)), key="variable_cost")
            st.number_input("Annual Volume", value=int(s.get("volume", 1000)), key="volume")
            st.number_input("Annual Fixed Costs (€)", value=float(s.get("fixed_cost", 20000.0)), key="fixed_cost")
            st.number_input("Target Profit (€)", value=float(s.get("target_profit_goal", 0.0)), key="target_profit_goal")

        with st.expander("🔄 Working Capital & Cash"):
            st.number_input("Opening Cash (€)", value=float(s.get("opening_cash", 10000.0)), key="opening_cash")
            st.number_input("A/R Days", value=float(s.get("ar_days", 45.0)), key="ar_days")
            st.number_input("Inventory Days", value=float(s.get("inv_days", 60.0)), key="inv_days")
            st.number_input("A/P Days", value=float(s.get("ap_days", 30.0)), key="ap_days")
            st.number_input("Annual Debt Service (€)", value=float(s.get("annual_debt_service", 0.0)), key="annual_debt_service")

        if st.button("🔒 Lock & Activate Simulation", type="primary", use_container_width=True):
            s.baseline_locked = True
            st.rerun()
            
        if st.button("💾 Save Current Scenario", use_container_width=True):
            s.saved_scenarios[s.scenario_name] = {
                "price": s.get("price"),
                "volume": s.get("volume"),
                "metrics": s.get("metrics")
            }
            st.success(f"Scenario '{s.scenario_name}' saved!")

    with col_right:
        st.subheader("🧠 Strategy Simulation Modules")
        
        if not s.get("baseline_locked"):
            st.info("👈 Please enter your data and lock the baseline to enable tools.")
        else:
            t1, t2, t3, t4 = st.tabs(["🎯 Strategy", "💰 Finance", "⚙️ Operations", "🛡️ Risk & Reports"])
            
            with t1: # STRATEGY & PRICING
                st.markdown("### Strategic Decisions")
                if st.button("🕹️ Mission Control / Tower", use_container_width=True): s.selected_tool="control_tower"; s.flow_step="tool"; st.rerun()
                if st.button("🎯 Pricing Strategy Lab", use_container_width=True): s.selected_tool="pricing_strategy"; s.flow_step="tool"; st.rerun()
                if st.button("📡 Pricing Radar (Competitive)", use_container_width=True): s.selected_tool="pricing_radar"; s.flow_step="tool"; st.rerun()
                if st.button("📉 Minimum Loss Threshold", use_container_width=True): s.selected_tool="loss_threshold"; s.flow_step="tool"; st.rerun()
                if st.button("🧭 QSPM Strategy Matrix", use_container_width=True): s.selected_tool="qspm_analyzer"; s.flow_step="tool"; st.rerun()
                if st.button("⚖️ Cash Survival Simulator", use_container_width=True): s.selected_tool="break_even_shift"; s.flow_step="tool"; st.rerun()
                if st.button("👥 Customer Lifetime Value (CLV)", use_container_width=True): s.selected_tool="clv_calculator"; s.flow_step="tool"; st.rerun()

            with t2: # FINANCE
                st.markdown("### Financial Engineering")
                if st.button("📈 Growth Funding Needed (AFN)", use_container_width=True): s.selected_tool="growth_funding"; s.flow_step="tool"; st.rerun()
                if st.button("📉 WACC Optimizer", use_container_width=True): s.selected_tool="wacc_optimizer"; s.flow_step="tool"; st.rerun()
                if st.button("⚖️ Loan vs Leasing Analyzer", use_container_width=True): s.selected_tool="loan_vs_leasing"; s.flow_step="tool"; st.rerun()

            with t3: # OPERATIONS
                st.markdown("### Operational Efficiency")
                if st.button("🔢 Unit Cost Analyzer", use_container_width=True): s.selected_tool="unit_cost_analyzer"; s.flow_step="tool"; st.rerun()
                if st.button("📦 Inventory Optimizer (EOQ)", use_container_width=True): s.selected_tool="inventory_manager"; s.flow_step="tool"; st.rerun()
                if st.button("📊 NPV Receivables Analyzer", use_container_width=True): s.selected_tool="receivables_npv"; s.flow_step="tool"; st.rerun()
                if st.button("🔄 Cash Conversion Cycle", use_container_width=True): s.selected_tool="cash_cycle"; s.flow_step="tool"; st.rerun()
                if st.button("🤝 Payables Manager", use_container_width=True): s.selected_tool="payables_manager"; s.flow_step="tool"; st.rerun()
                if st.button("💰 Working Capital Engine", use_container_width=True): s.selected_tool="wc_optimizer"; s.flow_step="tool"; st.rerun()

            with t4: # RISK & REPORTS
                st.markdown("### Resilience & Reporting")
                if st.button("🛡️ Strategic Shock Simulator", use_container_width=True): s.selected_tool="shock_simulator"; s.flow_step="tool"; st.rerun()
                if st.button("🚨 Cash Fragility Index", use_container_width=True): s.selected_tool="cash_fragility"; s.flow_step="tool"; st.rerun()
                if st.button("🗺️ Financial Resilience Map", use_container_width=True): s.selected_tool="resilience_map"; s.flow_step="tool"; st.rerun()
                if st.button("📉 Stress Test Simulator", use_container_width=True): s.selected_tool="stress_test"; s.flow_step="tool"; st.rerun()
                st.divider()
                if st.button("🏁 Executive Dashboard", use_container_width=True): s.selected_tool="executive_dashboard"; s.flow_step="tool"; st.rerun()
                if st.button("📄 Executive Decision Report (PDF/CSV)", use_container_width=True): s.selected_tool="decision_report"; s.flow_step="tool"; st.rerun()
                if st.button("📊 Compare Saved Scenarios", use_container_width=True): s.selected_tool="scenario_comparison"; s.flow_step="tool"; st.rerun()
