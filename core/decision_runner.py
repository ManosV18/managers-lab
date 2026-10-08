from typing import Dict, Any, Sequence, Tuple

from core.models import CompanyState
from core.decision import Decision
from core.investment_decision import InvestmentDecision
from core.decision_engine import DecisionEngine
from core.investment_integration import InvestmentIntegration
from core.investment_projection import InvestmentProjection


DecisionItem = Decision | InvestmentDecision


class DecisionRunner:
    """
    Canonical execution service for business Decisions
    and Investment Decisions.

    Core architecture:

        Locked Baseline
              ↓
        DecisionPlan
              ↓
        DecisionRunner
              ↓
        ┌───────────────────────────┐
        │ Direct Decisions          │
        │ Investment Decisions      │
        └─────────────┬─────────────┘
                      ↓
             Combined Projection
                      ↓
             Projected CompanyState

    Direct Decisions
    ----------------
    Direct Decisions modify canonical CompanyState drivers.

    They are combined and applied ONCE against the locked
    baseline.

    Investment Decisions
    --------------------
    Investments are composite project decisions.

    They are evaluated independently against the SAME locked
    baseline through InvestmentIntegration.

    Their Year-1 impacts are then integrated through
    InvestmentProjection.

    IMPORTANT
    ---------
    All decisions are evaluated from the SAME locked baseline.

    They are NOT evaluated sequentially against the result of
    another decision.

    The original CompanyState is never modified.

    DecisionRunner does NOT:

        - create Decisions
        - modify Decision objects
        - modify the original CompanyState
        - create DecisionPlans
        - manage UI state
        - calculate NPV / IRR itself
        - calculate investment economics itself

    It coordinates the execution services that own those
    responsibilities.
    """

    @classmethod
    def run_many(
        cls,
        state: CompanyState,
        decisions: Sequence[DecisionItem],
    ) -> Tuple[CompanyState, Dict[str, Any]]:
        """
        Execute a collection of direct and investment decisions.

        All items are evaluated against the same locked baseline.

        Direct Decisions:
            DecisionEngine

        Investment Decisions:
            InvestmentIntegration
            InvestmentProjection

        Returns:
            projected CompanyState
            execution report
        """

        if not isinstance(state, CompanyState):
            raise TypeError(
                "DecisionRunner expects a CompanyState."
            )

        for decision in decisions:
            if not isinstance(
                decision,
                (Decision, InvestmentDecision),
            ):
                raise TypeError(
                    "Every item in decisions must be a "
                    "Decision or InvestmentDecision."
                )

        # ---------------------------------------------------------
        # EMPTY PLAN
        # ---------------------------------------------------------

        if not decisions:
            report = {
                "base_version": state.version,
                "final_version": state.version,
                "decision_count": 0,
                "direct_decision_count": 0,
                "investment_count": 0,
                "decisions": [],
                "investments": [],
                "projection_mode": "baseline",
                "message": (
                    "No Decisions selected. "
                    "Projection equals locked baseline."
                ),
            }

            return state, report

        # ---------------------------------------------------------
        # SPLIT DECISION TYPES
        # ---------------------------------------------------------

        direct_decisions = [
            decision
            for decision in decisions
            if isinstance(decision, Decision)
        ]

        investment_decisions = [
            decision
            for decision in decisions
            if isinstance(decision, InvestmentDecision)
        ]

        # ---------------------------------------------------------
        # DIRECT DECISIONS
        # ---------------------------------------------------------

        combined_changes: Dict[str, Any] = {}
        decision_traces = []

        for decision in direct_decisions:
            changes = dict(decision.changes)

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

        direct_projected_state = state
        engine_trace = None

        if direct_decisions:
            combined_decision = Decision(
                id="combined_plan",
                name="Combined Decision Plan",
                description=(
                    f"Combined execution of "
                    f"{len(direct_decisions)} direct "
                    f"decision(s)."
                ),
                category="combined",
                changes=combined_changes,
            )

            direct_projected_state, engine_trace = (
                DecisionEngine.apply(
                    state,
                    combined_decision,
                )
            )

        # ---------------------------------------------------------
        # INVESTMENT DECISIONS
        # ---------------------------------------------------------
        #
        # IMPORTANT:
        # Investments are evaluated against `state`,
        # NOT `direct_projected_state`.
        #
        # This preserves the same-baseline architecture.
        # ---------------------------------------------------------

        investment_projected_state = state
        investment_impacts = ()
        investment_traces = []

        if investment_decisions:

            # First evaluate each investment independently.
            for investment in investment_decisions:
                result, impact = InvestmentIntegration.evaluate(
                    state,
                    investment,
                )

                investment_traces.append(
                    {
                        "investment_id": investment.id,
                        "investment_name": investment.name,
                        "description": investment.description,
                        "decision_type": "investment",
                        "status": "evaluated",
                        "npv": result.npv,
                        "irr": result.irr,
                        "payback_years": result.payback_years,
                        "year_1_impact": impact.summary(),
                    }
                )

            # Then integrate all Year-1 investment impacts
            # against the SAME locked baseline.
            investment_projected_state, investment_impacts = (
                InvestmentProjection.project(
                    state,
                    investment_decisions,
                )
            )

        # ---------------------------------------------------------
        # FINAL PROJECTION
        # ---------------------------------------------------------
        #
        # Cases:
        #
        # 1. Direct only
        #       → direct_projected_state
        #
        # 2. Investment only
        #       → investment_projected_state
        #
        # 3. Both
        #       → direct decisions are applied to the
        #         integrated investment state.
        #
        # The investment itself was still evaluated against
        # the original locked baseline.
        # ---------------------------------------------------------

        if direct_decisions and investment_decisions:

            projected_state, _ = DecisionEngine.apply(
                investment_projected_state,
                combined_decision,
            )

            projection_mode = "combined"

        elif direct_decisions:

            projected_state = direct_projected_state
            projection_mode = "direct_only"

        else:

            projected_state = investment_projected_state
            projection_mode = "investment_only"

        # ---------------------------------------------------------
        # REPORT
        # ---------------------------------------------------------

        report = {
            "base_version": state.version,
            "final_version": projected_state.version,
            "decision_count": len(decisions),
            "direct_decision_count": len(direct_decisions),
            "investment_count": len(investment_decisions),
            "projection_mode": projection_mode,
            "decisions": decision_traces,
            "investments": investment_traces,
            "combined_changes": combined_changes,
            "engine_trace": engine_trace,
            "investment_impacts": [
                impact.summary()
                for impact in investment_impacts
            ],
            "message": (
                "All items were evaluated against the same "
                "locked baseline. Direct Decisions were "
                "combined and applied once. Investment "
                "Decisions were evaluated independently and "
                "their Year-1 impacts were integrated into "
                "the projected CompanyState."
            ),
        }

        return projected_state, report
