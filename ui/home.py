import streamlit as st
from core.engine import compute_core_metrics

def show_home():
    # PHASE A: Entry Mode (No Baseline Defined)
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

        # 1. FETCH DATA VIA ENGINE FOR CONSISTENCY
        metrics = compute_core_metrics()
        
        # 2. EXECUTIVE METRICS DISPLAY
        
        c1, c2, c3 = st.columns(3)
        
        # Revenue
        c1.metric("Annual Revenue", f"{metrics['revenue']:,.0f} €")
        
        # Net Economic Profit (The cold truth including liquidity drain)
        c2.metric(
            "Net Economic Profit", 
            f"{metrics.get('ebit', 0.0):,.0f} €", 
            help="Final profit after interest AND liquidity drain (working capital friction)."
        )
        
        # Contribution Margin %
        p = st.session_state.get('price', 0.0)
        margin_pct = (metrics['unit_contribution'] / p * 100) if p > 0 else 0
        c3.metric("Contribution Margin", f"{margin_pct:.1f}%")

        # 3. STATUS VERDICT
        st.divider()
        if metrics['net_profit'] > 0:
            st.success(f"✅ **System Status: Functional.** The enterprise is generating a net surplus above its structural obligations.")
        else:
            st.error(f"🚨 **System Status: Deficit.** The enterprise is currently consuming capital to maintain operations.")

        # 4. NAVIGATION HUB
        st.subheader("Analysis Environment")
        col_a, col_b = st.columns(2)
        with col_a:
            if st.button("Enter Structured Path", use_container_width=True, type="primary"):
                st.session_state.mode = "path"
                # Start from Stage 1 as Baseline is already locked
                st.session_state.flow_step = 1
                st.rerun()
        with col_b:
            if st.button("Open Tool Library", use_container_width=True):
                st.session_state.mode = "library"
                st.rerun()

        st.divider()
        
        # 5. SYSTEM CONFIGURATION (Expander)
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
