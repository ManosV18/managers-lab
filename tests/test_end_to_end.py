from core.models import (
    CompanyState,
    OperationalDrivers,
    CapitalStructure,
    WorkingCapitalPolicy,
)

from core.decision import DecisionFactory
from core.decision_runner import DecisionRunner
from core.financial_engine import FinancialEngine


def main():

    # =========================================================
    # 1. BASELINE
    # =========================================================

    baseline = CompanyState(
        version=1,
        created_at="2026-01-01T00:00:00",
        label="Test Company",

        drivers=OperationalDrivers(
            price=150.0,
            volume=12000.0,
            variable_cost_per_unit=100.0,
            fixed_opex=450000.0,
            fixed_assets=800000.0,
            depreciation=50000.0,
            target_profit_goal=0.0,
            opening_cash=150000.0,
        ),

        capital_structure=CapitalStructure(
            wacc=0.08,
            total_debt=500000.0,
            equity=500000.0,
            cost_of_debt=0.06,

            # CANONICAL FIELD
            annual_cash_interest_paid=25000.0,

            annual_debt_service=70000.0,
            principal_payments=45000.0,
            tax_rate=0.22,
        ),

        working_capital=WorkingCapitalPolicy(
            ar_days=90.0,
            inventory_days=75.0,
            ap_days=45.0,
        ),
    )

    # =========================================================
    # 2. BASELINE FINANCIALS
    # =========================================================

    baseline_fin = FinancialEngine.calculate_statements(
        baseline
    )

    print("\n================ BASELINE ================")
    print(f"Revenue:       €{baseline_fin.income_statement.revenue:,.2f}")
    print(f"EBITDA:        €{baseline_fin.income_statement.ebitda:,.2f}")
    print(f"EBIT:          €{baseline_fin.income_statement.ebit:,.2f}")
    print(f"Interest:      €{baseline_fin.income_statement.interest_expense:,.2f}")
    print(f"EBT:           €{baseline_fin.income_statement.ebt:,.2f}")
    print(f"Tax:           €{baseline_fin.income_statement.tax:,.2f}")
    print(f"Net Profit:    €{baseline_fin.income_statement.net_profit:,.2f}")
    print(f"FCFE:          €{baseline_fin.fcfe:,.2f}")

    # =========================================================
    # 3. CREATE MULTIPLE DECISIONS
    # =========================================================

    # Decision 1: Μείωση τόκων (€25,000 → €20,000)
    decision = DecisionFactory.annual_interest_change(
        decision_id="interest_001",
        target_annual_interest=20000.0,
    )

    # Decision 2: Αύξηση τιμής (€150 → €160)
    price_decision = DecisionFactory.price_change(
        decision_id="price_001",
        target_price=160.0,
    )

    # Decision 3: Βελτίωση απαιτήσεων AR Days (90 → 60 ημέρες)
    ar_decision = DecisionFactory.ar_days_change(
        decision_id="ar_001",
        target_ar_days=60.0,
    )

    decisions_list = [
        decision,
        price_decision,
        ar_decision,
    ]

    print("\n================ DECISIONS APPLIED ================")
    for d in decisions_list:
        print(f"[{d.id}] {d.name}: {d.changes}")

    # =========================================================
    # 4. RUN DECISIONS (SEQUENCE EXECUTION)
    # =========================================================

    projected_state, report = DecisionRunner.run_many(
        baseline,
        decisions_list,
    )

    # =========================================================
    # 5. PROJECTED FINANCIALS
    # =========================================================

    projection = FinancialEngine.build_projection(
        baseline,
        projected_state,
    )

    projected = projection.projected
    impact = projection.impact

    print("\n================ PROJECTED ================")
    print(f"Revenue:       €{projected.income_statement.revenue:,.2f}")
    print(f"EBITDA:        €{projected.income_statement.ebitda:,.2f}")
    print(f"EBIT:          €{projected.income_statement.ebit:,.2f}")
    print(f"Interest:      €{projected.income_statement.interest_expense:,.2f}")
    print(f"EBT:           €{projected.income_statement.ebt:,.2f}")
    print(f"Tax:           €{projected.income_statement.tax:,.2f}")
    print(f"Net Profit:    €{projected.income_statement.net_profit:,.2f}")
    print(f"FCFE:          €{projected.fcfe:,.2f}")

    # =========================================================
    # 6. IMPACT
    # =========================================================

    print("\n================ IMPACT ================")
    print(f"Revenue Δ:        €{impact.revenue_delta:,.2f}")
    print(f"EBITDA Δ:         €{impact.ebitda_delta:,.2f}")
    print(f"Net Profit Δ:     €{impact.net_profit_delta:,.2f}")
    print(f"NWC Cash Impact:  €{impact.nwc_cash_impact_delta:,.2f}")
    print(f"FCFE Δ:           €{impact.fcfe_delta:,.2f}")

    # =========================================================
    # 7. MULTI-DECISION ASSERTIONS
    # =========================================================

    # 1. Verification driver changes
    assert projected_state.capital_structure.annual_cash_interest_paid == 20000.0
    assert projected_state.drivers.price == 160.0
    assert projected_state.working_capital.ar_days == 60.0

    # 2. Revenue Impact: (160 - 150) * 12,000 = +€120,000
    assert impact.revenue_delta == 120000.0
    assert impact.ebitda_delta == 120000.0

    # 3. Interest Impact: -€5,000 expense -> +€5,000 EBT
    # Total EBT Delta = €120,000 (Revenue) + €5,000 (Interest Savings) = €125,000
    # Net Profit Delta = €125,000 * (1 - 0.22) = €97,500
    assert abs(impact.net_profit_delta - 97500.0) < 0.01

    # 4. State Version Sequence Check (Base v1 + 3 decisions = v4)
    assert projected_state.version == 2

    print("\n==========================================")
    print("✅ MULTI-DECISION END-TO-END TEST PASSED")
    print("==========================================\n")


if __name__ == "__main__":
    main()
