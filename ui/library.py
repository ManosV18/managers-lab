import streamlit as st
import importlib

def show_library():
    # 1. Initialization
    if "selected_tool" not in st.session_state:
        st.session_state.selected_tool = None

    # 2. Dynamic Tool Loader (Safe Mode)
    if st.session_state.selected_tool:
        module_name, function_name = st.session_state.selected_tool
        try:
            module = importlib.import_module(f"tools.{module_name}")
            func = getattr(module, function_name)
            func()
        except Exception as e:
            st.error(f"❌ Error loading tool '{module_name}': {e}")
            if st.button("Back to Library Hub"):
                st.session_state.selected_tool = None
                st.rerun()
        return

    # 3. Main Library UI
    st.title("📚 Strategy & Operations Library")
    st.caption("Analytical toolsets for corporate decision making")
    
    tabs = st.tabs(["🎯 Strategy", "📈 Sales & Pricing", "⚙️ Operations"])

    with tabs[0]: # Strategy
        st.subheader("Strategic Frameworks")
        if st.button("🧭 QSPM Strategy Comparison", use_container_width=True):
            st.session_state.selected_tool = ("qspm_analyzer", "show_qspm_tool")
            st.rerun()

    with tabs[1]: # Sales & Pricing
        st.subheader("Revenue & Elasticity")
        if st.button("📉 Sales Loss Threshold (Price Cut)", use_container_width=True):
            st.session_state.selected_tool = ("loss_threshold", "show_loss_threshold_before_price_cut")
            st.rerun()
        
        if st.button("🎯 Pricing Strategy & Elasticity", use_container_width=True):
            st.session_state.selected_tool = ("pricing_elasticity", "show_pricing_strategy_tool")
            st.rerun()

    with tabs[2]: # Operations
        st.subheader("Working Capital Management")
        if st.button("📊 Receivables NPV Analyzer", use_container_width=True):
            st.session_state.selected_tool = ("receivables_analyzer", "show_receivables_analyzer_ui")
            st.rerun()
