import streamlit as st
import sys
import os

# Διασφάλιση ότι ο root φάκελος είναι στο path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# THE FIX: Διαβάζουμε και τα δύο από το ενοποιημένο αρχείο πλέον
from core.engine import initialize_system_state, compute_core_metrics

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
# CONFIG (Πρέπει να είναι το πρώτο Streamlit command)
# =========================================================
st.set_page_config(page_title="Managers' Lab Engine", layout="wide", page_icon="🧪")

# =========================================================
# INITIALIZE CORE (ΠΡΙΝ ΤΟ ROUTING)
# =========================================================
initialize_system_state()

# =========================================================
# UI LAYOUT
# =========================================================
render_sidebar() 

# =========================================================
# ROUTER
# =========================================================
mode = st.session_state.get("mode", "home")

if mode == "home":
    show_home()
elif mode == "about":
    show_about()
elif mode == "library":
    show_library()
elif mode == "path":
    step = st.session_state.get("flow_step", 0)
    stage_router = {
        0: run_stage0,
        1: run_stage1,
        2: run_stage2,
        3: run_stage3,
        4: run_stage4,
        5: run_stage5
    }
    
    # Ασφαλής κλήση του router
    if step in stage_router:
        stage_router[step]()
    else:
        st.error(f"Stage {step} not found.")
