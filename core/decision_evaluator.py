from dataclasses import dataclass
from typing import Dict, Any

from core.models import CompanyState
from core.decision_plan import DecisionPlan
from core.decision_runner import DecisionRunner
from core.financial_engine import (
    FinancialEngine,
    FinancialProjection,
)


# =========================================================
# DECISION EVALUATION
# =========================================================

@dataclass(frozen=True)
class DecisionEvaluation:
    """
    Complete evaluation of one DecisionPlan
    against one locked CompanyState.

    This is the business-facing result layer.

    It connects:

        CompanyState
             +
        DecisionPlan
             ↓
        DecisionRunner
             ↓
        Projected CompanyState
             ↓
        FinancialEngine
             ↓
        FinancialProjection
    """

    baseline_state: CompanyState
    projected_state: CompanyState
    plan: DecisionPlan
    execution_report: Dict[str, Any]
    financial_projection: FinancialProjection

    # =====================================================
    # CONVENIENCE PROPERTIES
    # =====================================================

    @property
    def impact(self):
        """
        Financial impact of the DecisionPlan.
        """
        return self.financial_projection.impact


# =========================================================
# DECISION EVALUATOR
# =========================================================

class DecisionEvaluator:
    """
    Canonical service for evaluating a DecisionPlan.

    Responsibilities:

        - accept a locked baseline
        - accept a DecisionPlan
        - execute the plan through DecisionRunner
        - calculate financial results through FinancialEngine
        - return one immutable DecisionEvaluation

    It does NOT:

        - create Decisions
        - modify Decisions
        - modify CompanyState
        - manage Streamlit state
        - resolve business conflicts
        - stack scenarios
    """

    # =====================================================
    # PUBLIC API
    # =====================================================

    @classmethod
    def evaluate(
        cls,
        baseline_state: CompanyState,
        plan: DecisionPlan,
    ) -> DecisionEvaluation:
        """
        Evaluate one DecisionPlan against one locked baseline.

        The original baseline_state is never modified.

        Returns:
            DecisionEvaluation
        """

        cls._validate_baseline(
            baseline_state
        )

        cls._validate_plan(
            plan
        )

        # =================================================
        # EMPTY PLAN
        # =================================================

        if plan.is_empty:

            projected_state = baseline_state

            execution_report = {
                "base_version": baseline_state.version,
                "final_version": baseline_state.version,
                "decision_count": 0,
                "decisions": [],
                "projection_mode": "baseline",
                "message": (
                    "Empty DecisionPlan. "
                    "Projection equals locked baseline."
                ),
            }

        # =================================================
        # EXECUTE PLAN
        # =================================================

        else:

            projected_state, execution_report = (
                DecisionRunner.run_many(
                    baseline_state,
                    list(plan.decisions),
                )
            )

        # =================================================
        # FINANCIAL PROJECTION
        # =================================================

        financial_projection = (
            FinancialEngine.build_projection(
                baseline_state,
                projected_state,
            )
        )

        # =================================================
        # RETURN IMMUTABLE EVALUATION
        # =================================================

        return DecisionEvaluation(
            baseline_state=baseline_state,
            projected_state=projected_state,
            plan=plan,
            execution_report=execution_report,
            financial_projection=financial_projection,
        )

    # =====================================================
    # VALIDATION
    # =====================================================

    @staticmethod
    def _validate_baseline(
        baseline_state: CompanyState,
    ) -> None:

        if not isinstance(
            baseline_state,
            CompanyState,
        ):
            raise TypeError(
                "DecisionEvaluator expects "
                "a CompanyState as baseline."
            )

    @staticmethod
    def _validate_plan(
        plan: DecisionPlan,
    ) -> None:

        if not isinstance(
            plan,
            DecisionPlan,
        ):
            raise TypeError(
                "DecisionEvaluator expects "
                "a DecisionPlan."
            )
