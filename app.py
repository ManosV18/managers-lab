import streamlit as st
import sys
import os

# Διασφάλιση ότι ο root φάκελος είναι στο path (βοηθάει στα imports του Cloud)
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.system_state import initialize_system_state
from core.engine import compute_core_metrics

# Imports από τον φάκελο ui
from ui.sidebar import render_sidebar
from ui.home import show_home
from ui.about import show_about
from ui.library import show_library

# Imports από τον φάκελο path
from path.stage0 import run_stage0
from path.stage1 import run_stage1
from path.stage2 import run_stage2
from path.stage3 import run_stage3
from path.stage4 import run_stage4
from path.stage5 import run_stage5

# =========================================================
# CONFIG
# =========================================================
st.set_page_config(page_title="Managers' Lab Engine", layout="wide", page_icon="🧪")

# =========================================================
# INITIALIZE CORE & UI
# =========================================================
initialize_system_state()
render_sidebar()  # <--- Απαραίτητο για να δουλέψει το μενού

# =========================================================
# ROUTER
# =========================================================
mode = st.session_state.mode

if mode == "home":
    show_home()
elif mode == "about":
    show_about()
elif mode == "library":
    show_library()
elif mode == "path":
    step = st.session_state.flow_step
    stage_router = {
        0: run_stage0,
        1: run_stage1,
        2: run_stage2,
        3: run_stage3,
        4: run_stage4,
        5: run_stage5
    }
    stage_router[step]()
