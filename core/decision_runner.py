from dataclasses import replace
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
              Same-Baseline Evaluation
                      ↓
              Integrated Projection

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

    Their Year-1 impacts are kept separately and are later
    consumed by the FinancialEngine.

    InvestmentProjection is used only to expose the
    unambiguous CompanyState-level effects of the investment
    (for example incremental fixed operating costs,
    fixed assets and depreciation).

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
            InvestmentProjection

        Returns:
            projected CompanyState
            execution report

        The execution report contains the explicit
        InvestmentCompanyImpact objects required by the
        FinancialEngine integration layer.
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
        # ---------------------------------------------------------

        investment_projected_state = state
        investment_impacts = ()
        investment_traces = []

        if investment_decisions:

            # -----------------------------------------------------
            # Evaluate each investment independently.
            # -----------------------------------------------------

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

            # -----------------------------------------------------
            # Build the investment-only CompanyState projection.
            #
            # This is NOT the financial projection.
            #
            # It only exposes safe CompanyState-level effects.
            # Project-specific revenue, price, variable cost,
            # project NWC and project cash remain in
            # InvestmentCompanyImpact.
            # -----------------------------------------------------

            investment_projected_state = InvestmentProjection.project(
                state,
                investment_impacts,
            )

        # ---------------------------------------------------------
        # FINAL COMPANY STATE
        # ---------------------------------------------------------
        #
        # IMPORTANT:
        #
        # We do NOT do:
        #
        #     baseline
        #        ↓
        #     investment
        #        ↓
        #     direct
        #
        # That would be sequential stacking.
        #
        # Instead:
        #
        #     baseline
        #        ├── direct changes
        #        └── investment state-level changes
        #
        # and then merge the independent effects.
        # ---------------------------------------------------------

        if direct_decisions and investment_decisions:

            projected_state = cls._merge_company_state_effects(
                baseline_state=state,
                direct_state=direct_projected_state,
                investment_state=investment_projected_state,
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
            # Kept as actual objects for DecisionEvaluator /
            # FinancialEngine integration.
            "investment_impact_objects": investment_impacts,

            "message": (
                "All items were evaluated against the same "
                "locked baseline. Direct Decisions were "
                "combined and evaluated once. Investment "
                "Decisions were evaluated independently and "
                "their Year-1 impacts were kept separately "
                "for financial integration."
            ),
        }

        return projected_state, report

    # ------------------------------------------------------------------
    # COMPANY STATE MERGE
    # ------------------------------------------------------------------

    @staticmethod
    def _merge_company_state_effects(
        baseline_state: CompanyState,
        direct_state: CompanyState,
        investment_state: CompanyState,
    ) -> CompanyState:
        """
        Merge independent direct and investment effects
        starting from the SAME baseline.

        Only unambiguous CompanyState-level investment effects
        are merged here.

        Investment-specific:
            - revenue
            - project price
            - project variable cost
            - project NWC
            - project cash flow
            - CAPEX funding

        are NOT represented through CompanyState and therefore
        are deliberately excluded.

        Investment effects represented in CompanyState:
            - fixed_opex
            - fixed_assets
            - depreciation

        Direct Decisions remain responsible for their own
        CompanyState driver changes.

        No sequential application occurs.
        """

        # ---------------------------------------------------------
        # Extract the investment deltas relative to the baseline.
        # ---------------------------------------------------------

        investment_fixed_opex_delta = (
            investment_state.drivers.fixed_opex
            - baseline_state.drivers.fixed_opex
        )

        investment_fixed_assets_delta = (
            investment_state.drivers.fixed_assets
            - baseline_state.drivers.fixed_assets
        )

        investment_depreciation_delta = (
            investment_state.drivers.depreciation
            - baseline_state.drivers.depreciation
        )

        # ---------------------------------------------------------
        # Apply those deltas to the DIRECT projected state.
        #
        # This is an additive merge of two independent branches,
        # not execution of one branch on the other.
        # ---------------------------------------------------------

        merged_drivers = replace(
            direct_state.drivers,
            fixed_opex=(
                direct_state.drivers.fixed_opex
                + investment_fixed_opex_delta
            ),
            fixed_assets=(
                direct_state.drivers.fixed_assets
                + investment_fixed_assets_delta
            ),
            depreciation=(
                direct_state.drivers.depreciation
                + investment_depreciation_delta
            ),
        )

        # ---------------------------------------------------------
        # Version
        #
        # The projected state represents one combined projection
        # from the baseline, so it receives one new version.
        # ---------------------------------------------------------

        return replace(
            direct_state,
            version=baseline_state.version + 1,
            drivers=merged_drivers,
        )
