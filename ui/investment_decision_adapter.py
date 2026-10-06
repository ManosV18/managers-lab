"""
Managers Lab — Investment Decision Adapter

Purpose
-------
Connect the Investment Decision Lab to the canonical Managers Lab flow.

Architecture
------------
Locked Baseline
    -> Investment Domain
    -> InvestmentCompanyImpact
    -> Canonical Investment Decision
    -> DecisionPlan
    -> DecisionEvaluator
    -> Projected CompanyState
    -> Financial Impact

Important
---------
Investment economics are incremental.

The investment does NOT replace the company's:
- price
- volume
- variable cost

Instead, the investment contributes incremental:
- volume
- revenue
- variable cost
- fixed opex
- fixed assets
- depreciation

Revenue and variable-cost deltas are authoritative when investment
overrides are used.

Project-specific assumptions remain in Decision.metadata.
"""

from __future__ import annotations

from dataclasses import asdict, is_dataclass
from typing import Any, Dict, Tuple

from core.decision import Decision, DecisionFactory
from core.decision_plan import DecisionPlan
from core.decision_evaluator import DecisionEvaluation
from core.company_state import CompanyState

from investment_decision_lab import (
    CompanyStateContext,
    InvestmentAssumptions,
    InvestmentResult,
    InvestmentCompanyImpact,
    build_investment_cash_flows,
    build_investment_year1_impact,
    build_investment_company_impact,
)


# ---------------------------------------------------------------------------
# 1. Build Investment Context from Locked CompanyState
# ---------------------------------------------------------------------------

def build_investment_context(
    baseline_state: CompanyState,
) -> CompanyStateContext:
    """
    Build the Investment Lab context directly from the locked CompanyState.

    The Investment Lab inherits:
        - price
        - variable cost
        - tax rate
        - WACC
        - AR days
        - Inventory days
        - AP days
        - fixed assets
        - depreciation

    No baseline value is re-entered by the user.
    """

    if not isinstance(baseline_state, CompanyState):
        raise TypeError(
            "baseline_state must be a CompanyState."
        )

    return CompanyStateContext(
        price=baseline_state.drivers.price,
        variable_cost_per_unit=(
            baseline_state.drivers.variable_cost_per_unit
        ),
        fixed_costs=baseline_state.drivers.fixed_opex,

        tax_rate=baseline_state.capital_structure.tax_rate,
        wacc=baseline_state.capital_structure.wacc,

        ar_days=baseline_state.working_capital.ar_days,
        inventory_days=baseline_state.working_capital.inventory_days,
        ap_days=baseline_state.working_capital.ap_days,

        fixed_assets=baseline_state.drivers.fixed_assets,
        depreciation=baseline_state.drivers.depreciation,
    )


# ---------------------------------------------------------------------------
# 2. Run Existing Investment Domain
# ---------------------------------------------------------------------------

def run_investment_analysis(
    baseline_state: CompanyState,
    assumptions: InvestmentAssumptions,
) -> InvestmentResult:
    """
    Run the existing Investment Lab calculations.

    No investment mathematics are duplicated here.
    """

    if not isinstance(baseline_state, CompanyState):
        raise TypeError(
            "baseline_state must be a CompanyState."
        )

    if not isinstance(assumptions, InvestmentAssumptions):
        raise TypeError(
            "assumptions must be InvestmentAssumptions."
        )

    context = build_investment_context(baseline_state)

    # The domain function already has a canonical signature:
    #
    # build_investment_cash_flows(
    #     assumptions,
    #     context,
    # )
    #
    # It returns yearly InvestmentYear structures.
    #
    # We construct InvestmentResult here so that this adapter remains
    # responsible only for connecting the domain to the application.

    yearly_flows = build_investment_cash_flows(
        assumptions,
        context,
    )

    cash_flows = [
        year.project_cash_flow
        for year in yearly_flows
    ]

    from investment_decision_lab import (
        calculate_npv,
        calculate_irr,
        calculate_payback,
    )

    wacc = assumptions.get_effective_wacc(context)

    npv = calculate_npv(
        cash_flows,
        wacc,
    )

    irr = calculate_irr(
        cash_flows,
    )

    payback = calculate_payback(
        cash_flows,
    )

    year_1_impact = build_investment_year1_impact(
        assumptions,
        context,
    )

    return InvestmentResult(
        npv=npv,
        irr=irr,
        payback_years=payback,
        initial_investment=assumptions.initial_investment,
        total_project_cash_flow=sum(cash_flows),
        yearly_cash_flows=yearly_flows,
        year_1_impact=year_1_impact,
    )


