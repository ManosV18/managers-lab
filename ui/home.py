import streamlit as st
from core.sync import sync_global_state

def run_home():
    st.markdown("<h1 style='text-align: center;'>🛡️ Strategic Decision Room</h1>", unsafe_allow_html=True)
    st.divider()

    # --- MAIN LAYOUT ---
    col_input, col_nav = st.columns([0.5, 0.5], gap="large")

    # LEFT COLUMN: Global Parameters
    with col_input:
        st.subheader("⚙️ Global Parameters")
        with st.expander("Business Baseline", expanded=True):
            st.session_state.price = st.number_input("Unit Price (€)", value=float(st.session_state.get('price', 100.0)))
            st.session_state.variable_cost = st.number_input("Variable Cost (€)", value=float(st.session_state.get('variable_cost', 60.0)))
            st.session_state.volume = st.number_input("Annual Volume", value=int(st.session_state.get('volume', 1000)))
            st.session_state.fixed_cost = st.number_input("Fixed Costs (€)", value=float(st.session_state.get('fixed_cost', 20000.0)))
        
        if st.button("🔄 Reset All Data (Zero-Base)", use_container_width=True):
            st.session_state.clear()
            st.rerun()

    # RIGHT COLUMN: Analysis Hub with Tabs
    with col_nav:
        st.subheader("📊 Strategic Tool Library")
        
        # We use tabs as categories exactly like your library code
        t1, t2, t3, t4 = st.tabs(["🚀 Strategy", "💰 Finance", "⚙️ Ops", "🛡️ Risk"])

        with t1: # Strategy & Pricing
            if st.button("🎯 Pricing Strategy", use_container_width=True):
                st.session_state.selected_tool = ("pricing_strategy", "show_pricing_strategy_tool")
                st.session_state.flow_step = "library"
                st.rerun()
            st.caption("Which pricing strategy will maximize my profit?")

            if st.button("⚖️ BEP Shift Analysis", use_container_width=True):
                st.session_state.selected_tool = ("break_even_shift_calculator", "show_break_even_shift_calculator")
                st.session_state.flow_step = "library"
                st.rerun()
            st.caption("If I change the price or costs increase, how many units do I need to sell to cover my expenses?")

            if st.button("📡 Pricing Radar", use_container_width=True):
                st.session_state.selected_tool = ("pricing_radar", "show_pricing_radar")
                st.session_state.flow_step = "library"
                st.rerun()
            st.caption("How do price changes affect competition and sales?")

        with t2: # Capital & Finance
            if st.button("📈 Growth Funding (AFN)", use_container_width=True):
                st.session_state.selected_tool = ("growth_funding", "show_growth_funding_needed")
                st.session_state.flow_step = "library"
                st.rerun()
            st.caption("How can I fund growth and calculate my capital needs?")

            if st.button("📉 WACC Optimizer", use_container_width=True):
                st.session_state.selected_tool = ("wacc_optimizer", "show_wacc_optimizer")
                st.session_state.flow_step = "library"
                st.rerun()
            st.caption("How can I find the optimal cost of capital for my investments?")

        with t3: # Operations & CCC
            if st.button("🔄 Cash Conversion Cycle", use_container_width=True):
                st.session_state.selected_tool = ("cash_cycle", "run_cash_cycle_app")
                st.session_state.flow_step = "library"
                st.rerun()
            st.caption("How fast do my sales convert into cash?")

            if st.button("🔢 Unit Cost Analyzer", use_container_width=True):
                st.session_state.selected_tool = ("unit_cost_analyzer", "show_unit_cost_app")
                st.session_state.flow_step = "library"
                st.rerun()
            st.caption("What is the actual cost to produce each unit of product?")

        with t4: # Risk & Control
            if st.button("🚨 Cash Fragility Index", use_container_width=True):
                st.session_state.selected_tool = ("cash_fragility_index", "show_cash_fragility_index")
                st.session_state.flow_step = "library"
                st.rerun()
            st.caption("If revenue stopped today, how long could my business survive?")

            if st.button("📉 Stress Test Simulator", use_container_width=True):
                st.session_state.selected_tool = ("stress_test_simulator", "show_stress_test_tool")
                st.session_state.flow_step = "library"
                st.rerun()
            st.caption("How will my business withstand extreme financial conditions?")

    st.divider()
    # Bottom Navigation for Stages
    st.subheader("🏁 Core Project Stages")
    st.info("Follow the sequential path for a full business audit.")
    s_col1, s_col2, s_col3, s_col4, s_col5 = st.columns(5)
    if s_col1.button("Stage 1", use_container_width=True):
        st.session_state.flow_step = "stage1"; st.rerun()
    if s_col2.button("Stage 2", use_container_width=True):
        st.session_state.flow_step = "stage2"; st.rerun()
    # ... repeat for other stages
