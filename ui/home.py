import streamlit as st
from core.sync import lock_baseline

def run_home():
    s = st.session_state

    # --- 1. DATA SYNC & PRE-CALCULATIONS ---
    # Διαβάζουμε απευθείας από τα keys των widgets για Real-Time ανταπόκριση
    p = float(s.get("input_price", 100.0))
    vc = float(s.get("input_vc", 60.0))
    v = int(s.get("input_volume", 1000))
    fc = float(s.get("input_fc", 20000.0))
    
    # Debt & Cash
    ads = float(s.get("input_ads", 0.0))
    cash = float(s.get("input_cash", 10000.0))

    # Working Capital Components
    ar = float(s.get("input_ar", 45.0))
    inv = float(s.get("input_inv", 60.0))
    ap = float(s.get("input_ap", 30.0))

    # Financial Math
    margin = p - vc
    revenue = p * v
    contribution = margin * v
    
    # Survival Break-even (365-day context)
    bep_units = (fc + ads) / margin if margin > 0 else 0
    
    # Margin of Safety Logic
    margin_of_safety = v - bep_units
    buffer_pct = (margin_of_safety / v * 100) if v > 0 else 0
    ccc = ar + inv - ap

    # --- HERO SECTION ---
    st.markdown(
        f"""
        <div style="text-align:center; padding: 20px 0 30px 0;">
            <h1 style="font-size:72px; font-weight:900; color:#1E3A8A; margin-bottom:0px; letter-spacing:-1px; line-height:1;">Managers Lab<span style="color:#ef4444;">.</span></h1>
            <div style="font-size:22px; font-weight:400; color:#64748b; letter-spacing:3px; text-transform:uppercase; margin-top:10px; margin-bottom:30px;">🛡️ Strategic Decision Room</div>
            <div style="max-width:850px; margin: 0 auto; border-top: 2px solid #f1f5f9; padding-top: 25px;">
                <h2 style="font-size:28px; font-weight:600; color:#1e293b; line-height:1.2; margin-bottom:10px;">Test your business decisions before you risk real money.</h2>
                <p style="font-size:19px; color:#475569; line-height:1.5;">Simulate price, cost, and volume shifts to analyze profit and cash survival.</p>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.divider()

    # --- EXECUTIVE SNAPSHOT ---
    st.subheader("📊 Executive Snapshot")
    col1, col2, col3, col4, col5 = st.columns(5)
    
    # Simulated Volume με το σωστό Delta (+500 surplus)
    col1.metric(
        label="Simulated Volume", 
        value=f"{v:,.0f} units",
        delta=f"+{margin_of_safety:,.0f} surplus" if margin_of_safety >= 0 else f"{margin_of_safety:,.0f} deficit",
        delta_color="normal" if margin_of_safety >= 0 else "inverse"
    )
    
    col2.metric("Contribution", f"€{contribution:,.0f}")
    
    col3.metric(
        label="Survival BEP", 
        value=f"{bep_units:,.0f} units",
        help="Volume needed to cover Fixed Costs + Annual Debt Service."
    )
    
    col4.metric(
        label="Survival Buffer", 
        value=f"{buffer_pct:.1f}%",
        delta="Risk Headroom",
        delta_color="normal" if buffer_pct > 20 else "inverse"
    )
    
    col5.metric("Cash Position", f"€{cash:,.0f}")

    st.divider()

    # --- MAIN LAYOUT ---
    col_input, col_nav = st.columns([0.45, 0.55], gap="large")

    # LEFT COLUMN: Parameters
    with col_input:
        st.subheader("⚙️ Global Parameters")

        if s.get('baseline_locked', False):
            st.success("✅ Baseline is currently LOCKED")
        else:
            st.warning("🔓 Baseline is OPEN")

        # SECTION 1: Business Baseline
        with st.expander("📊 Business Baseline", expanded=True):
            s.price = st.number_input("Unit Price (€)", value=p, key="input_price")
            s.variable_cost = st.number_input("Variable Cost (€)", value=vc, key="input_vc")
            s.volume = st.number_input("Annual Volume", value=v, key="input_volume")
            s.fixed_cost = st.number_input("Annual Fixed Costs (€)", value=fc, key="input_fc")

        # SECTION 2: Working Capital (Efficiency)
        with st.expander("🔄 Working Capital Cycle", expanded=False):
            s.ar_days = st.number_input("AR Days (Collection)", value=ar, key="input_ar")
            s.inventory_days = st.number_input("Inventory Days", value=inv, key="input_inv")
            s.ap_days = st.number_input("AP Days (Payment)", value=ap, key="input_ap")

        # SECTION 3: Liquidity & Debt
        with st.expander("💰 Liquidity & Obligations", expanded=False):
            s.opening_cash = st.number_input("Opening Cash (€)", value=cash, key="input_cash")
            s.annual_debt_service = st.number_input("Annual Debt Service (€)", value=ads, key="input_ads")

        # Reset Button
        if st.button("🔄 Reset All Data", type="secondary", use_container_width=True):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.session_state.flow_step = "home"
            st.rerun()

    # RIGHT COLUMN: Tool Library
    with col_nav:
        st.subheader("📊 Strategic Tool Library")
        t1, t2, t3, t4 = st.tabs(["🚀 Strategy", "💰 Finance", "⚙️ Ops", "🛡️ Risk"])

        with t1:
            if st.button("🎯 Pricing Strategy", use_container_width=True):
                s.selected_tool = ("pricing_strategy", "show_pricing_strategy_tool"); s.flow_step = "library"; st.rerun()
            if st.button("⚖️ Survival BEP Simulator", use_container_width=True):
                s.selected_tool = ("break_even_shift_calculator", "show_break_even_shift_calculator"); s.flow_step = "library"; st.rerun()
            if st.button("📡 Pricing Radar", use_container_width=True):
                s.selected_tool = ("pricing_radar", "show_pricing_radar"); s.flow_step = "library"; st.rerun()
            if st.button("📉 Loss Threshold", use_container_width=True):
                s.selected_tool = ("loss_threshold", "show_loss_threshold_before_price_cut"); s.flow_step = "library"; st.rerun()

        with t2:
            if st.button("📈 Growth Funding (AFN)", use_container_width=True):
                s.selected_tool = ("growth_funding", "show_growth_funding_needed"); s.flow_step = "library"; st.rerun()
            if st.button("⚖️ Loan vs Leasing", use_container_width=True):
                s.selected_tool = ("loan_vs_leasing", "loan_vs_leasing_ui"); s.flow_step = "library"; st.rerun()

        with t3:
            if st.button("🔄 Cash Conversion Cycle", use_container_width=True):
                s.selected_tool = ("cash_cycle", "run_cash_cycle_app"); s.flow_step = "library"; st.rerun()
            if st.button("🔢 Unit Cost Analyzer", use_container_width=True):
                s.selected_tool = ("unit_cost_analyzer", "show_unit_cost_app"); s.flow_step = "library"; st.rerun()

        with t4:
            if st.button("🚨 Cash Fragility Index", use_container_width=True):
                s.selected_tool = ("cash_fragility_index", "show_cash_fragility_index"); s.flow_step = "library"; st.rerun()
            if st.button("📉 Stress Test Simulator", use_container_width=True):
                s.selected_tool = ("stress_test_simulator", "show_stress_test_tool"); s.flow_step = "library"; st.rerun()
