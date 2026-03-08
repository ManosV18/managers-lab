import streamlit as st

def show_sidebar():
    if "flow_step" not in st.session_state:
        st.session_state.flow_step = "home"

    with st.sidebar:
        st.title("🚀 Strategy Command")

        # Navigation μόνο Home + Tools Library
        nav_options = {
            "🏠 Home": "home",
            "📚 Tools Library": "library"
        }

        current_step = st.session_state.flow_step
        options_list = list(nav_options.keys())
        values_list = list(nav_options.values())
        try:
            default_idx = values_list.index(current_step)
        except ValueError:
            default_idx = 0

        selection = st.selectbox("Navigate:", options_list, index=default_idx)
        if nav_options[selection] != current_step:
            st.session_state.flow_step = nav_options[selection]
            st.rerun()

        st.divider()

        # System Integrity
        st.subheader("🛡️ System Status")
        if st.session_state.get('baseline_locked', False):
            st.success("✅ Baseline: LOCKED")
        else:
            st.warning("🔓 Baseline: OPEN (Setup Phase)")

        st.divider()

        # Actions
        if not st.session_state.get('baseline_locked', False):
            if st.button("🔒 Lock Baseline", use_container_width=True):
                from core.sync import lock_baseline
                lock_baseline()
                st.session_state.flow_step = "home"
                st.rerun()

        if st.button("🔄 Reset All Data", use_container_width=True):
            st.session_state.clear()
            st.session_state.flow_step = "home"
            st.rerun()
