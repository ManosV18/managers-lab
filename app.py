import streamlit as st
import sys
import os
import importlib.util

# =========================================================
# 1️⃣ PAGE CONFIG
# =========================================================
st.set_page_config(
    page_title="Managers' Lab Engine v2.0",
    layout="wide",
    page_icon="🧪",
    initial_sidebar_state="expanded"
)

# [ΑΝΤΙΚΑΤΑΣΤΑΣΗ ΣΤΟ APP.PY]
# =========================================================
# 2️⃣ PATH CONFIGURATION & MANUAL IMPORT HELPER
# =========================================================
root_dir = os.path.dirname(os.path.abspath(__file__))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir) # ΔΙΟΡΘΩΣΗ ΕΔΩ

def manual_import(module_name, file_name):
    """Load a module from path/ folder manually"""
    file_path = os.path.join(root_dir, "path", file_name)
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"{file_name} not found in 'path/'")
    
    spec = importlib.util.spec_from_file_location(module_name, file_path)
    if spec is None or spec.loader is None:
        raise ImportError(f"Could not load spec for {file_name}")
    
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module

# =========================================================
# 3️⃣ SAFE IMPORTS
# =========================================================
try:
    # Core engine & UI
    from core.engine import initialize_system_state, compute_core_metrics
    from ui.sidebar import render_sidebar
    from ui.home import show_home
    from ui.about import show_about
    from ui.library import show_library

    # Stages
    s0 = manual_import("s0", "stage0.py")
    s1 = manual_import("s1", "stage1.py")
    s2 = manual_import("s2", "stage2.py")
    s3 = manual_import("s3", "stage3.py")
    s4 = manual_import("s4", "stage4.py")
    s5 = manual_import("s5", "stage5.py")

except Exception as e:
    st.error(f"🚨 Critical Failure: {e}")
    st.info(f"Checking Directory: {os.path.join(root_dir, 'path')}")
    if os.path.exists(os.path.join(root_dir, 'path')):
        st.write("Files found:", os.listdir(os.path.join(root_dir, 'path')))
    st.stop()

# =========================================================
# 4️⃣ INITIALIZE SYSTEM & COMPUTE METRICS
# =========================================================
initialize_system_state()
render_sidebar()

try:
    metrics = compute_core_metrics()
except Exception as e:
    st.warning(f"⚠️ Metrics could not be computed: {e}")
    metrics = {
        "net_profit": 0,
        "survival_bep": 0,
        "fcf": 0,
        "ending_cash": 0
    }

# Live Lab Header
if st.session_state.get("mode") == "path":
    st.markdown(f"### 📊 Live Analysis: Stage {st.session_state.flow_step}")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Net Profit", f"{metrics.get('net_profit',0):,.0f} €")
    c2.metric("Survival BEP", f"{metrics.get('survival_bep',0):,.0f} u")
    c3.metric("FCF", f"{metrics.get('fcf',0):,.0f} €")
    c4.metric("Ending Cash", f"{metrics.get('ending_cash',0):,.0f} €")
    st.divider()

# =========================================================
# 5️⃣ ROUTER LOGIC
# =========================================================
mode = st.session_state.get("mode", "home")

if mode == "home":
    show_home()
elif mode == "about":
    show_about()
elif mode == "library":
    show_library()
elif mode == "path":
    step = st.session_state.get("flow_step", 0)
    stage_router = {
        0: s0.run_stage0,
        1: s1.run_stage1,
        2: s2.run_stage2,
        3: s3.run_stage3,
        4: s4.run_stage4,
        5: s5.run_stage5
    }
    
    if step in stage_router:
        stage_router[step]()
    else:
        st.error(f"❌ Stage {step} not found.")
        if st.button("Return to Start"):
            st.session_state.flow_step = 0
            st.rerun()
