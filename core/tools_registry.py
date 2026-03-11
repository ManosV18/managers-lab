import streamlit as st
import importlib.util
import os
import sys

# =========================================================
# 🛠️ INTERNAL DIAGNOSTIC TOOL (Ο "ΜΑΡΤΥΡΑΣ" ΛΕΙΤΟΥΡΓΙΑΣ)
# =========================================================
def show_payables_manager_internal():
    """
    Αυτό το εργαλείο είναι εσωτερικό (Hardcoded). 
    Αν αυτό εμφανίζεται και λειτουργεί, σημαίνει ότι το 
    Session State και ο Router δουλεύουν σωστά.
    """
    st.warning("⚠️ MODE: Internal Diagnostic (Safety Net)")
    st.header("🤝 Payables Manager: Diagnostic Version")
    
    # Λήψη δεδομένων από το Global State (Αμφίδρομη κίνηση)
    s = st.session_state
    
    # Υπολογισμός ετήσιων αγορών βάσει των Global Parameters
    # Volume * Variable Cost
    calculated_purchases = float(s.get("volume", 0)) * float(s.get("variable_cost", 0))
    
    col1, col2 = st.columns(2)
    with col1:
        st.info(f"Base Volume: {s.get('volume', 0)} units")
        cred_days = st.number_input("Supplier Credit Period (Days)", value=60, key="diag_days")
        disc_prc = st.number_input("Cash Discount Offered (%)", value=2.0, key="diag_disc") / 100

    with col2:
        annual_purch = st.number_input("Annual Purchases (€)", value=calculated_purchases, key="diag_purch")
        wacc = st.number_input("WACC (%)", value=float(s.get('wacc', 0.15))*100, key="diag_wacc") / 100

    # Cold Analytical Logic (365 days) - Instruction [2026-02-18]
    disc_gain = annual_purch * disc_prc
    opp_cost = (annual_purch * (cred_days / 365)) * wacc
    net_benefit = disc_gain - opp_cost

    st.divider()
    res1, res2 = st.columns(2)
    res1.metric("Gross Discount Gain", f"€{disc_gain:,.0f}")
    res2.metric("Net Financial Benefit", f"€{net_benefit:,.0f}", 
                delta="Profitable" if net_benefit > 0 else "Loss-making",
                delta_color="normal" if net_benefit > 0 else "inverse")

# =========================================================
# 🚀 DYNAMIC LOADER & ROUTER
# =========================================================
def show_library():
    # Έλεγχος αν υπάρχει επιλεγμένο εργαλείο
    if st.session_state.get("selected_tool") is None:
        st.session_state.flow_step = "home"
        st.rerun()

    # Ενιαίο κουμπί επιστροφής για όλα τα εργαλεία
    if st.button("⬅️ Back to Control Tower", type="primary"):
        st.session_state.selected_tool = None
        st.session_state.flow_step = "home"
        st.rerun()

    st.divider()

    mod_name, func_name = st.session_state.selected_tool

    # ΕΛΕΓΧΟΣ: Αν το εργαλείο είναι το εσωτερικό διαγνωστικό
    if mod_name == "INTERNAL" or mod_name == "payables_manager_internal":
        show_payables_manager_internal()
        return

    # ΑΛΛΙΩΣ: Προσπάθεια δυναμικής φόρτωσης εξωτερικού αρχείου
    try:
        # Εύρεση του φακέλου /tools στην ιεραρχία του project
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        file_path = os.path.join(project_root, "tools", f"{mod_name}.py")

        if os.path.exists(file_path):
            spec = importlib.util.spec_from_file_location(mod_name, file_path)
            module = importlib.util.module_from_spec(spec)
            sys.modules[mod_name] = module
            spec.loader.exec_module(module)
            
            # Εκτέλεση της συνάρτησης
            func = getattr(module, func_name)
            func()
        else:
            st.error(f"❌ Το αρχείο '{mod_name}.py' δεν βρέθηκε στον φάκελο /tools.")
            st.info("💡 Δοκιμάστε το εσωτερικό Payables Manager για να βεβαιωθείτε ότι το σύστημα λειτουργεί.")
            if st.button("Run Internal Diagnostic"):
                st.session_state.selected_tool = ("INTERNAL", "show_payables_manager_internal")
                st.rerun()

    except Exception as e:
        st.error(f"❌ Σφάλμα κατά τη φόρτωση του εργαλείου: {e}")
        st.warning("Switching to Diagnostic Mode...")
        show_payables_manager_internal()
