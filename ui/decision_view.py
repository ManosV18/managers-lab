import streamlit as st
from core.decision import Decision
from core.decision_plan import DecisionPlan


# =========================================================
# WORKING CAPITAL CANDIDATE KEYS
# =========================================================

WC_AR_CANDIDATE = "wc_ar_candidate"
WC_INVENTORY_CANDIDATE = "wc_inventory_candidate"
WC_AP_CANDIDATE = "wc_ap_candidate"


# =========================================================
# HELPERS
# =========================================================

def _get_current_plan() -> DecisionPlan:
    """
    Return the current Decision Plan.

    The Current Decision Plan is the central workspace
    for business decisions.
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


def _get_wc_candidates():
    """
    Return temporary Working Capital Decision candidates.
    """

    candidates = []

    ar_candidate = st.session_state.get(
        WC_AR_CANDIDATE
    )

    inventory_candidate = st.session_state.get(
        WC_INVENTORY_CANDIDATE
    )

    ap_candidate = st.session_state.get(
        WC_AP_CANDIDATE
    )

    if isinstance(ar_candidate, Decision):
        candidates.append(
            ("Working Capital — AR", ar_candidate)
        )

    if isinstance(
        inventory_candidate,
        Decision,
    ):
        candidates.append(
            (
                "Working Capital — Inventory",
                inventory_candidate,
            )
        )

    if isinstance(ap_candidate, Decision):
        candidates.append(
            (
                "Working Capital — AP",
                ap_candidate,
            )
        )

    return candidates


def _get_available_decisions():
    """
    Collect Decisions that can still be added to the
    Current Decision Plan.

    Sources:
    - legacy saved Decisions
    - temporary Working Capital candidates
    """

    available = []

    # -----------------------------------------------------
    # Legacy saved Decisions
    # -----------------------------------------------------

    for decision in st.session_state.get(
        "decisions",
        [],
    ):

        if isinstance(decision, Decision):
            available.append(
                ("Decision Lab", decision)
            )

    # -----------------------------------------------------
    # Working Capital candidates
    # -----------------------------------------------------

    for source, decision in _get_wc_candidates():

        if not any(
            existing.id == decision.id
            for _, existing in available
        ):

            available.append(
                (source, decision)
            )

    return available


def _find_conflicting_driver(
    plan: DecisionPlan,
    decision: Decision,
):
    """
    Return the name of an existing Decision if the new
    Decision changes a driver already changed by the Plan.

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


def _source_for_decision(
    decision: Decision,
    wc_candidates,
) -> str:

    for source, candidate in wc_candidates:

        if candidate.id == decision.id:
            return source

    return "Decision Lab"


# =========================================================
# DECISION MANAGER
# =========================================================

