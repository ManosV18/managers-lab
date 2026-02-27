import streamlit as st
from ui.sidebar import show_sidebar
from ui.home import run_home

# Stage modules
try:
    from path.stage0 import run_stage0
    from path.stage1 import run_stage1
    # Stage 2 → Executive Dashboard
    from tools.executive_dashboard import show_executive_dashboard as run_stage2
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
    from ui.library import show_library
    show_library()
elif step == "stage0":
    run_stage0()
elif step == "stage1":
    run_stage1()
elif step == "stage2":
    run_stage2()
elif step == "stage3":
    run_stage3()
elif step == "stage4":
    run_stage4()
elif step == "stage5":
    run_stage5()
else:
    st.warning(f"Step '{step}' not found. Redirecting to Home.")
    st.session_state.flow_step = "home"
    st.rerun()
