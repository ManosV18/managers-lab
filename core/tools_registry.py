import streamlit as st
import importlib.util
import os
import sys

# --- INTERNAL TOOL: PAYABLES MANAGER (Backup) ---
def show_payables_manager_internal():
    st.header("🤝 Payables Manager (Internal Mode)")
    s = st.session_state
    
    # Λήψη δεδομένων από το Home
    v = float(s.get("input_volume", 1000))
    vc = float(s.get("input_vc", 60.0))
    
    col1, col2 = st.columns(2)
    with col1:
        cred_days = st.number_input("Supplier Credit Period (Days)", value=60, key="int_days")
        disc_prc = st.number_input("Cash Discount Offered (%)", value=2.0, key="int_disc") / 100
    with col2:
        annual_purch = st.number_input("Annual Purchase Volume (€)", value=v * vc, key="int_purch")
        wacc = st.number_input("WACC (%)", value=15.0, key="int_wacc") / 100

    # Υπολογισμός 365 ημέρες [2026-02-18]
    disc_gain = annual_purch * 0.5 * disc_prc
    opp_cost = (annual_purch * 0.5 * (cred_days / 365)) * wacc
    net_benefit = disc_gain - opp_cost

    st.divider()
    st.metric("Net Financial Benefit", f"€{net_benefit:,.0f}")

# --- UNIVERSAL LOADER ---
def show_library():
    if st.session_state.get('selected_tool') is None:
        st.session_state.flow_step = "home"
        st.rerun()

    if st.button("⬅️ Back to Main Dashboard"):
        st.session_state.selected_tool = None
        st.session_state.flow_step = "home"
        st.rerun()
    
    st.divider()

    mod_name, func_name = st.session_state.selected_tool
    
    if mod_name == "INTERNAL":
        show_payables_manager_internal()
    else:
        try:
            # ΑΠΟΛΥΤΟ PATH ΓΙΑ ΝΑ ΒΡΕΙ ΤΟΝ ΦΑΚΕΛΟ /tools/
            # Ανεβαίνει ένα επίπεδο πάνω από το core/
            current_dir = os.path.dirname(os.path.abspath(__file__))
            project_root = os.path.dirname(current_dir) 
            file_path = os.path.join(project_root, "tools", f"{mod_name}.py")
            
            if os.path.exists(file_path):
                spec = importlib.util.spec_from_file_location(mod_name, file_path)
                module = importlib.util.module_from_spec(spec)
                sys.modules[mod_name] = module
                spec.loader.exec_module(module)
                
                # Κλήση συνάρτησης
                func = getattr(module, func_name)
                func()
            else:
                st.error(f"❌ File Not Found: {file_path}")
                st.info("Check if the file is in the 'tools' folder at the root of your project.")
                if st.button("Run Internal Diagnostic"):
                    show_payables_manager_internal()
                    
        except Exception as e:
            st.error(f"❌ System Error: {e}")
