import streamlit as st
from core.sync import lock_baseline

def run_home():
    # Χρήση του st.session_state απευθείας για αποφυγή μπερδεμάτων
    if "input_price" not in st.session_state:
        st.session_state.input_price = 100.0
    if "input_vc" not in st.session_state:
        st.session_state.input_vc = 60.0
    if "input_volume" not in st.session_state:
        st.session_state.input_volume = 1000
    if "input_fc" not in st.session_state:
        st.session_state.input_fc = 20000.0
    if "input_ads" not in st.session_state:
        st.session_state.input_ads = 0.0
    if "input_cash" not in st.session_state:
        st.session_state.input_cash = 10000.0
    if "input_ar" not in st.session_state:
        st.session_state.input_ar = 45.0
    if "input_inv" not in st.session_state:
        st.session_state.input_inv = 60.0
    if "input_ap" not in st.session_state:
        st.session_state.input_ap = 30.0

    # Ανάγνωση τιμών για υπολογισμούς
    p = st.session_state.input_price
    vc = st.session_state.input_vc
    v = st.session_state.input_volume
    fc = st.session_state.input_fc
    ads = st.session_state.input_ads
    cash = st.session_state.input_cash
    
    # Financial Logic
    margin = p - vc
    contribution = margin * v
    bep_units = (fc + ads) / margin if margin > 0 else 0
    margin_of_safety = v - bep_units
    buffer_pct = (margin_of_safety / v * 100) if v > 0 else 0

    # --- HERO SECTION ---
    st.markdown(
        f"""
        <div style="text-align:center; padding: 10px 0;">
            <h1 style="font-size:62px; font-weight:900; color:#1E3A8A; margin-bottom:0px;">Managers Lab<span style="color:#ef4444;">.</span></h1>
            <div style="font-size:18px; color:#64748b; letter-spacing:2px; text-transform:uppercase;">🛡️ Strategic Decision Room</div>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.divider()

    # --- EXECUTIVE SNAPSHOT ---
    st.subheader("📊 Executive Snapshot")
    c1, c2, c3, c4, c5 = st.columns(5)
    
    c1.metric("Simulated Volume", f"{v:,.0f} units", 
              delta=f"+{margin_of_safety:,.0f} surplus" if margin_of_safety >= 0 else f"{margin_of_safety:,.0f} deficit")
    c2.metric("Contribution", f"€{contribution:,.0f}")
    c3.metric("Survival BEP", f"{bep_units:,.0f} units")
    c4.metric("Survival Buffer", f"{buffer_pct:.1f}%")
    c5.metric("Cash Position", f"€{cash:,.0f}")

    st.divider()

    # --- MAIN LAYOUT ---
    col_input, col_nav = st.columns([0.4, 0.6], gap="large")

    with col_input:
        st.subheader("⚙️ Global Parameters")
        
        with st.expander("📊 Business Baseline", expanded=True):
            st.number_input("Unit Price (€)", key="input_price")
            st.number_input("Variable Cost (€)", key="input_vc")
            st.number_input("Annual Volume", key="input_volume")
            st.number_input("Annual Fixed Costs (€)", key="input_fc")

        with st.expander("💰 Liquidity & Debt", expanded=False):
            st.number_input("Opening Cash (€)", key="input_cash")
            st.number_input("Annual Debt Service (€)", key="input_ads")

        if st.button("🔄 Reset All Data", use_container_width=True):
            st.session_state.clear()
            st.rerun()

    with col_nav:
        st.subheader("📊 Strategic Tool Library")
        # Εδώ είναι τα tabs με τα εργαλεία
        t1, t2, t3, t4 = st.tabs(["🚀 Strategy", "💰 Finance", "⚙️ Ops", "🛡️ Risk"])

        with t1:
            if st.button("🎯 Pricing Strategy", use_container_width=True):
                st.session_state.selected_tool = ("pricing_strategy", "show_pricing_strategy_tool")
                st.session_state.flow_step = "library"
                st.rerun()
            if st.button("⚖️ Survival BEP Simulator", use_container_width=True):
                st.session_state.selected_tool = ("break_even_shift_calculator", "show_break_even_shift_calculator")
                st.session_state.flow_step = "library"
                st.rerun()
            if st.button("📡 Pricing Radar", use_container_width=True):
                st.session_state.selected_tool = ("pricing_radar", "show_pricing_radar")
                st.session_state.flow_step = "library"
                st.rerun()

        with t2:
            if st.button("📈 Growth Funding (AFN)", use_container_width=True):
                st.session_state.selected_tool = ("growth_funding", "show_growth_funding_needed")
                st.session_state.flow_step = "library"
                st.rerun()
            if st.button("⚖️ Loan vs Leasing", use_container_width=True):
                st.session_state.selected_tool = ("loan_vs_leasing", "loan_vs_leasing_ui")
                st.session_state.flow_step = "library"
                st.rerun()

        with t3:
            if st.button("🔄 Cash Conversion Cycle", use_container_width=True):
                st.session_state.selected_tool = ("cash_cycle", "run_cash_cycle_app")
                st.session_state.flow_step = "library"
                st.rerun()
            if st.button("🔢 Unit Cost Analyzer", use_container_width=True):
                st.session_state.selected_tool = ("unit_cost_analyzer", "show_unit_cost_app")
                st.session_state.flow_step = "library"
                st.rerun()

        with t4:
            if st.button("🚨 Cash Fragility Index", use_container_width=True):
                st.session_state.selected_tool = ("cash_fragility_index", "show_cash_fragility_index")
                st.session_state.flow_step = "library"
                st.rerun()
            if st.button("📉 Stress Test Simulator", use_container_width=True):
                st.session_state.selected_tool = ("stress_test_simulator", "show_stress_test_tool")
                st.session_state.flow_step = "library"
                st.rerun()
