import streamlit as st
from core.sync import sync_global_state, lock_baseline


def check_required_inputs(required):

    missing = []

    for r in required:
        val = st.session_state.get(r, 0)

        if val == 0 or val is None:
            missing.append(r)

    return missing


def run_home():

    # ------------------------------------------------
    # TITLE
    # ------------------------------------------------

    st.title("Business Survival Calculator")

    st.write(
        "Test your business decisions before you risk real money."
    )

    st.write(
        "Change prices, costs or sales and instantly see what happens "
        "to profit, break-even point and cash survival."
    )

    st.write(
        "Before you lower a price, hire staff or order inventory — run the numbers first."
    )

    st.divider()

    # ------------------------------------------------
    # STAGE SELECTOR
    # ------------------------------------------------

    stage_options = {
        "Home": "home",
        "Stage 0: Setup": "stage0",
        "Stage 1: Survival & Break Even": "stage1",
        "Stage 2: Dashboard": "stage2",
        "Stage 3: Liquidity": "stage3",
        "Stage 4: Stress Test": "stage4",
        "Stage 5: Strategic Decision": "stage5",
        "Tools Library": "library"
    }

    selection = st.selectbox("Go to section", list(stage_options.keys()))

    if stage_options[selection] != st.session_state.get("flow_step", "home"):
        st.session_state.flow_step = stage_options[selection]
        st.rerun()

    st.divider()

    # ------------------------------------------------
    # BASIC BUSINESS INPUTS
    # ------------------------------------------------

    st.header("Enter your business numbers")

    col1, col2 = st.columns(2)

    with col1:

        st.session_state.price = st.number_input(
            "Price per product",
            value=float(st.session_state.get("price", 0.0))
        )

        st.session_state.variable_cost = st.number_input(
            "Cost to produce one unit",
            value=float(st.session_state.get("variable_cost", 0.0))
        )

        st.session_state.volume = st.number_input(
            "How many units you expect to sell",
            value=float(st.session_state.get("volume", 0.0))
        )

    with col2:

        st.session_state.fixed_cost = st.number_input(
            "Total yearly fixed expenses (rent, salaries, etc)",
            value=float(st.session_state.get("fixed_cost", 0.0))
        )

        st.session_state.opening_cash = st.number_input(
            "Cash currently in the bank",
            value=float(st.session_state.get("opening_cash", 0.0))
        )

        tax_percent = st.number_input(
            "Tax rate (%)",
            value=float(st.session_state.get("tax_rate", 0.0)) * 100
        )

        st.session_state.tax_rate = tax_percent / 100

    st.divider()

    # ------------------------------------------------
    # EXTRA PARAMETERS
    # ------------------------------------------------

    with st.expander("More optional inputs"):

        st.session_state.wacc = st.number_input(
            "Cost of capital",
            value=float(st.session_state.get("wacc", 0.0))
        )

        st.session_state.ar_days = st.number_input(
            "Days customers take to pay",
            value=float(st.session_state.get("ar_days", 0.0))
        )

        st.session_state.inventory_days = st.number_input(
            "Inventory days",
            value=float(st.session_state.get("inventory_days", 0.0))
        )

        st.session_state.ap_days = st.number_input(
            "Days you take to pay suppliers",
            value=float(st.session_state.get("ap_days", 0.0))
        )

    st.divider()

    # ------------------------------------------------
    # ACTION BUTTONS
    # ------------------------------------------------

    col1, col2 = st.columns(2)

    with col1:

        if st.button("Save these numbers"):

            lock_baseline()
            st.success("Numbers saved")

    with col2:

        if st.button("Start new scenario"):

            st.session_state.clear()
            st.session_state.flow_step = "home"
            st.rerun()

    st.divider()

    # ------------------------------------------------
    # QUESTIONS USER CAN ASK
    # ------------------------------------------------

    st.header("Questions business owners ask")

    col1, col2 = st.columns(2)

    with col1:

        if st.button("How much do I need to sell to not lose money?"):

            req = ["price", "variable_cost", "fixed_cost"]

            missing = check_required_inputs(req)

            if missing:

                st.warning(
                    "Please enter first:\n\n"
                    + "\n".join([f"• {m}" for m in missing])
                )

            else:

                st.session_state.flow_step = "stage1"
                st.rerun()

        if st.button("If I sell this many units will the business make money?"):

            req = ["price", "variable_cost", "fixed_cost", "volume"]

            missing = check_required_inputs(req)

            if missing:

                st.warning(
                    "Please enter first:\n\n"
                    + "\n".join([f"• {m}" for m in missing])
                )

            else:

                st.session_state.flow_step = "stage2"
                st.rerun()

    with col2:

        if st.button("What price should I charge so the business works?"):

            req = ["variable_cost", "fixed_cost", "volume"]

            missing = check_required_inputs(req)

            if missing:

                st.warning(
                    "Please enter first:\n\n"
                    + "\n".join([f"• {m}" for m in missing])
                )

            else:

                st.session_state.flow_step = "stage1"
                st.rerun()

        if st.button("With the cash I have how long can I survive?"):

            req = ["opening_cash", "price", "variable_cost", "fixed_cost", "volume"]

            missing = check_required_inputs(req)

            if missing:

                st.warning(
                    "Please enter first:\n\n"
                    + "\n".join([f"• {m}" for m in missing])
                )

            else:

                st.session_state.flow_step = "stage3"
                st.rerun()

    st.divider()

    # ------------------------------------------------
    # QUICK RESULTS
    # ------------------------------------------------

    if st.session_state.get("baseline_locked", False):

        metrics = sync_global_state()

        st.header("Quick numbers")

        c1, c2, c3 = st.columns(3)

        c1.metric("Revenue", f"{metrics['revenue']:,.0f}")
        c2.metric("Profit (EBIT)", f"{metrics['ebit']:,.0f}")
        c3.metric("Break-even units", f"{metrics['bep_units']:,.0f}")
