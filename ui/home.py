import streamlit as st
from core.sync import sync_global_state

def show_home():
    metrics = sync_global_state()
    st.title("🚀 Executive Control Center")

    if not st.session_state.get('baseline_locked', False):
        st.warning("⚠️ Baseline Not Defined. Please complete Stage 0.")
        if st.button("Go to Stage 0", use_container_width=True, type="primary"):
            st.session_state.flow_step = "stage0"
            st.rerun()
    else:
        # PHASE B: Η βιβλιοθήκη είναι πλέον διαθέσιμη
        st.success("✅ Baseline Locked. All analytical tools are online.")
        
        c1, c2, c3 = st.columns(3)
        c1.metric("Revenue", f"{metrics.get('revenue', 0):,.0f} €")
        c2.metric("FCF", f"{metrics.get('fcf', 0):,.0f} €")
        c3.metric("BEP Units", f"{metrics.get('survival_bep', 0):,.0f}")

        st.divider()
        col_left, col_right = st.columns(2)
        with col_left:
            if st.button("📈 Strategic Path (Stages)", use_container_width=True):
                st.session_state.flow_step = "stage1"
                st.rerun()
        with col_right:
            if st.button("🏛️ Open Tool Library", use_container_width=True, type="primary"):
                st.session_state.mode = "library"
                st.rerun()
