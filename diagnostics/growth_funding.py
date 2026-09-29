from __future__ import annotations

from dataclasses import dataclass, replace

from core.models import CompanyState
from core.financial_engine import FinancialEngine, FinancialProjection


@dataclass(frozen=True)
class GrowthDiagnosisResult:
    """
    Diagnostic result for the funding implications of the
    projected CompanyState.
    """

    baseline_revenue: float
    projected_revenue: float
    additional_revenue: float
    implied_growth_pct: float

    baseline_net_profit: float
    projected_net_profit: float
    net_profit_delta: float

    baseline_nwc: float
    projected_nwc: float
    working_capital_investment: float

    retained_profit: float
    debt_principal: float
    internal_funding_available: float
    additional_funding_required: float

    projected_fcf: float

    is_self_funded: bool
    is_profitable_growth: bool
    is_cash_positive_growth: bool
    is_growth_trap: bool


@dataclass(frozen=True)
class GrowthFundingCapacityResult:
    current_growth_pct: float
    current_revenue: float
    current_fcfe: float
    tested_additional_growth_pct: float
    tested_growth_revenue: float
    capacity_reached: bool
    current_state_requires_funding: bool


def diagnose_growth_funding(
    baseline_state: CompanyState,
    projected_state: CompanyState,
    financial_projection: FinancialProjection,
    retention_rate_pct: float = 100.0,
) -> GrowthDiagnosisResult:
    """
    Diagnose the funding implications of the projected CompanyState.

    CompanyState is the source of truth for business drivers/policies.
    FinancialProjection is the source of truth for financial results.
    This function is a pure diagnostic engine and does not apply decisions.
    """

    baseline_fin = financial_projection.baseline
    projected_fin = financial_projection.projected

    baseline_is = baseline_fin.income_statement
    projected_is = projected_fin.income_statement

    baseline_wc = baseline_fin.working_capital
    projected_wc = projected_fin.working_capital

    baseline_revenue = float(baseline_is.revenue)
    projected_revenue = float(projected_is.revenue)

    additional_revenue = projected_revenue - baseline_revenue

    implied_growth_pct = (
        additional_revenue / baseline_revenue * 100.0
        if baseline_revenue > 0
        else 0.0
    )

    baseline_net_profit = float(baseline_is.net_profit)
    projected_net_profit = float(projected_is.net_profit)
    net_profit_delta = projected_net_profit - baseline_net_profit

    baseline_nwc = float(baseline_wc.nwc)
    projected_nwc = float(projected_wc.nwc)
    working_capital_investment = projected_nwc - baseline_nwc

    retention_rate = max(
        0.0,
        min(100.0, float(retention_rate_pct)),
    ) / 100.0

    retained_profit = projected_net_profit * retention_rate

    debt_principal = max(
        0.0,
        float(projected_state.capital_structure.principal_payments),
    )

    projected_fcfe = float(projected_fin.fcfe)

    internal_funding_available = max(0.0, projected_fcfe)
    additional_funding_required = max(0.0, -projected_fcfe)

    is_profitable_growth = projected_net_profit > 0
    is_cash_positive_growth = projected_fcfe >= 0
    is_self_funded = projected_fcfe >= 0

    is_growth_trap = (
        is_profitable_growth
        and projected_fcfe < 0
    )

    return GrowthDiagnosisResult(
        baseline_revenue=baseline_revenue,
        projected_revenue=projected_revenue,
        additional_revenue=additional_revenue,
        implied_growth_pct=implied_growth_pct,
        baseline_net_profit=baseline_net_profit,
        projected_net_profit=projected_net_profit,
        net_profit_delta=net_profit_delta,
        baseline_nwc=baseline_nwc,
        projected_nwc=projected_nwc,
        working_capital_investment=working_capital_investment,
        retained_profit=retained_profit,
        debt_principal=debt_principal,
        internal_funding_available=internal_funding_available,
        additional_funding_required=additional_funding_required,
        projected_fcf=projected_fcfe,
        is_self_funded=is_self_funded,
        is_profitable_growth=is_profitable_growth,
        is_cash_positive_growth=is_cash_positive_growth,
        is_growth_trap=is_growth_trap,
    )


