import streamlit as st
from ui.sidebar import show_sidebar
from ui.home import run_home

st.set_page_config(page_title="Strategic Decision Room", layout="wide")

# Initialize session
if 'flow_step' not in st.session_state:
    st.session_state.flow_step = "home"

# Sidebar always visible
show_sidebar()

# Stage imports (Wrapped to prevent app crash)
try:
    from path.stage0 import run_stage0
    from path.stage1 import run_stage1
    from path.stage2 import run_stage2
    from path.stage3 import run_stage3
    from path.stage4 import run_stage4
    from path.stage5 import run_stage5
except ImportError as e:
    st.warning(f"Note: Some stages are still in development: {e}")

# Router Logic
step = st.session_state.flow_step

if step == "home":
    run_home()

elif step == "library":
    try:
        from core.tools_registry import show_library
        show_library()
    except ImportError:
        st.error("Tools registry component not found.")

elif step.startswith("stage"):
    func_name = f"run_{step}"
    if func_name in globals():
        globals()[func_name]()
    else:
        st.error(f"Stage function {func_name} is not defined or imported.")
        if st.button("Return Home"):
            st.session_state.flow_step = "home"
            st.rerun()

else:
    st.session_state.flow_step = "home"
    st.rerun()
