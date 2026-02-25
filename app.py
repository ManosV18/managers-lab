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

# 1. Page Configuration
st.set_page_config(page_title="Executive War Room", layout="wide", initial_sidebar_state="expanded")

# 2. State Initialization
# Προσοχή: Χρησιμοποιούμε παντού strings για τα στάδια για να μην μπερδευόμαστε
if 'flow_step' not in st.session_state:
    st.session_state.flow_step = "home"

if 'mode' not in st.session_state:
    st.session_state.mode = "path"

# Defaults (DNA)
defaults = {
    'price': 150.0, 'variable_cost': 90.0, 'volume': 1000,
    'fixed_cost': 40000.0, 'tax_rate': 0.22,
    'opening_cash': 50000.0, 'annual_loan_payment': 12000.0,
    'ar_days': 45, 'inventory_days': 30, 'ap_days': 60,
    'baseline_locked': False
}
for key, value in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = value

# 3. Sidebar Navigation
show_sidebar()

# 4. Main Flow Controller (Router)
if st.session_state.mode == "library":
    show_library()
else:
    # Καθαρή δρομολόγηση με strings
    step = str(st.session_state.flow_step) # Μετατροπή σε string για ασφάλεια

    if step == "home" or step == "0":
        show_home()
    elif step == "stage0":
        run_stage0()
    elif step == "stage1" or step == "1":
        run_stage1()
    elif step == "stage2" or step == "2":
        run_stage2()
    elif step == "stage3" or step == "3":
        run_stage3()
    elif step == "stage4" or step == "4":
        run_stage4()
    elif step == "stage5" or step == "5":
        run_stage5()
    else:
        # Fallback αν κάτι πάει στραβά
        show_home()
