import streamlit as st
import sys
import os

# =========================================================
# 1️⃣ PAGE CONFIG (ΠΡΕΠΕΙ ΝΑ ΕΙΝΑΙ Η ΠΡΩΤΗ ΕΝΤΟΛΗ)
# =========================================================
st.set_page_config(
    page_title="Managers' Lab Engine v2.0",
    layout="wide",
    page_icon="🧪",
    initial_sidebar_state="expanded"
)

# =========================================================
# 2️⃣ PATH & IMPORTS
# =========================================================
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Imports Engine & UI
from core.engine import initialize_system_state, compute_core_metrics
from ui.sidebar import render_sidebar
from ui.home import show_home
from ui.about import show_about
from ui.library import show_library

# Imports Stages (Μετά το set_page_config για αποφυγή σφαλμάτων)
try:
    from path.stage0 import run_stage0
    from path.stage1 import run_stage1
    from path.stage2 import run_stage2
    from path.stage3 import run_stage3
    from path.stage4 import run_stage4 
    from path.stage5 import run_stage5
except ImportError as e:
    st.error(f"🚨 Σφάλμα Import: {e}")
    st.stop()

# =========================================================
# 3️⃣ INITIALIZATION & METRICS
# =========================================================
initialize_system_state()
render_sidebar()
metrics = compute_core_metrics()

# =========================================================
# 4️⃣ ROUTER LOGIC
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
    
    if step in stage_router:
        stage_router[step]()
    else:
        st.error(f"❌ Error: Stage {step} not found.")
        if st.button("Return to Start"):
            st.session_state.flow_step = 0
            st.rerun()
