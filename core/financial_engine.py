from dataclasses import replace
from typing import Sequence, Tuple

from core.models import CompanyState
from core.investment_decision import InvestmentDecision
from core.investment_company_impact import InvestmentCompanyImpact
from core.investment_integration import InvestmentIntegration


class InvestmentProjection:
    """
    Builds the integrated CompanyState at the end of Year 1
    after accepting one or more investment decisions.

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
        Integrated CompanyState

    IMPORTANT
    ---------
    The investment may be multi-year.

    CompanyState is projected ONLY at the end of Year 1.

    The project remains a separate economic object during
    investment evaluation.

    Once the Year-1 impact is known, the project is integrated
    into the existing company through aggregate company
    economics.

    The integrated CompanyState therefore represents:

        Existing Company
              +
        Year-1 Project Impact

    without pretending that the project has the same price
    or variable cost per unit as the existing business.

    This class does NOT:
        - calculate NPV
        - calculate IRR
        - calculate Payback
        - evaluate project economics
        - modify the locked baseline
        - apply direct Decisions
        - project CompanyState year by year
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
        Evaluate all investments against the SAME locked baseline
        and build ONE integrated CompanyState at the end of Year 1.

        Multiple investments are additive.

        They are NOT evaluated sequentially against each other.
        """

        if not isinstance(state, CompanyState):
            raise TypeError(
                "InvestmentProjection expects a CompanyState."
            )

        for investment in investments:
            if not isinstance(
                investment,
                InvestmentDecision,
            ):
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
        Convert aggregate incremental investment economics into
        one integrated Year-1 CompanyState.

        The key rule is that project economics are NOT forced
        into the existing company's price or variable-cost
        assumptions individually.

        Instead, the integrated CompanyState uses mathematically
        equivalent blended company drivers:

            Total Revenue
                =
            Existing Revenue + Project Revenue

            Total COGS
                =
            Existing COGS + Project Variable Cost

        This preserves the economics of both businesses while
        allowing the existing FinancialEngine to calculate one
        integrated company state.

        The blended drivers are therefore a representation of
        the combined company, not a statement that the project
        itself has the company's baseline price or cost structure.
        """

        if not impacts:
            return state

        # ---------------------------------------------------------
        # 1. BASELINE ECONOMICS
        # ---------------------------------------------------------

        base_volume = float(state.drivers.volume)
        base_price = float(state.drivers.price)
        base_variable_cost = float(
            state.drivers.variable_cost_per_unit
        )

        base_revenue = base_volume * base_price
        base_cogs = base_volume * base_variable_cost

        # ---------------------------------------------------------
        # 2. AGGREGATE PROJECT IMPACT
        # ---------------------------------------------------------

        total_volume_delta = sum(
            impact.volume_delta
            for impact in impacts
        )

        total_revenue_delta = sum(
            impact.revenue_delta
            for impact in impacts
        )

        total_variable_cost_delta = sum(
            impact.variable_cost_delta
            for impact in impacts
        )

        total_fixed_opex_delta = sum(
            impact.fixed_opex_delta
            for impact in impacts
        )

        total_depreciation_delta = sum(
            impact.depreciation_delta
            for impact in impacts
        )

        total_fixed_assets_delta = sum(
            impact.fixed_assets_delta
            for impact in impacts
        )

        total_cash_impact = sum(
            impact.project_cash_impact
            for impact in impacts
        )

        # ---------------------------------------------------------
        # 3. INTEGRATED COMPANY VOLUME
        # ---------------------------------------------------------

        projected_volume = (
            base_volume
            + total_volume_delta
        )

        if projected_volume <= 0:
            raise ValueError(
                "Integrated company volume must be positive."
            )

        # ---------------------------------------------------------
        # 4. INTEGRATED REVENUE
        # ---------------------------------------------------------

        projected_revenue = (
            base_revenue
            + total_revenue_delta
        )

        # Blended price preserves total company revenue.
        projected_price = (
            projected_revenue
            / projected_volume
        )

        # ---------------------------------------------------------
        # 5. INTEGRATED COGS
        # ---------------------------------------------------------

        projected_cogs = (
            base_cogs
            + total_variable_cost_delta
        )

        # Blended variable cost preserves total company COGS.
        projected_variable_cost = (
            projected_cogs
            / projected_volume
        )

        # ---------------------------------------------------------
        # 6. OTHER OPERATING DRIVERS
        # ---------------------------------------------------------

        projected_fixed_opex = (
            state.drivers.fixed_opex
            + total_fixed_opex_delta
        )

        projected_fixed_assets = (
            state.drivers.fixed_assets
            + total_fixed_assets_delta
        )

        projected_depreciation = (
            state.drivers.depreciation
            + total_depreciation_delta
        )

        projected_opening_cash = (
            state.drivers.opening_cash
            + total_cash_impact
        )

        # ---------------------------------------------------------
        # 7. BUILD INTEGRATED DRIVERS
        # ---------------------------------------------------------

        drivers = replace(
            state.drivers,
            price=projected_price,
            volume=projected_volume,
            variable_cost_per_unit=(
                projected_variable_cost
            ),
            fixed_opex=projected_fixed_opex,
            fixed_assets=projected_fixed_assets,
            depreciation=projected_depreciation,
            opening_cash=projected_opening_cash,
        )

        # ---------------------------------------------------------
        # 8. BUILD PROJECTED COMPANY STATE
        # ---------------------------------------------------------

        return replace(
            state,
            version=state.version + 1,
            label=f"{state.label} + Investment Year 1",
            drivers=drivers,
        )
