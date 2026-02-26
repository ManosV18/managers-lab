import streamlit as st
from ui.sidebar import show_sidebar
from core.sync import sync_global_state

st.set_page_config(page_title="Managers Lab", layout="wide")

# Initialize lock state
if "baseline_locked" not in st.session_state:
    st.session_state.baseline_locked = False

# Sidebar
show_sidebar()

# Engine Sync
metrics = sync_global_state()

st.title("Managers Lab")

if not st.session_state.baseline_locked:
    st.warning("Baseline not locked. Please lock baseline.")
elif metrics is None:
    st.error("Engine returned no metrics. Check inputs.")
else:
    st.success("Engine Active")
    st.write(metrics)
