import streamlit as st
import sys
import os

# =========================================================
# 1️⃣ PAGE CONFIG (Πάντα πρώτο)
# =========================================================
st.set_page_config(
    page_title="Managers' Lab Engine v2.0",
    layout="wide",
    page_icon="🧪",
    initial_sidebar_state="expanded"
)

# =========================================================
# 2️⃣ PATH CONFIGURATION (Επιθετικό Routing)
# =========================================================
# Παίρνουμε το απόλυτο path του project root
root_dir = os.path.dirname(os.path.abspath(__file__))

# Επιβάλλουμε στην Python να κοιτάξει πρώτα στο δικό μας root
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

# =========================================================
# 3️⃣ SAFE IMPORTS (Με Error Diagnostics)
# =========================================================
try:
    from core.engine import initialize_system_state, compute_core_metrics
    from ui.sidebar import render_sidebar
    from ui.home import show_home
    from ui.about import show_about
    from ui.library import show_library
    
    # Imports των Stages ως modules για σταθερότητα
    import path.stage0 as s0
    import path.stage1 as s1
    import path.stage2 as s2
    import path.stage3 as s3
    import path.stage4 as s4
    import path.stage5 as s5
    
except ImportError as e:
    st.error(f"🚨 **Import Error:** {e}")
    # Debug info για τον χρήστη
    st.info(f"Root: {root_dir}")
    if os.path.exists(os.path.join(root_dir, 'path')):
        st.write("Files in path/:", os.listdir(os.path.join(root_dir, 'path')))
    else:
        st.error("Folder 'path/' not found! Check case-sensitivity (must be lowercase).")
    st.stop()

# =========================================================
# 4️⃣ INITIALIZATION & STATE
# =========================================================
initialize_system_state()
render_sidebar()
metrics = compute_core_metrics()

# =========================================================
# 5️⃣ GLOBAL STATUS BAR (Προαιρετικό αλλά χρήσιμο)
# =========================================================
# Εμφανίζεται μόνο όταν είμαστε μέσα στο Lab (Path)
if st.session_state.get("mode") == "path":
    with st.container():
        c1, c2, c3, c4 = st.columns(4)
        c1.caption("📍 Stage")
        c1.write(f"**{st.session_state.flow_step}**")
        c2.caption("💰 Net Profit")
        c2.write(f"**{metrics['net_profit']:,.0f} €**")
        c3.caption("🛡️ Survival BEP")
        c3.write(f"**{metrics['survival_bep']:,.0f} u**")
        c4.caption("🌊 FCF")
        c4.write(f"**{metrics['fcf']:,.0f} €**")
        st.divider()

# =========================================================
# 6️⃣ ROUTER LOGIC
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
    
    # Mapping των συναρτήσεων από τα modules
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
