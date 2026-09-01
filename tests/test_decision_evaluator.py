from datetime import datetime
from core.models import (
    CompanyState,
    OperationalDrivers,
    CapitalStructure,
    WorkingCapitalPolicy,
)

from core.decision import Decision
from core.decision_plan import DecisionPlan
from core.decision_evaluator import DecisionEvaluator


def build_baseline() -> CompanyState:
    """
    Create a controlled locked baseline for the test.
    """

    drivers = OperationalDrivers(
        price=150.0,
        volume=12000.0,
        variable_cost_per_unit=100.0,
        fixed_opex=450000.0,
        depreciation=50000.0,
        fixed_assets=800000.0,
        target_profit_goal=0.0,
        opening_cash=150000.0,
    )

    capital = CapitalStructure(
        total_debt=500000.0,
        equity=500000.0,
        annual_cash_interest_paid=25000.0,
        annual_debt_service=70000.0,
        cost_of_debt=0.05,
        tax_rate=0.22,
        wacc=0.08,
        principal_payments=20000.0,
    )
    working_capital = WorkingCapitalPolicy(
        ar_days=90.0,
        inventory_days=75.0,
        ap_days=45.0,
    )

    return CompanyState(
        version=1,
        label="Locked Baseline",
        drivers=drivers,
        capital_structure=capital,
        working_capital=working_capital,
        created_at=datetime.now(),
    )


def main() -> None:

    # =====================================================
    # BASELINE
    # =====================================================

    baseline = build_baseline()

    # =====================================================
    # DECISIONS
    # =====================================================

    interest_decision = Decision(
        id="interest_001",
        name="Annual Interest Expense",
        description="Reduce annual cash interest expense.",
        category="financing",
        changes={
            "annual_cash_interest_paid": 20000.0,
        },
    )

    price_decision = Decision(
        id="price_001",
        name="Price Change",
        description="Increase selling price.",
        category="pricing",
        changes={
            "price": 160.0,
        },
    )

    ar_decision = Decision(
        id="ar_001",
        name="AR Days",
        description="Reduce receivables days.",
        category="working_capital",
        changes={
            "ar_days": 60.0,
        },
    )

    # =====================================================
    # PLAN
    # =====================================================

    plan = DecisionPlan.create(
        plan_id="plan_001",
        name="Test Management Plan",
    )

    plan = plan.add(interest_decision)
    plan = plan.add(price_decision)
    plan = plan.add(ar_decision)

    # =====================================================
    # EVALUATE
    # =====================================================

    evaluation = DecisionEvaluator.evaluate(
        baseline,
        plan,
    )

    projected = evaluation.projected_state
    impact = evaluation.impact

    # =====================================================
    # OUTPUT
    # =====================================================

    print()
    print("================ EVALUATION TEST ================")

    print(
        f"Baseline version:   {evaluation.baseline_state.version}"
    )

    print(
        f"Projected version:  {projected.version}"
    )

    print(
        f"Decisions:          {plan.decision_count}"
    )

    print(
        f"Revenue Δ:          €{impact.revenue_delta:,.2f}"
    )

    print(
        f"EBITDA Δ:           €{impact.ebitda_delta:,.2f}"
    )

    print(
        f"Net Profit Δ:       €{impact.net_profit_delta:,.2f}"
    )

    print(
        f"NWC Cash Impact:    €{impact.nwc_cash_impact_delta:,.2f}"
    )

    print(
        f"FCFE Δ:             €{impact.fcfe_delta:,.2f}"
    )

    # =====================================================
    # STRUCTURAL ASSERTIONS
    # =====================================================

    assert evaluation.baseline_state is baseline

    assert evaluation.plan is plan

    assert plan.decision_count == 3

    assert projected.version == baseline.version + 1

    # =====================================================
    # DRIVER ASSERTIONS
    # =====================================================

    assert (
        projected.drivers.price
        == 160.0
    )

    assert (
        projected.capital_structure.annual_cash_interest_paid
        == 20000.0
    )

    assert (
        projected.working_capital.ar_days
        == 60.0
    )

    # =====================================================
    # BASELINE IMMUTABILITY
    # =====================================================

    assert (
        baseline.drivers.price
        == 150.0
    )

    assert (
        baseline.capital_structure.annual_cash_interest_paid
        == 25000.0
    )

    assert (
        baseline.working_capital.ar_days
        == 90.0
    )

    assert baseline.version == 1

    # =====================================================
    # FINANCIAL ASSERTIONS
    # =====================================================

    assert (
        evaluation.financial_projection.baseline
        is not None
    )

    assert (
        evaluation.financial_projection.projected
        is not None
    )

    assert (
        impact.revenue_delta
        == 120000.0
    )

    assert (
        impact.ebitda_delta
        == 120000.0
    )

    assert (
        impact.net_profit_delta
        == 97500.0
    )

    # =====================================================
    # SUCCESS
    # =====================================================

    print()
    print("==========================================")
    print("✅ DECISION EVALUATOR TEST PASSED")
    print("==========================================")


if __name__ == "__main__":
    main()
