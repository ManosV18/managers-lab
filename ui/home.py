import streamlit as st
from core.sync import sync_global_state

def run_home():
    # 1. Ανάκτηση Metrics μέσω του Orchestrator
    metrics = sync_global_state()
    is_locked = st.session_state.get('baseline_locked', False)
    
    st.title("🛡️ Strategic War Room")
    st.markdown("### Decision Support & Risk Analysis Engine")
    
    # Status Alert: Ενημερώνει τον χρήστη για την κατάσταση του συστήματος
    if not is_locked:
        st.info("💡 **System Ready:** Please proceed to **Stage 0** to lock your baseline parameters and activate analytics.")
    else:
        st.success("✅ **Baseline Active:** All strategic simulations are synced with your locked configuration.")

    st.divider()

    # --- KPI DASHBOARD (Safe View Logic) ---
    # Εμφανίζει τιμές μόνο αν έχει γίνει Lock, αλλιώς εμφανίζει παύλα (—)
    st.subheader("Key Performance Indicators (Current Baseline)")
    c1, c2, c3, c4 = st.columns(4)
    
    rev_val = metrics.get('revenue') if is_locked else None
    ebit_val = metrics.get('ebit') if is_locked else None
    bep_val = metrics.get('bep_units') if is_locked else None
    fcf_val = metrics.get('fcf') if is_locked else None

    c1.metric("Projected Revenue", f"€{rev_val:,.0f}" if rev_val is not None else "—")
    c2.metric("EBIT", f"€{ebit_val:,.0f}" if ebit_val is not None else "—")
    c3.metric("Break-Even (Units)", f"{bep_val:,.0f}" if bep_val is not None else "—")
    c4.metric("Free Cash Flow", f"€{fcf_val:,.0f}" if fcf_val is not None else "—")

    st.divider()

    # --- QUICK ACTIONS (Navigation Fixes) ---
    st.subheader("Strategic Navigation")
    col1, col2 = st.columns(2)
    
    with col1:
        with st.expander("🚀 Getting Started", expanded=True):
            st.write("Define your unit economics, fixed costs, and sales volume to initialize the engine.")
            # Κουμπί για Stage 0: Επιβάλλει mode='path' για να δουλέψει ο Router
            if st.button("Go to Stage 0", key="h_btn_s0", use_container_width=True):
                st.session_state.mode = "path"
                st.session_state.flow_step = "stage0"
                st.rerun()

    with col2:
        with st.expander("📚 Library & Tools", expanded=True):
            st.write("Access specialized calculators for WACC, QSPM, and advanced financial modeling.")
            # Κουμπί για Library: Επιβάλλει mode='library'
            if st.button("Open Library", key="h_btn_lib", use_container_width=True):
                st.session_state.mode = "library"
                st.session_state.flow_step = "library" 
                st.rerun()

    st.divider()
    st.caption("Strategic Engine v2.0 | Standardized 365-day Financial Logic")
