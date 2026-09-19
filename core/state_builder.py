from datetime import datetime
from typing import Dict, Any

from core.models import (
    CapitalStructure,
    CompanyState,
    OperationalDrivers,
    WorkingCapitalPolicy,
)
from core.baseline_repository import BaselineRepository


class StateBuilder:

    def __init__(
        self,
        baseline_repository: BaselineRepository,
    ):
        self.baseline_repository = baseline_repository

    # =====================================================
    # DEFAULT / DEMO BASELINE
    # =====================================================

    def build_default_baseline(self) -> CompanyState:

        drivers = OperationalDrivers(
            price=150.0,
            volume=12000.0,
            variable_cost_per_unit=100.0,
            fixed_opex=450000.0,
            fixed_assets=800000.0,
            depreciation=50000.0,
            target_profit_goal=200000.0,
            opening_cash=150000.0,
        )

        capital_structure = CapitalStructure(
            wacc=0.08,
            total_debt=500000.0,
            equity=500000.0,
            cost_of_debt=0.06,
            annual_cash_interest_paid=25000.0,
            annual_debt_service=70000.0,
            principal_payments=45000.0,
            tax_rate=0.22,
        )

        working_capital = WorkingCapitalPolicy(
            ar_days=90.0,
            inventory_days=75.0,
            ap_days=45.0,
        )

        return CompanyState(
            version=1,
            created_at=datetime.utcnow().isoformat(
                timespec="seconds"
            ),
            label="Managers Lab Demo Company",
            drivers=drivers,
            capital_structure=capital_structure,
            working_capital=working_capital,
            profit_before_tax=150000.0,
            tax=33000.0,
            net_profit=117000.0,
        )

    # =====================================================
    # BASELINE
    # =====================================================

    def build_baseline_only(
        self,
    ) -> CompanyState:

        return self.baseline_repository.get()
