import streamlit as st
import sys
import os

# 1. PATH CONFIGURATION
# Διασφάλιση ότι ο root φάκελος είναι στο path για απρόσκοπτα imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# 2. CORE ENGINE IMPORTS
from core.engine import initialize_system_state, compute_core_metrics

# 3. UI & STAGES IMPORTS
from ui.sidebar import render_sidebar
from ui.home import show_home
from ui.about import show_about
from ui.library import show_library

from path.stage0 import run_stage0
from path.stage1 import run_stage1
from path.stage2 import run_stage2
from path.stage3 import run_stage3
# Προσάρμοσε τα παρακάτω αν έχεις αλλάξει ονόματα αρχείων/συναρτήσεων
from path.stage4 import run_stage4 
from path.stage5 import run_stage5

# =========================================================
# PAGE CONFIG (Πρέπει να είναι το πρώτο Streamlit command)
# =========================================================
st.set_page_config(
    page_title="Managers' Lab Engine v2.0",
    layout="wide",
    page_icon="🧪",
    initial_sidebar_state="expanded"
)

# =========================================================
# 1️⃣ INITIALIZATION (Single Source of Truth)
# =========================================================
# Δημιουργεί όλα τα defaults στο session_state πριν από οτιδήποτε άλλο
initialize_system_state()

# =========================================================
# 2️⃣ SIDEBAR RENDER
# =========================================================
# Η sidebar διαβάζει/γράφει στο session_state (mode, flow_step)
render_sidebar()

# =========================================================
# 3️⃣ GLOBAL METRICS CALCULATOR
# =========================================================
# Υπολογίζουμε τα metrics μια φορά στην αρχή κάθε rerun. 
# Έτσι, κάθε stage μπορεί να τα καλέσει αν χρειαστεί, 
# αλλά η αρχική τους κατάσταση είναι πάντα διαθέσιμη.
metrics = compute_core_metrics()

# =========================================================
# 4️⃣ ROUTER LOGIC
# =========================================================
mode = st.session_state.get("mode", "home")

# Διαχωρισμός Main Views από το "Path" (Lab Analysis)
if mode == "home":
    show_home()
elif mode == "about":
    show_about()
elif mode == "library":
    show_library()
elif mode == "path":
    # Lab Stages Routing
    step = st.session_state.get("flow_step", 0)
    
    stage_router = {
        0: run_stage0,
        1: run_stage1,
        2: run_stage2,
        3: run_stage3,
        4: run_stage4,
        5: run_stage5
    }
    
    # Ασφαλής εκτέλεση του stage
    if step in stage_router:
        stage_router[step]()
    else:
        st.error(f"❌ Error: Stage {step} not found in the lab sequence.")
        if st.button("Return to Start"):
            st.session_state.flow_step = 0
            st.rerun()

# =========================================================
# FOOTER / DEBUG (Optional)
# =========================================================
# st.sidebar.divider()
# st.sidebar.caption(f"Current Mode: {mode} | Step: {st.session_state.get('flow_step')}")
