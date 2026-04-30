import streamlit as st


def show_sidebar():
    with st.sidebar:
        st.markdown(
            "<h2 style='color:#1E3A8A;'>🧠 Managers Lab</h2>",
            unsafe_allow_html=True
        )
        st.divider()

        # Επιστροφή στην κεντρική οθόνη
        if st.button("🏠 Control Tower", use_container_width=True):
            st.session_state.flow_step = "home"
            st.session_state.selected_tool = None
            st.rerun()

        # About / System Architecture
        if st.button("🧪 System Architecture", use_container_width=True):
            st.session_state.flow_step = "about"
            st.rerun()

        st.divider()

        # Κατάσταση Συστήματος
        if st.session_state.get("baseline_locked", False):
            st.success("✅ Baseline: LOCKED")
        else:
            st.warning("🔓 Baseline: OPEN")

        # Global Reset
        if st.button("🔄 Global Reset", type="secondary", use_container_width=True):
            st.session_state.clear()
            st.rerun()

        st.divider()

        # Product Hunt badge
        st.markdown("### 🚀 Featured on Product Hunt")

        st.markdown(
            """
            <a href="https://www.producthunt.com/products/managers-lab?embed=true&utm_source=badge-featured&utm_medium=badge&utm_campaign=badge-managers-lab"
               target="_blank"
               rel="noopener noreferrer">
                <img
                    src="https://api.producthunt.com/widgets/embed-image/v1/featured.svg?post_id=1132085&theme=light"
                    alt="Managers' Lab - Built for better decisions. Not more software. | Product Hunt"
                    width="250"
                />
            </a>
            """,
            unsafe_allow_html=True
        )
