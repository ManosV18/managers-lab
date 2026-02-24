import streamlit as st
from core.engine import compute_core_metrics

def run_stage0():
    st.header("🏗️ Stage 0: Structural Baseline Definition")
    st.caption("Establish the core economic DNA of the enterprise before starting the simulation.")
    st.divider()

    # 1. Fetch Current State (Initial or from Sidebar)
    m = compute_core_metrics()
    s = st.session_state

    # 2. EXECUTIVE SUMMARY OF BASELINE
    st.subheader("Current Economic Profile")
    c1, c2, c3 = st.columns(3)
    
    c1.metric("Unit Contribution", f"{m['unit_contribution']:,.2f} €", help="Price minus Variable Cost")
    c2.metric("Annual Fixed Load", f"{(s.fixed_cost + s.annual_loan_payment):,.0f} €", help="Fixed Costs + Debt Service")
    c3.metric("WC Lock", f"{m['wc_requirement']:,.0f} €", help="Capital tied in operations")

    # 3. VIABILITY CHECK
    if m['is_non_viable']:
        st.error("🚨 **STRUCTURAL ERROR:** Variable costs exceed price. The system loses money on every unit sold. Correct the Baseline in the sidebar to proceed.")
    else:
        st.success("✅ **VIABILITY CONFIRMED:** The unit economics allow for potential break-even.")

    # 4. DATA VALIDATION TABLE
    st.subheader("Structural Inputs")
    data = {
        "Parameter": ["Volume", "Price", "Variable Cost", "Fixed Cost", "Debt Service", "AR Days", "Inv. Days", "AP Days"],
        "Current Value": [
            f"{s.volume:,}", f"{s.price:,.2f} €", f"{s.variable_cost:,.2f} €", 
            f"{s.fixed_cost:,.0f} €", f"{s.annual_loan_payment:,.0f} €",
            s.ar_days, s.inventory_days, s.ap_days
        ]
    }
    st.table(data)

    

    # 5. LOCKING MECHANISM
    st.divider()
    st.warning("Once you lock the baseline, the current parameters will be used as the 'Healthy State' for all shock simulations and stress tests.")
    
    if st.button("🔒 Lock Baseline & Activate Control Center", use_container_width=True, type="primary", disabled=m['is_non_viable']):
        st.session_state.baseline_locked = True
        # Save a snapshot of the baseline FCF for Stage 2 comparisons
        st.session_state.last_computed_metrics = m
        st.session_state.flow_step = 0 # Go back to Home which now will show Phase B
        st.rerun()

    # 6. RESET OPTION
    if st.button("Reset to Defaults", type="secondary"):
        st.session_state.clear()
        st.rerun()
