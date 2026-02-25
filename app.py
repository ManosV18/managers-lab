import streamlit as st
from ui.sidebar import show_sidebar
from ui.home import show_home
from path.stage0 import run_stage0
from ui.library import show_library

st.set_page_config(page_title="Executive War Room", layout="wide")

# DNA Initialization
if 'mode' not in st.session_state: st.session_state.mode = "path"
if 'flow_step' not in st.session_state: st.session_state.flow_step = "home"
if 'baseline_locked' not in st.session_state: st.session_state.baseline_locked = False

show_sidebar()

# ROUTER LOGIC
if st.session_state.mode == "library":
    show_library()
else:
    step = str(st.session_state.flow_step)
    if step == "home":
        show_home()
    elif step == "stage0":
        run_stage0()
    else:
        # Αν προσθέσεις stage1, stage2 κλπ, τα βάζεις εδώ
        st.info(f"Stage {step} is active. Coming soon.")
        if st.button("Back to Home"):
            st.session_state.flow_step = "home"
            st.rerun()
