import streamlit as st
from core.sync import sync_global_state, lock_baseline

def run_stage0():
    st.title("🎯 Stage 0: Structural Baseline")
    
    # 1. FETCH DATA (Ενοποιημένος συγχρονισμός)
    # Καλούμε το sync και παίρνουμε τα αποτελέσματα σε μια μεταβλητή 'm'
    m = sync_global_state()
    s = st.session_state

    st.markdown("""
    Define the fundamental economic engine of your business. 
    This setup creates the **Control Snapshot** used for all future stress tests.
    """)

    # 2. EXECUTIVE SUMMARY (Υπολογισμένα επί τόπου για απόλυτη ακρίβεια)
    unit_contribution = s.price - s.variable_cost
    is_non_viable = unit_contribution <= 0
    
    st.subheader("Current Economic Profile")
    c1, c2, c3 = st.columns(3)
    
    c1.metric("Unit Contribution", f"{unit_contribution:,.2f} €", help="Price minus Variable Cost")
    c2.metric("Annual Fixed Load", f"{(s.fixed_cost + s.annual_loan_payment):,.0f} €", help="Fixed Costs + Debt Service")
    c3.metric("Break-Even Units", f"{m['survival_bep']:,.0f}", help="Units needed to cover EVERYTHING")

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
            f"{s.volume:,}", f"{s.price:,.2f} €", f"{s.variable_cost:,.2f} €", 
            f"{s.fixed_cost:,.0f} €", f"{s.annual_loan_payment:,.0f} €",
            f"{s.ar_days} days", f"{s.inventory_days} days", f"{s.ap_days} days"
        ]
    }
    st.table(data)

    # 5. LOCKING MECHANISM
    st.divider()
    st.warning("Once you lock the baseline, these parameters will be saved as the 'Healthy State' for comparison.")
    
    # Χρήση της lock_baseline από το core.sync
    if st.button("🔒 Lock Baseline & Activate Control Center", use_container_width=True, type="primary", disabled=is_non_viable):
        lock_baseline() # Snapshot current state
        st.session_state.mode = "home" # Return to home to see the Control Center
        st.rerun()

    # 6. RESET OPTION
    if st.button("Reset All Data", type="secondary"):
        st.session_state.clear()
        st.rerun()
