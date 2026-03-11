import streamlit as st
import importlib
import os
import sys

# 1. ΠΡΟΣΘΗΚΗ ΤΟΥ PROJECT ROOT ΣΤΟ SYSTEM PATH
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
if project_root not in sys.path:
    sys.path.append(project_root)

def show_library():
    s = st.session_state
    
    if s.get('selected_tool') is None:
        s.flow_step = "home"
        st.rerun()

    if st.button("⬅️ Back to Main Dashboard"):
        s.selected_tool = None
        s.flow_step = "home"
        st.rerun()
    
    st.divider()

    mod_name, func_name = s.selected_tool
    
    try:
        # Προσπάθεια άμεσης εισαγωγής από τον φάκελο tools
        # Χρησιμοποιούμε το format: tools.όνομα_αρχείου
        full_module_path = f"tools.{mod_name}"
        
        # Reload για να βλέπει τις αλλαγές αν αλλάξεις κάτι στο .py
        if full_module_path in sys.modules:
            module = importlib.reload(sys.modules[full_module_path])
        else:
            module = importlib.import_module(full_module_path)
        
        # Εκτέλεση της συνάρτησης
        if hasattr(module, func_name):
            func = getattr(module, func_name)
            func()
        else:
            st.error(f"Function '{func_name}' not found in '{mod_name}.py'")

    except ModuleNotFoundError:
        st.error(f"❌ Could not find 'tools/{mod_name}.py'")
        st.info(f"Looking in: {os.path.join(project_root, 'tools')}")
        # FALLBACK ΣΤΟ ΕΣΩΤΕΡΙΚΟ ΓΙΑ ΝΑ ΜΗ ΜΕΙΝΕΙΣ ΜΕ ΑΔΕΙΑ ΟΘΟΝΗ
        show_payables_manager_internal()
        
    except Exception as e:
        st.error(f"❌ Error: {e}")

def show_payables_manager_internal():
    st.header("🤝 Payables Manager (Emergency Internal Mode)")
    s = st.session_state
    v = float(s.get("input_volume", 1000))
    vc = float(s.get("input_vc", 60.0))
    
    col1, col2 = st.columns(2)
    with col1:
        cred_days = st.number_input("Credit Days", value=60, key="err_days")
        disc = st.number_input("Discount %", value=2.0, key="err_disc") / 100
    with col2:
        purch = st.number_input("Purchases €", value=v*vc, key="err_purch")
        wacc = st.number_input("WACC %", value=15.0, key="err_wacc") / 100

    benefit = (purch * 0.5 * disc) - (purch * 0.5 * (cred_days/365) * wacc)
    st.metric("Net Benefit", f"€{benefit:,.0f}")
