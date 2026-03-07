import streamlit as st
from core.sync import sync_global_state, lock_baseline


def run_home():

    # --- Sync metrics ---
    metrics = sync_global_state()
    is_locked = st.session_state.get("baseline_locked", False)

    # --- HERO SECTION ---
    st.markdown(
        """
        <div style="text-align:center; padding: 30px 0;">
            <h1 style="font-size:48px;">🛡️ Strategic Decision Room</h1>
            <h2 style="font-size:28px; font-weight:600; margin-top:10px;">
                Test your business decisions before you risk real money
            </h2>
            <h3 style="font-size:20px; font-weight:normal; color:#555; margin-top:10px;">
                Change prices, costs or investments and instantly see the impact on
                profit, break-even and cash survival.
            </h3>
            <p style="font-size:18px; color:#777; margin-top:15px;">
                Know the outcome before you commit.
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.divider()

    # --- STATUS ---
    if not is_locked:
        st.info("💡 System Ready: Please lock your baseline parameters to activate the dashboard.")
    else:
        st.success("✅ Baseline Active: Metrics calculated successfully.")

    st.divider()

    # --- KPI DASHBOARD ---
    st.markdown("<br>", unsafe_allow_html=True)

    c1, c2, c3, c4 = st.columns(4)

    rev_val = metrics.get("revenue") if is_locked else None
    ebit_val = metrics.get("ebit") if is_locked else None
    bep_val = metrics.get("bep_units") if is_locked else None
    fcf_val = metrics.get("fcf") if is_locked else None

    def colorize(value, low, high, suffix=""):
        if value is None:
            return "—"
        if value < low:
            return f"🔴 {value:,.0f}{suffix}"
        elif value < high:
            return f"🟠 {value:,.0f}{suffix}"
        else:
            return f"🟢 {value:,.0f}{suffix}"

    c1.metric("Projected Revenue", colorize(rev_val, 20000, 50000, " €"))
    c2.metric("EBIT", colorize(ebit_val, 5000, 20000, " €"))
    c3.metric("Break-Even Units", colorize(bep_val, 50, 200))
    c4.metric("Free Cash Flow", colorize(fcf_val, 5000, 15000, " €"))

    st.markdown("### Performance Overview")

    if rev_val:
        st.progress(min(rev_val / 50000, 1))
    if ebit_val:
        st.progress(min(ebit_val / 20000, 1))
    if fcf_val:
        st.progress(min(fcf_val / 15000, 1))

    st.divider()

    # --- ACTIONS ---
    st.subheader("Run Your First Scenario")
    st.write("Lock your baseline numbers and then use the tools to test scenarios.")

    col1, col2 = st.columns(2)

    # LOCK BASELINE
    with col1:
        with st.expander("🚀 Getting Started", expanded=True):

            if st.button("Lock Baseline & Start", use_container_width=True):
                lock_baseline()
                st.session_state["flow_step"] = "stage1"
                st.rerun()

    # OPEN TOOL LIBRARY
    with col2:
        with st.expander("📚 Library & Tools", expanded=True):

            if st.button("Open Tool Library", use_container_width=True):
                st.session_state["flow_step"] = "library"
                st.rerun()
