from __future__ import annotations

from dataclasses import dataclass

from core.models import CompanyState
from core.financial_engine import FinancialProjection


@dataclass(frozen=True)
class GrowthDiagnosisResult:
    """
    Diagnostic result for the funding implications of the
    projected CompanyState.

    Important architectural rule:

        CompanyState
            = source of truth for business drivers/policies

        FinancialProjection
            = source of truth for financial results

        GrowthDiagnosisResult
            = analytical interpretation of those results
    """

    # ---------------------------------------------------------
    # Revenue / Growth
    # ---------------------------------------------------------

    baseline_revenue: float
    projected_revenue: float
    additional_revenue: float
    implied_growth_pct: float

    # ---------------------------------------------------------
    # Profitability
    # ---------------------------------------------------------

    baseline_net_profit: float
    projected_net_profit: float
    net_profit_delta: float

    # ---------------------------------------------------------
    # Working Capital
    # ---------------------------------------------------------

    baseline_nwc: float
    projected_nwc: float
    working_capital_investment: float

    # ---------------------------------------------------------
    # Funding
    # ---------------------------------------------------------

    retained_profit: float
    debt_principal: float
    internal_funding_available: float

    additional_funding_required: float

    # ---------------------------------------------------------
    # Cash Flow
    # ---------------------------------------------------------

    projected_fcf: float

    # ---------------------------------------------------------
    # Diagnostics
    # ---------------------------------------------------------

    is_self_funded: bool
    is_profitable_growth: bool
    is_cash_positive_growth: bool
    is_growth_trap: bool


def diagnose_growth_funding(
    baseline_state: CompanyState,
    projected_state: CompanyState,
    financial_projection: FinancialProjection,
    retention_rate_pct: float = 100.0,
) -> GrowthDiagnosisResult:
    """
    Diagnose the funding implications of the projected CompanyState.

    Architectural contract
    -----------------------

    1. CompanyState is the source of truth for business drivers
       and financing / working-capital policies.

    2. FinancialProjection is the source of truth for:
         - revenue
         - net profit
         - NWC
         - FCFE

    3. This function does NOT reconstruct the company's
       financial statements.

    4. This function does NOT read Streamlit session state.

    5. This function does NOT apply Decisions.

    6. This function is a pure diagnostic engine.

    The projected state is assumed to have already been produced
    by the V2 DecisionPlan -> DecisionEvaluator pipeline.
    """

    # =========================================================
    # FINANCIAL RESULTS — CANONICAL SOURCE
    # =========================================================

    baseline_fin = financial_projection.baseline
    projected_fin = financial_projection.projected

    baseline_is = baseline_fin.income_statement
    projected_is = projected_fin.income_statement

    baseline_wc = baseline_fin.working_capital
    projected_wc = projected_fin.working_capital

    # ---------------------------------------------------------
    # Revenue
    # ---------------------------------------------------------

    baseline_revenue = float(
        baseline_is.revenue
    )

    projected_revenue = float(
        projected_is.revenue
    )

    additional_revenue = (
        projected_revenue
        - baseline_revenue
    )

    implied_growth_pct = (
        additional_revenue
        / baseline_revenue
        * 100.0
        if baseline_revenue > 0
        else 0.0
    )

    # ---------------------------------------------------------
    # Profitability
    # ---------------------------------------------------------

    baseline_net_profit = float(
        baseline_is.net_profit
    )

    projected_net_profit = float(
        projected_is.net_profit
    )

    net_profit_delta = (
        projected_net_profit
        - baseline_net_profit
    )

    # ---------------------------------------------------------
    # Working Capital
    # ---------------------------------------------------------

    baseline_nwc = float(
        baseline_wc.nwc
    )

    projected_nwc = float(
        projected_wc.nwc
    )

    working_capital_investment = (
        projected_nwc
        - baseline_nwc
    )

    # =========================================================
    # FUNDING LOGIC
    # =========================================================

    # Retention is a diagnostic assumption, not a CompanyState
    # mutation.
    retention_rate = max(
        0.0,
        min(
            100.0,
            float(retention_rate_pct),
        ),
    ) / 100.0

    retained_profit = (
        projected_net_profit
        * retention_rate
    )

    # Principal repayment comes from the canonical CompanyState.
    debt_principal = max(
        0.0,
        float(
            projected_state
            .capital_structure
            .principal_payments
        ),
    )

    # ---------------------------------------------------------
    # Internal funding capacity
    # ---------------------------------------------------------
    #
    # The Financial Engine already calculates FCFE as:
    #
    # Net Profit
    # + Depreciation
    # - Principal Payments
    # + WC Cash Impact
    #
    # Therefore we must NOT reconstruct FCF here.
    #
    # We use the projected FCFE as the canonical cash-flow
    # measure and retain the retained-profit figure as a
    # diagnostic decomposition metric.
    # ---------------------------------------------------------

    projected_fcfe = float(
        projected_fin.fcfe
    )

    # Internal funding available for the projected state.
    #
    # For the diagnostic we treat positive FCFE as internally
    # generated funding capacity. Negative FCFE represents a
    # funding requirement.
    internal_funding_available = max(
        0.0,
        projected_fcfe,
    )

    additional_funding_required = max(
        0.0,
        -projected_fcfe,
    )

    # =========================================================
    # DIAGNOSTIC FLAGS
    # =========================================================

    is_profitable_growth = (
        projected_net_profit > 0
    )

    is_cash_positive_growth = (
        projected_fcfe >= 0
    )

    is_self_funded = (
        projected_fcfe >= 0
    )

    # A growth trap exists when the projected company is
    # profitable but its financing/cash position is negative.
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
