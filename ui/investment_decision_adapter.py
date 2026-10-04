"""
Managers Lab — Investment Decision Adapter

Purpose
-------
Connect the existing Investment Decision Lab to the canonical Managers Lab flow
without changing the core architecture.

Canonical flow:
    Locked Baseline
        -> Investment Decision
        -> DecisionPlan
        -> DecisionEvaluator
        -> Projected CompanyState
        -> Financial Impact

Important design rule
---------------------
CompanyState changes contain only company drivers that genuinely change.

Project-specific assumptions such as:
- initial working capital
- project life
- depreciation schedule
- salvage value
- WACC override
- tax override
- NPV / IRR / payback

remain project-analysis data and are kept in Decision.metadata rather than
being forced into CompanyState v1.

This file does NOT modify:
- Decision
- DecisionPlan
- DecisionRunner
- DecisionEvaluator
- FinancialEngine
- Investment Decision Lab formulas
"""

from __future__ import annotations

import inspect
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
    build_investment_cash_flows,
)


def build_investment_context(baseline_state: CompanyState) -> CompanyStateContext:
    """
    Build the Investment Lab context directly from the locked CompanyState.

    This is the key baseline-reuse rule:
    the investment tool does not ask the user to re-enter values already
    available in Managers Lab.
    """
    return CompanyStateContext(
        variable_cost_per_unit=baseline_state.drivers.variable_cost_per_unit,
        tax_rate=baseline_state.capital_structure.tax_rate,
        wacc=baseline_state.capital_structure.wacc,
        price=baseline_state.drivers.price,
        fixed_costs=baseline_state.drivers.fixed_opex,
    )


def _effective_value(
    explicit_value: Any,
    baseline_value: Any,
) -> Any:
    """Use the investment override when supplied; otherwise use baseline."""
    return baseline_value if explicit_value is None else explicit_value


def _investment_values(
    baseline_state: CompanyState,
    assumptions: InvestmentAssumptions,
) -> Dict[str, Any]:
    """
    Resolve the project values against the locked baseline.

    The InvestmentAssumptions object already supports optional overrides.
    """
    context = build_investment_context(baseline_state)

    price = _effective_value(assumptions.price, context.price)
    variable_cost = _effective_value(
        assumptions.override_variable_cost_per_unit,
        context.variable_cost_per_unit,
    )
    tax_rate = _effective_value(
        assumptions.override_tax_rate,
        context.tax_rate,
    )
    wacc = _effective_value(
        assumptions.override_wacc,
        context.wacc,
    )

    return {
        "price": price,
        "variable_cost_per_unit": variable_cost,
        "tax_rate": tax_rate,
        "wacc": wacc,
        "units": assumptions.units,
        "incremental_fixed_costs": assumptions.incremental_fixed_costs,
        "initial_investment": assumptions.initial_investment,
        "initial_working_capital": assumptions.initial_working_capital,
        "project_years": assumptions.project_years,
        "after_tax_salvage_value": assumptions.after_tax_salvage_value,
        "depreciation_years": assumptions.effective_depreciation_years,
    }


def build_investment_decision(
    baseline_state: CompanyState,
    assumptions: InvestmentAssumptions,
    *,
    decision_name: str = "Investment Decision",
) -> Decision:
    """
    Convert Investment Lab assumptions into one canonical Managers Lab Decision.

    CompanyState changes:
        price
        volume
        variable_cost_per_unit
        fixed_opex
        fixed_assets

    Project-only assumptions are attached as metadata.
    """
    if not isinstance(baseline_state, CompanyState):
        raise TypeError("baseline_state must be a CompanyState.")

    if not isinstance(assumptions, InvestmentAssumptions):
        raise TypeError("assumptions must be InvestmentAssumptions.")

    values = _investment_values(baseline_state, assumptions)

    baseline_fixed_assets = baseline_state.drivers.fixed_assets
    baseline_fixed_opex = baseline_state.drivers.fixed_opex

    # Investment changes the company's operating state.
    # The initial investment is added to fixed assets.
    target_fixed_assets = (
        baseline_fixed_assets + assumptions.initial_investment
    )

    target_fixed_opex = (
        baseline_fixed_opex + assumptions.incremental_fixed_costs
    )

    changes = {
        "price": values["price"],
        "volume": values["units"],
        "variable_cost_per_unit": values["variable_cost_per_unit"],
        "fixed_opex": target_fixed_opex,
        "fixed_assets": target_fixed_assets,
    }

    metadata = {
        "decision_type": "investment",
        "investment": {
            "initial_investment": values["initial_investment"],
            "project_years": values["project_years"],
            "units": values["units"],
            "annual_volume_growth": assumptions.annual_volume_growth,
            "annual_price_growth": assumptions.annual_price_growth,
            "annual_variable_cost_growth": (
                assumptions.annual_variable_cost_growth
            ),
            "annual_fixed_cost_growth": assumptions.annual_fixed_cost_growth,
            "initial_working_capital": values["initial_working_capital"],
            "after_tax_salvage_value": values["after_tax_salvage_value"],
            "incremental_fixed_costs": values["incremental_fixed_costs"],
            "depreciation_years": values["depreciation_years"],
            "allow_company_tax_shield": (
                assumptions.allow_company_tax_shield
            ),
            "wacc": values["wacc"],
            "tax_rate": values["tax_rate"],
            "price": values["price"],
            "variable_cost_per_unit": values["variable_cost_per_unit"],
        },
    }

    return DecisionFactory.create(
        name=decision_name,
        description=(
            "Investment decision linked to the locked Managers Lab "
            "CompanyState and evaluated through the canonical DecisionPlan."
        ),
        category="investment",
        changes=changes,
        metadata=metadata,
    )


