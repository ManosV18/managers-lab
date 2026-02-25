import streamlit as st
from core.sync import sync_global_state

def show_home():
    # Force sync and get current metrics
    metrics = sync_global_state()
    
    # PHASE A: Initial Setup
    if not st.session_state.get('baseline_locked', False):
        st.title("🚀 Welcome to Managers' Lab")
        st.subheader("System Status: Baseline Not Defined")
        st.divider()
        st.write(
            "The system requires a structural baseline before analysis can begin. "
            "Define revenue structure, cost behavior, and operating assumptions."
        )

        if st.button("Define Baseline (Stage 0)", use_container_width=True, type="primary"):
            st.session_state.mode = "path"
            st.session_state.flow_step = "stage0"
            st.rerun()

    # PHASE B: Control Center Mode
    else:
        st.title("🧪 Managers’ Lab — Control Center")
        st.caption("Structural Overview — 365-Day Operating Model")
        st.markdown("---")

        c1, c2, c3 = st.columns(3)
        c1.metric("Annual Revenue", f"{metrics['revenue']:,.0f} €")
        c2.metric("Free Cash Flow (FCF)", f"{metrics['fcf']:,.0f} €", help="Net liquidity after all obligations.")
        c3.metric("Contribution Margin", f"{metrics['contribution_ratio']*100:.1f}%")

        st.divider()
        if metrics['fcf'] > 0:
            st.success(f"✅ **System Status: Functional.** Surplus of {metrics['fcf']:,.0f}€.")
        else:
            st.error(f"🚨 **System Status: Deficit.** Monthly burn: {abs(metrics['fcf']/12):,.0f}€.")

        col_a, col_b = st.columns(2)
        with col_a:
            if st.button("Enter War Room Path", use_container_width=True, type="primary"):
                st.session_state.mode = "path"
                st.session_state.flow_step = "stage1" # Η αλλαγή ΠΡΙΝ το rerun
                st.rerun()
        with col_b:
            if st.button("Open Tool Library", use_container_width=True):
                st.session_state.mode = "library"
                st.rerun()

        with st.expander("System Configuration"):
            st.write(f"**Survival BEP:** {metrics['survival_bep']:,.0f} units")
            st.write(f"**Cash Conversion Cycle:** {metrics['ccc']} days")
