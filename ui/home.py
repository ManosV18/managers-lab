import streamlit as st
from core.sync import sync_global_state
from core.sync import lock_baseline


def run_home():

    st.title("🛡 Strategic Decision Room")

    st.write(
        "Enter your basic business numbers. "
        "Then choose what analysis you want to see."
    )

    st.divider()

    # ---------------------------------------------------
    # STAGE SELECTOR
    # ---------------------------------------------------

    stage_options = {
        "Home": "home",
        "Stage 0: Setup": "stage0",
        "Stage 1: Survival & BEP": "stage1",
        "Stage 2: Dashboard": "stage2",
        "Stage 3: Liquidity Physics": "stage3",
        "Stage 4: Stress Testing": "stage4",
        "Stage 5: Strategic Decision": "stage5",
        "Tools Library": "library"
    }

    selection = st.selectbox(
        "Go to stage",
        list(stage_options.keys())
    )

    if stage_options[selection] != st.session_state.get("flow_step", "home"):
        st.session_state.flow_step = stage_options[selection]
        st.rerun()

    st.divider()

    # ---------------------------------------------------
    # GLOBAL PARAMETERS (ΠΡΩΗΝ SIDEBAR)
    # ---------------------------------------------------

    st.header("Global Parameters")

    col1, col2 = st.columns(2)

    with col1:

        st.session_state.price = st.number_input(
            "Unit Price (€)",
            value=float(st.session_state.get("price", 0.0))
        )

        st.session_state.variable_cost = st.number_input(
            "Variable Cost (€)",
            value=float(st.session_state.get("variable_cost", 0.0))
        )

        st.session_state.volume = st.number_input(
            "Annual Volume",
            value=float(st.session_state.get("volume", 0.0))
        )

        st.session_state.fixed_cost = st.number_input(
            "Annual Fixed Costs",
            value=float(st.session_state.get("fixed_cost", 0.0))
        )

    with col2:

        st.session_state.annual_debt_service = st.number_input(
            "Annual Debt Service",
            value=float(st.session_state.get("annual_debt_service", 0.0))
        )

        st.session_state.opening_cash = st.number_input(
            "Opening Cash",
            value=float(st.session_state.get("opening_cash", 0.0))
        )

        tax_percent = st.number_input(
            "Tax Rate (%)",
            value=float(st.session_state.get("tax_rate", 0.0)) * 100
        )

        st.session_state.tax_rate = tax_percent / 100

    st.divider()

    # ---------------------------------------------------
    # ADVANCED PARAMETERS (EXPANDER)
    # ---------------------------------------------------

    with st.expander("More Parameters"):

        st.session_state.wacc = st.number_input(
            "WACC",
            value=float(st.session_state.get("wacc", 0.0))
        )

        st.session_state.ar_days = st.number_input(
            "AR Days",
            value=float(st.session_state.get("ar_days", 0.0))
        )

        st.session_state.inventory_days = st.number_input(
            "Inventory Days",
            value=float(st.session_state.get("inventory_days", 0.0))
        )

        st.session_state.ap_days = st.number_input(
            "AP Days",
            value=float(st.session_state.get("ap_days", 0.0))
        )

    st.divider()

    # ---------------------------------------------------
    # ACTIONS
    # ---------------------------------------------------

    col1, col2 = st.columns(2)

    with col1:

        if st.button("Lock Baseline"):

            lock_baseline()

            st.success("Baseline locked")

    with col2:

        if st.button("Start New Scenario"):

            st.session_state.clear()

            st.session_state.flow_step = "home"

            st.rerun()

    st.divider()

    # ---------------------------------------------------
    # RESULTS REQUEST
    # ---------------------------------------------------

    st.header("What do you want to see?")

    if st.button("Calculate Break Even"):
        st.session_state.flow_step = "stage1"
        st.rerun()

    if st.button("Check Liquidity"):
        st.session_state.flow_step = "stage3"
        st.rerun()

    if st.button("Run Stress Test"):
        st.session_state.flow_step = "stage4"
        st.rerun()

    if st.button("Open Tool Library"):
        st.session_state.flow_step = "library"
        st.rerun()

    st.divider()

    # ---------------------------------------------------
    # OPTIONAL LIVE METRICS
    # ---------------------------------------------------

    if st.session_state.get("baseline_locked", False):

        metrics = sync_global_state()

        st.subheader("Quick Results")

        c1, c2, c3 = st.columns(3)

        c1.metric("Revenue", f"{metrics['revenue']:,.0f}")
        c2.metric("EBIT", f"{metrics['ebit']:,.0f}")
        c3.metric("Break Even", f"{metrics['bep_units']:,.0f}")

