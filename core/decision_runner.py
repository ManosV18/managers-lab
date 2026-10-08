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
        ┌───────────────────────────┐
        │ Direct Decisions          │
        │ Investment Decisions      │
        └─────────────┬─────────────┘
                      ↓
              Same-Baseline Evaluation
                      ↓
        ┌───────────────────────────────┐
        │ CompanyState projection       │
        │ InvestmentCompanyImpact(s)    │
        └───────────────────────────────┘

    Direct Decisions
    ----------------
    Direct Decisions modify canonical CompanyState drivers.

    They are combined and evaluated once against the locked
    baseline.

    Investment Decisions
    --------------------
    Investments are composite project decisions.

    They are evaluated independently against the SAME locked
    baseline through InvestmentIntegration.

    Their Year-1 impacts are kept separately as canonical
    InvestmentCompanyImpact objects.

    IMPORTANT ARCHITECTURAL RULE
    ----------------------------
    Investment economics are NOT written into CompanyState.

    In particular, investment:

        - revenue
        - variable cost
        - fixed opex
        - depreciation
        - project NWC
        - CAPEX
        - operating cash flow

    remain represented by InvestmentCompanyImpact and are
    integrated by FinancialEngine.

    This prevents the same investment effect from being
    represented both inside CompanyState and again inside
    InvestmentCompanyImpact.

    CompanyState therefore represents:

        baseline company
        +
        direct Decision effects

    while investment economics remain a separate incremental
    layer.

    IMPORTANT
    ---------
    No decision is evaluated against the result of another
    decision.

    All decisions start from the same locked baseline.

    The original CompanyState is never modified.

    DecisionRunner does NOT:

        - create Decisions
        - modify Decision objects
        - modify the original CompanyState
        - create DecisionPlans
        - manage UI state
        - calculate NPV / IRR itself
        - calculate investment economics itself
        - calculate financial statements
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

        Returns:
            projected CompanyState
            execution report

        The execution report contains the explicit
        InvestmentCompanyImpact objects required by the
        FinancialEngine integration layer.

        Important
        ---------
        Investment Decisions do NOT modify CompanyState.

        Their Year-1 financial effects remain in
        InvestmentCompanyImpact.
        """

        if not isinstance(state, CompanyState):
            raise TypeError(
                "DecisionRunner expects a CompanyState."
            )

        decisions = tuple(decisions)

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
                "combined_changes": {},
                "engine_trace": None,
                "investment_impacts": [],
                "investment_impact_objects": (),
                "message": (
                    "No Decisions selected. "
                    "Projection equals locked baseline."
                ),
            }

            return state, report

        # ---------------------------------------------------------
        # SPLIT DECISION TYPES
        # ---------------------------------------------------------

        direct_decisions = tuple(
            decision
            for decision in decisions
            if isinstance(decision, Decision)
        )

        investment_decisions = tuple(
            decision
            for decision in decisions
            if isinstance(decision, InvestmentDecision)
        )

        # ---------------------------------------------------------
        # DIRECT DECISIONS
        # ---------------------------------------------------------
        #
        # All direct decisions are combined first.
        #
        # They are then applied ONCE to the locked baseline.
        #
        # No direct decision is evaluated against another direct
        # decision.
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
        # Every investment is evaluated against the ORIGINAL
        # locked baseline.
        #
        # Never use direct_projected_state here.
        #
        # IMPORTANT:
        # Investment results are NOT projected into CompanyState.
        #
        # The canonical investment representation is:
        #
        #     InvestmentCompanyImpact
        #
        # FinancialEngine consumes those objects separately.
        # ---------------------------------------------------------

        investment_impacts = ()
        investment_traces = []

        if investment_decisions:

            evaluated_impacts = []

            for investment in investment_decisions:
                result, impact = InvestmentIntegration.evaluate(
                    state,
                    investment,
                )

                evaluated_impacts.append(impact)

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

            investment_impacts = tuple(
                evaluated_impacts
            )

        # ---------------------------------------------------------
        # FINAL COMPANY STATE
        # ---------------------------------------------------------
        #
        # CompanyState contains ONLY:
        #
        #     baseline
        #       +
        #     direct Decision effects
        #
        # Investment effects are NOT merged into CompanyState.
        #
        # This is intentional because the investment impact is
        # passed separately to FinancialEngine.
        #
        # Therefore:
        #
        #     CompanyState
        #             +
        #     InvestmentCompanyImpact
        #
        # are two complementary layers, not two representations
        # of the same effect.
        # ---------------------------------------------------------

        if direct_decisions:
            projected_state = direct_projected_state
            projection_mode = (
                "direct_plus_investment_impacts"
                if investment_decisions
                else "direct_only"
            )

        elif investment_decisions:
            projected_state = state
            projection_mode = "investment_impacts_only"

        else:
            # Defensive fallback.
            projected_state = state
            projection_mode = "baseline"

        # ---------------------------------------------------------
        # REPORT
        # ---------------------------------------------------------

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
            "projection_mode": projection_mode,
            "decisions": decision_traces,
            "investments": investment_traces,
            "combined_changes": combined_changes,
            "engine_trace": engine_trace,
            "investment_impacts": [
                impact.summary()
                for impact in investment_impacts
            ],

            # IMPORTANT:
            # Kept as actual immutable objects for
            # DecisionEvaluator / FinancialEngine integration.
            "investment_impact_objects": investment_impacts,

            "message": (
                "All items were evaluated against the same "
                "locked baseline. Direct Decisions were "
                "combined and evaluated once. Investment "
                "Decisions were evaluated independently. "
                "Investment Year-1 impacts remain separate "
                "from CompanyState and are available to the "
                "financial integration layer."
            ),
        }

        return projected_state, report
