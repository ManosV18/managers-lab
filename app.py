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

# ROUTER LOGIC
if st.session_state.mode == "library":
    from ui.library import show_library
    show_library()
else:
    step = str(st.session_state.flow_step)
    
    if step == "home":
        show_home()
    
    elif step == "stage0":
        run_stage0()
        
    elif step == "stage1":
        run_stage1() # Εδώ τρέχει το Leverage & BEP
        
    elif step == "stage2":
        run_stage2() # Εδώ τρέχει το Liquidity Dashboard (Working Capital)
        
    elif step == "stage3":
        # Εδώ θα μπει το Capital Allocation Matrix που ζήτησες
        st.header("💰 Stage 3: Capital Allocation Matrix")
        st.info("Coming Soon: Διάθεση της ρευστότητας σε στρατηγικές επενδύσεις.")
        if st.button("Back to Stage 2"):
            st.session_state.flow_step = "stage2"
            st.rerun()
            
    else:
        st.warning(f"Unknown Stage: {step}")
        if st.button("Reset to Home"):
            st.session_state.flow_step = "home"
            st.rerun()
