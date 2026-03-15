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
            "Price": data["price"],
            "Volume": data["volume"],
            "ROIC": data["metrics"].get("roic",0),
            "Break Even": data["metrics"].get("bep_units",0),
            "Net Cash": data["metrics"].get("net_cash_position",0)
        })
    df = pd.DataFrame(rows)
    st.dataframe(df, use_container_width=True)
    st.caption("Compare financial resilience across scenarios.")

def run_home():
    s = st.session_state
    m = s.get("metrics", {})

    # --------------------------------------------------
    # BASELINE STATE
    # --------------------------------------------------
    p = s.get("price", 100.0)
    vc = s.get("variable_cost", 60.0)
    v = s.get("volume", 1000)
    fc = s.get("fixed_cost", 20000.0)
    ads = s.get("annual_debt_service", 0.0)
    cash = s.get("opening_cash", 10000.0)
    tp = s.get("target_profit_goal", 0.0)

    net_cash = m.get("net_cash_position", cash)
    bep_units = m.get("bep_units", 0)
    margin = p - vc
    roic = m.get("roic", 0.0)

    # --------------------------------------------------
    # SNAPSHOT LOGIC
    # --------------------------------------------------
    if margin > 0 and bep_units:
        margin_of_safety = v - bep_units
        buffer_pct = (margin_of_safety / v * 100) if v > 0 else 0
        bep_display = f"{bep_units:,.0f} units"
        delta_val = f"{margin_of_safety:,.0f} surplus" if margin_of_safety >= 0 else f"{abs(margin_of_safety):,.0f} deficit"
        delta_col = "normal" if margin_of_safety >= 0 else "inverse"
    else:
        buffer_pct = -100.0
        bep_display = "N/A"
        delta_val = "⚠ Not viable"
        delta_col = "inverse"

    # --------------------------------------------------
    # HERO
    # --------------------------------------------------
    st.markdown("""
        <div style='text-align:center; padding: 10px 0 30px 0;'>
        <h1 style='font-size:64px; font-weight:900; color:#1E3A8A;'>Managers Lab<span style='color:#ef4444;'>.</span></h1>
        <div style='font-size:26px; font-weight:700; margin-top:10px;'>Business Strategy Simulator</div>
        </div>
        """, unsafe_allow_html=True)

    colA, colB = st.columns(2)
    with colA:
        st.markdown("### ⚙️ Financial Simulation Engine\nCalculates Break-Even, Liquidity, and ROIC.")
    with colB:
        st.markdown("### 🔁 Strategy Simulation Loop\nDefine baseline, run diagnostics, and simulate shocks.")

    st.divider()

    # --------------------------------------------------
    # SNAPSHOT
    # --------------------------------------------------
    st.subheader("📊 Executive Simulation Snapshot")
    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("Simulated Volume", f"{v:,.0f} units")
    c2.metric("Unit Contribution", f"€{margin:,.2f}")
    c3.metric("Cash Break-Even", bep_display, delta=delta_val, delta_color=delta_col)
    c4.metric("Survival Buffer", f"{buffer_pct:.1f}%")
    c5.metric("ROIC", f"{roic*100:.1f}%")

    st.divider()

    # --------------------------------------------------
    # LAYOUT
    # --------------------------------------------------
    col_input, col_nav = st.columns([0.40, 0.60], gap="large")

    with col_input:
        st.subheader("⚙️ Business Baseline")
        with st.expander("📊 Core Business Model", expanded=True):
            st.number_input("Unit Price (€)", value=float(p), key="price")
            st.number_input("Variable Cost (€)", value=float(vc), key="variable_cost")
            st.number_input("Annual Volume", value=int(v), key="volume")
            st.number_input("Annual Fixed Costs (€)", value=float(fc), key="fixed_cost")
            st.number_input("Target Profit Goal (€)", value=float(tp), key="target_profit_goal")
        
        with st.expander("💰 Liquidity & Debt"):
            st.number_input("Opening Cash (€)", value=float(cash), key="opening_cash")
            st.number_input("Annual Debt Service (€)", value=float(ads), key="annual_debt_service")

        if st.button("🔒 Lock Baseline & Activate Simulation", type="primary", use_container_width=True):
            st.session_state.baseline_locked = True
            st.rerun()

    with col_nav:
        st.subheader("🧠 Strategy Simulation Modules")
        if not s.get("baseline_locked"):
            st.info("🔒 Lock the baseline to activate the simulation modules.")
        else:
            t1, t2, t3, t4 = st.tabs(["Strategic Decisions", "Financial Structure", "Operations & Cash Flow", "Risk & Stress Tests"])
            
            with t1:
                if st.button("🕹️ Mission Control", use_container_width=True):
                    s.selected_tool = "control_tower"; s.flow_step = "tool"; st.rerun()
                if st.button("🎯 Pricing Strategy", use_container_width=True):
                    s.selected_tool = "pricing_strategy"; s.flow_step = "tool"; st.rerun()
                if st.button("⚖️ Cash Survival Simulator", use_container_width=True):
                    s.selected_tool = "break_even_shift"; s.flow_step = "tool"; st.rerun()
                if st.button("📡 Pricing Radar", use_container_width=True):
                    s.selected_tool = "pricing_radar"; s.flow_step = "tool"; st.rerun()

            with t2:
                if st.button("📈 Growth Funding (AFN)", use_container_width=True):
                    s.selected_tool = "growth_funding"; s.flow_step = "tool"; st.rerun()
                if st.button("📉 WACC Optimizer", use_container_width=True):
                    s.selected_tool = "wacc_optimizer"; s.flow_step = "tool"; st.rerun()

            with t3:
                if st.button("🔄 Cash Conversion Cycle", use_container_width=True):
                    s.selected_tool = "cash_cycle"; s.flow_step = "tool"; st.rerun()
                if st.button("💰 Working Capital Engine", use_container_width=True):
                    s.selected_tool = "wc_optimizer"; s.flow_step = "tool"; st.rerun()

            with t4:
                if st.button("🛡️ Strategic Shock Simulator", use_container_width=True):
                    s.selected_tool = "shock_simulator"; s.flow_step = "tool"; st.rerun()
                if st.button("🏁 Executive Dashboard", use_container_width=True):
                    s.selected_tool = "executive_dashboard"; s.flow_step = "tool"; st.rerun()
                st.divider()
                # ΕΔΩ ΚΑΛΟΥΝΤΑΙ ΤΑ ΝΕΑ ΕΡΓΑΛΕΙΑ
                if st.button("📄 Generate Decision Report", use_container_width=True):
                    s.selected_tool = "decision_report"; s.flow_step = "tool"; st.rerun()
                if st.button("📊 Compare Saved Scenarios", use_container_width=True):
                    s.selected_tool = "scenario_comparison"; s.flow_step = "tool"; st.rerun()
