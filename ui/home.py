import streamlit as st


def run_home():

    st.title("Managers Lab")

    st.markdown(
        """
Select a category to open the corresponding tools.
"""
    )

    col1, col2 = st.columns(2)

    with col1:
        if st.button("🚀 Strategy & Pricing", use_container_width=True):
            st.session_state.library_tab = 0
            st.session_state.flow_step = "library"
            st.rerun()

    with col2:
        if st.button("💰 Capital & Finance", use_container_width=True):
            st.session_state.library_tab = 1
            st.session_state.flow_step = "library"
            st.rerun()

    col3, col4 = st.columns(2)

    with col3:
        if st.button("⚙️ Operations & CCC", use_container_width=True):
            st.session_state.library_tab = 2
            st.session_state.flow_step = "library"
            st.rerun()

    with col4:
        if st.button("🛡️ Risk & Control", use_container_width=True):
            st.session_state.library_tab = 3
            st.session_state.flow_step = "library"
            st.rerun()
