"""
ui/pricing_lab.py

Pricing Decision Lab.

Pricing decisions are added directly to the
Current Decision Plan.

The locked baseline is never modified.

Execution is NOT performed here.

Architecture:

    Pricing Lab
         ↓
    Current Decision Plan
         ↓
    DecisionEvaluator / DecisionRunner
         ↓
    Projected CompanyState
"""

from __future__ import annotations

import streamlit as st
from uuid import uuid4

from core.decision import Decision, DecisionFactory
from core.decision_plan import DecisionPlan


# =========================================================
# HELPERS
# =========================================================

def _get_current_plan() -> DecisionPlan:
    """
    Return the Current Decision Plan.

    If no plan exists yet, create the central plan.
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


def _find_conflicting_driver(
    plan: DecisionPlan,
    decision: Decision,
):
    """
    Check whether the new Decision changes a driver
    already changed by an existing Decision in the plan.

    Returns:
        None
        or
        (driver_name, existing_decision_name)
    """

    existing_drivers = {}

    for existing in plan.decisions:

        for driver in existing.changes:

            existing_drivers[driver] = (
                existing.name
            )

    for driver in decision.changes:

        if driver in existing_drivers:

            return (
                driver,
                existing_drivers[driver],
            )

    return None


def _add_to_current_plan(
    decision: Decision,
) -> bool:
    """
    Add a Decision directly to the Current Decision Plan.

    Returns:
        True  -> successfully added
        False -> rejected because of conflict
    """

    current_plan = _get_current_plan()

    # -----------------------------------------------------
    # DUPLICATE CHECK
    # -----------------------------------------------------

    if current_plan.contains(decision.id):

        st.warning(
            f"Decision '{decision.name}' "
            "is already in the Current Decision Plan."
        )

        return False

    # -----------------------------------------------------
    # DRIVER CONFLICT CHECK
    # -----------------------------------------------------

    conflict = _find_conflicting_driver(
        current_plan,
        decision,
    )

    if conflict is not None:

        driver, existing_name = conflict

        st.error(
            "Conflicting Decisions detected."
        )

        st.info(
            f"'{existing_name}' and "
            f"'{decision.name}' both change "
            f"the driver '{driver}'. "
            "Remove one of them before adding "
            "another pricing decision."
        )

        return False

    # -----------------------------------------------------
    # ADD TO IMMUTABLE PLAN
    # -----------------------------------------------------

    updated_plan = current_plan.add(
        decision
    )

    st.session_state.decision_plan = (
        updated_plan
    )

    return True


def _get_pricing_decisions(
    plan: DecisionPlan,
):
    """
    Return pricing Decisions currently contained
    in the Current Decision Plan.
    """

    return [
        decision
        for decision in plan.decisions
        if getattr(
            decision,
            "category",
            None,
        ) == "pricing"
    ]


# =========================================================
# MAIN UI
# =========================================================

def render_pricing_lab(
    baseline_state,
):
    """
    Pricing Decision Lab.

    Creates pricing Decisions and adds them directly
    to the central Current Decision Plan.

    The baseline CompanyState is never modified.

    Execution remains centralized outside this UI.
    """

    st.title("💰 Pricing Lab")

    st.markdown(
        """
        Test pricing decisions against the locked baseline.

        The baseline CompanyState is never modified.

        Every pricing choice is added directly to the
        Current Decision Plan and can be evaluated together
        with other business decisions.
        """
    )

    # =====================================================
    # CURRENT DECISION PLAN
    # =====================================================

    current_plan = _get_current_plan()

    st.caption(
        f"Current Decision Plan: "
        f"{current_plan.decision_count} decision(s)"
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

        st.subheader(
            "Set a Target Price"
        )

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

            if _add_to_current_plan(
                decision
            ):

                st.success(
                    f"✓ Added to Current Decision Plan: "
                    f"{decision.name}"
                )

                st.rerun()

    # =====================================================
    # TAB 2 — PERCENTAGE CHANGE
    # =====================================================

    with tab2:

        st.subheader(
            "Adjust Price by Percentage"
        )

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
            f"Resulting price: "
            f"€ {target_price_pct:,.2f}"
        )

        if st.button(
            "Add Pricing Decision",
            key="add_pricing_pct",
        ):

            decision = DecisionFactory.price_change(
                decision_id=f"pricing_{uuid4().hex}",
                target_price=target_price_pct,
            )

            if _add_to_current_plan(
                decision
            ):

                st.success(
                    f"✓ Added to Current Decision Plan: "
                    f"{decision.name}"
                )

                st.rerun()

    # =====================================================
    # CURRENT PRICING DECISIONS
    # =====================================================

    st.divider()

    st.subheader(
        "Pricing Decisions in Current Plan"
    )

    # Refresh the plan after possible changes.
    current_plan = _get_current_plan()

    pricing_decisions = _get_pricing_decisions(
        current_plan
    )

    if not pricing_decisions:

        st.caption(
            "No pricing decisions in the "
            "Current Decision Plan."
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
    # PLAN SUMMARY
    # =====================================================

    if not current_plan.is_empty:

        st.subheader(
            "Current Decision Plan"
        )

        st.info(
            current_plan.summary()
        )

    # =====================================================
    # INFORMATION
    # =====================================================

    st.caption(
        "Pricing Lab adds Decisions directly to the "
        "Current Decision Plan. Execution is performed "
        "centrally through DecisionEvaluator / "
        "DecisionRunner."
    )
