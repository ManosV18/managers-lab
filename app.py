import streamlit as st
from ui.sidebar import show_sidebar
from ui.home import run_home

# Stage modules
try:
    from path.stage0 import run_stage0
    from path.stage1 import run_stage1
    from path.stage2 import run_stage2
    from path.stage3 import run_stage3
    from path.stage4 import run_stage4
    from path.stage5 import run_stage5
except ImportError as e:
    st.error(f"Module Loading Error: {e}")

# Page config
st.set_page_config(page_title="Strategic Decision Room", layout="wide")

# Initialize session
if 'flow_step' not in st.session_state:
    st.session_state.flow_step = "home"

# Show sidebar
show_sidebar()

# --- ROUTER ---
step = st.session_state.flow_step

if step == "home":
    run_home()
elif step == "library":
    # ΔΙΟΡΘΩΣΗ: Καλούμε το αρχείο tools.py που είναι μέσα στο core
    from core.tools import show_library
    show_library()
elif step.startswith("stage"):
    # Δυναμική κλήση των stages για συντομία
    globals()[f"run_{step}"]()
else:
    st.warning(f"Step '{step}' not found. Redirecting to Home.")
    st.session_state.flow_step = "home"
    st.rerun()
