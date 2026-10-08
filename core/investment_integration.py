from typing import Any, Dict, Tuple

from core.models import CompanyState
from core.investment_decision import InvestmentDecision
from core.investment_company_impact import InvestmentCompanyImpact

from tools.investment_decision import (
    CompanyStateContext,
    InvestmentResult,
    evaluate_investment,
)


class InvestmentIntegration:
    """
    Integration boundary between the investment decision domain
    and the existing company decision architecture.

    Responsibilities
    ----------------
    1. Build the investment engine context from the locked CompanyState.
    2. Evaluate an InvestmentDecision using the existing investment engine.
    3. Convert the engine's Year-1 impact into the canonical
       InvestmentCompanyImpact contract.

    This class does NOT:
        - modify CompanyState
        - apply direct Decisions
        - create DecisionPlans
        - calculate company-level FinancialProjection
        - execute investments sequentially
        - build CompanyState for every project year

    Investment evaluation remains multi-year.

    CompanyState integration is limited to the investment's
    Year-1 impact.

    Architecture:

        Locked CompanyState
                ↓
        CompanyStateContext
                ↓
        InvestmentDecision
                ↓
        Existing Investment Engine
                ↓
        InvestmentResult
                +
        InvestmentCompanyImpact
    """

    @staticmethod
    def build_context(
        state: CompanyState,
    ) -> CompanyStateContext:
        """
        Convert the locked CompanyState into the context expected
        by the investment engine.
        """
        if not isinstance(state, CompanyState):
            raise TypeError(
                "InvestmentIntegration expects a CompanyState."
            )

        return CompanyStateContext(
            price=state.drivers.price,
            variable_cost_per_unit=(
                state.drivers.variable_cost_per_unit
            ),
            fixed_costs=state.drivers.fixed_opex,
            tax_rate=state.capital_structure.tax_rate,
            wacc=state.capital_structure.wacc,
            ar_days=state.working_capital.ar_days,
            inventory_days=state.working_capital.inventory_days,
            ap_days=state.working_capital.ap_days,
            fixed_assets=state.drivers.fixed_assets,
            depreciation=state.drivers.depreciation,
        )

    @staticmethod
    def evaluate(
        state: CompanyState,
        investment: InvestmentDecision,
    ) -> Tuple[
        InvestmentResult,
        InvestmentCompanyImpact,
    ]:
        """
        Evaluate one InvestmentDecision against the locked baseline.

        Returns:
            InvestmentResult
                Complete multi-year project evaluation
                (NPV, IRR, payback, cash flows, Year-1 impact).

            InvestmentCompanyImpact
                Canonical Year-1 incremental impact used later
                by the company projection layer.
        """
        if not isinstance(state, CompanyState):
            raise TypeError(
                "InvestmentIntegration expects a CompanyState."
            )

        if not isinstance(investment, InvestmentDecision):
            raise TypeError(
                "InvestmentIntegration expects an "
                "InvestmentDecision."
            )

        context = InvestmentIntegration.build_context(state)

        result = evaluate_investment(
            assumptions=investment.assumptions,
            context=context,
        )

        if result.year_1_impact is None:
            raise ValueError(
                f"Investment '{investment.id}' did not produce "
                "a Year-1 impact."
            )

        impact = InvestmentIntegration._build_company_impact(
            result
        )

        return result, impact

    @staticmethod
    def _build_company_impact(
        result: InvestmentResult,
    ) -> InvestmentCompanyImpact:
        """
        Convert the investment engine's Year-1 result into the
        canonical company-impact object.

        No company-level values are calculated here.
        Everything remains incremental to the investment.
        """
        year_1 = result.year_1_impact

        if year_1 is None:
            raise ValueError(
                "Cannot build company impact without "
                "Year-1 investment impact."
            )

        return InvestmentCompanyImpact(
            volume_delta=year_1.incremental_units,
            revenue_delta=year_1.incremental_revenue,
            variable_cost_delta=(
                year_1.incremental_variable_cost
            ),
            fixed_opex_delta=(
                year_1.incremental_fixed_costs
            ),
            depreciation_delta=year_1.depreciation,
            fixed_assets_delta=(
                year_1.incremental_fixed_assets
            ),
            ar_delta=year_1.incremental_ar,
            inventory_delta=year_1.incremental_inventory,
            ap_delta=year_1.incremental_ap,
            nwc_delta=year_1.incremental_nwc,
            operating_cash_flow_delta=(
                year_1.incremental_operating_cash_flow
            ),
            initial_capex=year_1.initial_capex,
            initial_nwc_requirement=(
                year_1.initial_nwc_requirement
            ),
            initial_funding_requirement=(
                year_1.initial_funding_requirement
            ),
        )

    @staticmethod
    def summary(
        investment: InvestmentDecision,
        result: InvestmentResult,
        impact: InvestmentCompanyImpact,
    ) -> Dict[str, Any]:
        """
        Produce a compact execution summary suitable for traces,
        Control Tower data, or UI reporting.
        """
        return {
            "investment_id": investment.id,
            "investment_name": investment.name,
            "decision_type": "investment",
            "npv": result.npv,
            "irr": result.irr,
            "payback_years": result.payback_years,
            "year_1_impact": impact.summary(),
        }
