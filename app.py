import streamlit as st
from ui.sidebar import show_sidebar
from ui.home import run_home

st.set_page_config(page_title="Strategic Decision Room", layout="wide")

# Initialize session
if 'flow_step' not in st.session_state:
    st.session_state.flow_step = "home"

# Sidebar
show_sidebar()

step = st.session_state.flow_step


# ROUTER
if step == "home":

    run_home()


elif step == "library":

    try:
        from core.tools_registry import show_library
        show_library()
    except ImportError:
        st.error("Tools registry component not found.")


elif step == "tool":

    tool = st.session_state.get("selected_tool")

    if tool:

        module_name, function_name = tool

        try:
            module = __import__(f"tools.{module_name}", fromlist=[function_name])
            func = getattr(module, function_name)
            func()

        except Exception as e:
            st.error(f"Tool failed to load: {e}")

    else:
        st.session_state.flow_step = "home"
        st.rerun()


else:
    st.session_state.flow_step = "home"
    st.rerun()
