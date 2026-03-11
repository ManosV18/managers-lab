import streamlit as st
import importlib.util
import os
import sys

# =========================================================
# 🛠️ INTERNAL DIAGNOSTIC TOOL (Safe & Silent)
# =========================================================
def show_payables_manager_internal():
    st.header("🤝 Payables Manager (Internal Mode)")
    
    s = st.session_state
    
    # Auto-initialize values to avoid zeros
    v = s.get("volume", 1000) if s.get("volume", 0) > 0 else 1000
    vc = s.get("variable_cost", 60.0) if s.get("variable_cost", 0) > 0 else 60.0
    calculated_purchases = float(v) * float(vc)
    
    col1, col2 = st.columns(2)
    with col1:
        cred_days = st.number_input("Supplier Credit Period (Days)", value=60, key="diag_days")
        disc_prc = st.number_input("Cash Discount Offered (%)", value=2.0, key="diag_disc") / 100

    with col2:
        annual_purch = st.number_input("Annual Purchases (€)", value=calculated_purchases, key="diag_purch")
        wacc = st.number_input("Cost of Capital - WACC (%)", value=15.0, key="diag_wacc") / 100

    # Logic based on 365 days [2026-02-18]
    disc_gain = annual_purch * disc_prc
    opp_cost = (annual_purch * (cred_days / 365)) * wacc
    net_benefit = disc_gain - opp_cost

    st.divider()
    res1, res2 = st.columns(2)
    res1.metric("Gross Discount Gain", f"€{disc_gain:,.0f}")
    res2.metric("Net Financial Benefit", f"€{net_benefit:,.0f}")

# =========================================================
# 🚀 DYNAMIC LOADER (Silent & Direct)
# =========================================================
def show_library():
    if st.session_state.get("selected_tool") is None:
        st.session_state.flow_step = "home"
        st.rerun()

    # Minimal Navigation
    if st.button("⬅️ Return to Dashboard"):
        st.session_state.selected_tool = None
        st.session_state.flow_step = "home"
        st.rerun()

    st.divider()

    mod_name, func_name = st.session_state.selected_tool

    # Internal Route
    if mod_name == "INTERNAL":
        show_payables_manager_internal()
        return

    # External File Route
    try:
        current_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.abspath(os.path.join(current_dir, ".."))
        file_path = os.path.join(project_root, "tools", f"{mod_name}.py")

        if os.path.exists(file_path):
            spec = importlib.util.spec_from_file_location(mod_name, file_path)
            module = importlib.util.module_from_spec(spec)
            sys.modules[mod_name] = module
            spec.loader.exec_module(module)
            
            # Execute tool function
            func = getattr(module, func_name)
            func()
        else:
            # Silent fallback to internal if file is missing
            show_payables_manager_internal()

    except Exception as e:
        # Only show error if tool exists but has syntax issues
        st.error(f"Module Loading Error: {e}")
        if st.button("Run Internal Diagnostic"):
            show_payables_manager_internal()
