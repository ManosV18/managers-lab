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
            <h2 style="font-size:28px; font-weight:600; margin-top:10px;">
                See the real impact on your cash and survival before committing
            </h2>
            <h3 style="font-size:20px; font-weight:normal; color:#555; margin-top:10px;">
                Change prices, costs, or volumes and instantly see the effect on profit, break-even, and cash survival.
            </h3>
            <p style="font-size:18px; color:#777; margin-top:15px;">
                Know the outcome before you spend a euro.
            </p>
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

    # --- INTERACTIVE SCENARIO SLIDERS ---
    st.subheader("Scenario Tester")
    st.write("Adjust price, cost, or volume to see live impact on your KPIs.")

    col1, col2, col3 = st.columns(3)
    price_mult = col1.slider("Price Multiplier", 0.5, 2.0, 1.0, 0.05)
    cost_mult = col2.slider("Cost Multiplier", 0.5, 2.0, 1.0, 0.05)
    volume_mult = col3.slider("Volume Multiplier", 0.5, 2.0, 1.0, 0.05)

    # --- CALCULATE SCENARIO METRICS ---
    rev_val = metrics.get('revenue') if is_locked else None
    ebit_val = metrics.get('ebit') if is_locked else None
    bep_val = metrics.get('bep_units') if is_locked else None
    fcf_val = metrics.get('fcf') if is_locked else None
    cash_val = metrics.get('cash') if is_locked else None

    if is_locked:
        rev_val = rev_val * price_mult * volume_mult
        ebit_val = ebit_val * price_mult * volume_mult - (metrics.get('fixed_costs',0)*(cost_mult-1))
        bep_val = bep_val / (price_mult)  # simplified
        fcf_val = fcf_val * price_mult * volume_mult - (metrics.get('fixed_costs',0)*(cost_mult-1))
        cash_val = cash_val + (fcf_val - metrics.get('fcf',0))  # incremental cash effect

    # --- KPI DASHBOARD ---
    st.markdown("<br>", unsafe_allow_html=True)
    c1, c2, c3, c4, c5 = st.columns(5)

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
    c5.metric("Available Cash", colorize(cash_val, (1000, 20000)), "€")

    # --- Progress bars ---
    st.markdown("### Performance Overview")
    st.progress(min(rev_val / 50000, 1) if rev_val else 0)
    st.progress(min(ebit_val / 20000, 1) if ebit_val else 0)
    st.progress(min(fcf_val / 15000, 1) if fcf_val else 0)
    st.progress(min(cash_val / 20000, 1) if cash_val else 0)

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
