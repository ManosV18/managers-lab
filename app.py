import streamlit as st

from ui.sidebar import show_sidebar
from ui.home import run_home
from core.tools_registry import show_library

st.set_page_config(
    page_title="Managers Lab",
    layout="wide"
)

# session state
if "flow_step" not in st.session_state:
    st.session_state.flow_step = "home"

# sidebar
show_sidebar()

# router
step = st.session_state.flow_step

if step == "home":
    run_home()

elif step == "library":
    show_library()

else:
    st.session_state.flow_step = "home"
    st.rerun()
