import streamlit as st
import importlib.util
import os
import sys


# INTERNAL TOOL
def show_payables_manager_internal():

    st.header("🤝 Payables Manager: Supplier Credit Analysis")

    col1, col2 = st.columns(2)

    with col1:
        cred_days = st.number_input("Supplier Credit Period (Days)", value=60, key="int_cred_days")
        disc_prc = st.number_input("Cash Discount Offered (%)", value=2.0, key="int_disc_prc") / 100
        cash_take = st.number_input("% of Purchases for Discount", value=50.0, key="int_cash_prc") / 100

    with col2:
        annual_purch = st.number_input("Annual Purchase Volume (€)", value=1000000, key="int_ann_purch")
        wacc = st.number_input("Cost of Capital (%)", value=10.0, key="int_wacc") / 100

    disc_gain = annual_purch * disc_prc * cash_take
    opp_cost = (annual_purch * cash_take * (cred_days / 365)) * wacc

    net_benefit = disc_gain - opp_cost

    st.divider()

    c1, c2, c3 = st.columns(3)

    c1.metric("Discount Gain", f"€{disc_gain:,.0f}")
    c2.metric("Credit Opportunity Cost", f"-€{opp_cost:,.0f}")
    c3.metric("Net Benefit", f"€{net_benefit:,.0f}")


# TOOL LOADER
def show_library():

    if st.session_state.get("selected_tool") is None:
        st.session_state.flow_step = "home"
        st.rerun()

    if st.button("⬅ Return to Main Dashboard", type="primary"):
        st.session_state.selected_tool = None
        st.session_state.flow_step = "home"
        st.rerun()

    st.divider()

    mod_name, func_name = st.session_state.selected_tool

    if mod_name == "INTERNAL":
        show_payables_manager_internal()

    else:

        try:

            current_dir = os.path.dirname(os.path.abspath(__file__))

            file_path = os.path.join(current_dir, "tools", f"{mod_name}.py")

            spec = importlib.util.spec_from_file_location(mod_name, file_path)

            if spec is None:
                raise FileNotFoundError(file_path)

            module = importlib.util.module_from_spec(spec)

            sys.modules[mod_name] = module

            spec.loader.exec_module(module)

            getattr(module, func_name)()

        except Exception as e:

            st.error(f"❌ Error loading tool '{mod_name}': {e}")

            if st.button("Emergency Back to Home"):
                st.session_state.selected_tool = None
                st.session_state.flow_step = "home"
                st.rerun()
