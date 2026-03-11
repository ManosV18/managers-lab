import streamlit as st
import importlib.util
import os
import sys

# =========================================================
# 🚀 UNIVERSAL DYNAMIC LOADER
# =========================================================
def show_library():
    s = st.session_state
    
    # 1. Safety Gate: If no tool is selected, redirect to home
    if s.get("selected_tool") is None:
        s.flow_step = "home"
        st.rerun()

    # 2. Clean Navigation Header
    if st.button("⬅️ Return to Control Tower"):
        s.selected_tool = None
        s.flow_step = "home"
        st.rerun()

    st.divider()

    # 3. Extract Module and Function names
    # Expected format in session_state: ("file_name", "function_name")
    tool_info = s.get("selected_tool")
    mod_name, func_name = tool_info

    # 4. Handle Internal Diagnostic Case
    if mod_name == "INTERNAL":
        show_internal_diagnostic()
        return

    # 5. External File Loader Logic
    try:
        # Resolve absolute paths dynamically
        current_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.abspath(os.path.join(current_dir, ".."))
        file_path = os.path.join(project_root, "tools", f"{mod_name}.py")

        if os.path.exists(file_path):
            # Load the external module
            spec = importlib.util.spec_from_file_location(mod_name, file_path)
            module = importlib.util.module_from_spec(spec)
            sys.modules[mod_name] = module
            spec.loader.exec_module(module)
            
            # Execute the specified function from the file
            if hasattr(module, func_name):
                func = getattr(module, func_name)
                func()
            else:
                st.error(f"Function Error: '{func_name}' not found in '{mod_name}.py'")
        else:
            # File missing error
            st.error(f"Missing File: tools/{mod_name}.py")
            st.info(f"Target path: {file_path}")
            if st.button("Run Diagnostic"):
                show_internal_diagnostic()

    except Exception as e:
        st.error(f"Runtime Error: {e}")
        if st.button("Back to Home"):
            s.selected_tool = None
            s.flow_step = "home"
            st.rerun()

# =========================================================
# 🛠️ INTERNAL SYSTEM DIAGNOSTIC (Fallback Mode)
# =========================================================
def show_internal_diagnostic():
    st.header("🤝 System Diagnostic Mode")
    st.info("Core engine is functional. External tool failed to load.")
    
    s = st.session_state
    
    # Simple calculation to verify state sync (365 days)
    v = s.get("volume", 1000)
    vc = s.get("variable_cost", 60.0)
    p = s.get("price", 100.0)
    
    annual_purchases = float(v) * float(vc)
    margin = float(p) - float(vc)
    
    st.subheader("Data Synchronization Check")
    col1, col2 = st.columns(2)
    col1.metric("Global Volume", f"{v:,}")
    col2.metric("Unit Margin", f"€{margin:,.2f}")
    
    st.success("State sync is active. Check file names in /tools folder.")
