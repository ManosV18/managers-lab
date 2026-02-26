import streamlit as st
from core.sync import lock_baseline

def run_stage0():
    st.header("🏗️ Stage 0: Baseline Configuration")
    st.caption("Strategic Phase: Decomposing cost structures for absolute precision.")
    st.divider()

    # 1. ANALYSIS METHOD
    input_method = st.radio(
        "How would you like to define your baseline data?", 
        ["Quick Entry (Sidebar)", "🧪 Professional Cost Analyzer"],
        horizontal=True
    )

    if input_method == "🧪 Professional Cost Analyzer":
        # --- VARIABLE COST ANALYZER ---
        st.subheader("1. Variable Cost Breakdown")
        with st.container(border=True):
            v_col1, v_col2 = st.columns(2)
            raw_mat = v_col1.number_input("Raw Materials (€/unit)", min_value=0.0, value=float(st.session_state.get('raw_mat', 30.0)))
            labor = v_col2.number_input("Direct Labor (€/unit)", min_value=0.0, value=float(st.session_state.get('labor', 15.0)))
            shipping = v_col1.number_input("Logistics (€/unit)", min_value=0.0, value=float(st.session_state.get('shipping', 5.0)))
            
            calc_vc = raw_mat + labor + shipping
            st.session_state.variable_cost = calc_vc # FORCE SYNC TO SIDEBAR
            st.info(f"**Total Variable Cost:** €{calc_vc:,.2f}")

        # --- FIXED COST ANALYZER ---
        st.subheader("2. Annual Fixed Cost Breakdown")
        with st.container(border=True):
            f_col1, f_col2 = st.columns(2)
            rent = f_col1.number_input("Monthly Rent (€)", min_value=0.0, value=1000.0) * 12
            salaries = f_col2.number_input("Annual Admin Salaries (€)", min_value=0.0, value=10000.0)
            marketing = f_col1.number_input("Annual Marketing Spend (€)", min_value=0.0, value=2000.0)
            
            calc_fixed = rent + salaries + marketing
            st.session_state.fixed_cost = calc_fixed # FORCE SYNC TO SIDEBAR
            st.info(f"**Total Fixed Costs:** €{calc_fixed:,.2f} / year")

    else:
        st.info("ℹ️ Using manual values from the Sidebar.")

    st.divider()

    # 2. FINAL VALIDATION
    st.subheader("Final Verification")
    price = float(st.session_state.get('price', 0.0))
    vc = float(st.session_state.get('variable_cost', 0.0))
    fixed = float(st.session_state.get('fixed_cost', 0.0))
    
    # Επιβεβαίωση Δεδομένων
    c1, c2, c3 = st.columns(3)
    c1.metric("Unit Price", f"€{price:,.2f}")
    c2.metric("Variable Cost", f"€{vc:,.2f}")
    c3.metric("Fixed Costs", f"€{fixed:,.2f}")

    

    # 3. LOCKING LOGIC
    if price <= vc:
        st.error("⚠️ **Logic Error:** Price must be higher than Variable Cost to calculate Break-Even.")
    elif price == 0 or vc == 0:
        st.warning("⚠️ Enter Price and Costs to initialize.")
    else:
        if st.button("🔒 Lock Baseline & Initialize Engine", use_container_width=True):
            lock_baseline()
            st.session_state.flow_step = "stage1"
            st.rerun()
