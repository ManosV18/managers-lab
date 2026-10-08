from typing import Dict, Any, Sequence, Tuple

from core.models import CompanyState
from core.decision import Decision
from core.investment_decision import InvestmentDecision
from core.decision_engine import DecisionEngine
from core.investment_integration import InvestmentIntegration


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
        Combined Projection
              ↓
        Projected CompanyState

    Direct Decisions and Investment Decisions are different
    decision types and therefore follow different execution paths.

    Direct Decisions
    ----------------
    Direct Decisions modify canonical CompanyState drivers.

    They are combined and applied ONCE against the same
    locked baseline.

    Investment Decisions
    --------------------
    Investments are composite project decisions.

    They are evaluated independently against the SAME locked
    baseline through InvestmentIntegration.

    The investment's multi-year economics are evaluated, but
    CompanyState integration is limited to the Year-1 impact.

    IMPORTANT
    ---------
    Multiple Decisions are evaluated together against the
    SAME locked baseline.

    They are NOT sequentially stacked.

    The original CompanyState is never modified.

    DecisionRunner does NOT:

        - create Decisions
        - modify Decision objects
        - modify the original CompanyState
        - create DecisionPlans
        - manage UI state
        - calculate company-level FinancialProjection
        - resolve business conflicts

    It is responsible for converting a collection of Decisions
    and Investment Decisions into execution results.
    """

    @classmethod
    def run_many(
        cls,
        state: CompanyState,
        decisions: Sequence[DecisionItem],
    ) -> Tuple[CompanyState, Dict[str, Any]]:
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

        projected_state = state

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

            projected_state, engine_trace = (
                DecisionEngine.apply(
                    state,
                    combined_decision,
                )
            )

        # ---------------------------------------------------------
        # INVESTMENT DECISIONS
        # ---------------------------------------------------------

        investment_traces = []

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

        # ---------------------------------------------------------
        # REPORT
        # ---------------------------------------------------------

        report = {
            "base_version": state.version,
            "final_version": projected_state.version,
            "decision_count": len(decisions),
            "direct_decision_count": len(direct_decisions),
            "investment_count": len(investment_decisions),
            "projection_mode": (
                "combined"
                if direct_decisions
                else "investment_only"
            ),
            "decisions": decision_traces,
            "investments": investment_traces,
            "combined_changes": combined_changes,
            "engine_trace": engine_trace,
            "message": (
                "All items were evaluated against "
                "the same locked baseline. Direct Decisions "
                "were combined and applied once. Investment "
                "Decisions were evaluated independently and "
                "their Year-1 impacts were captured."
            ),
        }

        return projected_state, report
