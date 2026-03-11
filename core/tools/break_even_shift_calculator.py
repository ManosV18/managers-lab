import streamlit as st
import plotly.graph_objects as go


def show_break_even_shift_calculator():

    s = st.session_state

    st.header("🛡️ Survival Simulator")

    # -------------------------------------------------
    # BASELINE FROM HOME
    # -------------------------------------------------

    b_price = float(s.get("price", 100))
    b_vc = float(s.get("variable_cost", 60))
    b_volume = float(s.get("volume", 1000))
    b_fc = float(s.get("fixed_cost", 20000))
    b_debt = float(s.get("annual_debt_service", 0))
    b_profit = float(s.get("target_profit_goal", 0))

    # -------------------------------------------------
    # SIMULATION CONTROLS
    # -------------------------------------------------

    st.subheader("🕹️ Simulation Controls")

    col1, col2, col3 = st.columns(3)

    with col1:

        sim_price = st.slider(
            "Unit Price (€)",
            b_price * 0.5,
            b_price * 2,
            b_price
        )

        sim_vc = st.slider(
            "Variable Cost (€)",
            b_vc * 0.5,
            b_vc * 2,
            b_vc
        )

    with col2:

        sim_fc = st.slider(
            "Fixed Costs",
            b_fc * 0.5,
            b_fc * 2.5,
            b_fc
        )

        sim_debt = st.slider(
            "Debt Service",
            0.0,
            (b_debt + 5000) * 3,
            b_debt
        )

    with col3:

        sim_volume = st.slider(
            "Sales Volume",
            b_volume * 0.1,
            b_volume * 3,
            b_volume
        )

        sim_profit = st.slider(
            "Target Profit",
            0.0,
            (b_profit + 10000) * 3,
            b_profit
        )

    # -------------------------------------------------
    # CALCULATIONS
    # -------------------------------------------------

    total_burden = sim_fc + sim_debt + sim_profit

    unit_margin = sim_price - sim_vc

    if unit_margin <= 0:
        new_bep = None
    else:
        new_bep = total_burden / unit_margin

    safety_margin = sim_volume - new_bep if new_bep else None

    # -------------------------------------------------
    # RESULTS
    # -------------------------------------------------

    st.divider()

    c1, c2, c3 = st.columns(3)

    if new_bep:

        c1.metric("Break Even Units", f"{new_bep:,.0f}")

        c3.metric(
            "Volume Gap",
            f"{safety_margin:,.0f}",
            delta=f"{safety_margin:,.0f}",
            delta_color="normal" if safety_margin >= 0 else "inverse"
        )

    else:

        c1.metric("Break Even", "N/A")

        st.error("Variable cost exceeds price")

    c2.metric("Cash Burden", f"€{total_burden:,.0f}")

    # -------------------------------------------------
    # CHART
    # -------------------------------------------------

    if new_bep:

        fig = go.Figure()

        fig.add_bar(
            name="Break Even",
            x=["Scenario"],
            y=[new_bep]
        )

        fig.add_bar(
            name="Sales Volume",
            x=["Scenario"],
            y=[sim_volume]
        )

        fig.update_layout(
            barmode="group",
            height=400
        )

        st.plotly_chart(fig, use_container_width=True)

    # -------------------------------------------------
    # VERDICT
    # -------------------------------------------------

    if new_bep is None:
        st.error("🚨 Negative unit margin")

    elif safety_margin < 0:
        st.error(f"⚠️ {abs(safety_margin):,.0f} units below survival")

    else:
        st.success(f"✅ {safety_margin:,.0f} units above survival")

    if st.button("⬅ Back to Hub"):
        st.session_state.selected_tool = None
        st.rerun()
