import streamlit as st

def run_home():
    s = st.session_state
    
    # 1. Λήψη δεδομένων από τον Engine (που τρέχει στο app.py)
    m = s.get("metrics", {})
    
    # Defaults για την πρώτη φορά
    p = s.get("price", 100.0)
    vc = s.get("variable_cost", 60.0)
    v = s.get("volume", 1000)
    fc = s.get("fixed_cost", 20000.0)
    ads = s.get("annual_debt_service", 0.0)
    cash = s.get("opening_cash", 10000.0)
    tp = s.get("target_profit_goal", 0.0)

    # Δεδομένα από τον Engine
    net_cash = m.get("net_cash_position", cash)
    bep_units = m.get("bep_units", 0)
    margin = p - vc

    # Snapshot Logic
    if margin > 0 and bep_units:
        margin_of_safety = v - bep_units
        buffer_pct = (margin_of_safety / v * 100) if v > 0 else 0
        bep_display = f"{bep_units:,.0f} units"
        delta_val = f"{margin_of_safety:,.0f} surplus" if margin_of_safety >= 0 else f"{abs(margin_of_safety):,.0f} deficit"
        delta_col = "normal" if margin_of_safety >= 0 else "inverse"
    else:
        buffer_pct = -100.0
        bep_display = "N/A"
        delta_val = "⚠ Business model not viable"
        delta_col = "inverse"

    # --- HERO SECTION ---
    st.markdown(
        """
        <div style="text-align:center; padding: 10px 0 20px 0;">
            <h1 style="font-size:62px; font-weight:900; color:#1E3A8A; margin-bottom:0px;">Managers Lab<span style="color:#ef4444;">.</span></h1>
            <div style="font-size:18px; color:#64748b; letter-spacing:2px; text-transform:uppercase;">🛡️ Strategic Decision Room</div>
        </div>
        """,
        unsafe_allow_html=True
    )

    # --- EXECUTIVE SNAPSHOT ---
    st.subheader("📊 Executive Snapshot")
    c1, c2, c3, c4, c5 = st.columns(5)
    
    c1.metric("Simulated Volume", f"{v:,.0f} units")
    c2.metric("Unit Contribution", f"€{margin:,.2f}")
    c3.metric(label="Cash Break-Even", value=bep_display, delta=delta_val, delta_color=delta_col)
    c4.metric("Survival Buffer", f"{buffer_pct:.1f}%")
    c5.metric("Net Cash Position", f"€{net_cash:,.0f}", help="Cash after Working Capital requirements")

    st.divider()

    # --- MAIN LAYOUT ---
    col_input, col_nav = st.columns([0.40, 0.60], gap="large")

    with col_input:
        st.subheader("⚙️ Global Parameters")
        with st.expander("📊 Business Baseline", expanded=True):
            st.number_input("Unit Price (€)", value=float(p), key="price")
            st.number_input("Variable Cost (€)", value=float(vc), key="variable_cost")
            st.number_input("Annual Volume", value=int(v), key="volume")
            st.number_input("Annual Fixed Costs (€)", value=float(fc), key="fixed_cost")
            st.number_input("Target Profit Goal (€)", value=float(tp), key="target_profit_goal")

        with st.expander("🔄 Working Capital Cycle", expanded=False):
            st.number_input("AR Days", value=float(s.get('ar_days', 45.0)), key="ar_days")
            st.number_input("Inventory Days", value=float(s.get('inventory_days', 60.0)), key="inventory_days")
            st.number_input("AP Days", value=float(s.get('ap_days', 30.0)), key="ap_days")

        with st.expander("💰 Liquidity & Debt", expanded=False):
            st.number_input("Opening Cash (€)", value=float(cash), key="opening_cash")
            st.number_input("Annual Debt Service (€)", value=float(ads), key="annual_debt_service")

        st.divider()
        if st.button("🔒 Lock Baseline & Sync Engine", type="primary", use_container_width=True):
            st.session_state.baseline_locked = True
            st.rerun()

    with col_nav:
        st.subheader("📊 Strategic Tool Library")
        
        if not s.get("baseline_locked"):
            st.info("🔒 Lock your baseline parameters to enable the analysis tools.")
        else:
            t1, t2, t3, t4 = st.tabs(["🚀 Strategy", "💰 Finance", "⚙️ Ops", "🛡️ Risk"])

            with t1:
                if st.button("🎯 Pricing Strategy", use_container_width=True):
                    s.selected_tool = "pricing_strategy"; s.flow_step = "tool"; st.rerun()
                if st.button("⚖️ Cash Survival Simulator", use_container_width=True):
                    s.selected_tool = "break_even_shift"; s.flow_step = "tool"; st.rerun()
                if st.button("📡 Pricing Radar", use_container_width=True):
                    s.selected_tool = "pricing_radar"; s.flow_step = "tool"; st.rerun()
                if st.button("📉 Loss Threshold", use_container_width=True):
                    s.selected_tool = "loss_threshold"; s.flow_step = "tool"; st.rerun()

            with t2:
                if st.button("📈 Growth Funding (AFN)", use_container_width=True):
                    s.selected_tool = "growth_funding"; s.flow_step = "tool"; st.rerun()
                if st.button("📉 WACC Optimizer", use_container_width=True):
                    s.selected_tool = "wacc_optimizer"; s.flow_step = "tool"; st.rerun()

            with t3:
                if st.button("🔄 Cash Conversion Cycle", use_container_width=True):
                    s.selected_tool = "cash_cycle"; s.flow_step = "tool"; st.rerun()
                if st.button("📦 Inventory Optimizer", use_container_width=True):
                    s.selected_tool = "inventory_manager"; s.flow_step = "tool"; st.rerun()
                if st.button("🤝 Payables Manager", use_container_width=True):
                    s.selected_tool = "payables_manager"; s.flow_step = "tool"; st.rerun()

            with t4:
                if st.button("🚨 Cash Fragility Index", use_container_width=True):
                    s.selected_tool = "cash_fragility"; s.flow_step = "tool"; st.rerun()
                if st.button("🛡️ Resilience & Shock Map", use_container_width=True):
                    s.selected_tool = "resilience_map"; s.flow_step = "tool"; st.rerun()
                if st.button("📉 Stress Test Simulator", use_container_width=True):
                    s.selected_tool = "stress_test"; s.flow_step = "tool"; st.rerun()
