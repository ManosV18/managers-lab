import streamlit as st
from core.sync import lock_baseline

def run_home():
    s = st.session_state

    # --- 1. INITIALIZATION (Αρχικοποίηση αν είναι άδειο το Session State) ---
    if "input_price" not in s:
        s.input_price = 100.0
    if "input_vc" not in s:
        s.input_vc = 60.0
    if "input_volume" not in s:
        s.input_volume = 1000
    if "input_fc" not in s:
        s.input_fc = 20000.0
    if "input_ads" not in s:
        s.input_ads = 0.0
    if "input_cash" not in s:
        s.input_cash = 10000.0
    if "input_ar" not in s:
        s.input_ar = 45.0
    if "input_inv" not in s:
        s.input_inv = 60.0
    if "input_ap" not in s:
        s.input_ap = 30.0

    # --- 2. DATA EXTRACTION & CALCULATIONS ---
    p = s.input_price
    vc = s.input_vc
    v = s.input_volume
    fc = s.input_fc
    ads = s.input_ads
    cash = s.input_cash
    
    # Financial Logic
    margin = p - vc
    revenue = p * v
    contribution = margin * v
    
    # Survival BEP (Σημείο Μηδέν που περιλαμβάνει και το χρέος)
    # Υπολογισμός με βάση το έτος 365 ημερών σύμφωνα με τις οδηγίες σου
    bep_units = (fc + ads) / margin if margin > 0 else 0
    
    # Margin of Safety (Το πλεόνασμα των μονάδων)
    margin_of_safety = v - bep_units
    buffer_pct = (margin_of_safety / v * 100) if v > 0 else 0
    
    # Cash Cycle
    ccc = s.input_ar + s.input_inv - s.input_ap

    # --- 3. HERO SECTION (UI) ---
    st.markdown(
        f"""
        <div style="text-align:center; padding: 20px 0 30px 0;">
            <h1 style="font-size:72px; font-weight:900; color:#1E3A8A; margin-bottom:0px; letter-spacing:-1px; line-height:1;">Managers Lab<span style="color:#ef4444;">.</span></h1>
            <div style="font-size:22px; font-weight:400; color:#64748b; letter-spacing:3px; text-transform:uppercase; margin-top:10px; margin-bottom:30px;">🛡️ Strategic Decision Room</div>
            <div style="max-width:850px; margin: 0 auto; border-top: 2px solid #f1f5f9; padding-top: 25px;">
                <h2 style="font-size:28px; font-weight:600; color:#1e293b; line-height:1.2; margin-bottom:10px;">Test your business decisions before you risk real money.</h2>
                <p style="font-size:19px; color:#475569; line-height:1.5;">Change prices, costs, or volumes and instantly see the effect on profit, break-even, and cash survival.</p>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.divider()

    # --- 4. EXECUTIVE SNAPSHOT ---
    st.subheader("📊 Executive Snapshot")
    col1, col2, col3, col4, col5 = st.columns(5)
    
    # Simulated Volume με το Surplus (+500 units)
    col1.metric(
        label="Simulated Volume", 
        value=f"{v:,.0f} units",
        delta=f"+{margin_of_safety:,.0f} units surplus" if margin_of_safety >= 0 else f"{margin_of_safety:,.0f} units deficit",
        delta_color="normal" if margin_of_safety >= 0 else "inverse"
    )
    
    col2.metric("Contribution", f"€{contribution:,.0f}")
    
    col3.metric(
        label="Survival BEP", 
        value=f"{bep_units:,.0f} units",
        help="Volume needed to cover Fixed Costs + Debt Service."
    )
    
    col4.metric(
        label="Survival Buffer", 
        value=f"{buffer_pct:.1f}%",
        delta="Risk Headroom",
        delta_color="normal" if buffer_pct > 20 else "inverse"
    )
    
    col5.metric("Cash Position", f"€{cash:,.0f}")

    

    st.divider()

    # --- 5. MAIN LAYOUT: PARAMETERS & TOOLS ---
    col_input, col_nav = st.columns([0.45, 0.55], gap="large")

    with col_input:
        st.subheader("⚙️ Global Parameters")

        if s.get('baseline_locked', False):
            st.success("✅ Baseline is currently LOCKED")
        else:
            st.warning("🔓 Baseline is OPEN")

        with st.expander("📊 Business Baseline", expanded=True):
            st.number_input("Unit Price (€)", key="input_price")
            st.number_input("Variable Cost (€)", key="input_vc")
            st.number_input("Annual Volume", key="input_volume")
            st.number_input("Annual Fixed Costs (€)", key="input_fc")

        with st.expander("🔄 Working Capital Cycle", expanded=False):
            st.number_input("AR Days (Collection)", key="input_ar")
            st.number_input("Inventory Days", key="input_inv")
            st.number_input("AP Days (Payment)", key="input_ap")

        with st.expander("💰 Liquidity & Obligations", expanded=False):
            st.number_input("Opening Cash (€)", key="input_cash")
            st.number_input("Annual Debt Service (€)", key="input_ads")

        col_btn1, col_btn2 = st.columns(2)
        with col_btn1:
            if st.button("🔒 Lock Baseline", use_container_width=True, type="primary"):
                lock_baseline()
                st.rerun()
        with col_btn2:
            if st.button("🔄 Reset All Data", type="secondary", use_container_width=True):
                st.session_state.clear()
                st.rerun()

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
