import streamlit as st

def show_home():
    # PHASE A: Entry Mode (No Baseline Defined)
    # Ελέγχει αν έχει κλειδώσει η βάση δεδομένων από το Stage 0
    if not st.session_state.get('baseline_locked', False):
        st.title("🧪 Managers’ Lab")
        st.subheader("System Status: Baseline Not Defined")
        st.divider()
        st.write(
            "The system requires a structural baseline before analysis can begin. "
            "Define revenue structure, cost behavior, and operating assumptions "
            "to activate the decision environment."
        )

        if st.button("Define Baseline (Stage 0)", use_container_width=True, type="primary"):
            st.session_state.mode = "path"
            st.session_state.flow_step = 0
            st.rerun()

    # PHASE B: Control Center Mode (System Operational)
    else:
        st.title("🧪 Managers’ Lab — Control Center")
        st.caption("Structural Overview — 365-Day Operating Model")
        st.markdown("---")

        # Ανάκτηση δεδομένων από το session_state (αρχικοποιημένα στο core/system_state.py)
        p = st.session_state.get('price', 0.0)
        v = st.session_state.get('volume', 0)
        vc = st.session_state.get('variable_cost', 0.0)
        fc = st.session_state.get('fixed_cost', 0.0)
        debt = st.session_state.get('debt', 0.0)
        rate = st.session_state.get('interest_rate', 0.0)
        
        # Αναλυτικοί Υπολογισμοί
        rev = p * v
        ebit = ((p - vc) * v) - fc
        interest_expense = debt * rate
        net_profit = ebit - interest_expense
        margin = (p - vc) / p if p > 0 else 0

        # Executive Metrics Display
        c1, c2, c3 = st.columns(3)
        c1.metric("Annual Revenue", f"{rev:,.0f} €")
        c2.metric("Net Profit (Post-Interest)", f"{net_profit:,.0f} €", delta=f"EBIT: {ebit:,.0f} €")
        c3.metric("Contribution Margin", f"{margin:.1%}")

        st.divider()
        
        # Navigation Hub
        st.subheader("Analysis Environment")
        col_a, col_b = st.columns(2)
        with col_a:
            if st.button("Enter Structured Path", use_container_width=True, type="primary"):
                st.session_state.mode = "path"
                st.session_state.flow_step = 1
                st.rerun()
        with col_b:
            if st.button("Open Tool Library", use_container_width=True):
                st.session_state.mode = "library"
                st.rerun()

        st.divider()
        
        # Ρυθμίσεις Συστήματος (Expander)
        with st.expander("System Configuration"):
            st.write(
                "The baseline defines the structural mechanics of the system. "
                "Modifying it will recalibrate all analytical modules."
            )
            if st.button("Unlock Baseline & Recalibrate", use_container_width=True):
                st.session_state.baseline_locked = False
                st.session_state.mode = "path"
                st.session_state.flow_step = 0
                st.rerun()
