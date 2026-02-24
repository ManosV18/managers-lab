import streamlit as st
from ui.sidebar import show_sidebar
from ui.home import show_home
# Εισαγωγή των Stages
from path.stage0 import run_stage0
from path.stage1 import run_stage1
from path.stage2 import run_stage2
from path.stage3 import run_stage3
from path.stage4 import run_stage4
from path.stage5 import run_stage5
# Εισαγωγή της Library
from ui.library import show_library

# 1. Page Configuration
st.set_page_config(page_title="Executive War Room", layout="wide", initial_sidebar_state="expanded")

# 2. State Initialization (The System DNA)
if 'flow_step' not in st.session_state:
    st.session_state.flow_step = 0

if 'baseline_locked' not in st.session_state:
    st.session_state.baseline_locked = False

# Baseline Inputs - Defaults
defaults = {
    'price': 150.0, 'variable_cost': 90.0, 'volume': 1000,
    'fixed_cost': 40000.0, 'tax_rate': 0.22,
    'opening_cash': 50000.0, 'annual_loan_payment': 12000.0,
    'ar_days': 45, 'inventory_days': 30, 'ap_days': 60,
    'mode': 'path', # 'path' ή 'library'
    'active_tool': None
}

for key, value in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = value

# 3. Sidebar Navigation & Global Controls
show_sidebar()

# 4. Main Flow Controller (Router)
# ΕΛΕΓΧΟΣ MODE: Αν ο χρήστης επέλεξε Library
if st.session_state.mode == "library":
    show_library()

# ΑΝ ΕΙΝΑΙ ΣΕ PATH MODE (Stages)
else:
    if st.session_state.flow_step == 0:
        show_home() 
        
    elif st.session_state.flow_step == "stage0":
        run_stage0()
        
    elif st.session_state.flow_step == 1:
        run_stage1()
    elif st.session_state.flow_step == 2:
        run_stage2()
    elif st.session_state.flow_step == 3:
        run_stage3()
    elif st.session_state.flow_step == 4:
        run_stage4()
    elif st.session_state.flow_step == 5:
        run_stage5()
