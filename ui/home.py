import streamlit as st
from core.sync import sync_global_state, lock_baseline

# -----------------------------
# Helpers
# -----------------------------
def check_required_inputs(required):
    missing = []
    for r in required:
        val = st.session_state.get(r, 0)
        if val == 0 or val is None:
            missing.append(r)
    return missing

def reset_home_session():
    """Καθαρίζει τα inputs χωρίς να σπάει το rerun"""
    keys_to_keep = ["flow_step", "baseline_locked"]
    for key in list(st.session_state.keys()):
        if key not in keys_to_keep:
            del st.session_state[key]

# -----------------------------
# Main Home
# -----------------------------
def run_home():
    st.title("Business Survival Calculator")

    st.write(
        "Enter the numbers of your business and ask simple questions like:\n"
        "- How much do I need to sell?\n"
        "- Will this price work?\n"
        "- Can the business survive?"
    )

    st.divider()

    # -----------------------------
    # Stage Selector
    # -----------------------------
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
        st.experimental_rerun()

    st.divider()

    # -----------------------------
    # Basic Business Inputs
    # -----------------------------
    st.header("Your Business Numbers")
    col1, col2 = st.columns(2)

    with col1:
        st.session_state.price = st.number_input(
            "Price per unit (€)",
            value=float(st.session_state.get("price", 0.0))
        )
        st.session_state.variable_cost = st.number_input(
            "Cost per unit (€)",
            value=float(st.session_state.get("variable_cost", 0.0))
        )
        st.session_state.volume = st.number_input(
            "Units you expect to sell",
            value=float(st.session_state.get("volume", 0.0))
        )

    with col2:
        st.session_state.fixed_cost = st.number_input(
            "Total yearly fixed expenses (€)",
            value=float(st.session_state.get("fixed_cost", 0.0))
        )
        st.session_state.opening_cash = st.number_input(
            "Cash currently in the bank (€)",
            value=float(st.session_state.get("opening_cash", 0.0))
        )
        tax_percent = st.number_input(
            "Tax rate (%)",
            value=float(st.session_state.get("tax_rate", 0.0)) * 100
        )
        st.session_state.tax_rate = tax_percent / 100

    st.divider()

    # -----------------------------
    # Extra Parameters
    # -----------------------------
    with st.expander("More optional inputs"):
        st.session_state.wacc = st.number_input(
            "Cost of capital (WACC)",
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

    # -----------------------------
    # Action Buttons
    # -----------------------------
    col1, col2 = st.columns(2)

    with col1:
        if st.button("Lock numbers"):
            lock_baseline()
            st.success("Numbers saved")

    with col2:
        if st.button("Start new scenario"):
            reset_home_session()
            st.session_state.flow_step = "home"
            st.experimental_rerun()

    st.divider()

    # -----------------------------
    # Questions User Can Ask
    # -----------------------------
    st.header("What do you want to know?")
    col1, col2 = st.columns(2)

    with col1:
        if st.button("How much do I need to sell to not lose money?"):
            req = ["price", "variable_cost", "fixed_cost"]
            missing = check_required_inputs(req)
            if missing:
                st.warning("Please enter first:\n\n" + "\n".join([f"• {m}" for m in missing]))
            else:
                st.session_state.flow_step = "stage1"
                st.experimental_rerun()

        if st.button("If I sell this many units will the business make money?"):
            req = ["price", "variable_cost", "fixed_cost", "volume"]
            missing = check_required_inputs(req)
            if missing:
                st.warning("Please enter first:\n\n" + "\n".join([f"• {m}" for m in missing]))
            else:
                st.session_state.flow_step = "stage2"
                st.experimental_rerun()

    with col2:
        if st.button("What price should I charge so the business works?"):
            req = ["variable_cost", "fixed_cost", "volume"]
            missing = check_required_inputs(req)
            if missing:
                st.warning("Please enter first:\n\n" + "\n".join([f"• {m}" for m in missing]))
            else:
                st.session_state.flow_step = "stage1"
                st.experimental_rerun()

        if st.button("With the cash I have how long can I survive?"):
            req = ["opening_cash", "price", "variable_cost", "fixed_cost", "volume"]
            missing = check_required_inputs(req)
            if missing:
                st.warning("Please enter first:\n\n" + "\n".join([f"• {m}" for m in missing]))
            else:
                st.session_state.flow_step = "stage3"
                st.experimental_rerun()

    st.divider()

    # -----------------------------
    # Quick Results
    # -----------------------------
    if st.session_state.get("baseline_locked", False):
        metrics = sync_global_state()
        st.header("Quick numbers")
        c1, c2, c3 = st.columns(3)
        c1.metric("Revenue", f"{metrics['revenue']:,.0f} €")
        c2.metric("EBIT", f"{metrics['ebit']:,.0f} €")
        c3.metric("Break even units", f"{metrics['bep_units']:,.0f}")
