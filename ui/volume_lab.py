import streamlit as st
from uuid import uuid4

from core.decision import DecisionFactory
from core.decision_plan import DecisionPlan


def _get_current_plan() -> DecisionPlan:
    """
    Return the current Decision Plan.

    If no valid plan exists in session state, create
    the default Current Decision Plan.
    """
    plan = st.session_state.get("decision_plan")

    if isinstance(plan, DecisionPlan):
        return plan

    plan = DecisionPlan.create(
        plan_id="main_plan",
        name="Current Decision Plan",
    )

    st.session_state.decision_plan = plan

    return plan


def render_volume_lab(baseline_state):
    """
    Volume Decision Lab.

    Creates Volume Decisions only.

    Execution is handled centrally through:

        Decision
            ↓
        DecisionPlan
            ↓
        DecisionRunner
            ↓
        Projected CompanyState
    """

    st.title("📦 Volume Lab")

    st.markdown(
        """
        Test how a change in sales volume could affect your business.
        """
    )

    # =====================================================
    # BASELINE
    # =====================================================

    current_volume = float(
        baseline_state.drivers.volume
    )

    st.info(
        f"Current baseline volume: "
        f"{current_volume:,.0f} units"
    )

    # =====================================================
    # VOLUME CHANGE
    # =====================================================

    st.subheader("Expected Volume Change")

    volume_change_pct = st.slider(
        "Change in sales volume (%)",
        min_value=-50,
        max_value=50,
        value=0,
        step=1,
        format="%d%%",
        key="volume_change_pct",
    )

    target_volume = (
        current_volume
        * (1.0 + volume_change_pct / 100.0)
    )

    st.metric(
        "Expected Volume",
        f"{target_volume:,.0f} units",
        delta=f"{volume_change_pct:+d}%",
    )

    # =====================================================
    # ADD DECISION
    # =====================================================

    if st.button(
        "Add Volume Decision",
        key="add_volume_decision",
    ):

        current_plan = _get_current_plan()

        decision = DecisionFactory.volume_change(
            decision_id=f"volume_{uuid4().hex}",
            target_volume=target_volume,
        )

        updated_plan = current_plan.add(
            decision
        )

        st.session_state.decision_plan = (
            updated_plan
        )

        st.success(
            f"Added: {decision.name}"
        )

        st.rerun()

    # =====================================================
    # CREATED VOLUME DECISIONS
    # =====================================================

    st.divider()

    st.subheader(
        "Created Volume Decisions"
    )

    current_plan = _get_current_plan()

    volume_decisions = [
        decision
        for decision in current_plan.decisions
        if decision.category == "sales"
        and "volume" in decision.changes
    ]

    if not volume_decisions:

        st.caption(
            "No volume decisions created yet."
        )

    else:

        for decision in volume_decisions:

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
        "Volume Lab creates Decisions only. "
        "Execution is performed centrally through "
        "DecisionPlan → DecisionRunner.run_many()."
    )
