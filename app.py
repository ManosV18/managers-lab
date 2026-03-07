import streamlit as st

# --- Sidebar ---
from ui.sidebar import show_sidebar

# --- Home ---
from ui.home import run_home

# --- Stage modules (αν υπάρχουν τα αρχεία stage0, stage1 κλπ.) ---
try:
    from path.stage0 import run_stage0
    from path.stage1 import run_stage1
    from path.stage2 import run_stage2
    from path.stage3 import run_stage3
    from path.stage4 import run_stage4
    from path.stage5 import run_stage5
except ImportError:
    # Αν δεν υπάρχουν stages ακόμα, δεν κάνει τίποτα
    pass

# --- Page setup ---
st.set_page_config(page_title="Strategic Decision Room", layout="wide")

# --- Session defaults ---
if "flow_step" not in st.session_state:
    st.session_state.flow_step = "home"

# --- Show sidebar ---
#    show_sidebar()

# --- Router ---
step = st.session_state.flow_step

if step == "home":
    run_home()

elif step.startswith("stage"):
    # Δυναμική κλήση stages
    stage_func = f"run_{step}"
    if stage_func in globals():
        globals()[stage_func]()
    else:
        st.warning(f"Stage {step} not found. Returning Home.")
        st.session_state.flow_step = "home"
        st.rerun()

elif step == "library":
    from core.tools_registry import show_library
    show_library()

elif step == "about":
    try:
        from ui.about import show_about
        show_about()
    except ImportError:
        st.info("About page not implemented yet.")

else:
    st.warning(f"Step '{step}' not recognized. Redirecting Home.")
    st.session_state.flow_step = "home"
    st.rerun()
