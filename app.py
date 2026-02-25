import streamlit as st
from ui.sidebar import show_sidebar
from ui.home import show_home
from path.stage0 import run_stage0
from path.stage1 import run_stage1
from path.stage2 import run_stage2
from path.stage3 import run_stage3
from path.stage4 import run_stage4
from path.stage5 import run_stage5
from ui.library import show_library

# 1. Page Config
st.set_page_config(page_title="Executive War Room", layout="wide")

# 2. State Initialization (DNA)
if 'mode' not in st.session_state:
    st.session_state.mode = "path"
if 'flow_step' not in st.session_state:
    st.session_state.flow_step = "home"

# 3. Sidebar
show_sidebar()

# --- DEBUG SECTION (Προσωρινό) ---
# st.sidebar.write(f"DEBUG: Mode = {st.session_state.mode}")
# st.sidebar.write(f"DEBUG: Step = {st.session_state.flow_step}")
# --------------------------------

# 4. ROUTER (The Decider)
if st.session_state.mode == "library":
    show_library()

else:
    # Μετατροπή σε string για να αποφύγουμε Type Errors
    current_step = str(st.session_state.flow_step)

    if current_step == "home" or current_step == "0":
        show_home()
    
    elif current_step == "stage0":
        run_stage0()
        
    elif current_step == "stage1":
        run_stage1()
        
    elif current_step == "stage2":
        run_stage2()
        
    elif current_step == "stage3":
        run_stage3()
        
    elif current_step == "stage4":
        run_stage4()
        
    elif current_step == "stage5":
        run_stage5()
        
    else:
        # Αν χαθεί το σύστημα, γύρνα στην αρχή
        show_home()