def render_decision_view() -> None:
    """
    Current Decision Plan manager.

    Responsibilities:
    - Display the current Decision Plan.
    - Display Decisions that can be added.
    - Allow Decisions to be added to the current Plan.
    - Allow Decisions to be removed from the current Plan.
    - Show combined driver changes.
    - Direct the user to the Control Tower.

    This UI does NOT:
    - execute Decisions
    - calculate financial impact
    - modify CompanyState
    - apply Decisions
    - resolve conflicting Decisions silently
    """

    st.title("🎯 Decision Manager")

    st.caption(
        "Build and review the Current Decision Plan "
        "before evaluating its combined impact in the Control Tower."
    )

    # =====================================================
    # SESSION STATE
    # =====================================================

    current_plan = _get_current_plan()

    # =====================================================
    # CURRENT DECISION PLAN
    # =====================================================

    st.subheader("🎯 Current Decision Plan")

    if current_plan.is_empty:

        st.info(
            "No decisions have been added to the current plan yet."
        )

        st.caption(
            "Go to a Decision Lab, create a decision, "
            "and add it to the Current Decision Plan."
        )

    else:

        st.success(
            f"{current_plan.decision_count} decision(s) "
            "currently in the plan."
        )

        wc_candidates = _get_wc_candidates()

        plan_rows = []

        for position, decision in enumerate(
            current_plan.decisions,
            start=1,
        ):

            plan_rows.append(
                {
                    "Order": position,
                    "Decision": decision.name,
                    "Category": decision.category,
                    "Source": _source_for_decision(
                        decision,
                        wc_candidates,
                    ),
                    "ID": decision.id,
                }
            )

        st.dataframe(
            plan_rows,
            use_container_width=True,
            hide_index=True,
        )

        st.caption(
            current_plan.summary()
        )

        # -------------------------------------------------
        # COMBINED DRIVER CHANGES
        # -------------------------------------------------

        st.markdown(
            "#### Combined Driver Changes"
        )

        change_rows = []

        for decision in current_plan.decisions:

            for driver, value in (
                decision.changes.items()
            ):

                change_rows.append(
                    {
                        "Decision": decision.name,
                        "Driver": driver,
                        "Value": value,
                    }
                )

        if change_rows:

            st.dataframe(
                change_rows,
                use_container_width=True,
                hide_index=True,
            )

        # -------------------------------------------------
        # REMOVE DECISION
        # -------------------------------------------------

        st.markdown(
            "#### Remove a Decision"
        )

        remove_labels = {
            f"{decision.name} [{decision.id}]":
                decision.id
            for decision in current_plan.decisions
        }

        selected_to_remove = st.selectbox(
            "Decision",
            options=list(
                remove_labels.keys()
            ),
            index=None,
            placeholder="Select a decision to remove",
            key="decision_to_remove",
        )

        if st.button(
            "Remove Selected Decision",
            use_container_width=True,
            disabled=selected_to_remove is None,
            key="remove_selected_decision",
        ):

            decision_id = remove_labels[
                selected_to_remove
            ]

            st.session_state.decision_plan = (
                current_plan.remove(
                    decision_id
                )
            )

            st.rerun()

    # =====================================================
    # ADD AVAILABLE DECISIONS
    # =====================================================

    st.divider()

    st.subheader(
        "➕ Add Decisions to Current Plan"
    )

    available_decisions = (
        _get_available_decisions()
    )

    current_plan_ids = {
        decision.id
        for decision in current_plan.decisions
    }

    addable_decisions = [
        (source, decision)
        for source, decision in available_decisions
        if decision.id not in current_plan_ids
    ]

    if not addable_decisions:

        st.caption(
            "No additional Decisions are currently available."
        )

    else:

        decision_labels = []

        label_to_decision = {}

        for source, decision in addable_decisions:

            label = (
                f"{decision.name} "
                f"[{decision.id}]"
            )

            decision_labels.append(
                label
            )

            label_to_decision[label] = (
                decision
            )

        selected_labels = st.multiselect(
            "Available Decisions",
            options=decision_labels,
            help=(
                "Select one or more Decisions "
                "to add to the Current Decision Plan."
            ),
            key="available_decisions_to_add",
        )

        selected_decisions = [
            label_to_decision[label]
            for label in selected_labels
        ]

        if selected_decisions:

            st.markdown(
                "#### Selected"
            )

            preview_rows = []

            for decision in selected_decisions:

                source = _source_for_decision(
                    decision,
                    _get_wc_candidates(),
                )

                preview_rows.append(
                    {
                        "Decision": decision.name,
                        "Category": decision.category,
                        "Source": source,
                    }
                )

            st.dataframe(
                preview_rows,
                use_container_width=True,
                hide_index=True,
            )

        if st.button(
            "➕ Add Selected to Current Decision Plan",
            type="primary",
            use_container_width=True,
            disabled=not selected_decisions,
            key="add_selected_to_current_plan",
        ):

            updated_plan = current_plan

            conflict_found = False

            for decision in selected_decisions:

                # -----------------------------------------
                # DUPLICATE CHECK
                # -----------------------------------------

                if updated_plan.contains(
                    decision.id
                ):
                    continue

                # -----------------------------------------
                # DRIVER CONFLICT CHECK
                # -----------------------------------------

                conflict = (
                    _find_conflicting_driver(
                        updated_plan,
                        decision,
                    )
                )

                if conflict is not None:

                    driver, existing_name = (
                        conflict
                    )

                    st.error(
                        "Conflicting Decisions detected."
                    )

                    st.info(
                        f"'{existing_name}' and "
                        f"'{decision.name}' both change "
                        f"the driver '{driver}'. "
                        "Select only one of these Decisions."
                    )

                    conflict_found = True
                    break

                # -----------------------------------------
                # ADD TO CURRENT PLAN
                # -----------------------------------------

                updated_plan = (
                    updated_plan.add(
                        decision
                    )
                )

            if not conflict_found:

                st.session_state.decision_plan = (
                    updated_plan
                )

                st.success(
                    "✓ Selected Decisions added "
                    "to the Current Decision Plan."
                )

                st.rerun()

    # =====================================================
    # CONTROL TOWER
    # =====================================================

    if not current_plan.is_empty:

        st.divider()

        st.subheader(
            "📊 Evaluate the Decision Plan"
        )

        st.write(
            "The Current Decision Plan will be evaluated "
            "against the same locked baseline in the Control Tower."
        )

        st.info(
            "Decisions change the company. "
            "The Control Tower shows the combined financial "
            "and liquidity consequences."
        )

        if st.button(
            "📊 Go to Control Tower",
            type="primary",
            use_container_width=True,
            key="go_to_control_tower",
        ):

            st.session_state.current_page = (
                "📊 Control Tower"
            )

            st.rerun()

    # =====================================================
    # CLEAR CURRENT PLAN
    # =====================================================

    if not current_plan.is_empty:

        st.divider()

        if st.button(
            "🗑️ Clear Current Decision Plan",
            use_container_width=True,
            key="clear_decision_plan",
        ):

            st.session_state.decision_plan = (
                DecisionPlan.create(
                    plan_id="main_plan",
                    name="Current Decision Plan",
                )
            )

            st.rerun()

    # =====================================================
    # RESET DECISION WORKSPACE
    # =====================================================

    st.divider()

    st.subheader(
        "🧹 Reset Decision Workspace"
    )

    st.caption(
        "Remove all saved Decisions and Working Capital "
        "candidates and start a new decision cycle. "
        "The locked Baseline is not affected."
    )

    if st.button(
        "🗑️ Reset All Decisions",
        use_container_width=True,
        key="reset_all_decisions",
    ):

        # -------------------------------------------------
        # CLEAR LEGACY SAVED DECISIONS
        # -------------------------------------------------

        st.session_state["decisions"] = []

        # -------------------------------------------------
        # CLEAR CURRENT PLAN
        # -------------------------------------------------

        st.session_state["decision_plan"] = (
            DecisionPlan.create(
                plan_id="main_plan",
                name="Current Decision Plan",
            )
        )

        # -------------------------------------------------
        # CLEAR WORKING CAPITAL CANDIDATES
        # -------------------------------------------------

        st.session_state.pop(
            WC_AR_CANDIDATE,
            None,
        )

        st.session_state.pop(
            WC_INVENTORY_CANDIDATE,
            None,
        )

        st.session_state.pop(
            WC_AP_CANDIDATE,
            None,
        )

        # -------------------------------------------------
        # CLEAR OTHER DECISION-RELATED STATE
        # -------------------------------------------------

        st.session_state.pop(
            "selected_decision",
            None,
        )

        st.session_state.pop(
            "wacc_locked",
            None,
        )

        st.session_state.pop(
            "wacc_result",
            None,
        )

        st.success(
            "🧹 Decision Workspace reset. "
            "You can now start a new decision cycle."
        )

        st.rerun()
