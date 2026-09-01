import streamlit as st
from uuid import uuid4

from core.decision import DecisionFactory


def render_pricing_lab(baseline_state):
    """
    Pricing Decision Lab.

    Creates Decision objects only.

    Execution is NOT performed here.

    Application execution path:

        Decision
            ↓
        DecisionPlan
            ↓
        DecisionRunner.run_many()
    """

    st.title("💰 Pricing Lab")

    st.markdown(
        """
        Test pricing decisions against the locked baseline.

        The baseline CompanyState is never modified.

        Every pricing choice creates a Decision that can be
        added to the active DecisionPlan.
        """
    )

    # =====================================================
    # BASELINE
    # =====================================================

    current_price = float(
        baseline_state.drivers.price
    )

    st.info(
        f"Current baseline price: € {current_price:,.2f}"
    )

    # =====================================================
    # PRICING OPTIONS
    # =====================================================

    tab1, tab2 = st.tabs(
        [
            "Target Price",
            "Price Adjustment %",
        ]
    )

    # =====================================================
    # TAB 1 — ABSOLUTE PRICE
    # =====================================================

    with tab1:

        st.subheader("Set a Target Price")

        target_price = st.number_input(
            "New Unit Price (€)",
            min_value=0.0,
            value=current_price,
            step=1.0,
            key="pricing_target_price",
        )

        if st.button(
            "Add Pricing Decision",
            key="add_pricing_absolute",
        ):

            decision = DecisionFactory.price_change(
                decision_id=f"pricing_{uuid4().hex}",
                target_price=target_price,
            )

            st.session_state.decisions.append(
                decision
            )

            st.success(
                f"Added: {decision.name}"
            )

            st.rerun()

    # =====================================================
    # TAB 2 — PERCENTAGE CHANGE
    # =====================================================

    with tab2:

        st.subheader("Adjust Price by Percentage")

        pct_change = st.number_input(
            "Price Change (%)",
            min_value=-99.0,
            max_value=500.0,
            value=0.0,
            step=1.0,
            key="pricing_pct_change",
        )

        target_price_pct = (
            current_price
            * (1.0 + pct_change / 100.0)
        )

        st.caption(
            f"Resulting price: € {target_price_pct:,.2f}"
        )

        if st.button(
            "Add Pricing Decision",
            key="add_pricing_pct",
        ):

            decision = DecisionFactory.price_change(
                decision_id=f"pricing_{uuid4().hex}",
                target_price=target_price_pct,
            )

            st.session_state.decisions.append(
                decision
            )

            st.success(
                f"Added: {decision.name}"
            )

            st.rerun()

    # =====================================================
    # CREATED DECISIONS
    # =====================================================

    st.divider()

    st.subheader(
        "Created Pricing Decisions"
    )

    pricing_decisions = [
        decision
        for decision in st.session_state.get(
            "decisions",
            [],
        )
        if decision.category == "pricing"
    ]

    if not pricing_decisions:

        st.caption(
            "No pricing decisions created yet."
        )

    else:

        for decision in pricing_decisions:

            st.markdown(
                f"**{decision.name}**"
            )

            st.caption(
                decision.description
            )

            st.caption(
                f"ID: `{decision.id}`"
            )

            st.divider()

    # =====================================================
    # INFORMATION
    # =====================================================

    st.caption(
        "Pricing Lab creates Decisions only. "
        "Execution is performed centrally through "
        "DecisionPlan → DecisionRunner.run_many()."
    )
