import streamlit as st
from core.system_state import initialize_system_state
from core.sidebar import render_sidebar
from core.home import show_home
from core.library import show_library
from core.about import show_about

# Δυναμικό import των Stages
import path.step0_calib as stage0
import path.step1_break as stage1
import path.step2_cash as stage2
import path.step3_clv as stage3
import path.step4_sustain as stage4
import path.step5_strategy as stage5

# Αρχικοποίηση
st.set_page_config(page_title="Managers' Lab", layout="wide", page_icon="🧪")
initialize_system_state()

# Sidebar
render_sidebar()

# Routing Logic
mode = st.session_state.mode

if mode == "home":
    show_home()
elif mode == "about":
    show_about()
elif mode == "library":
    show_library()
elif mode == "path":
    step = st.session_state.flow_step
    if step == 0: stage0.run_step()
    elif step == 1: stage1.run_step()
    elif step == 2: stage2.run_step()
    elif step == 3: stage3.run_step()
    elif step == 4: stage4.run_step()
    elif step == 5: stage5.run_step()
