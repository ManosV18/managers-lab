import streamlit as st
from ui.sidebar import show_sidebar
from ui.home import run_home

# Stage modules - Standard Imports
try:
    from path.stage0 import run_stage0
    from path.stage1 import run_stage1
    from path.stage2 import run_stage2
    from path.stage3 import run_stage3
    from path.stage4 import run_stage4
    from path.stage5 import run_stage5
except ImportError as e:
    st.error(f"Module Loading Error: {e}")

# Page config
st.set_page_config(page_title="Strategic Decision Room", layout="wide")

# --- Initialize session ---
if 'flow_step' not in st.session_state:
    st.session_state.flow_step = "home"

# ------------------- Initialize critical session variables -------------------
for key, default in [
    ("price", 100.0),
    ("variable_cost", 60.0),
    ("volume", 1000),
    ("fixed_cost", 20000.0),
    ("wacc", 0.15),
    ("tax_rate", 0.22),
    ("annual_debt_service", 0.0),
    ("opening_cash", 10000.0),
    ("ar_days", 45),
    ("inventory_days", 60),
    ("ap_days", 30)
]:
    if key not in st.session_state:
        st.session_state[key] = default
# ------------------------------------------------------------------------------

# Show sidebar
show_sidebar()

# --- ROUTER ---
step = st.session_state.flow_step

if step == "home":
    run_home()
elif step == "library":
    from core.tools_registry import show_library
    show_library()
elif step.startswith("stage"):
    # Δυναμική κλήση των stages
    try:
        globals()[f"run_{step}"]()
    except KeyError:
        st.error(f"Function run_{step} not found.")
else:
    st.warning(f"Step '{step}' not found. Redirecting to Home.")
    st.session_state.flow_step = "home"
    st.rerun()
