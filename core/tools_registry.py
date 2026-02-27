import streamlit as st
import importlib

# --- INTERNAL TOOL: PAYABLES MANAGER ---
def show_payables_manager_internal():
    st.header("🤝 Payables Manager: Supplier Credit Analysis")
    st.info("Evaluate cash discounts vs. supplier credit terms (365-day basis).")
    
    col1, col2 = st.columns(2)
    with col1:
        cred_days = st.number_input("Supplier Credit Period (Days)", value=60, key="int_cred_days")
        disc_prc = st.number_input("Cash Discount Offered (%)", value=2.0, key="int_disc_prc") / 100
        cash_take = st.number_input("% of Purchases for Discount", value=50.0, key="int_cash_prc") / 100
    with col2:
        annual_purch = st.number_input("Annual Purchase Volume (€)", value=1000000, key="int_ann_purch")
        wacc = st.number_input("Cost of Capital / Interest (%)", value=10.0, key="int_wacc") / 100

    # Calculation based on instruction [2026-02-18]
    disc_gain = annual_purch * disc_prc * cash_take
    opp_cost = (annual_purch * cash_take * (cred_days / 365)) * wacc
    net_benefit = disc_gain - opp_cost

    st.divider()
    c1, c2, c3 = st.columns(3)
    c1.metric("Discount Gain", f"€{disc_gain:,.0f}")
    c2.metric("Credit Opp. Cost", f"-€{opp_cost:,.0f}")
    c3.metric("Net Benefit", f"€{net_benefit:,.0f}", delta=f"{net_benefit:,.0f}")

    if st.button("⬅️ Back to Library Hub", key="back_from_internal"):
        st.session_state.selected_tool = None
        st.rerun()

# --- MAIN LIBRARY FUNCTION ---
def show_library():
    if st.sidebar.button("🏠 Exit Library", key="exit_lib"):
        st.session_state.flow_step = "home"
        st.session_state.selected_tool = None
        st.rerun()

    st.title("🏛️ Strategic Tool Library")

    if st.session_state.get('selected_tool') is None:
        t1, t2, t3, t4 = st.tabs(["🚀 Strategy", "💰 Finance", "⚙️ Operations", "🛡️ Risk"])
        
        with t1:
            if st.button("👥 CLV Simulator", use_container_width=True, key="btn_clv"):
                st.session_state.selected_tool = ("clv_calculator", "show_clv_calculator")
                st.rerun()
        
        with t3:
            if st.button("📊 Receivables Analyzer", use_container_width=True, key="btn_receivables"):
                st.session_state.selected_tool = ("receivables_analyzer", "show_receivables_analyzer_ui")
                st.rerun()
            if st.button("📦 Inventory Optimizer", use_container_width=True, key="btn_inv"):
                st.session_state.selected_tool = ("inventory_manager", "show_inventory_manager")
                st.rerun()
            if st.button("🤝 Payables Manager", use_container_width=True, key="btn_payables"):
                st.session_state.selected_tool = ("INTERNAL", "show_payables_manager_internal")
                st.rerun()

    else:
        mod_name, func_name = st.session_state.selected_tool
        
        if mod_name != "INTERNAL":
            if st.button("⬅️ Back to Library Hub", key="global_back"):
                st.session_state.selected_tool = None
                st.rerun()
            st.divider()

        if mod_name == "INTERNAL":
            globals()[func_name]()
        else:
            try:
                # Εδώ καλούμε τα εργαλεία από τον ΦΑΚΕΛΟ core/tools/
                module = importlib.import_module(f"core.tools.{mod_name}")
                importlib.reload(module)
                tool_func = getattr(module, func_name)
                tool_func()
            except Exception as e:
                st.error(f"❌ Error loading tool: {e}")
                if st.button("Reset Selection"):
                    st.session_state.selected_tool = None
                    st.rerun()
