import streamlit as st
import importlib.util
import os
import sys

# --- INTERNAL TOOLS (Εργαλεία που ζουν μέσα στο registry) ---

def show_payables_manager_internal():
    st.header("🤝 Payables Manager: Supplier Credit Analysis")
    
    # Λήψη δεδομένων από το Global State (Αμφίδρομη κίνηση)
    s = st.session_state
    base_purchases = s.get("volume", 1000) * s.get("variable_cost", 60.0)
    base_wacc = s.get("wacc", 0.10)

    col1, col2 = st.columns(2)
    with col1:
        cred_days = st.number_input("Supplier Credit Period (Days)", value=60, key="int_cred_days")
        disc_prc = st.number_input("Cash Discount Offered (%)", value=2.0, key="int_disc_prc") / 100
        cash_take = st.number_input("% of Purchases for Discount", value=50.0, key="int_cash_prc") / 100

    with col2:
        annual_purch = st.number_input("Annual Purchase Volume (€)", value=float(base_purchases), key="int_ann_purch")
        wacc = st.number_input("Cost of Capital (%)", value=float(base_wacc * 100), key="int_wacc_w") / 100

    # Cold Analytical Logic (365 days) - [2026-02-18]
    disc_gain = annual_purch * disc_prc * cash_take
    opp_cost = (annual_purch * cash_take * (cred_days / 365)) * wacc
    net_benefit = disc_gain - opp_cost

    st.divider()
    c1, c2, c3 = st.columns(3)
    c1.metric("Discount Gain", f"€{disc_gain:,.0f}")
    c2.metric("Credit Opportunity Cost", f"-€{opp_cost:,.0f}")
    c3.metric("Net Benefit", f"€{net_benefit:,.0f}", delta=f"{'Accept' if net_benefit > 0 else 'Reject'}")

# --- TOOL LOADER (Ο "Τροχονόμος" των εργαλείων) ---

def show_library():
    # 1. Έλεγχος αν υπάρχει επιλεγμένο εργαλείο
    if st.session_state.get("selected_tool") is None:
        st.session_state.flow_step = "home"
        st.rerun()

    # 2. Navigation Bar
    col_nav1, col_nav2 = st.columns([0.8, 0.2])
    with col_nav2:
        if st.button("⬅ Home", type="primary", use_container_width=True):
            st.session_state.selected_tool = None
            st.session_state.flow_step = "home"
            st.rerun()

    st.divider()

    # 3. Dynamic Loading Logic
    tool_info = st.session_state.selected_tool
    mod_name, func_name = tool_info

    # Περίπτωση Internal Tool
    if mod_name == "INTERNAL":
        if func_name == "show_payables_manager_internal":
            show_payables_manager_internal()
    
    # Περίπτωση Εξωτερικού Αρχείου (Φάκελος /tools)
    else:
        try:
            # Διόρθωση Path: Πηγαίνουμε στον κεντρικό φάκελο του project
            project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            file_path = os.path.join(project_root, "tools", f"{mod_name}.py")

            if not os.path.exists(file_path):
                st.error(f"🚨 File not found: {file_path}")
                return

            spec = importlib.util.spec_from_file_location(mod_name, file_path)
            module = importlib.util.module_from_spec(spec)
            sys.modules[mod_name] = module
            spec.loader.exec_module(module)
            
            # Εκτέλεση της συνάρτησης του εργαλείου
            func = getattr(module, func_name)
            func()

        except Exception as e:
            st.error(f"❌ Error loading tool '{mod_name}': {e}")
            if st.button("Emergency Back to Home"):
                st.session_state.selected_tool = None
                st.session_state.flow_step = "home"
                st.rerun()
