import streamlit as st
from core.sync import sync_global_state, lock_baseline

def run_stage0():
    st.title("🎯 Stage 0: Structural Baseline")
    
    # 1. FETCH DATA (Ασφαλής ανάκτηση)
    m = sync_global_state()
    s = st.session_state

    # Χρήση .get() για να αποφύγουμε το AttributeError
    price = s.get('price', 0.0)
    v_cost = s.get('variable_cost', 0.0)
    f_cost = s.get('fixed_cost', 0.0)
    loan = s.get('annual_loan_payment', 0.0)
    volume = s.get('volume', 0)
    ar_days = s.get('ar_days', 0)
    inv_days = s.get('inventory_days', 0)
    ap_days = s.get('ap_days', 0)

    st.markdown("""
    Define the fundamental economic engine of your business. 
    This setup creates the **Control Snapshot** used for all future stress tests.
    """)

    # 2. EXECUTIVE SUMMARY
    unit_contribution = price - v_cost
    is_non_viable = unit_contribution <= 0
    
    st.subheader("Current Economic Profile")
    c1, c2, c3 = st.columns(3)
    
    c1.metric("Unit Contribution", f"{unit_contribution:,.2f} €", help="Price minus Variable Cost")
    c2.metric("Annual Fixed Load", f"{(f_cost + loan):,.0f} €", help="Fixed Costs + Debt Service")
    c3.metric("Break-Even Units", f"{m.get('survival_bep', 0):,.0f}", help="Units needed to cover EVERYTHING")

    # 3. VIABILITY CHECK
    if is_non_viable:
        st.error("🚨 **STRUCTURAL ERROR:** Variable costs exceed price. Correct the Baseline in the sidebar to proceed.")
    else:
        st.success("✅ **VIABILITY CONFIRMED:** The unit economics allow for potential profit.")

    # 4. DATA VALIDATION TABLE
    st.subheader("Structural Inputs")
    data = {
        "Parameter": ["Volume", "Price", "Variable Cost", "Fixed Cost", "Debt Service", "AR Days", "Inv. Days", "AP Days"],
        "Current Value": [
            f"{volume:,}", 
            f"{price:,.2f} €", 
            f"{v_cost:,.2f} €", 
            f"{f_cost:,.0f} €", 
            f"{loan:,.0f} €",
            f"{ar_days} days", 
            f"{inv_days} days", 
            f"{ap_days} days"
        ]
    }
    st.table(data)
    
    # 5. LOCKING MECHANISM
    st.divider()
    st.warning("Once you lock the baseline, these parameters will be saved as the 'Healthy State' for comparison.")
    
    col_lock, col_next = st.columns(2)

    with col_lock:
        if st.button("🔒 Lock Baseline & Sync", use_container_width=True, type="primary", disabled=is_non_viable):
            lock_baseline()
            # ΑΥΤΗ Η ΓΡΑΜΜΗ ΕΙΝΑΙ ΤΟ ΚΛΕΙΔΙ:
            st.session_state.baseline_locked = True 
            st.success("✅ Baseline Secured! You can now use the Library.")

    with col_next:
        if st.button("Next: Strategic Diagnostic ➡️", use_container_width=True):
            # Εξασφαλίζουμε ότι αν προχωρήσει, θεωρείται κλειδωμένο
            st.session_state.baseline_locked = True 
            st.session_state.mode = "path"
            st.session_state.flow_step = "stage1"
            st.rerun()

    # 6. RESET OPTION
    if st.button("Reset All Data", type="secondary"):
        st.session_state.clear()
        st.rerun()
