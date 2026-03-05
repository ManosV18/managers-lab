import streamlit as st
from core.sync import sync_global_state

def run_home():
    # --- Sync metrics ---
    metrics = sync_global_state()
    is_locked = st.session_state.get('baseline_locked', False)

    # --- HERO SECTION ---
    st.markdown(
        """
        <div style="text-align:center; padding: 30px 0;">
            <h1 style="font-size:48px;">🛡️ Strategic Decision Room</h1>
            <h3 style="font-size:22px; font-weight:normal; color:#555;">
                Before you change your price, see the impact on profit, break-even, and survival — instantly.
            </h3>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.divider()

    # --- INFO STATUS ---
    if not is_locked:
        st.info("💡 **System Ready:** Please proceed to **Stage 0** to lock your baseline parameters.")
    else:
        st.success("✅ **Baseline Active:** All systems synced.")

    st.divider()

    # --- KPI DASHBOARD ---
    st.markdown("<br>", unsafe_allow_html=True)
    c1, c2, c3, c4 = st.columns(4)

    rev_val = metrics.get('revenue') if is_locked else None
    ebit_val = metrics.get('ebit') if is_locked else None
    bep_val = metrics.get('bep_units') if is_locked else None
    fcf_val = metrics.get('fcf') if is_locked else None

    # Χρωματισμός KPI
    def colorize(value, thresholds):
        if value is None:
            return "—"
        low, high = thresholds
        if value < low:
            return f"🔴 {value:,.0f}"
        elif value < high:
            return f"🟠 {value:,.0f}"
        else:
            return f"🟢 {value:,.0f}"

    c1.metric("Projected Revenue", colorize(rev_val, (20000, 50000)), "€")
    c2.metric("EBIT", colorize(ebit_val, (5000, 20000)), "€")
    c3.metric("Break-Even (Units)", colorize(bep_val, (50, 200)), "units")
    c4.metric("Free Cash Flow", colorize(fcf_val, (5000, 15000)), "€")

    # Progress bars για πιο visual αίσθηση
    st.markdown("### Performance Overview")
    st.progress(min(rev_val / 50000, 1) if rev_val else 0)
    st.progress(min(ebit_val / 20000, 1) if ebit_val else 0)
    st.progress(min(fcf_val / 15000, 1) if fcf_val else 0)

    st.divider()

    # --- QUICK ACTIONS / EXPANDERS ---
    st.subheader("Quick Start")
    st.write("Lock your baseline parameters or explore tools to guide your strategic decisions.")

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
