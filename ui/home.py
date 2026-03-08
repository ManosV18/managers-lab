import streamlit as st
from core.sync import sync_global_state

def run_home():
    # --- HERO SECTION ---
    st.markdown("<h1 style='text-align: center;'>🛡️ Strategic Decision Room</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #666;'>Define your parameters and select your analysis path.</p>", unsafe_allow_html=True)
    st.divider()

    # --- MAIN LAYOUT: SPLIT VIEW ---
    col_input, col_nav = st.columns([0.6, 0.4], gap="large")

    # LEFT SIDE: Global Parameters (The "Sidebar" contents moved here)
    with col_input:
        st.subheader("⚙️ Global Parameters")
        
        with st.expander("1. Operations (Price, Cost, Volume)", expanded=True):
            st.session_state.price = st.number_input("Unit Price (€)", value=float(st.session_state.get('price', 100.0)))
            st.session_state.variable_cost = st.number_input("Variable Cost (€)", value=float(st.session_state.get('variable_cost', 60.0)))
            st.session_state.volume = st.number_input("Annual Volume", value=int(st.session_state.get('volume', 1000)))
            st.session_state.fixed_cost = st.number_input("Annual Fixed Costs (€)", value=float(st.session_state.get('fixed_cost', 20000.0)))

        with st.expander("2. Financials & Taxes"):
            st.session_state.opening_cash = st.number_input("Opening Cash (€)", value=float(st.session_state.get('opening_cash', 10000.0)))
            st.session_state.annual_debt_service = st.number_input("Annual Debt Service (€)", value=float(st.session_state.get('annual_debt_service', 0.0)))
            tax_p = st.number_input("Tax Rate (%)", value=float(st.session_state.get('tax_rate', 0.22)) * 100)
            st.session_state.tax_rate = tax_p / 100

        with st.expander("3. Working Capital (Days)"):
            st.session_state.ar_days = st.number_input("AR Days (Collection)", value=float(st.session_state.get('ar_days', 45.0)))
            st.session_state.inventory_days = st.number_input("Inventory Days", value=float(st.session_state.get('inventory_days', 60.0)))
            st.session_state.ap_days = st.number_input("AP Days (Payment)", value=float(st.session_state.get('ap_days', 30.0)))

        if st.button("🔄 Reset All Data", type="secondary", use_container_width=True):
            st.session_state.clear()
            st.rerun()

    # RIGHT SIDE: Navigation & Tools
    with col_nav:
        st.subheader("📊 Analysis Hub")
        
        # NAVIGATION DROPDOWN
        nav_options = {
            "Select Analysis...": "home",
            "📊 Stage 1: Survival & BEP": "stage1",
            "🏁 Stage 2: Dashboard": "stage2",
            "💧 Stage 3: Liquidity Physics": "stage3",
            "🌪️ Stage 4: Stress Testing": "stage4",
            "⚖️ Stage 5: Strategic Decision": "stage5",
            "📚 Full Tools Library": "library"
        }
        
        selected_label = st.selectbox("Navigate to:", list(nav_options.keys()))
        target_step = nav_options[selected_label]

        if target_step != "home":
            # GATEKEEPER LOGIC
            # If basic data is missing, prompt the user before allowing navigation
            if st.session_state.get('price', 0) <= 0 or st.session_state.get('volume', 0) <= 0:
                st.error("⚠️ Basic data missing. Please set Price and Volume to unlock this analysis.")
            else:
                st.session_state.flow_step = target_step
                st.rerun()

        st.divider()
        
        # SCENARIO MODE (ZERO-BASE)
        st.subheader("🆕 Scenario Mode")
        st.info("Start a fresh calculation from zero.")
        if st.button("Start New Scenario", type="primary", use_container_width=True):
            # Atomic Reset: Clear data but keep the current page
            current_page = st.session_state.flow_step
            st.session_state.clear()
            st.session_state.flow_step = current_page
            st.rerun()

        st.divider()
        st.caption("Common Shortcuts")
        if st.button("🎯 Break-Even Shift", use_container_width=True):
            st.session_state.selected_tool = ("break_even_shift_calculator", "show_break_even_shift_calculator")
            st.session_state.flow_step = "library"
            st.rerun()
