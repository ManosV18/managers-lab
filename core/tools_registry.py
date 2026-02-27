import streamlit as st
import importlib
import os
import sys
import importlib.util

# --- INTERNAL TOOLS (Standalone) ---

def show_pricing_standalone():
    st.header("🎯 Pricing Strategy & Elasticity")
    st.info("Direct simulation: Explore price changes without affecting global state.")
    col1, col2 = st.columns(2)
    with col1:
        p_current = st.number_input("Current Price (€)", value=100.0)
        p_new = st.number_input("Proposed Price (€)", value=110.0)
    with col2:
        v_current = st.number_input("Current Volume (Units)", value=1000)
        elasticity = st.slider("Price Elasticity of Demand", 0.0, 5.0, 1.5)
    
    price_change_pct = (p_new - p_current) / p_current
    volume_change_pct = -elasticity * price_change_pct
    new_volume = v_current * (1 + volume_change_pct)
    
    st.divider()
    c1, c2 = st.columns(2)
    c1.metric("Volume Impact", f"{volume_change_pct:+.1%}", delta=f"{new_volume - v_current:,.0f} units")
    c2.metric("New Revenue", f"€{new_volume * p_new:,.0f}", delta=f"{(new_volume * p_new) - (v_current * p_current):,.0f}")
    
    if st.button("⬅️ Back to Library"):
        st.session_state.selected_tool = None
        st.rerun()

def show_loss_standalone():
    st.header("📉 Price Cut: Sales Increase Required")
    st.info("Calculate required volume to maintain profit after a price reduction.")
    margin = st.slider("Current Gross Margin (%)", 5, 80, 30) / 100
    price_cut = st.slider("Price Reduction (%)", 1, 25, 10) / 100
    
    if margin > price_cut:
        req_increase = price_cut / (margin - price_cut)
        st.warning(f"To maintain profit, you need a **{req_increase:.1%}** increase in unit sales.")
    else:
        st.error("The price cut exceeds your margin. Profit is impossible.")
        
    if st.button("⬅️ Back to Library"):
        st.session_state.selected_tool = None
        st.rerun()

def show_payables_manager_internal():
    st.header("🤝 Payables Manager")
    annual_purch = st.number_input("Annual Purchase Volume (€)", value=1000000)
    # Calculation based on instruction [2026-02-18] (365 days)
    st.write(f"Standard calculation based on 365-day year logic.")
    
    if st.button("⬅️ Back to Library"):
        st.session_state.selected_tool = None
        st.rerun()

# --- MAIN LIBRARY HUB ---

def show_library():
    if st.sidebar.button("🏠 Exit Library", key="exit_lib"):
        st.session_state.flow_step = "home"
        st.session_state.selected_tool = None
        st.rerun()

    st.title("🏛️ Strategic Tool Library")

    if st.session_state.get('selected_tool') is None:
        t1, t2, t3, t4 = st.tabs(["🚀 Strategy", "💰 Finance", "⚙️ Operations", "🛡️ Risk"])
        
        with t1:
            if st.button("🎯 Pricing Strategy & Elasticity", use_container_width=True):
                st.session_state.selected_tool = ("INTERNAL", "show_pricing_standalone")
                st.rerun()
            if st.button("📉 Loss Threshold (Price Cut)", use_container_width=True):
                st.session_state.selected_tool = ("INTERNAL", "show_loss_standalone")
                st.rerun()
            if st.button("⚖️ BEP Shift Analysis", use_container_width=True):
                st.session_state.selected_tool = ("break_even_shift_calculator", "show_break_even_shift_calculator")
                st.rerun()

        with t2:
            # Εδώ είναι η θέση του Leasing, το αφήνω ως απλό κουμπί αν θες να το συνδέσεις αργότερα
            st.info("Finance tools and Capital structure analysis.")
            if st.button("📉 WACC Optimizer", use_container_width=True):
                st.session_state.selected_tool = ("wacc_optimizer", "show_wacc_optimizer")
                st.rerun()

        with t3:
            if st.button("🤝 Payables Manager", use_container_width=True):
                st.session_state.selected_tool = ("INTERNAL", "show_payables_manager_internal")
                st.rerun()
            if st.button("📊 Receivables Analyzer", use_container_width=True):
                st.session_state.selected_tool = ("receivables_analyzer", "show_receivables_analyzer_ui")
                st.rerun()

        with t4:
            if st.button("🛡️ Cash Flow Stress Test", use_container_width=True):
                st.session_state.selected_tool = ("stress_test_simulator", "show_stress_test_simulator")
                st.rerun()

    else:
        mod_name, func_name = st.session_state.selected_tool
        
        # Back button for external tools
        if mod_name != "INTERNAL":
            if st.button("⬅️ Back to Library Hub"):
                st.session_state.selected_tool = None
                st.rerun()
            st.divider()

        if mod_name == "INTERNAL":
            # Execution of local functions defined above
            if func_name in globals():
                globals()[func_name]()
        else:
            try:
                # Dynamic loading of external files from /tools folder
                current_dir = os.path.dirname(os.path.abspath(__file__))
                file_path = os.path.join(current_dir, "tools", f"{mod_name}.py")
                spec = importlib.util.spec_from_file_location(mod_name, file_path)
                module = importlib.util.module_from_spec(spec)
                sys.modules[mod_name] = module 
                spec.loader.exec_module(module)
                getattr(module, func_name)()
            except Exception as e:
                st.error(f"❌ Error loading tool: {e}")
                if st.button("Reset"):
                    st.session_state.selected_tool = None
                    st.rerun()
