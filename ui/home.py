import streamlit as st
from core.sync import sync_global_state

def run_home():
    metrics = sync_global_state()
    is_locked = st.session_state.get('baseline_locked', False)
    
    st.title("🛡️ Strategic Decision Room")
    st.markdown("### Decision Support & Risk Analysis Engine")
    
    if not is_locked:
        st.info("💡 **System Ready:** Please proceed to **Stage 0** to lock your baseline parameters.")
    else:
        st.success("✅ **Baseline Active:** All systems synced.")

    st.divider()

    # --- KPI DASHBOARD ---
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

    # --- QUICK ACTIONS ---
    st.subheader("Strategic Navigation")
    col1, col2 = st.columns(2)
    
    with col1:
        with st.expander("🚀 Getting Started", expanded=True):
            st.write("Define your unit economics and fixed costs.")
            if st.button("Go to Stage 0", key="h_btn_s0", use_container_width=True):
                st.session_state.flow_step = "stage0"
                st.rerun()

    with col2:
        with st.expander("📚 Library & Tools", expanded=True):
            st.write("Access specialized calculators and strategic tools.")
            if st.button("Open Library", key="h_btn_lib", use_container_width=True):
                st.session_state.flow_step = "library"
                st.rerun()
