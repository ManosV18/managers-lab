from dataclasses import replace
from typing import Sequence, Tuple

from core.models import CompanyState
from core.investment_decision import InvestmentDecision
from core.investment_company_impact import InvestmentCompanyImpact
from core.investment_integration import InvestmentIntegration


class InvestmentProjection:
    """
    Builds the end-of-Year-1 CompanyState impact of investments.

    Architecture:

        Locked CompanyState
                ↓
        InvestmentDecision(s)
                ↓
        InvestmentIntegration
                ↓
        InvestmentCompanyImpact(s)
                ↓
        Aggregate Year-1 Impact
                ↓
        Projected CompanyState

    IMPORTANT
    ---------
    The investment itself may be multi-year.

    CompanyState is NOT projected year by year.

    Only the end-of-Year-1 impact is integrated into the
    existing company state.

    This class does NOT:
        - calculate NPV
        - calculate IRR
        - calculate payback
        - evaluate project economics
        - modify the locked baseline
        - apply direct Decisions
        - model future CompanyState values

    Investment economics remain the responsibility of the
    investment engine.

    This class is only the bridge from project economics to
    the company's Year-1 projected state.
    """

    @classmethod
    def project(
        cls,
        state: CompanyState,
        investments: Sequence[InvestmentDecision],
    ) -> Tuple[
        CompanyState,
        Tuple[InvestmentCompanyImpact, ...],
    ]:
        """
        Evaluate investments against the same locked baseline
        and build one projected CompanyState at the end of Year 1.

        Multiple investments are additive at Year 1.

        They are NOT evaluated sequentially against one another.
        """

        if not isinstance(state, CompanyState):
            raise TypeError(
                "InvestmentProjection expects a CompanyState."
            )

        for investment in investments:
            if not isinstance(investment, InvestmentDecision):
                raise TypeError(
                    "Every item in investments must be "
                    "an InvestmentDecision."
                )

        if not investments:
            return state, ()

        impacts = []

        for investment in investments:
            _, impact = InvestmentIntegration.evaluate(
                state,
                investment,
            )
            impacts.append(impact)

        projected_state = cls._apply_aggregate_impact(
            state,
            impacts,
        )

        return projected_state, tuple(impacts)

    @staticmethod
    def _apply_aggregate_impact(
        state: CompanyState,
        impacts: Sequence[InvestmentCompanyImpact],
    ) -> CompanyState:
        """
        Apply the aggregate Year-1 investment impact to the
        existing CompanyState.

        The investment remains incremental.

        Existing company drivers are not replaced by project
        economics such as project selling price or project
        variable cost per unit.

        Only aggregate company-level effects are added.
        """

        if not impacts:
            return state

        total_volume_delta = sum(
            impact.volume_delta
            for impact in impacts
        )

        total_fixed_assets_delta = sum(
            impact.fixed_assets_delta
            for impact in impacts
        )

        total_depreciation_delta = sum(
            impact.depreciation_delta
            for impact in impacts
        )

        total_fixed_opex_delta = sum(
            impact.fixed_opex_delta
            for impact in impacts
        )

        total_nwc_delta = sum(
            impact.nwc_delta
            for impact in impacts
        )

        total_cash_impact = sum(
            impact.project_cash_impact
            for impact in impacts
        )

        drivers = replace(
            state.drivers,
            volume=(
                state.drivers.volume
                + total_volume_delta
            ),
            fixed_opex=(
                state.drivers.fixed_opex
                + total_fixed_opex_delta
            ),
            fixed_assets=(
                state.drivers.fixed_assets
                + total_fixed_assets_delta
            ),
            depreciation=(
                state.drivers.depreciation
                + total_depreciation_delta
            ),
        )

        projected_state = replace(
            state,
            version=state.version + 1,
            label=f"{state.label} + Investment Year 1",
            drivers=drivers,
        )

        return projected_state
