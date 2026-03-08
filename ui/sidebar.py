import streamlit as st
from core.sync import lock_baseline

def show_sidebar():
    # ----------------------------
    # 1. Default session variables
    # ----------------------------
    if "wacc" not in st.session_state:
        st.session_state.wacc = 0.15
    if "flow_step" not in st.session_state:
        st.session_state.flow_step = "home"

    # ----------------------------
    # 2. Sidebar layout
    # ----------------------------
    with st.sidebar:
        st.title("🚀 Strategy Command")
        
        # ----------------------------
        # Navigation Menu
        # ----------------------------
        nav_options = {
            "🏠 Home": "home",
            "🏗️ Stage 0: Setup": "stage0",
            "📊 Stage 1: Survival & BEP": "stage1",
            "🏁 Stage 2: Dashboard": "stage2",
            "💧 Stage 3: Liquidity Physics": "stage3",
            "🌪️ Stage 4: Stress Testing": "stage4",
            "⚖️ Stage 5: Strategic Decision": "stage5",
            "📚 Tools Library": "library"
        }
        
        current_step = st.session_state.flow_step
        options_list = list(nav_options.keys())
        values_list = list(nav_options.values())
        try:
            default_idx = values_list.index(current_step)
        except ValueError:
            default_idx = 0

        selection = st.selectbox("Tool Selection:", options_list, index=default_idx)
        if nav_options[selection] != current_step:
            st.session_state.flow_step = nav_options[selection]
            st.rerun()

        st.divider()

        # ----------------------------
        # System Integrity
        # ----------------------------
        st.subheader("🛡️ System Integrity")

        if st.session_state.get('baseline_locked', False):
            st.success("✅ Baseline: LOCKED")
        else:
            st.warning("🔓 Baseline: OPEN (Setup Phase)")
            
        if st.session_state.get('wacc_locked', False):
            st.info(f"🎯 WACC: {st.session_state.wacc:.2%} (Optimized)")
        else:
            st.caption("Using manual WACC estimate")

        st.divider()

       
        # ----------------------------
        # Actions: Lock Baseline / Reset
        # ----------------------------
        if not st.session_state.get('baseline_locked', False):
            if st.button("🔒 Lock Baseline", use_container_width=True, type="primary"):
                lock_baseline()
                st.session_state.flow_step = "stage1"
                st.rerun()
        
        if st.button("🔄 Reset All Data", type="secondary", use_container_width=True):
            st.session_state.clear()
            st.session_state.flow_step = "home"
            st.session_state.wacc = 0.15
            st.rerun()
