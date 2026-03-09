import streamlit as st

def show_sidebar():
    if "flow_step" not in st.session_state:
        st.session_state.flow_step = "home"

    with st.sidebar:
        st.markdown(
            """
            <div style="text-align:center; padding: 10px; border-radius:10px; background-color:#f8fafc; border: 1px solid #e2e8f0; margin-bottom:20px;">
                <h2 style="margin:0; color:#1E3A8A; font-size:24px;">🧠 Managers Lab</h2>
                <p style="font-size:11px; color:#64748b; text-transform:uppercase; letter-spacing:1px; margin-top:5px;">
                    Executive Control Panel
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
