import streamlit as st

# --- Sidebar ---
from ui.sidebar import show_sidebar

# --- Home ---
from ui.home import run_home

# --- Stage modules ---
# Αν δεν υπάρχουν, απλά δεν τα φορτώνει
stages = {}
for i in range(6):
    try:
        mod = __import__(f"path.stage{i}", fromlist=[f"run_stage{i}"])
        stages[f"stage{i}"] = getattr(mod, f"run_stage{i}")
    except ImportError:
        pass

# --- Page setup ---
st.set_page_config(page_title="Strategic Decision Room", layout="wide")

# --- Session defaults ---
if "flow_step" not in st.session_state:
    st.session_state.flow_step = "home"

# --- Show sidebar ---
show_sidebar()

# --- Router ---
step = st.session_state.flow_step

if step == "home":
    run_home()

elif step.startswith("stage"):
    stage_func = stages.get(step)
    if stage_func:
        stage_func()
    else:
        st.warning(f"Stage '{step}' not found. Returning Home.")
        st.session_state.flow_step = "home"
        st.experimental_rerun()

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
    st.experimental_rerun()
