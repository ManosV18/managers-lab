import streamlit as st
from core.sync import lock_baseline

def show_sidebar():
    # Initialize session defaults
    if "wacc" not in st.session_state:
        st.session_state.wacc = 0.15
    if "flow_step" not in st.session_state:
        st.session_state.flow_step = "home"

    with st.sidebar:
        st.title("💧 Cash Survival OS")

        # Navigation
        nav_options = {
            "🛡️ Strategic Decision Room": "home",
            "🏗️ Business Setup": "stage0",
            "📊 Profit Structure": "stage1",
            "🏁 Executive Overview": "stage2",
            "💧 Cash Flow Engine": "stage3",
            "🌪️ Stress Scenarios": "stage4",
            "⚖️ Decision Impact": "stage5",
            "📚 Tools Library": "library",
            "ℹ️ About System": "about"
        }

        current_step = st.session_state.flow_step
        options_list = list(nav_options.keys())
        values_list = list(nav_options.values())

        try:
            default_idx = values_list.index(current_step)
        except ValueError:
            default_idx = 0

        selection = st.selectbox("Navigation:", options_list, index=default_idx)

        if nav_options[selection] != current_step:
            st.session_state.flow_step = nav_options[selection]
            st.rerun()

        st.divider()

        # System Integrity
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

        # Baseline Inputs (basic 4 numbers)
        st.subheader("⚙️ Baseline Inputs")
        st.session_state.price = st.number_input(
            "Price (€)", value=float(st.session_state.get('price', 100.0))
        )
        st.session_state.variable_cost = st.number_input(
            "Variable Cost (€)", value=float(st.session_state.get('variable_cost', 60.0))
        )
        st.session_state.volume = st.number_input(
            "Annual Volume", value=int(st.session_state.get('volume', 1000))
        )
        st.session_state.fixed_cost = st.number_input(
            "Fixed Costs (€)", value=float(st.session_state.get('fixed_cost', 20000.0))
        )

        st.divider()

        # Actions
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
