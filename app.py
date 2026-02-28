import streamlit as st

# 1. PAGE CONFIGURATION (Must be the first Streamlit command)
st.set_page_config(
    page_title="Cash Survival OS | Managers' Lab",
    page_icon="💧",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 2. IMPORT CORE UI ELEMENTS
try:
    from ui.sidebar import show_sidebar
    from ui.home import run_home
    from ui.about import show_about
    from core.tools_registry import show_library
except ImportError as e:
    st.error(f"Critical Import Error: {e}")
    st.stop()

# 3. IMPORT STAGE MODULES
# We import them and map them to their corresponding run_ functions
try:
    from path.stage0 import run_stage0
    from path.stage1 import run_stage1
    from path.stage2 import run_stage2
    from path.stage3 import run_stage3
    from path.stage4 import run_stage4
    from path.stage5 import run_stage5
    
    # Mapping for dynamic execution
    stage_functions = {
        "stage0": run_stage0,
        "stage1": run_stage1,
        "stage2": run_stage2,
        "stage3": run_stage3,
        "stage4": run_stage4,
        "stage5": run_stage5
    }
except ImportError as e:
    st.warning(f"Note: Some stage modules are missing: {e}")
    stage_functions = {}

# 4. INITIALIZE GLOBAL SESSION STATE
if 'flow_step' not in st.session_state:
    st.session_state.flow_step = "home"

# 5. EXECUTE SIDEBAR (Handles navigation and global parameters)
show_sidebar()

# 6. --- MAIN ROUTER LOGIC ---
step = st.session_state.flow_step

# Display the correct page based on the navigation state
if step == "home":
    run_home()

elif step == "about":
    show_about()

elif step == "library":
    show_library()

elif step.startswith("stage"):
    # Execute the requested stage function
    if step in stage_functions:
        try:
            stage_functions[step]()
        except Exception as e:
            st.error(f"⚠️ Error running {step}: {e}")
            if st.button("Return Home"):
                st.session_state.flow_step = "home"
                st.rerun()
    else:
        st.error(f"Module for '{step}' is not loaded correctly.")
        if st.button("Go to Setup (Stage 0)"):
            st.session_state.flow_step = "stage0"
            st.rerun()

else:
    # Safety fallback
    st.warning(f"Step '{step}' not recognized. Returning to Command Center.")
    st.session_state.flow_step = "home"
    if st.button("Reload System"):
        st.rerun()

# 7. SYSTEM FOOTER (Optional)
st.sidebar.markdown("---")
st.sidebar.caption("⚡ Powered by Managers' Lab Engine v2.0")