def _fcfe_at_additional_growth(
    projected_state: CompanyState,
    baseline_nwc: float,
    additional_growth_pct: float,
) -> tuple[float, float]:
    """
    Run the canonical Financial Engine for an additional volume-growth
    scenario around the already projected CompanyState.

    This is a read-only diagnostic what-if. It does not create or store
    a DecisionPlan decision and does not mutate CompanyState.
    """

    current_volume = float(projected_state.drivers.volume)
    scenario_volume = current_volume * (
        1.0 + additional_growth_pct / 100.0
    )

    scenario_drivers = replace(
        projected_state.drivers,
        volume=scenario_volume,
    )

    scenario_state = replace(
        projected_state,
        drivers=scenario_drivers,
    )

    statements = FinancialEngine.calculate_statements(
        scenario_state,
        prior_nwc=baseline_nwc,
    )

    return (
        float(statements.fcfe),
        float(statements.income_statement.revenue),
    )


def calculate_growth_funding_capacity(
    baseline_state: CompanyState,
    projected_state: CompanyState,
    financial_projection: FinancialProjection,
    max_additional_growth_pct: float = 500.0,
    tolerance_pct: float = 0.01,
) -> GrowthFundingCapacityResult:
    """
    Calculate additional revenue growth that the resulting projected
    CompanyState can support before projected FCFE becomes negative.

    Canonical flow:
        Locked Baseline
            -> Current Decision Plan
            -> Projected CompanyState
            -> FinancialProjection
            -> Funding Capacity diagnostic

    The capacity calculation is read-only. It does not mutate CompanyState,
    DecisionPlan or Streamlit session state.
    """

    baseline_fin = financial_projection.baseline
    projected_fin = financial_projection.projected

    baseline_revenue = float(baseline_fin.income_statement.revenue)
    current_revenue = float(projected_fin.income_statement.revenue)
    current_fcfe = float(projected_fin.fcfe)

    current_growth_pct = (
        ((current_revenue / baseline_revenue) - 1.0) * 100.0
        if baseline_revenue > 0
        else 0.0
    )

    if current_fcfe < 0:
        return GrowthFundingCapacityResult(
            current_growth_pct=current_growth_pct,
            current_revenue=current_revenue,
            current_fcfe=current_fcfe,
            tested_additional_growth_pct=0.0,
            tested_growth_revenue=current_revenue,
            capacity_reached=True,
            current_state_requires_funding=True,
        )
        
    baseline_nwc = float(baseline_fin.working_capital.nwc)
    upper = max(0.0, float(max_additional_growth_pct))

    if upper == 0.0:
        return GrowthFundingCapacityResult(
            current_growth_pct=current_growth_pct,
            current_revenue=current_revenue,
            current_fcfe=current_fcfe,
            tested_additional_growth_pct=0.0,
            tested_growth_revenue=current_revenue,
            capacity_reached=False,
            current_state_requires_funding=False,
        )
        
    upper_fcfe, upper_revenue = _fcfe_at_additional_growth(
        projected_state=projected_state,
        baseline_nwc=baseline_nwc,
        additional_growth_pct=upper,
    )

    if upper_fcfe >= 0:
        return GrowthFundingCapacityResult(
            current_growth_pct=current_growth_pct,
            current_revenue=current_revenue,
            current_fcfe=current_fcfe,
            tested_additional_growth_pct=upper,
            tested_growth_revenue=upper_revenue,
            capacity_reached=False,
            current_state_requires_funding=False,
        )

    lower = 0.0
    high = upper

    for _ in range(80):
        midpoint = (lower + high) / 2.0
        fcfe, _ = _fcfe_at_additional_growth(
            projected_state=projected_state,
            baseline_nwc=baseline_nwc,
            additional_growth_pct=midpoint,
        )

        if fcfe >= 0:
            lower = midpoint
        else:
            high = midpoint

        if high - lower <= tolerance_pct:
            break

    capacity = max(0.0, lower)

    _, capacity_revenue = _fcfe_at_additional_growth(
        projected_state=projected_state,
        baseline_nwc=baseline_nwc,
        additional_growth_pct=capacity,
    )

    return GrowthFundingCapacityResult(
        current_growth_pct=current_growth_pct,
        current_revenue=current_revenue,
        current_fcfe=current_fcfe,
        tested_additional_growth_pct=capacity,
        tested_growth_revenue=capacity_revenue,
        capacity_reached=True,
        current_state_requires_funding=False,
    )
