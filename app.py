import streamlit as st
from ui.sidebar import show_sidebar
from ui.home import run_home
from ui.library import show_library

# 🛠️ Δυναμικά Imports για τα Stages
try:
    from path.stage0 import run_stage0
    from path.stage1 import run_stage1
    from tools.executive_dashboard import show_executive_dashboard as run_stage2
    # Πρόσθεσε εδώ μελλοντικά τα Stage 3, 4, 5
except ImportError as e:
    st.error(f"Module Loading Error: {e}")

st.set_page_config(page_title="Executive War Room", layout="wide")

# DNA Initialization (Μόνο flow_step πλέον)
if 'flow_step' not in st.session_state:
    st.session_state.flow_step = "home"

# Εμφάνιση Sidebar
show_sidebar()

# --- ROUTER LOGIC (Single Source of Truth) ---
step = st.session_state.flow_step

if step == "home":
    run_home()
elif step == "library":
    show_library()
elif step == "stage0":
    run_stage0()
elif step == "stage1":
    run_stage1()
elif step == "stage2":
    run_stage2()
elif step in ["stage3", "stage4", "stage5"]:
    st.info(f"🚀 {step.capitalize()} is under construction but mapped!")
else:
    st.warning(f"Step '{step}' not found. Redirecting to Home.")
    st.session_state.flow_step = "home"
    st.rerun()
