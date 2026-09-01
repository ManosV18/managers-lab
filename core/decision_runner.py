from typing import Dict, Any, Sequence, Tuple

from core.models import CompanyState
from core.decision import Decision
from core.decision_engine import DecisionEngine


class DecisionRunner:
    """
    Canonical execution service for business Decisions.

    Core architecture:

        Locked Baseline
              ↓
        DecisionPlan
              ↓
        DecisionRunner
              ↓
        Combined Projection
              ↓
        Projected CompanyState

    IMPORTANT
    ---------
    Multiple Decisions are evaluated together against
    the SAME locked baseline.

    They are NOT sequentially stacked.

    Example:

        Baseline
           │
           ├── Price change
           ├── AR days change
           ├── AP days change
           ├── Inventory days change
           └── WACC change
                    │
                    ↓
          Combined Projected State

    The original CompanyState is never modified.

    DecisionRunner does NOT:

        - create Decisions
        - modify Decision objects
        - modify the original CompanyState
        - create DecisionPlans
        - manage UI state
        - calculate financial impact
        - resolve business conflicts

    It is responsible only for converting a collection
    of Decisions into ONE combined projected CompanyState.
    """

    # =========================================================
    # CANONICAL EXECUTION PATH
    # =========================================================

    @classmethod
    def run_many(
        cls,
        state: CompanyState,
        decisions: Sequence[Decision],
    ) -> Tuple[CompanyState, Dict[str, Any]]:
        """
        Execute multiple Decisions as ONE Combined Plan.

        All Decisions are evaluated against the SAME
        starting CompanyState.

        Example:

            Baseline
               │
               ├── Price → €160
               ├── AR → 60 days
               ├── AP → 60 days
               ├── Inventory → 60 days
               └── WACC → 7%
                       │
                       ↓
                Combined State

        This is NOT:

            Baseline
                ↓
            Price
                ↓
            AR
                ↓
            AP
                ↓
            WACC

        Parameters
        ----------
        state:
            Locked baseline CompanyState.

        decisions:
            List of Decisions forming the Combined Plan.

        Returns
        -------
        projected_state:
            One CompanyState containing the combined changes.

        execution_report:
            Transparent execution trace.
        """

        # =====================================================
        # VALIDATION
        # =====================================================

        if not isinstance(
            state,
            CompanyState,
        ):
            raise TypeError(
                "DecisionRunner expects a CompanyState."
            )

        for decision in decisions:

            if not isinstance(
                decision,
                Decision,
            ):
                raise TypeError(
                    "Every item in decisions "
                    "must be a Decision."
                )

        # =====================================================
        # EMPTY PLAN
        # =====================================================

        if not decisions:

            report = {
                "base_version": state.version,
                "final_version": state.version,
                "decision_count": 0,
                "decisions": [],
                "projection_mode": "baseline",
                "message": (
                    "No Decisions selected. "
                    "Projection equals locked baseline."
                ),
            }

            return (
                state,
                report,
            )

        # =====================================================
        # COLLECT ALL CHANGES
        # =====================================================
        #
        # Every Decision is evaluated against the ORIGINAL
        # baseline.
        #
        # We deliberately do NOT call:
        #
        #     DecisionEngine.apply(current_state, decision)
        #
        # because that would create sequential stacking.
        #
        # =====================================================

        combined_changes: Dict[str, Any] = {}

        decision_traces = []

        for decision in decisions:
            
            changes = dict(
                decision.changes
            )

            # ---------------------------------------------
            # Detect duplicate drivers
            # ---------------------------------------------
            #
            # Example:
            #
            # Decision A:
            #     price = 160
            #
            # Decision B:
            #     price = 170
            #
            # This is ambiguous and should NOT silently
            # overwrite the first decision.
            #
            # ---------------------------------------------

            for key, value in changes.items():

                if key in combined_changes:

                    raise ValueError(
                        f"Conflicting Decisions detected: "
                        f"driver '{key}' is changed by "
                        f"more than one Decision."
                    )

                combined_changes[key] = value

            decision_traces.append(
                {
                    "decision_id": decision.id,
                    "decision_name": decision.name,
                    "decision_category": decision.category,
                    "description": decision.description,
                    "changes": changes,
                }
            )

        # =====================================================
        # BUILD COMBINED DECISION
        # =====================================================
        #
        # DecisionEngine already knows how to apply the
        # supported driver changes.
        #
        # We therefore create ONE internal combined Decision
        # and apply it ONCE to the ORIGINAL baseline.
        #
        # This preserves the existing DecisionEngine contract.
        #
        # =====================================================

        combined_decision = Decision(
            id="combined_plan",
            name="Combined Decision Plan",
            description=(
                f"Combined execution of "
                f"{len(decisions)} decision(s)."
            ),
            category="combined",
            changes=combined_changes,
        )

        # =====================================================
        # SINGLE APPLICATION TO BASELINE
        # =====================================================

        projected_state, engine_trace = (
            DecisionEngine.apply(
                state,
                combined_decision,
            )
        )

        # =====================================================
        # EXECUTION REPORT
        # =====================================================

        report = {
            "base_version": state.version,
            "final_version": projected_state.version,
            "decision_count": len(decisions),
            "projection_mode": "combined",
            "decisions": decision_traces,
            "combined_changes": combined_changes,
            "engine_trace": engine_trace,
            "message": (
                "All Decisions were evaluated together "
                "against the same locked baseline."
            ),
        }

        return (
            projected_state,
            report,
        )
