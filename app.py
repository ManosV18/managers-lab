import streamlit as st
from ui.sidebar import show_sidebar
from ui.home import run_home

st.set_page_config(page_title="Strategic Decision Room", layout="wide")

# Initialize session
if 'flow_step' not in st.session_state:
    st.session_state.flow_step = "home"

# Sidebar
show_sidebar()

# Stage imports
try:
    from path.stage0 import run_stage0
    from path.stage1 import run_stage1
    from path.stage2 import run_stage2
    from path.stage3 import run_stage3
    from path.stage4 import run_stage4
    from path.stage5 import run_stage5
except ImportError as e:
    st.error(f"Module Loading Error: {e}")

# Router
step = st.session_state.flow_step

if step == "home":
    run_home()

elif step == "library":
    try:
        from core.tools_registry import show_library
        show_library()
    except ImportError:
        st.error("Tools library not found.")

elif step.startswith("stage"):
    try:
        globals()[f"run_{step}"]()
    except KeyError:
        st.error(f"Function run_{step} not found.")

else:
    st.session_state.flow_step = "home"
    st.rerun()
