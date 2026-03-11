import streamlit as st
import importlib.util
import os
import sys

# --- INTERNAL TOOL (Backup) ---
def show_payables_manager_internal():
    st.header("🤝 Payables Manager (Internal Mode)")
    s = st.session_state
    
    # Χρήση των τιμών από το Home (input_volume, input_vc)
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

# --- MAIN LIBRARY FUNCTION ---
def show_library():
    s = st.session_state
    
    if s.get('selected_tool') is None:
        s.flow_step = "home"
        st.rerun()

    if st.button("⬅️ Return to Main Dashboard", type="primary"):
        s.selected_tool = None
        s.flow_step = "home"
        st.rerun()
    
    st.divider()

    mod_name, func_name = s.selected_tool
    
    # Αν το κουμπί στέλνει "INTERNAL", τρέξε το εσωτερικό
    if mod_name == "INTERNAL":
        show_payables_manager_internal()
        return

    try:
        # ΕΠΙΣΤΡΟΦΗ ΣΤΟ PATH ΤΟΥ ΠΡΩΙΝΟΥ:
        # Ψάχνει στον φάκελο core/tools/ (εκεί που το είχες το πρωί)
        current_dir = os.path.dirname(os.path.abspath(__file__))
        file_path = os.path.join(current_dir, "tools", f"{mod_name}.py")
        
        # Αν δεν το βρει εκεί, ψάχνει στον κεντρικό φάκελο tools/
        if not os.path.exists(file_path):
            project_root = os.path.dirname(current_dir)
            file_path = os.path.join(project_root, "tools", f"{mod_name}.py")

        spec = importlib.util.spec_from_file_location(mod_name, file_path)
        module = importlib.util.module_from_spec(spec)
        sys.modules[mod_name] = module
        spec.loader.exec_module(module)
        
        # Εκτέλεση
        getattr(module, func_name)()
        
    except Exception as e:
        st.error(f"❌ Error loading tool: {e}")
        st.info("Falling back to internal tool...")
        show_payables_manager_internal()
