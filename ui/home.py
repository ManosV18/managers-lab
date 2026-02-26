import streamlit as st
from core.sync import sync_global_state

def run_home():
    # Λήψη των metrics μέσω του ενοποιημένου sync
    metrics = sync_global_state()
    
    st.title("🛡️ Strategic War Room")
    st.markdown("### Decision Support & Risk Analysis Engine")
    
    # Status Alert
    if not st.session_state.get('baseline_locked', False):
        st.info("💡 **System Ready:** Please proceed to **Stage 0** to lock your baseline parameters and activate full analytics.")
    else:
        st.success("✅ **Baseline Active:** All strategic simulations are synced with your locked configuration.")

    st.divider()

    # --- KPI DASHBOARD ---
    st.subheader("Key Performance Indicators (Current Baseline)")
    c1, c2, c3, c4 = st.columns(4)
    
    # Χρήση των σωστών keys από την Engine
    revenue = metrics.get('revenue')
    ebit = metrics.get('ebit')
    bep = metrics.get('bep_units')
    fcf = metrics.get('fcf')

    c1.metric("Projected Revenue", f"€{revenue:,.0f}" if revenue is not None else "—")
    c2.metric("EBIT", f"€{ebit:,.0f}" if ebit is not None else "—")
    c3.metric("Break-Even (Units)", f"{bep:,.0f}" if bep is not None else "—")
    c4.metric("Free Cash Flow", f"€{fcf:,.0f}" if fcf is not None else "—")

    st.divider()

    # --- QUICK ACTIONS ---
    st.subheader("Strategic Navigation")
    col1, col2 = st.columns(2)
    
    with col1:
        with st.expander("🚀 Getting Started", expanded=True):
            st.write("1. **Configure:** Define price and costs in Stage 0.")
            st.write("2. **Analyze:** Check survival limits in Stage 1.")
            st.write("3. **Stress Test:** Simulate crises in Stage 4.")
            if st.button("Go to Stage 0", use_container_width=True):
                st.session_state.flow_step = "stage0"
                st.rerun()

    with col2:
        with st.expander("📚 Library & Tools", expanded=True):
            st.write("Access advanced calculators for WACC, QSPM, and specialized unit cost analysis.")
            if st.button("Open Library", use_container_width=True):
                st.session_state.mode = "library"
                st.session_state.flow_step = "library_home" # Ή το αντίστοιχο flow_step της βιβλιοθήκης
                st.rerun()
