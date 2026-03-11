import streamlit as st
from core.sync import sync_global_state


def run_home():

    s = st.session_state

    # --------------------------------------------
    # ENGINE SYNC
    # --------------------------------------------

    metrics = sync_global_state() if s.get("baseline_locked") else {}

    # --------------------------------------------
    # READ PARAMETERS
    # --------------------------------------------

    p = s.get("price", 100.0)
    vc = s.get("variable_cost", 60.0)
    v = s.get("volume", 1000)
    fc = s.get("fixed_cost", 20000.0)

    net_cash = metrics.get("net_cash_position", s.get("opening_cash", 10000.0))
    bep_units = metrics.get("bep_units") if metrics else None

    margin = p - vc

    # --------------------------------------------
    # SNAPSHOT LOGIC
    # --------------------------------------------

    if margin > 0 and bep_units is not None:

        margin_of_safety = v - bep_units

        buffer_pct = (margin_of_safety / v * 100) if v > 0 else 0

        bep_display = f"{bep_units:,.0f} units"

        delta_val = (
            f"{margin_of_safety:,.0f} surplus"
            if margin_of_safety >= 0
            else f"{abs(margin_of_safety):,.0f} deficit"
        )

        delta_col = "normal" if margin_of_safety >= 0 else "inverse"

    else:

        buffer_pct = -100.0
        bep_display = "N/A"
        delta_val = "⚠ Business model not viable"
        delta_col = "inverse"

    # --------------------------------------------
    # HERO
    # --------------------------------------------

    st.markdown(
        """
        <div style="text-align:center; padding: 10px 0 20px 0;">
            <h1 style="font-size:62px; font-weight:900; color:#1E3A8A; margin-bottom:0px;">
            Managers Lab<span style="color:#ef4444;">.</span></h1>
            <div style="font-size:18px; color:#64748b; letter-spacing:2px; text-transform:uppercase;">
            🛡️ Strategic Decision Room</div>
        </div>
        """,
        unsafe_allow_html=True
    )

    # --------------------------------------------
    # EXECUTIVE SNAPSHOT
    # --------------------------------------------

    st.subheader("📊 Executive Snapshot")

    c1, c2, c3, c4, c5 = st.columns(5)

    c1.metric("Simulated Volume", f"{v:,.0f} units")
    c2.metric("Unit Contribution", f"€{margin:,.2f}")

    c3.metric(
        label="Cash Break-Even",
        value=bep_display,
        delta=delta_val,
        delta_color=delta_col
    )

    c4.metric("Survival Buffer", f"{buffer_pct:.1f}%")

    c5.metric(
        "Net Cash Position",
        f"€{net_cash:,.0f}",
        help="Cash after Working Capital requirements"
    )

    st.divider()

    # --------------------------------------------
    # MAIN LAYOUT
    # --------------------------------------------

    col_input, col_nav = st.columns([0.42, 0.58], gap="large")

    # --------------------------------------------
    # INPUT PANEL
    # --------------------------------------------

    with col_input:

        st.subheader("⚙️ Global Parameters")

        with st.expander("📊 Business Baseline", expanded=True):

            st.number_input("Unit Price (€)", value=float(p), key="price")
            st.number_input("Variable Cost (€)", value=float(vc), key="variable_cost")
            st.number_input("Annual Volume", value=int(v), key="volume")
            st.number_input("Annual Fixed Costs (€)", value=float(fc), key="fixed_cost")

            st.number_input(
                "Target Profit Goal (€)",
                value=float(s.get("target_profit_goal", 0.0)),
                key="target_profit_goal"
            )

        with st.expander("🔄 Working Capital Cycle", expanded=False):

            st.number_input(
                "AR Days (Collection)",
                value=float(s.get("ar_days", 45.0)),
                key="ar_days"
            )

            st.number_input(
                "Inventory Days",
                value=float(s.get("inventory_days", 60.0)),
                key="inventory_days"
            )

            st.number_input(
                "AP Days (Payment)",
                value=float(s.get("ap_days", 30.0)),
                key="ap_days"
            )

        with st.expander("💰 Liquidity & Obligations", expanded=False):

            st.number_input(
                "Opening Cash (€)",
                value=float(s.get("opening_cash", 10000.0)),
                key="opening_cash"
            )

            st.number_input(
                "Annual Debt Service (€)",
                value=float(s.get("annual_debt_service", 0.0)),
                key="annual_debt_service"
            )

        st.divider()

        if st.button("🔒 Lock Baseline & Sync Engine", type="primary", use_container_width=True):

            st.session_state.baseline_locked = True
            st.rerun()

    # --------------------------------------------
    # TOOL LIBRARY
    # --------------------------------------------

    with col_nav:

        st.subheader("📊 Strategic Tool Library")

        st.info("Select a tool to analyze the locked baseline.")

        # εδώ θα μπαίνουν τα tools
