from typing import Dict, Any, Sequence, Tuple

from core.models import CompanyState
from core.decision import Decision
from core.investment_decision import InvestmentDecision
from core.decision_engine import DecisionEngine


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
        ┌───────────────┐
        │               │
        ↓               ↓
    Direct Decisions   Investments
        │               │
        ↓               ↓
    DecisionEngine   Investment Engine
        │               │
        └───────┬───────┘
                ↓
        Year-1 Integration
                ↓
        Projected CompanyState

    IMPORTANT
    ---------
    All items are evaluated against the SAME locked baseline.

    Direct Decisions are combined and applied once.

    Investment Decisions are NOT converted into
    Decision.changes and are NOT sequentially stacked
    onto the CompanyState.

    The original CompanyState is never modified.

    DecisionRunner does NOT:

        - create Decisions
        - create InvestmentDecisions
        - modify decision objects
        - modify the original CompanyState
        - create DecisionPlans
        - manage UI state
        - calculate financial impact
        - perform investment calculations
        - sequentially stack decisions

    Its responsibility is to orchestrate the execution
    of the items contained in a DecisionPlan.
    """

    # =========================================================
    # CANONICAL EXECUTION PATH
    # =========================================================

    @classmethod
    def run_many(
        cls,
        state: CompanyState,
        decisions: Sequence[DecisionItem],
    ) -> Tuple[CompanyState, Dict[str, Any]]:
        """
        Execute multiple Decisions and Investment Decisions
        as ONE Combined Plan.

        All items are evaluated against the SAME
        starting CompanyState.

        Direct Decisions:
            - combined into one set of driver changes
            - applied once through DecisionEngine

        Investment Decisions:
            - remain separate investment objects
            - are evaluated through the investment layer
            - their Year-1 impacts are later integrated
              into the projected CompanyState

        Parameters
        ----------
        state:
            Locked baseline CompanyState.

        decisions:
            Sequence containing Decision and/or InvestmentDecision.

        Returns
        -------
        projected_state:
            Projected CompanyState.

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
                (Decision, InvestmentDecision),
            ):
                raise TypeError(
                    "Every item in decisions must be "
                    "a Decision or InvestmentDecision."
                )

        # =====================================================
        # EMPTY PLAN
        # =====================================================

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

            return (
                state,
                report,
            )

        # =====================================================
        # SEPARATE DECISION TYPES
        # =====================================================

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

        # =====================================================
        # DIRECT DECISIONS
        # =====================================================
        #
        # Direct Decisions retain their existing execution
        # architecture.
        #
        # They are combined against the ORIGINAL baseline
        # and applied exactly once.
        #
        # =====================================================

        projected_state = state

        combined_changes: Dict[str, Any] = {}
        decision_traces = []

        for decision in direct_decisions:

            changes = dict(
                decision.changes
            )

            # ---------------------------------------------
            # Detect duplicate drivers
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
        # APPLY DIRECT DECISIONS
        # =====================================================

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

        # =====================================================
        # INVESTMENT DECISIONS
        # =====================================================
        #
        # IMPORTANT:
        #
        # Investments are NOT converted into changes such as:
        #
        #     price = ...
        #     volume = ...
        #     fixed_opex = ...
        #
        # They have their own project economics and will
        # produce a Year-1 InvestmentCompanyImpact.
        #
        # The actual investment evaluation/integration layer
        # is deliberately kept outside DecisionEngine.
        #
        # =====================================================

        investment_traces = []

        for investment in investment_decisions:

            investment_traces.append(
                {
                    "investment_id": investment.id,
                    "investment_name": investment.name,
                    "description": investment.description,
                    "decision_type": "investment",
                    "status": "pending_year_1_integration",
                }
            )

        # =====================================================
        # EXECUTION REPORT
        # =====================================================

        report = {
            "base_version": state.version,
            "final_version": projected_state.version,
            "decision_count": len(decisions),
            "direct_decision_count": len(
                direct_decisions
            ),
            "investment_count": len(
                investment_decisions
            ),
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
                "Decisions remain separate project decisions "
                "for Year-1 integration."
            ),
        }

        return (
            projected_state,
            report,
        )
