import streamlit as st
import importlib.util
import os
import sys

def show_library():
    s = st.session_state
    
    # 1. Safety Check: If no tool is selected, go home
    if s.get("selected_tool") is None:
        s.flow_step = "home"
        st.rerun()

    # 2. Top Navigation Bar (English & Clean)
    if st.button("⬅️ Back to Control Tower"):
        s.selected_tool = None
        s.flow_step = "home"
        st.rerun()

    st.divider()

    # 3. Get Module and Function names from session
    # Example: ("pricing_strategy", "show_pricing_strategy_tool")
    mod_name, func_name = s.selected_tool

    # 4. INTERNAL DIAGNOSTIC ONLY (If explicitly called)
    if mod_name == "INTERNAL":
        show_payables_manager_internal()
        return

    # 5. UNIVERSAL EXTERNAL LOADER
    try:
        # Construct absolute path to the /tools directory
        current_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.abspath(os.path.join(current_dir, ".."))
        file_path = os.path.join(project_root, "tools", f"{mod_name}.py")

        if os.path.exists(file_path):
            # Dynamic Import Logic
            spec = importlib.util.spec_from_file_location(mod_name, file_path)
            module = importlib.util.module_from_spec(spec)
            sys.modules[mod_name] = module
            spec.loader.exec_module(module)
            
            # Call the specific function of the selected tool
            if hasattr(module, func_name):
                func = getattr(module, func_name)
                func()
            else:
                st.error(f"Function '{func_name}' not found in '{mod_name}.py'")
        else:
            st.error(f"File Not Found: tools/{mod_name}.py")
            st.info("Ensure the file exists in your /tools directory.")

    except Exception as e:
        st.error(f"System Error loading tool: {e}")

# --- Keep as emergency backup only ---
def show_payables_manager_internal():
    st.header("🤝 System Diagnostic (Internal Mode)")
    st.info("This is a hardcoded fallback to verify the engine is running.")
    # (Existing internal logic here...)
