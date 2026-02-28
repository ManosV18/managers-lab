import streamlit as st
from core.sync import lock_baseline

def run_stage0():
    st.header("🏗️ Business Setup")
    st.divider()

    # Ορισμός του 's' για να μην βγάζει NameError
    s = st.session_state

    # SECTION 1: REVENUE
    st.subheader("📊 Sales Parameters")
    c1, c2 = st.columns(2)
    # Χρησιμοποιούμε key για αυτόματη αποθήκευση στο session_state
    price = c1.number_input("Unit Price (€)", value=float(s.get('price', 100.0)), key='price')
    volume = c2.number_input("Annual Volume", value=int(s.get('volume', 1000)), key='volume')

    # SECTION 2: COSTS
    st.subheader("💰 Cost Structure Analyzer")
    col_a, col_b = st.columns(2)
    
    with col_a:
        st.markdown("**Variable Costs**")
        v1 = st.number_input("Materials (€/unit)", value=30.0, key='in_mat', format="%.2f")
        v2 = st.number_input("Labor (€/unit)", value=15.0, key='in_lab', format="%.2f")
        # Ενημέρωση του συνολικού VC
        s.variable_cost = v1 + v2
        st.info(f"Total VC: €{s.variable_cost:,.2f}")

    with col_b:
        st.markdown("**Fixed Costs (Annual)**")
        f1 = st.number_input("Annual Rent & Utilities (€)", value=12000.0, key='in_rent', format="%.2f")
        f2 = st.number_input("Annual Salaries & Admin (€)", value=8000.0, key='in_sal', format="%.2f")
        # Ενημέρωση του συνολικού Fixed Cost
        s.fixed_cost = f1 + f2
        st.info(f"Total Fixed: €{s.fixed_cost:,.2f}")
    
    st.divider()
    
    # SECTION 3: FINANCIAL & RISK (Hidden but Important)
    with st.expander("⚙️ Advanced Financial Settings"):
        c1, c2, c3 = st.columns(3)
        # Προσοχή στα κλειδιά (keys) να ταυτίζονται με αυτά που ζητάει η sync_global_state
        c1.number_input("Cost of Capital (WACC %)", value=float(s.get('wacc', 0.15)), key='wacc', format="%.4f")
        c2.number_input("Tax Rate (0.xx)", value=float(s.get('tax_rate', 0.22)), key='tax_rate', format="%.2f")
        c3.number_input("Annual Debt Service (€)", value=float(s.get('annual_debt_service', 0.0)), key='annual_debt_service')

        st.markdown("**Working Capital Assumptions (Days)**")
        d1, d2, d3 = st.columns(3)
        d1.number_input("AR Days", value=int(s.get('ar_days', 45)), key='ar_days')
        d2.number_input("Inventory Days", value=int(s.get('inventory_days', 60)), key='inventory_days')
        d3.number_input("AP Days", value=int(s.get('ap_days', 30)), key='ap_days')

    st.divider()
    
    # LOCK LOGIC
    if st.button("🔒 Lock Baseline & Initialize Engine", use_container_width=True):
        # Έλεγχος περιθωρίου κέρδους
        if s.price > s.variable_cost:
            lock_baseline()
            s.flow_step = "stage1"
            st.rerun()
        else:
            st.error("🚨 Margin Error: Unit Price must be higher than Variable Cost.")
