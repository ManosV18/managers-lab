import streamlit as st
from ui.sidebar import show_sidebar
from ui.home import show_home
# Εισαγωγή των Stages (Προσθήκη του stage0)
from path.stage0 import run_stage0
from path.stage1 import run_stage1
from path.stage2 import run_stage2
from path.stage3 import run_stage3
from path.stage4 import run_stage4
from path.stage5 import run_stage5

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
    'mode': 'path'
}

for key, value in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = value

# 3. Sidebar Navigation & Global Controls
show_sidebar()

# 4. Main Flow Controller (Router)
# Το logic εδώ διασφαλίζει ότι αν το Baseline δεν είναι κλειδωμένο, 
# ο χρήστης βλέπει μόνο το Stage 0 ή το Phase A του Home.
if st.session_state.flow_step == 0:
    if not st.session_state.baseline_locked:
        # Αν πατήσει "Define Baseline" στο Home, στείλτον στο Stage 0
        # Αλλιώς δείξε το Home (Phase A)
        show_home() 
    else:
        show_home() # Θα δείξει αυτόματα το Phase B (Control Center)
        
elif st.session_state.flow_step == "stage0": # Ειδικό βήμα για τον ορισμό
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
