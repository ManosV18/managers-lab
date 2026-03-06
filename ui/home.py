import streamlit as st
from core.sync import sync_global_state

def run_home():
    # --- Sync metrics ---
    metrics = sync_global_state()
    is_locked = st.session_state.get('baseline_locked', False)

    # --- HERO SECTION ---
    st.title("🛡️ Strategic Decision Room")
    st.header("Test your business decisions before you risk real money")
    st.subheader("Change prices, costs or investments and instantly see the impact on profit, break-even and cash survival.")
    st.markdown("Know the outcome before you commit.")

    st.divider()

    # --- INFO STATUS ---
    if not is_locked:
        st.info("💡 **System Ready:** Please proceed to **Stage 0** to lock your baseline parameters.")
    else:
        st.success("✅ **Baseline Active:** All systems synced.")

    st.divider()

    # --- LIVE INPUTS FOR KPI SIMULATION ---
    st.subheader("📊 Adjust your numbers and see live impact")

    col_price, col_cost, col_volume = st.columns(3)

    with col_price:
        rev_input = st.number_input("Projected Revenue (€)", value=metrics.get('revenue', 30000), step=1000)
    with col_cost:
        ebit_input = st.number_input("EBIT (€)", value=metrics.get('ebit', 10000), step=500)
    with col_volume:
        bep_input = st.number_input("Break-Even Units", value=metrics.get('bep_units', 120), step=10)

    fcf_input = st.number_input("Free Cash Flow (€)", value=metrics.get('fcf', 8000), step=500)

    # --- KPI LIVE DASHBOARD ---
    def colorize(value, thresholds):
        low, high = thresholds
        if value is None:
            return "—"
        if value < low:
            return f"🔴 {value:,.0f}"
        elif value < high:
            return f"🟠 {value:,.0f}"
        else:
            return f"🟢 {value:,.0f}"

    st.markdown("<br>", unsafe_allow_html=True)
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Projected Revenue", colorize(rev_input, (20000, 50000)), "€")
    c2.metric("EBIT", colorize(ebit_input, (5000, 20000)), "€")
    c3.metric("Break-Even (Units)", colorize(bep_input, (50, 200)), "units")
    c4.metric("Free Cash Flow", colorize(fcf_input, (5000, 15000)), "€")

    st.markdown("### Performance Overview")
    st.progress(min(rev_input / 50000, 1))
    st.progress(min(ebit_input / 20000, 1))
    st.progress(min(fcf_input / 15000, 1))

    st.divider()

    # --- QUICK ACTIONS / EXPANDERS ---
    st.subheader("Run Your First Scenario")
    st.write("Lock your baseline numbers and test what happens if you change price, costs or volume.")

    col1, col2 = st.columns(2)

    with col1:
        with st.expander("🚀 Getting Started", expanded=True):
            st.write("Define your baseline numbers before testing business decisions.")
            if st.button("Go to Stage 0", key="h_btn_s0", use_container_width=True):
                st.session_state.flow_step = "stage0"
                st.rerun()

    with col2:
        with st.expander("📚 Library & Tools", expanded=True):
            st.write("Access specialized calculators and strategic tools.")
            if st.button("Open Library", key="h_btn_lib", use_container_width=True):
                st.session_state.flow_step = "library"
                st.rerun()
