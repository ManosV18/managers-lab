import streamlit as st
from core.system_state import initialize_system_state
from core.engine import compute_core_metrics

from ui.home import show_home
from ui.about import show_about
from ui.library import show_library

from path.stage0 import run_stage0
from path.stage1 import run_stage1
from path.stage2 import run_stage2
from path.stage3 import run_stage3
from path.stage4 import run_stage4
from path.stage5 import run_stage5

# =========================================================
# CONFIG
# =========================================================
st.set_page_config(page_title="Managers' Lab Engine", layout="wide")

# =========================================================
# INITIALIZE CORE
# =========================================================
initialize_system_state()

# =========================================================
# ROUTER
# =========================================================

if st.session_state.mode == "home":
    show_home()

elif st.session_state.mode == "about":
    show_about()

elif st.session_state.mode == "library":
    show_library()

elif st.session_state.mode == "path":

    stage_router = {
        0: run_stage0,
        1: run_stage1,
        2: run_stage2,
        3: run_stage3,
        4: run_stage4,
        5: run_stage5
    }

    stage_router[st.session_state.flow_step]()
