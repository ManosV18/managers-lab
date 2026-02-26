import streamlit as st
from core.sync import lock_baseline, sync_global_state

def run_stage0():
    st.header("🏗️ Stage 0: Baseline Configuration")
    st.caption("Strategic Phase: Establishing core parameters and initializing the analytical engine.")
    st.divider()

    # 1. ANALYSIS METHOD SELECTION
    input_method = st.radio(
        "Choose Data Entry Method:", 
        ["Quick Entry (Sidebar)", "🧪 Professional Cost Analyzer"],
        horizontal=True
    )

    if input_method == "🧪 Professional Cost Analyzer":
        # VARIABLE COST ANALYZER
        st.subheader("1. Variable Cost Breakdown")
        with st.container(border=True):
            v_col1, v_col2 = st.columns(2)
            raw_mat = v_col1.number_input("Raw Materials (€/unit)", min_value=0.0, value=float(st.session_state.get('raw_mat', 30.0)))
            labor = v_col2.number_input("Direct Labor (€/unit)", min_value=0.0, value=float(st.session_state.get('labor', 15.0)))
            shipping = v_col1.number_input("Logistics (€/unit)", min_value=0.0, value=float(st.session_state.get('shipping', 5.0)))
            
            calc_vc = raw_mat + labor + shipping
            st.session_state.variable_cost = calc_vc  # Updates Sidebar
            st.info(f"**Total Variable Cost:** €{calc_vc:,.2f}")

        # FIXED COST ANALYZER
        st.subheader("2. Annual Fixed Cost Breakdown")
        with st.container(border=True):
            f_col1, f_col2 = st.columns(2)
            rent = f_col1.number_input("Monthly Rent (€)", min_value=0.0, value=1000.0) * 12
            salaries = f_col2.number_input("Annual Admin Salaries (€)", min_value=0.0, value=10000.0)
            marketing = f_col1.number_input("Annual Marketing Spend (€)", min_value=0.0, value=2000.0)
            
            calc_fixed = rent + salaries + marketing
            st.session_state.fixed_cost = calc_fixed  # Updates Sidebar
            st.info(f"**Total Fixed Costs:** €{calc_fixed:,.2f} / year")
    else:
        st.info("ℹ️ Using manual values currently defined in the Sidebar.")

    st.divider()

    # 2. DATA VERIFICATION
    st.subheader("System Preview")
    # Τρέχουμε το sync_global_state για να δούμε αν η engine "ακούει"
    current_metrics = sync_global_state()
    
    if current_metrics:
        c1, c2, c3 = st.columns(3)
        c1.metric("Unit Price", f"€{st.session_state.get('price', 0.0):,.2f}")
        c2.metric("Variable Cost", f"€{st.session_state.get('variable_cost', 0.0):,.2f}")
        c3.metric("Fixed Costs", f"€{st.session_state.get('fixed_cost', 0.0):,.2f}")

    

    # 3. LOCKING LOGIC (Using your specific lock_baseline)
    st.write("---")
    if st.session_state.get('baseline_locked', False):
        st.success("✅ Baseline is already locked. You can proceed to Stage 1.")
        if st.button("Go to Stage 1 ➡️", use_container_width=True):
            st.session_state.flow_step = "stage1"
            st.rerun()
    else:
        if st.button("🔒 Lock Baseline & Initialize Engine", use_container_width=True):
            if st.session_state.get('price', 0) > st.session_state.get('variable_cost', 0):
                lock_baseline() # Αυτό καλεί τη δική σου συνάρτηση που φτιάχνει το 'baseline' στο session_state
                st.session_state.flow_step = "stage1"
                st.rerun()
            else:
                st.error("Cannot lock baseline with negative margin (Price <= Variable Cost).")

    # OPTIONAL: RESET BUTTON
    if st.session_state.get('baseline_locked', False):
        if st.button("🔓 Unlock to Edit Baseline", type="secondary"):
            del st.session_state.baseline
            st.session_state.baseline_locked = False
            st.rerun()
