import streamlit as st


def show_sidebar():

    with st.sidebar:

        st.title("Managers Lab")

        if st.button("🏠 Home", use_container_width=True):
            st.session_state.flow_step = "home"
            st.rerun()

        if st.button("🧠 Tools Library", use_container_width=True):
            st.session_state.flow_step = "library"
            st.rerun()

        st.divider()

        st.markdown("### Controls")

        lock = st.checkbox("Lock Parameters", value=False)

        st.session_state.lock_parameters = lock
