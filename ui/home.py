import streamlit as st
from core.sync import sync_global_state, lock_baseline


def run_home():

    metrics = sync_global_state()
    is_locked = st.session_state.get("baseline_locked", False)

    st.title("🛡️ Strategic Decision Room")
    st.subheader("Test your business decisions before risking real money")

    st.write(
        "Change prices, costs or investments and instantly see the impact on "
        "profit, break-even and cash survival."
    )

    st.divider()

    if not is_locked:

        st.info("Step 1: Enter your basic business numbers")

        col1, col2 = st.columns(2)

        with col1:
            st.session_state.price = st.number_input(
                "Unit Price (€)", value=float(st.session_state.get("price", 100.0))
            )

            st.session_state.variable_cost = st.number_input(
                "Variable Cost (€)", value=float(st.session_state.get("variable_cost", 60.0))
            )

        with col2:
            st.session_state.volume = st.number_input(
                "Annual Sales Volume",
                value=int(st.session_state.get("volume", 1000)),
            )

            st.session_state.fixed_cost = st.number_input(
                "Annual Fixed Costs (€)",
                value=float(st.session_state.get("fixed_cost", 20000.0)),
            )

        st.divider()

        if st.button("🚀 Create Baseline & Start Simulation", use_container_width=True):
            lock_baseline()
            st.session_state.flow_step = "stage1"
            st.rerun()

        st.caption(
            "💡 Tip: If you don't know a number, open the Tools Library to calculate it."
        )

        if st.button("📚 Open Tools Library"):
            st.session_state.flow_step = "library"
            st.rerun()

    else:

        st.success("Baseline locked. System ready for analysis.")

        c1, c2, c3, c4 = st.columns(4)

        c1.metric("Revenue", f"{metrics.get('revenue',0):,.0f} €")
        c2.metric("EBIT", f"{metrics.get('ebit',0):,.0f} €")
        c3.metric("Break-Even Units", f"{metrics.get('bep_units',0):,.0f}")
        c4.metric("Free Cash Flow", f"{metrics.get('fcf',0):,.0f} €")

        st.divider()

        if st.button("📊 Go To Analysis"):
            st.session_state.flow_step = "stage1"
            st.rerun()
