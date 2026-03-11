import streamlit as st
import importlib.util
import os
import sys

def show_library():
    s = st.session_state
    
    if s.get("selected_tool") is None:
        s.flow_step = "home"
        st.rerun()

    if st.button("⬅️ Back to Dashboard"):
        s.selected_tool = None
        s.flow_step = "home"
        st.rerun()

    st.divider()

    mod_name, func_name = s.selected_tool

    try:
        # Βρίσκει τη διαδρομή του αρχείου ό,τι και να γίνει
        current_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.abspath(os.path.join(current_dir, ".."))
        file_path = os.path.join(project_root, "tools", f"{mod_name}.py")

        # Φόρτωση του αρχείου
        spec = importlib.util.spec_from_file_location(mod_name, file_path)
        module = importlib.util.module_from_spec(spec)
        sys.modules[mod_name] = module
        spec.loader.exec_module(module)
        
        # Εκτέλεση της συνάρτησης
        func = getattr(module, func_name)
        func()

    except Exception as e:
        st.error(f"CRITICAL ERROR: Could not load tool '{mod_name}'.")
        st.error(f"Error Details: {e}")
        st.info(f"Make sure 'tools/{mod_name}.py' exists and is named correctly.")
