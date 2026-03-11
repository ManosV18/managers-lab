import streamlit as st
from ui.sidebar import show_sidebar
from ui.home import run_home

# Ρύθμιση Σελίδας
st.set_page_config(page_title="Managers Lab - Strategic Decision Room", layout="wide")

# Αρχικοποίηση Session State
if 'flow_step' not in st.session_state:
    st.session_state.flow_step = "home"
if 'selected_tool' not in st.session_state:
    st.session_state.selected_tool = None

# Εμφάνιση Sidebar (αν υπάρχει)
show_sidebar()

step = st.session_state.flow_step

# --- ROUTER LOGIC ---
if step == "home":
    run_home()

elif step == "library":
    # Προσπάθεια φόρτωσης της βιβλιοθήκης
    try:
        from core.tools_registry import show_library
        show_library()
    except Exception as e:
        st.warning("Library view not found, redirecting to direct tool loader...")
        st.session_state.flow_step = "tool"
        st.rerun()

elif step == "tool":
    tool_data = st.session_state.get("selected_tool")

    if tool_data:
        # tool_data: ("module_name", "function_name")
        module_name, function_name = tool_data

        try:
            # Δυναμικό Import του εργαλείου από τον φάκελο tools
            module = __import__(f"tools.{module_name}", fromlist=[function_name])
            func = getattr(module, function_name)
            
            # Εμφάνιση κουμπιού επιστροφής πριν το εργαλείο (προαιρετικά)
            if st.button("⬅ Back to Control Tower"):
                st.session_state.flow_step = "home"
                st.session_state.selected_tool = None
                st.rerun()
            
            st.divider()
            # Εκτέλεση εργαλείου
            func()

        except Exception as e:
            st.error(f"❌ Critical Error loading tool '{module_name}': {e}")
            if st.button("Return Home"):
                st.session_state.flow_step = "home"
                st.rerun()
    else:
        st.session_state.flow_step = "home"
        st.rerun()

else:
    # Fail-safe επιστροφή στην αρχική
    st.session_state.flow_step = "home"
    st.rerun()
