import streamlit as st
from ui.sidebar import show_sidebar
from ui.home import show_home
from path.stage0 import run_stage0

# 1. ΠΡΟΣΘΗΚΗ ΤΩΝ ΝΕΩΝ IMPORTS
try:
    from path.stage1 import run_stage1 
    from tools.executive_dashboard import show_executive_dashboard as run_stage2
except ImportError as e:
    st.error(f"Missing Module: {e}")

st.set_page_config(page_title="Executive War Room", layout="wide")

# DNA Initialization
if 'mode' not in st.session_state: st.session_state.mode = "path"
if 'flow_step' not in st.session_state: st.session_state.flow_step = "home"

show_sidebar()

# --- ROUTER LOGIC in app.py ---
if st.session_state.mode == "library":
    show_library()
else:
    step = str(st.session_state.flow_step)
    
    if step == "home":
        show_home()
    elif step == "stage0":
        from path.stage0 import run_stage0
        run_stage0()
    elif step == "stage1":
        from path.stage1 import run_stage1
        run_stage1()
    elif step == "stage2":
        from path.stage2 import run_stage2 # This is your Dashboard
        run_stage2()
    elif step == "stage3":
        from path.stage3 import run_stage3 # Liquidity Physics
        run_stage3()
    elif step == "stage4":
        from path.stage4 import run_stage4 # Stress Testing
        run_stage4()
    elif step == "stage5":
        from path.stage5 import run_stage5 # Recovery Decision
        run_stage5()
    else:
        st.warning(f"Step {step} not mapped.")