# ---------------------------------------------------------------------------
# 3. Build Incremental Company Impact
# ---------------------------------------------------------------------------

def build_company_impact(
    result: InvestmentResult,
) -> InvestmentCompanyImpact:
    """
    Convert the accepted investment's Year-1 impact into the
    authoritative company-level incremental impact.

    This is NOT a new CompanyState.

    It is the bridge between:
        Investment Domain
            ->
        Existing Company
    """

    if result.year_1_impact is None:
        raise ValueError(
            "InvestmentResult does not contain Year-1 impact."
        )

    return build_investment_company_impact(
        result.year_1_impact
    )


# ---------------------------------------------------------------------------
# 4. Build Canonical Investment Decision
# ---------------------------------------------------------------------------

def build_investment_decision(
    baseline_state: CompanyState,
    assumptions: InvestmentAssumptions,
    result: InvestmentResult,
    *,
    decision_name: str = "Investment Decision",
) -> Decision:
    """
    Convert the investment proposal into one canonical Decision.

    IMPORTANT:
    The Decision stores project-specific assumptions and the
    authoritative incremental Year-1 impact in metadata.

    It does NOT overwrite company price / volume / variable cost.
    """

    if not isinstance(baseline_state, CompanyState):
        raise TypeError(
            "baseline_state must be a CompanyState."
        )

    if not isinstance(assumptions, InvestmentAssumptions):
        raise TypeError(
            "assumptions must be InvestmentAssumptions."
        )

    if not isinstance(result, InvestmentResult):
        raise TypeError(
            "result must be an InvestmentResult."
        )

    context = build_investment_context(
        baseline_state
    )

    impact = build_company_impact(
        result
    )

    metadata = {
        "decision_type": "investment",

        "investment": {
            # Proposal
            "initial_investment": (
                assumptions.initial_investment
            ),
            "project_years": (
                assumptions.project_years
            ),
            "units": assumptions.units,
            "depreciation_years": (
                assumptions.depreciation_years
            ),
            "incremental_fixed_costs": (
                assumptions.incremental_fixed_costs
            ),

            # Growth
            "annual_volume_growth": (
                assumptions.annual_volume_growth
            ),
            "annual_price_growth": (
                assumptions.annual_price_growth
            ),
            "annual_variable_cost_growth": (
                assumptions.annual_variable_cost_growth
            ),
            "annual_fixed_cost_growth": (
                assumptions.annual_fixed_cost_growth
            ),

            # Terminal value
            "salvage_value": assumptions.salvage_value,

            # Overrides
            "price_override": (
                assumptions.price_override
            ),
            "variable_cost_override": (
                assumptions.variable_cost_override
            ),
            "tax_rate_override": (
                assumptions.tax_rate_override
            ),
            "wacc_override": (
                assumptions.wacc_override
            ),

            # Flexibility
            "allow_exit_after_year_1": (
                assumptions.allow_exit_after_year_1
            ),
            "exit_value": assumptions.exit_value,
            "exit_cost": assumptions.exit_cost,

            # Effective economics
            "effective_price": (
                assumptions.get_effective_price(context)
            ),
            "effective_variable_cost": (
                assumptions.get_effective_variable_cost(
                    context
                )
            ),
            "effective_tax_rate": (
                assumptions.get_effective_tax_rate(
                    context
                )
            ),
            "effective_wacc": (
                assumptions.get_effective_wacc(
                    context
                )
            ),

            # Project economics
            "npv": result.npv,
            "irr": result.irr,
            "payback_years": result.payback_years,

            # Authoritative Year-1 company impact
            "company_impact": {
                "volume_delta": impact.volume_delta,
                "revenue_delta": impact.revenue_delta,
                "variable_cost_delta": (
                    impact.variable_cost_delta
                ),
                "fixed_opex_delta": (
                    impact.fixed_opex_delta
                ),
                "fixed_assets_delta": (
                    impact.fixed_assets_delta
                ),
                "depreciation_delta": (
                    impact.depreciation_delta
                ),
            },

            # Calculated funding requirement
            "initial_capex": (
                result.year_1_impact.initial_capex
                if result.year_1_impact
                else 0.0
            ),
            "initial_nwc_requirement": (
                result.year_1_impact.initial_nwc_requirement
                if result.year_1_impact
                else 0.0
            ),
            "initial_funding_requirement": (
                result.year_1_impact.initial_funding_requirement
                if result.year_1_impact
                else 0.0
            ),
        },
    }

    return DecisionFactory.create(
        name=decision_name,
        description=(
            "Investment decision evaluated as an incremental "
            "expansion of the existing company."
        ),
        category="investment",

        # No company-driver replacement here.
        #
        # The incremental economics are stored in metadata until
        # the canonical DecisionEvaluator / FinancialEngine boundary
        # is explicitly extended to consume InvestmentCompanyImpact.
        changes={},

        metadata=metadata,
    )


