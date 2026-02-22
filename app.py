import streamlit as st
from core.system_state import initialize_system_state
from core.sidebar import render_sidebar
from core.library import show_library
from core.about import show_about

# Εδώ είναι η αλλαγή για το home.py που βρίσκεται στο φάκελο UI
from UI.home import show_home  

# Import τα stages
import path.step0_calibration as stage0
import path.step1_survival as stage1
import path.step2_cash as stage2
import path.step3_unit_economics as stage3
import path.step4_sustainability as stage4
import path.step5_strategy as stage5

# Αρχικοποίηση Συστήματος
st.set_page_config(page_title="Managers' Lab", layout="wide")
initialize_system_state()

# Sidebar (σταθερό σε όλες τις σελίδες)
render_sidebar()

# Routing Logic
mode = st.session_state.get('mode', 'home')

if mode == "home":
    show_home()
elif mode == "about":
    show_about()
elif mode == "library":
    show_library()
elif mode == "path":
    step = st.session_state.get('flow_step', 0)
    if step == 0: stage0.run_step()
    elif step == 1: stage1.run_step()
    elif step == 2: stage2.run_step()
    elif step == 3: stage3.run_step()
    elif step == 4: stage4.run_step()
    elif step == 5: stage5.run_step()
