import streamlit as st
from ui.sidebar import show_sidebar
# Διόρθωση: Κάνουμε import τη σωστή συνάρτηση από το ui/home.py
from ui.home import run_home 
from ui.library import show_library

# 1. Κεντρική Διαχείριση Imports (για αποφυγή σφαλμάτων στη διαδρομή)
try:
    from path.stage0 import run_stage0
    from path.stage1 import run_stage1
    # Υποθέτουμε ότι το Stage 2 είναι το Executive Dashboard
    from tools.executive_dashboard import show_executive_dashboard as run_stage2
    # Πρόσθεσε εδώ τα υπόλοιπα stages αν είναι έτοιμα
except ImportError as e:
    st.error(f"Missing Module Error: {e}")

st.set_page_config(page_title="Executive War Room", layout="wide")

# DNA Initialization (Cold Start)
if 'mode' not in st.session_state: st.session_state.mode = "path"
if 'flow_step' not in st.session_state: st.session_state.flow_step = "home"

# Εμφάνιση Sidebar (ελέγχει το flow_step και το mode)
show_sidebar()

# --- ROUTER LOGIC ---
# 
if st.session_state.mode == "library":
    show_library()
else:
    step = str(st.session_state.flow_step)
    
    if step == "home":
        run_home() # Καλεί τη συνάρτηση από το ui/home.py
        
    elif step == "stage0":
        run_stage0()
        
    elif step == "stage1":
        run_stage1()
        
    elif step == "stage2":
        # Διασφάλιση ότι η συνάρτηση υπάρχει πριν την κλήση
        if 'run_stage2' in locals():
            run_stage2()
        else:
            st.warning("Stage 2 module not loaded.")
            
    elif step == "stage3":
        try: from path.stage3 import run_stage3; run_stage3()
        except: st.error("Stage 3 (Liquidity Physics) not found.")
        
    elif step == "stage4":
        try: from path.stage4 import run_stage4; run_stage4()
        except: st.error("Stage 4 (Stress Testing) not found.")
        
    elif step == "stage5":
        try: from path.stage5 import run_stage5; run_stage5()
        except: st.error("Stage 5 (QSPM) not found.")
        
    else:
        st.warning(f"Step '{step}' is not mapped in the central router.")
