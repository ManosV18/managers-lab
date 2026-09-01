import streamlit as st
from uuid import uuid4

from core.decision import Decision
from core.decision_plan import DecisionPlan


# =========================================================
# WORKING CAPITAL CANDIDATE KEYS
# =========================================================

WC_AR_CANDIDATE = "wc_ar_candidate"
WC_INVENTORY_CANDIDATE = "wc_inventory_candidate"
WC_AP_CANDIDATE = "wc_ap_candidate"


# =========================================================
# DECISION MANAGER
# =========================================================

def render_decision_view() -> None:
    """
    Decision Manager UI.

    Responsibilities:
    - Display saved Decisions.
    - Display Working Capital candidates.
    - Allow selection of ONE or MULTIPLE decisions.
    - Create a DecisionPlan.
    - Store the DecisionPlan in session state.

    IMPORTANT
    ---------
    Working Capital candidates are temporary candidates.

    They are NOT copied into:
        st.session_state.decisions

    Instead, the Decision Manager reads them directly from
    their Working Capital candidate keys.

    Execution is handled separately by:

        DecisionPlan
             ↓
        DecisionRunner
             ↓
        Projected CompanyState
             ↓
        Control Tower

    This UI does NOT:
    - execute Decisions
    - calculate financial impact
    - modify CompanyState
    - apply Decisions
    - resolve conflicts
    """

    st.title("🎯 Decision Manager")

    st.caption(
        "Select one or multiple business decisions "
        "for combined evaluation in the Control Tower."
    )

    # =====================================================
    # SESSION STATE
    # =====================================================

    if "decisions" not in st.session_state:
        st.session_state.decisions = []

    if "decision_plan" not in st.session_state:
        st.session_state.decision_plan = None

    # =====================================================
    # COLLECT AVAILABLE DECISIONS
    # =====================================================
    #
    # There are two sources:
    #
    # 1. Normal Decisions
    #
    #       st.session_state.decisions
    #
    # 2. Working Capital candidates
    #
    #       wc_ar_candidate
    #       wc_inventory_candidate
    #       wc_ap_candidate
    #
    # Working Capital candidates remain candidates.
    # We only expose them here for selection.
    #
    # =====================================================

    saved_decisions = st.session_state.get(
        "decisions",
        [],
    )

    valid_saved_decisions = [
        decision
        for decision in saved_decisions
        if isinstance(decision, Decision)
    ]

    # =====================================================
    # WORKING CAPITAL CANDIDATES
    # =====================================================

    wc_candidates = []

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
        wc_candidates.append(ar_candidate)

    if isinstance(
        inventory_candidate,
        Decision,
    ):
        wc_candidates.append(
            inventory_candidate
        )

    if isinstance(ap_candidate, Decision):
        wc_candidates.append(ap_candidate)

    # =====================================================
    # COMBINED AVAILABLE DECISIONS
    # =====================================================

    available_decisions = []

    # -----------------------------------------------------
    # Add normal Decisions
    # -----------------------------------------------------

    for decision in valid_saved_decisions:

        available_decisions.append(
            decision
        )

    # -----------------------------------------------------
    # Add Working Capital candidates
    # -----------------------------------------------------

    for decision in wc_candidates:

        # Prevent accidental duplication if a candidate
        # was somehow already stored in decisions.
        if not any(
            existing.id == decision.id
            for existing in available_decisions
        ):

            available_decisions.append(
                decision
            )

    # =====================================================
    # NO DECISIONS
    # =====================================================

    if not available_decisions:

        st.info(
            "No business decisions are currently available."
        )

        st.caption(
            "Use one of the Decision Labs to create a "
            "Decision or select a Working Capital policy."
        )

        return

    # =====================================================
    # AVAILABLE DECISIONS
    # =====================================================

    st.subheader(
        "Available Decisions"
    )

    rows = []

    for decision in available_decisions:

        # Identify source for transparency.
        if decision in wc_candidates:

            if decision is ar_candidate:
                source = "Working Capital — AR"

            elif decision is inventory_candidate:
                source = "Working Capital — Inventory"

            elif decision is ap_candidate:
                source = "Working Capital — AP"

            else:
                source = "Working Capital"

        else:

            source = "Decision Lab"

        rows.append(
            {
                "Decision": decision.name,
                "Category": decision.category,
                "Source": source,
                "Description": decision.description,
            }
        )

    st.dataframe(
        rows,
        use_container_width=True,
        hide_index=True,
    )

    st.divider()

    # =====================================================
    # MULTI-DECISION SELECTION
    # =====================================================

    st.subheader(
        "🎯 Select Decisions"
    )

    st.caption(
        "Select one or more decisions. "
        "They will be evaluated together against "
        "the same locked baseline."
    )

    # =====================================================
    # CURRENT PLAN
    # =====================================================

    current_plan = (
        st.session_state.get(
            "decision_plan"
        )
    )

    current_plan_ids = set()

    if isinstance(
        current_plan,
        DecisionPlan,
    ):

        current_plan_ids = {
            decision.id
            for decision in current_plan.decisions
            if isinstance(
                decision,
                Decision,
            )
        }

    # =====================================================
    # DECISION LABELS
    # =====================================================

    decision_labels = []

    label_to_decision = {}

    for decision in available_decisions:

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

    # =====================================================
    # DEFAULT SELECTION
    # =====================================================

    default_selections = [
        label
        for label, decision
        in label_to_decision.items()
        if decision.id in current_plan_ids
    ]

    selected_labels = st.multiselect(
        "Business Decisions",
        options=decision_labels,
        default=default_selections,
        help=(
            "Select one or more decisions. "
            "They will be combined into one "
            "Decision Plan."
        ),
    )

    selected_decisions = [
        label_to_decision[label]
        for label in selected_labels
    ]

    # =====================================================
    # SELECTED DECISIONS PREVIEW
    # =====================================================

    if selected_decisions:

        st.markdown(
            "### Selected Decision Plan"
        )

        st.info(
            f"{len(selected_decisions)} decision(s) "
            "will be evaluated together."
        )

        preview_rows = []

        for decision in selected_decisions:

            if decision in wc_candidates:

                if decision is ar_candidate:
                    source = "Working Capital — AR"

                elif decision is inventory_candidate:
                    source = (
                        "Working Capital — Inventory"
                    )

                elif decision is ap_candidate:
                    source = (
                        "Working Capital — AP"
                    )

                else:
                    source = "Working Capital"

            else:

                source = "Decision Lab"

            preview_rows.append(
                {
                    "Decision": decision.name,
                    "Category": decision.category,
                    "Source": source,
                    "ID": decision.id,
                }
            )

        st.dataframe(
            preview_rows,
            use_container_width=True,
            hide_index=True,
        )

        # =================================================
        # COMBINED DRIVER CHANGES
        # =================================================

        st.markdown(
            "#### Combined Driver Changes"
        )

        change_rows = []

        for decision in selected_decisions:

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

    else:

        st.warning(
            "No decisions selected."
        )

    # =====================================================
    # CREATE DECISION PLAN
    # =====================================================

    st.divider()

    if st.button(
        "🚀 Use Selected Decisions in Control Tower",
        type="primary",
        use_container_width=True,
        disabled=not selected_decisions,
    ):

        # -------------------------------------------------
        # DUPLICATE DRIVER CHECK
        # -------------------------------------------------
        #
        # We do an early UI-level check so the user can see
        # obvious conflicts before reaching DecisionRunner.
        #
        # DecisionRunner remains the canonical execution
        # authority and performs its own validation.
        #
        # -------------------------------------------------

        drivers = {}

        conflict_found = False

        for decision in selected_decisions:

            for driver in decision.changes:

                if driver in drivers:

                    st.error(
                        "Conflicting Decisions detected: "
                        f"driver '{driver}' is changed by "
                        "more than one selected Decision."
                    )

                    st.info(
                        f"Conflict between "
                        f"'{drivers[driver]}' and "
                        f"'{decision.name}'. "
                        "Please select only one Decision "
                        f"for driver '{driver}'."
                    )

                    conflict_found = True

                    break

                drivers[driver] = (
                    decision.name
                )

            if conflict_found:
                break

        # -------------------------------------------------
        # STOP IF CONFLICT EXISTS
        # -------------------------------------------------

        if conflict_found:

            st.warning(
                "Decision Plan was not created. "
                "Resolve the conflicting driver first."
            )

            return

        # -------------------------------------------------
        # CREATE PLAN
        # -------------------------------------------------

        decision_plan = DecisionPlan(
            id=(
                f"plan_"
                f"{uuid4().hex}"
            ),
            name=" + ".join(
                decision.name
                for decision in selected_decisions
            ),
            decisions=tuple(
                selected_decisions
            ),
        )

        # -------------------------------------------------
        # STORE PLAN
        # -------------------------------------------------

        st.session_state.decision_plan = (
            decision_plan
        )

        # -------------------------------------------------
        # CONFIRMATION
        # -------------------------------------------------

        st.success(
            f"Decision Plan created with "
            f"{len(selected_decisions)} decision(s)."
        )

        st.info(
            "Go to Control Tower to evaluate the "
            "combined financial impact."
        )

    # =====================================================
    # CURRENT ACTIVE PLAN
    # =====================================================

    active_plan = (
        st.session_state.get(
            "decision_plan"
        )
    )

    if isinstance(
        active_plan,
        DecisionPlan,
    ):

        st.divider()

        st.success(
            f"🎯 Current Control Tower Plan: "
            f"{active_plan.name}"
        )

        st.write(
            f"**Decisions in Plan:** "
            f"{active_plan.decision_count}"
        )

        plan_rows = []

        for decision in active_plan.decisions:

            if decision in wc_candidates:

                if decision is ar_candidate:
                    source = "Working Capital — AR"

                elif decision is inventory_candidate:
                    source = (
                        "Working Capital — Inventory"
                    )

                elif decision is ap_candidate:
                    source = (
                        "Working Capital — AP"
                    )

                else:
                    source = "Working Capital"

            else:

                source = "Decision Lab"

            plan_rows.append(
                {
                    "Decision": decision.name,
                    "Category": decision.category,
                    "Source": source,
                    "ID": decision.id,
                }
            )

        st.dataframe(
            plan_rows,
            use_container_width=True,
            hide_index=True,
        )

        # -------------------------------------------------
        # PLAN SUMMARY
        # -------------------------------------------------

        st.caption(
            active_plan.summary()
        )


        # -------------------------------------------------
        # CLEAR PLAN
        # -------------------------------------------------

        if st.button(
            "🗑️ Clear Decision Plan",
            use_container_width=True,
            key="clear_decision_plan",
        ):

            st.session_state.decision_plan = None

            st.rerun()


    # =====================================================
    # RESET DECISION WORKSPACE
    # =====================================================

    st.divider()

    st.subheader("🧹 Reset Decision Workspace")

    st.caption(
        "Remove all saved decisions and working-capital "
        "candidates and start a new decision cycle. "
        "The locked Baseline is not affected."
    )

    if st.button(
        "🗑️ Reset All Decisions",
        use_container_width=True,
        key="reset_all_decisions",
    ):

        # -------------------------------------------------
        # CLEAR SAVED DECISIONS
        # -------------------------------------------------

        st.session_state["decisions"] = []

        # -------------------------------------------------
        # CLEAR CURRENT DECISION PLAN
        # -------------------------------------------------

        st.session_state["decision_plan"] = None

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
