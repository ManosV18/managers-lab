import streamlit as st
from core.sync import sync_global_state

def show_home():
    metrics = sync_global_state()
    
    # PHASE A: Αν ΔΕΝ είναι κλειδωμένο το baseline
    if not st.session_state.get('baseline_locked', False):
        st.title("🚀 Welcome to Managers' Lab")
        st.subheader("System Status: Baseline Not Defined")
        st.divider()
        st.write("The system requires a structural baseline before analysis can begin.")

        if st.button("Define Baseline (Stage 0)", use_container_width=True, type="primary"):
            st.session_state.mode = "path"
            st.session_state.flow_step = "stage0"
            st.rerun()

    # PHASE B: Αν ΕΙΝΑΙ κλειδωμένο (Control Center)
    else:
        st.title("🧪 Managers’ Lab — Control Center")
        st.markdown("---")

        c1, c2, c3 = st.columns(3)
        c1.metric("Annual Revenue", f"{metrics.get('revenue', 0):,.0f} €")
        c2.metric("FCF", f"{metrics.get('fcf', 0):,.0f} €")
        c3.metric("Margin", f"{metrics.get('contribution_ratio', 0)*100:.1f}%")

        st.divider()
        col_a, col_b = st.columns(2)
        with col_a:
            if st.button("Enter War Room Path", use_container_width=True, type="primary"):
                st.session_state.mode = "path"
                st.session_state.flow_step = "stage1"
                st.rerun()
        with col_b:
            if st.button("Open Tool Library", use_container_width=True):
                st.session_state.mode = "library"
                st.rerun()
