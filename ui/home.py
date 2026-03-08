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

    # RIGHT SIDE: Analysis Hub
    with col_nav:
        st.subheader("📊 Strategic Analysis Hub")
        st.write("What would you like to solve today?")

        # 1. CATEGORY SELECTION (The "Need")
        categories = {
            "Select a category...": None,
            "🎯 Strategy & Pricing": "strategy",
            "💰 Capital & Finance": "finance",
            "⚙️ Operations & Efficiency": "ops",
            "🛡️ Risk & Resilience": "risk"
        }
        
        selected_cat = st.selectbox("I want to analyze:", list(categories.keys()))
        cat_key = categories[selected_cat]

        st.divider()

        # 2. TOOL DISPLAY BASED ON CATEGORY
        if cat_key == "strategy":
            st.markdown("**Pricing & Growth Tools**")
            
            # Tool 1
            if st.button("🎯 Pricing Strategy", use_container_width=True):
                st.session_state.selected_tool = ("pricing_strategy", "show_pricing_strategy_tool")
                st.session_state.flow_step = "library"
                st.rerun()
            st.caption("Which pricing strategy will maximize my profit?")

            # Tool 2
            if st.button("⚖️ BEP Shift Analysis", use_container_width=True):
                st.session_state.selected_tool = ("break_even_shift_calculator", "show_break_even_shift_calculator")
                st.session_state.flow_step = "library"
                st.rerun()
            st.caption("If I change the price or costs increase, how many units do I need to sell?")

        elif cat_key == "finance":
            st.markdown("**Capital & Funding Tools**")
            
            if st.button("📈 Growth Funding (AFN)", use_container_width=True):
                st.session_state.selected_tool = ("growth_funding", "show_growth_funding_needed")
                st.session_state.flow_step = "library"
                st.rerun()
            st.caption("How can I fund growth and calculate my capital needs?")

        elif cat_key == "ops":
            st.markdown("**Efficiency & Cash Flow Tools**")
            
            if st.button("🔄 Cash Conversion Cycle", use_container_width=True):
                st.session_state.selected_tool = ("cash_cycle", "run_cash_cycle_app")
                st.session_state.flow_step = "library"
                st.rerun()
            st.caption("How fast do my sales convert into cash?")

        elif cat_key == "risk":
            st.markdown("**Survival & Stress Tools**")
            
            if st.button("🚨 Cash Fragility Index", use_container_width=True):
                st.session_state.selected_tool = ("cash_fragility_index", "show_cash_fragility_index")
                st.session_state.flow_step = "library"
                st.rerun()
            st.caption("If revenue stopped today, how long could my business survive?")
