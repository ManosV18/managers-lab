from dataclasses import replace
from typing import Sequence

from core.models import CompanyState
from core.investment_company_impact import InvestmentCompanyImpact


class InvestmentProjection:
    """
    Builds the integrated CompanyState at the end of Year 1
    from already evaluated investment impacts.

    Architecture:

        Locked CompanyState
                ↓
        InvestmentDecision(s)
                ↓
        InvestmentIntegration
                ↓
        InvestmentCompanyImpact(s)
                ↓
        InvestmentProjection
                ↓
        Aggregate Year-1 Impact
                ↓
        Integrated CompanyState

    IMPORTANT
    ---------
    Investment evaluation happens ONLY in InvestmentIntegration.

    This class does NOT evaluate investments again.

    The investment may be multi-year.

    CompanyState is projected ONLY at the end of Year 1.

    The project remains a separate economic object during
    investment evaluation.

    This class integrates only those Year-1 effects that can
    be represented directly and unambiguously by the existing
    CompanyState model.

    Project-specific financial economics such as:

        - project revenue
        - project variable cost
        - project volume
        - project NWC
        - project CAPEX
        - project operating cash flow

    remain in InvestmentCompanyImpact.

    They are NOT forced into the existing Company's:

        - price
        - variable_cost_per_unit
        - opening_cash

    This is intentional.

    This class does NOT:
        - calculate NPV
        - calculate IRR
        - calculate Payback
        - evaluate project economics
        - modify the locked baseline
        - apply direct Decisions
        - project CompanyState year by year
        - calculate company-level FinancialProjection
        - re-evaluate InvestmentDecisions
    """

    @classmethod
    def project(
        cls,
        state: CompanyState,
        impacts: Sequence[InvestmentCompanyImpact],
    ) -> CompanyState:
        """
        Build ONE integrated CompanyState at the end of Year 1
        from already evaluated investment impacts.

        All impacts must have been generated independently
        against the SAME locked baseline by InvestmentIntegration.

        Multiple investments are additive.

        They are NOT evaluated sequentially against each other.

        Parameters
        ----------
        state:
            Locked baseline CompanyState.

        impacts:
            Already evaluated Year-1 InvestmentCompanyImpact
            objects produced by InvestmentIntegration.

        Returns
        -------
        CompanyState
            CompanyState containing the Year-1 company-level
            state changes that can safely be represented by the
            current CompanyState model.

        Important
        ---------
        This method consumes canonical InvestmentCompanyImpact
        objects. It never evaluates InvestmentDecision objects.

        The detailed incremental financial effects remain available
        through InvestmentCompanyImpact and are intended to be
        consumed by the financial integration layer.
        """

        if not isinstance(state, CompanyState):
            raise TypeError(
                "InvestmentProjection expects a CompanyState."
            )

        impacts = tuple(impacts)

        for impact in impacts:
            if not isinstance(
                impact,
                InvestmentCompanyImpact,
            ):
                raise TypeError(
                    "Every item in impacts must be an "
                    "InvestmentCompanyImpact."
                )

        if not impacts:
            return state

        return cls._apply_aggregate_impact(
            state,
            impacts,
        )

    @staticmethod
    def _apply_aggregate_impact(
        state: CompanyState,
        impacts: Sequence[InvestmentCompanyImpact],
    ) -> CompanyState:
        """
        Apply aggregate Year-1 investment effects to CompanyState.

        Only effects that have an unambiguous representation in the
        current CompanyState are integrated here:

            fixed_opex
            fixed_assets
            depreciation

        Project-specific revenue, variable cost and volume are NOT
        converted into blended company drivers.

        Likewise, investment cash impact is NOT written into
        opening_cash because opening_cash represents the beginning
        cash position of the CompanyState, not end-of-Year-1 cash.

        The detailed incremental financial effects remain available
        through InvestmentCompanyImpact and are intended to be
        consumed by the financial integration layer.
        """

        if not impacts:
            return state

        # ---------------------------------------------------------
        # 1. AGGREGATE REPRESENTABLE COMPANY-LEVEL IMPACTS
        # ---------------------------------------------------------

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

        # ---------------------------------------------------------
        # 2. UPDATE COMPANY-LEVEL DRIVERS
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

        # ---------------------------------------------------------
        # 3. BUILD PROJECTED DRIVERS
        # ---------------------------------------------------------

        drivers = replace(
            state.drivers,
            fixed_opex=projected_fixed_opex,
            fixed_assets=projected_fixed_assets,
            depreciation=projected_depreciation,
        )

        # ---------------------------------------------------------
        # 4. BUILD PROJECTED COMPANY STATE
        # ---------------------------------------------------------

        return replace(
            state,
            version=state.version + 1,
            label=f"{state.label} + Investment Year 1",
            drivers=drivers,
        )