# ---------------------------------------------------------------------------
# 5. Package
# ---------------------------------------------------------------------------

def build_investment_package(
    baseline_state: CompanyState,
    assumptions: InvestmentAssumptions,
    *,
    decision_name: str = "Investment Decision",
) -> Tuple[
    Decision,
    InvestmentResult,
    InvestmentCompanyImpact,
]:
    """
    Return the three objects needed by the application:

        1. canonical Decision
        2. InvestmentResult
        3. InvestmentCompanyImpact
    """

    result = run_investment_analysis(
        baseline_state,
        assumptions,
    )

    impact = build_company_impact(
        result
    )

    decision = build_investment_decision(
        baseline_state,
        assumptions,
        result,
        decision_name=decision_name,
    )

    return (
        decision,
        result,
        impact,
    )


# ---------------------------------------------------------------------------
# 6. Add Investment to DecisionPlan
# ---------------------------------------------------------------------------

def add_investment_to_plan(
    baseline_state: CompanyState,
    plan: DecisionPlan,
    assumptions: InvestmentAssumptions,
    *,
    decision_name: str = "Investment Decision",
) -> Tuple[
    DecisionPlan,
    InvestmentResult,
    InvestmentCompanyImpact,
]:
    """
    Add the investment decision to an existing DecisionPlan.

    The project economics remain available separately.
    """

    (
        decision,
        result,
        impact,
    ) = build_investment_package(
        baseline_state,
        assumptions,
        decision_name=decision_name,
    )

    return (
        plan.add(decision),
        result,
        impact,
    )


# ---------------------------------------------------------------------------
# 7. Streamlit / Application Evaluation Helper
# ---------------------------------------------------------------------------

def evaluate_investment(
    baseline_state: CompanyState,
    plan: DecisionPlan,
    assumptions: InvestmentAssumptions,
    *,
    decision_name: str = "Investment Decision",
) -> Tuple[
    DecisionEvaluation,
    InvestmentResult,
    InvestmentCompanyImpact,
]:
    """
    Evaluate the investment through the canonical DecisionEvaluator.

    IMPORTANT:
    The current DecisionEvaluator can only apply ordinary CompanyState
    changes through Decision.changes.

    Therefore this function deliberately does NOT fake the application
    of the incremental investment economics.

    The InvestmentCompanyImpact is returned separately and must be consumed
    by the canonical projection layer once that layer is extended to support
    incremental investment economics.
    """

    from core.decision_evaluator import DecisionEvaluator

    (
        new_plan,
        investment_result,
        investment_impact,
    ) = add_investment_to_plan(
        baseline_state,
        plan,
        assumptions,
        decision_name=decision_name,
    )

    evaluation = DecisionEvaluator.evaluate(
        baseline_state,
        new_plan,
    )

    return (
        evaluation,
        investment_result,
        investment_impact,
    )


# ---------------------------------------------------------------------------
# 8. Simple Result Summary for UI
# ---------------------------------------------------------------------------

def investment_result_summary(
    result: InvestmentResult,
) -> Dict[str, Any]:
    """
    Convert InvestmentResult to a simple dictionary for UI display.

    No calculation is performed here.
    """

    if is_dataclass(result):
        return asdict(result)

    return {
        "npv": result.npv,
        "irr": result.irr,
        "payback_years": result.payback_years,
        "initial_investment": result.initial_investment,
        "total_project_cash_flow": (
            result.total_project_cash_flow
        ),
        "yearly_cash_flows": result.yearly_cash_flows,
        "year_1_impact": result.year_1_impact,
    }
