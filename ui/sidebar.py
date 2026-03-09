import streamlit as st

def show_sidebar():

    if "flow_step" not in st.session_state:
        st.session_state.flow_step = "home"

    with st.sidebar:

        st.markdown(
            """
            <div style="text-align:center;">
                <h2>🧠 Managers Lab</h2>
                <p style="font-size:12px;color:gray;">
                Strategic Finance Tools
                </p>
            </div>
            """,
            unsafe_allow_html=True
        )

        st.divider()

        st.title("🚀 Strategy Command")
        st.caption("v2.0 | Zero-Base Logic")

        if st.button("🏠 Back to Main Dashboard", use_container_width=True):
            st.session_state.selected_tool = None
            st.session_state.flow_step = "home"
            st.rerun()

        st.divider()

        st.subheader("🛡️ System Integrity")

        if st.session_state.get('baseline_locked', False):
            st.success("✅ Baseline: LOCKED")
        else:
            st.warning("🔓 Baseline: OPEN")

        st.divider()

        if st.button("🔄 Global Reset", type="secondary", use_container_width=True):
            st.session_state.clear()
            st.session_state.flow_step = "home"
            st.rerun()
