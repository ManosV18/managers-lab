import streamlit as st
import importlib
import os
import sys
import importlib.util

# ==========================================
# 🛠️ INTERNAL STANDALONE TOOLS
# ==========================================

def show_pricing_standalone():
    st.header("🎯 Strategic Pricing & Elasticity")
    st.info("Simulate how price changes affect demand and total revenue.")
    col1, col2 = st.columns(2)
    with col1:
        p_current = st.number_input("Current Price (€)", value=100.0)
        p_new = st.number_input("Proposed Price (€)", value=110.0)
    with col2:
        v_current = st.number_input("Current Volume (Units)", value=1000)
        elasticity = st.slider("Price Elasticity (Sensitivity)", 0.0, 5.0, 1.5)
    
    price_change = (p_new - p_current) / p_current
    volume_change = -elasticity * price_change
    new_rev = (v_current * (1 + volume_change)) * p_new
    
    st.divider()
    st.metric("Projected Revenue Impact", f"€{new_rev:,.0f}", delta=f"{(new_rev - (p_current*v_current)):,.0f}")
    if st.button("⬅️ Back"): st.session_state.selected_tool = None; st.rerun()

def show_loan_vs_leasing_standalone():
    st.header("⚖️ Capital Acquisition: Loan vs Leasing")
    tax_rate = float(st.session_state.get('tax_rate', 22.0)) / 100
    st.caption(f"Tax Shield calculated at {tax_rate:.0%}")
    col1, col2 = st.columns(2)
    with col1:
        asset_val = st.number_input("Asset Value (€)", value=50000)
        loan_rate = st.number_input("Loan Interest (%)", value=6.5) / 100
    with col2:
        lease_pmt = st.number_input("Monthly Lease (€)", value=1100)
        months = st.number_input("Duration (Months)", value=48)
    
    loan_cost = (asset_val + (asset_val * loan_rate * (months/12))) * (1 - (loan_rate * tax_rate))
    lease_cost = (lease_pmt * months) * (1 - tax_rate)
    
    st.divider()
    c1, c2 = st.columns(2)
    c1.metric("Net Loan Cost (Post-Tax)", f"€{loan_cost:,.0f}")
    c2.metric("Net Lease Cost (Post-Tax)", f"€{lease_cost:,.0f}")
    if st.button("⬅️ Back"): st.session_state.selected_tool = None; st.rerun()

# ==========================================
# 🏛️ MAIN LIBRARY HUB
# ==========================================

def show_library():
    if st.sidebar.button("🏠 Exit Library"):
        st.session_state.flow_step = "home"
        st.session_state.selected_tool = None
        st.rerun()

    st.title("🏛️ Strategic Tool Library")
    st.markdown("---")

    if st.session_state.get('selected_tool') is None:
        # ΚΑΤΗΓΟΡΙΕΣ ΜΕ ΛΟΓΙΚΗ ΣΕΙΡΑ ΡΟΗΣ
        tabs = st.tabs([
            "🎯 Growth & Strategy", 
            "💰 Financial Engineering", 
            "⚙️ Operational Efficiency", 
            "🛡️ Risk & Resilience"
        ])
        
        # TAB 1: Ανάπτυξη και Στρατηγική (Πώς βγάζω λεφτά;)
        with tabs[0]:
            st.subheader("Market & Revenue Strategy")
            if st.button("🎯 Pricing & Elasticity Simulator", use_container_width=True):
                st.session_state.selected_tool = ("INTERNAL", "show_pricing_standalone")
                st.rerun()
            if st.button("⚖️ Break-Even Shift Analysis", use_container_width=True):
                st.session_state.selected_tool = ("break_even_shift_calculator", "show_break_even_shift_calculator")
                st.rerun()
            if st.button("👥 Customer Lifetime Value (CLV)", use_container_width=True):
                st.session_state.selected_tool = ("clv_calculator", "show_clv_calculator")
                st.rerun()

        # TAB 2: Οικονομική Μηχανική (Πώς διαχειρίζομαι το κεφάλαιο;)
        with tabs[1]:
            st.subheader("Capital & Funding Optimization")
            if st.button("⚖️ CAPEX: Loan vs Leasing Analyzer", use_container_width=True):
                st.session_state.selected_tool = ("INTERNAL", "show_loan_vs_leasing_standalone")
                st.rerun()
            if st.button("📉 WACC Optimizer (Cost of Capital)", use_container_width=True):
                st.session_state.selected_tool = ("wacc_optimizer", "show_wacc_optimizer")
                st.rerun()
            if st.button("📈 AFN: Growth Funding Needs", use_container_width=True):
                st.session_state.selected_tool = ("growth_funding", "show_growth_funding_needed")
                st.rerun()

        # TAB 3: Επιχειρησιακή Αποδοτικότητα (Πώς βελτιώνω το Cash Flow;)
        with tabs[2]:
            st.subheader("Working Capital Management")
            if st.button("🔄 Cash Conversion Cycle (CCC)", use_container_width=True):
                st.session_state.selected_tool = ("cash_cycle", "run_cash_cycle_app")
                st.rerun()
            if st.button("📊 Receivables (DSO) Analyzer", use_container_width=True):
                st.session_state.selected_tool = ("receivables_analyzer", "show_receivables_analyzer_ui")
                st.rerun()
            if st.button("📦 Inventory & EOQ Optimizer", use_container_width=True):
                st.session_state.selected_tool = ("inventory_manager", "show_inventory_manager")
                st.rerun()

        # TAB 4: Διαχείριση Κινδύνου (Πώς δεν θα καταρρεύσω;)
        with tabs[3]:
            st.subheader("Survival & Shock Protection")
            if st.button("🛡️ Cash Flow Stress Test", use_container_width=True):
                st.session_state.selected_tool = ("stress_test_simulator", "show_stress_test_simulator")
                st.rerun()
            if st.button("🚨 Cash Fragility Index", use_container_width=True):
                st.session_state.selected_tool = ("cash_fragility_index", "show_cash_fragility_index")
                st.rerun()
            if st.button("🏁 Executive Command Center", use_container_width=True):
                st.session_state.selected_tool = ("executive_dashboard", "show_executive_dashboard")
                st.rerun()

    else:
        # EXECUTION LOGIC (Internal vs External)
        mod_name, func_name = st.session_state.selected_tool
        if mod_name != "INTERNAL":
            if st.button("⬅️ Back to Library Hub"):
                st.session_state.selected_tool = None
                st.rerun()
            st.divider()

        if mod_name == "INTERNAL":
            globals()[func_name]()
        else:
            try:
                current_dir = os.path.dirname(os.path.abspath(__file__))
                file_path = os.path.join(current_dir, "tools", f"{mod_name}.py")
                spec = importlib.util.spec_from_file_location(mod_name, file_path)
                module = importlib.util.module_from_spec(spec)
                sys.modules[mod_name] = module 
                spec.loader.exec_module(module)
                getattr(module, func_name)()
            except Exception as e:
                st.error(f"❌ Error: {e}")
                if st.button("Reset"): st.session_state.selected_tool = None; st.rerun()