def _run_existing_investment_lab(
    baseline_state: CompanyState,
    assumptions: InvestmentAssumptions,
) -> InvestmentResult:
    """
    Run the existing Investment Lab without duplicating or changing its math.

    A small signature adapter is used so this connector remains compatible
    if the Investment Lab's argument order is changed between versions.
    """
    context = build_investment_context(baseline_state)
    signature = inspect.signature(build_investment_cash_flows)

    kwargs: Dict[str, Any] = {}
    unresolved = []

    for parameter in signature.parameters.values():
        if parameter.kind in (
            inspect.Parameter.VAR_POSITIONAL,
            inspect.Parameter.VAR_KEYWORD,
        ):
            continue

        name = parameter.name.lower()

        if "assumption" in name:
            kwargs[parameter.name] = assumptions
        elif "context" in name or "company_state" in name:
            kwargs[parameter.name] = context
        else:
            unresolved.append(parameter)

    if not unresolved:
        return build_investment_cash_flows(**kwargs)

    # Fallback for a simple two-positional-argument implementation.
    positional = [
        p for p in signature.parameters.values()
        if p.kind in (
            inspect.Parameter.POSITIONAL_ONLY,
            inspect.Parameter.POSITIONAL_OR_KEYWORD,
        )
    ]

    if len(positional) == 2:
        first = positional[0].name.lower()
        if "context" in first or "company_state" in first:
            return build_investment_cash_flows(context, assumptions)
        return build_investment_cash_flows(assumptions, context)

    raise TypeError(
        "Could not determine the argument signature of "
        "build_investment_cash_flows()."
    )


def build_investment_package(
    baseline_state: CompanyState,
    assumptions: InvestmentAssumptions,
    *,
    decision_name: str = "Investment Decision",
) -> Tuple[Decision, InvestmentResult]:
    """
    Return the two outputs needed by the application:

        1. canonical Managers Lab Decision
        2. existing Investment Lab result

    The project result is NOT put inside CompanyState.
    """
    decision = build_investment_decision(
        baseline_state,
        assumptions,
        decision_name=decision_name,
    )

    result = _run_existing_investment_lab(
        baseline_state,
        assumptions,
    )

    return decision, result


def add_investment_to_plan(
    baseline_state: CompanyState,
    plan: DecisionPlan,
    assumptions: InvestmentAssumptions,
    *,
    decision_name: str = "Investment Decision",
) -> Tuple[DecisionPlan, InvestmentResult]:
    """
    Add the investment as a normal Decision to an existing DecisionPlan.

    This is the preferred Streamlit integration point.

    Example
    -------
        new_plan, investment_result = add_investment_to_plan(
            baseline_state,
            current_plan,
            investment_assumptions,
        )

    The returned plan can then go through the existing DecisionEvaluator.
    """
    decision, result = build_investment_package(
        baseline_state,
        assumptions,
        decision_name=decision_name,
    )

    return plan.add(decision), result


def evaluate_investment(
    baseline_state: CompanyState,
    plan: DecisionPlan,
    assumptions: InvestmentAssumptions,
    *,
    decision_name: str = "Investment Decision",
) -> Tuple[DecisionEvaluation, InvestmentResult]:
    """
    One-call integration helper for Streamlit.

    It:
        1. creates the canonical investment Decision,
        2. adds it to the existing DecisionPlan,
        3. evaluates the whole plan through DecisionEvaluator,
        4. returns both CompanyState/Financial Impact and project economics.

    No alternative execution path is created.
    """
    from core.decision_evaluator import DecisionEvaluator

    new_plan, investment_result = add_investment_to_plan(
        baseline_state,
        plan,
        assumptions,
        decision_name=decision_name,
    )

    evaluation = DecisionEvaluator.evaluate(
        baseline_state,
        new_plan,
    )

    return evaluation, investment_result


def investment_result_summary(
    result: InvestmentResult,
) -> Dict[str, Any]:
    """
    Convert InvestmentResult to a simple dictionary for Streamlit display.

    No calculation is performed here.
    """
    if is_dataclass(result):
        data = asdict(result)
    else:
        data = {
            key: getattr(result, key)
            for key in (
                "npv",
                "irr",
                "payback_period",
                "cash_flows",
            )
            if hasattr(result, key)
        }

    return data
