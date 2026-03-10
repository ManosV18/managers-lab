import streamlit as st
from core.sync import lock_baseline

def run_home():
    s = st.session_state

    # --- HERO SECTION ---
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

    # --- EXECUTIVE SNAPSHOT ---
    # Fetch variables - Χρησιμοποιούμε τα inputs αν υπάρχουν, αλλιώς defaults
    p = s.get("input_price", 100.0)
    vc = s.get("input_vc", 60.0)
    v = s.get("input_volume", 1000)
    fc = s.get("input_fc", 20000.0)
    ads = s.get("opening_cash_ads", 0.0) # Συνεπές όνομα με τα inputs
    cash = s.get("opening_cash_val", 10000.0)

    # Core Calculations
    margin = p - vc
    revenue = p * v
    contribution = margin * v
    
    # Survival Break-even (including Debt Service) - 365 Days
    bep_units = (fc + ads) / margin if margin > 0 else 0
    margin_of_safety = v - bep_units
    buffer_pct = (margin_of_safety / v * 100) if v > 0 else 0

    # Layout Metrics
    col1, col2, col3, col4, col5 = st.columns(5)
    
    col1.metric("Simulated Volume", f"{v:,.0f} units")
    col2.metric("Contribution", f"€{contribution:,.0f}")
    col3.metric(
        label="Survival BEP", 
        value=f"{bep_units:,.0f} units", 
        delta=f"{margin_of_safety:,.0f} surplus" if margin_of_safety >= 0 else f"{abs(margin_of_safety):,.0f} deficit",
        delta_color="normal" if margin_of_safety >= 0 else "inverse"
    )
    col4.metric("Survival Buffer", f"{buffer_pct:.1f}%", delta="Risk Headroom")
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

        with st.expander("📊 Business Baseline", expanded=True):
            s.price = st.number_input("Unit Price (€)", value=float(p), key="input_price")
            s.variable_cost = st.number_input("Variable Cost (€)", value=float(vc), key="input_vc")
            s.volume = st.number_input("Annual Volume", value=int(v), key="input_volume")
            s.fixed_cost = st.number_input("Annual Fixed Costs (€)", value=float(fc), key="input_fc")

        with st.expander("🔄 Working Capital Cycle", expanded=False):
            # Χρήση κλειδιών για να τα διαβάζει το NPV Tool
            s.ar_days = st.number_input("AR Days (Collection)", value=float(s.get('ar_days', 45.0)), key="input_ar")
            s.inventory_days = st.number_input("Inventory Days", value=float(s.get('inventory_days', 60.0)), key="input_inv")
            s.ap_days = st.number_input("AP Days (Payment)", value=float(s.get('ap_days', 30.0)), key="input_ap")

        with st.expander("💰 Liquidity & Obligations", expanded=False):
            s.opening_cash = st.number_input("Opening Cash (€)", value=float(cash), key="opening_cash_val")
            s.annual_debt_service = st.number_input("Annual Debt Service (€)", value=float(ads), key="opening_cash_ads")

        if st.button("🔄 Reset All Data", type="secondary", use_container_width=True):
            st.session_state.clear()
            st.rerun()

    # RIGHT COLUMN: Tool Tabs
    with col_nav:
        st.subheader("📊 Strategic Tool Library")
        t1, t2, t3, t4 = st.tabs(["🚀 Strategy", "💰 Finance", "⚙️ Ops", "🛡️ Risk"])

        with t1:
            if st.button("🎯 Pricing Strategy", use_container_width=True):
                s.selected_tool = ("pricing_strategy", "show_pricing_strategy_tool"); s.flow_step = "library"; st.rerun()
            if st.button("⚖️ Survival BEP Simulator", use_container_width=True):
                s.selected_tool = ("break_even_shift_calculator", "show_break_even_shift_calculator"); s.flow_step = "library"; st.rerun()

        with t2:
            if st.button("📈 Growth Funding (AFN)", use_container_width=True):
                s.selected_tool = ("growth_funding", "show_growth_funding_needed"); s.flow_step = "library"; st.rerun()

        with t3:
            # ΕΔΩ ΕΙΝΑΙ Η ΑΛΛΑΓΗ: Συνδέουμε το NPV Tool που μου έστειλες
            if st.button("🔄 NPV Receivables Analyzer", use_container_width=True):
                s.selected_tool = ("receivables_npv", "show_receivables_analyzer_ui"); s.flow_step = "library"; st.rerun()
            
            if st.button("🔢 Unit Cost Analyzer", use_container_width=True):
                s.selected_tool = ("unit_cost_analyzer", "show_unit_cost_app"); s.flow_step = "library"; st.rerun()

        with t4:
            if st.button("🚨 Cash Fragility Index", use_container_width=True):
                s.selected_tool = ("cash_fragility_index", "show_cash_fragility_index"); s.flow_step = "library"; st.rerun()
            if st.button("📉 Stress Test Simulator", use_container_width=True):
                s.selected_tool = ("stress_test_simulator", "show_stress_test_tool"); s.flow_step = "library"; st.rerun()
