import streamlit as st
from core.sync import lock_baseline, sync_global_state

def run_stage0():
    st.header("🏗️ Stage 0: Strategic Baseline Setup")
    st.write("Fill in your core business data below. The sidebar will update automatically.")
    st.divider()

    # --- BLOCK 1: REVENUE & VOLUME ---
    st.subheader("📊 Sales & Pricing")
    c1, c2 = st.columns(2)
    
    # Ενημερώνουμε απευθείας το session_state
    st.session_state.price = c1.number_input(
        "Unit Sales Price (€)", 
        value=float(st.session_state.get('price', 100.0)),
        key="main_price"
    )
    st.session_state.volume = c2.number_input(
        "Planned Annual Volume (Units)", 
        value=int(st.session_state.get('volume', 1000)),
        key="main_volume"
    )

    # --- BLOCK 2: COST ANALYSIS ---
    st.subheader("💰 Cost Structure")
    col_a, col_b = st.columns(2)
    
    with col_a:
        st.markdown("**Variable Costs**")
        raw_mat = st.number_input("Raw Materials (€/unit)", value=float(st.session_state.get('raw_mat', 30.0)))
        labor = st.number_input("Direct Labor (€/unit)", value=float(st.session_state.get('labor', 15.0)))
        ship = st.number_input("Shipping/Other (€/unit)", value=float(st.session_state.get('ship', 5.0)))
        
        # Υπολογισμός και ενημέρωση Sidebar
        total_vc = raw_mat + labor + ship
        st.session_state.variable_cost = total_vc
        st.session_state.raw_mat = raw_mat
        st.session_state.labor = labor
        st.session_state.ship = ship
        st.info(f"Total Variable Cost: **€{total_vc:,.2f}**")

    with col_b:
        st.markdown("**Fixed Costs (Annual)**")
        rent = st.number_input("Rent & Utilities (Annual)", value=float(st.session_state.get('rent_ann', 12000.0)))
        salaries = st.number_input("Admin Salaries (Annual)", value=float(st.session_state.get('sal_ann', 8000.0)))
        
        # Υπολογισμός και ενημέρωση Sidebar
        total_fc = rent + salaries
        st.session_state.fixed_cost = total_fc
        st.session_state.rent_ann = rent
        st.session_state.sal_ann = salaries
        st.info(f"Total Fixed Costs: **€{total_fc:,.2f}**")

    

    # --- BLOCK 3: ADVANCED TOOLS REDIRECT ---
    st.divider()
    st.subheader("⚙️ Advanced Parameters")
    st.write("For Capital Structure (WACC), Taxes, or Working Capital Days, use the specialized tool:")
    
    if st.button("🔧 Open Advanced Capital & WC Tool"):
        # Εδώ τον στέλνουμε στη βιβλιοθήκη ή αλλάζουμε το flow
        st.session_state.flow_step = "library" 
        st.rerun()

    # --- FINAL LOCK ---
    st.divider()
    st.subheader("✅ Finalize Baseline")
    
    # Έλεγχος Margin
    if st.session_state.price <= st.session_state.variable_cost:
        st.error("⚠️ Negative Margin! Check your Price vs Variable Costs.")
    else:
        if st.button("🔒 Lock Data & Initialize Engine", use_container_width=True):
            lock_baseline()
            st.session_state.flow_step = "stage1"
            st.rerun()

    if st.session_state.get('baseline_locked', False):
        st.success("System Status: **LOCKED & READY**")
        if st.button("Reset Baseline"):
            st.session_state.baseline_locked = False
            if 'baseline' in st.session_state: del st.session_state.baseline
            st.rerun()
