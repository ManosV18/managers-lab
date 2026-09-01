from typing import Dict, Any

from core.models import CompanyState
from core.baseline_repository import BaselineRepository


class StateBuilder:
    """
    Builds projected CompanyState objects.

    Architecture:

        Locked Baseline
              ↓
          Decision
              ↓
        DecisionEngine
              ↓
        Projected CompanyState

    Exactly ONE Decision is evaluated at a time.

    No scenario stacking.
    No scenario priority.
    No active/inactive scenario logic.
    """

    def __init__(
        self,
        baseline_repository: BaselineRepository,
    ):
        self.baseline_repository = baseline_repository

    # =====================================================
    # BASELINE
    # =====================================================

    def build_baseline_only(
        self,
    ) -> CompanyState:

        return self.baseline_repository.get()


    # =====================================================
    # COMPARE STATES
    # =====================================================

    def compare_states(
        self,
        baseline: CompanyState,
        projected: CompanyState,
    ) -> Dict[str, Any]:

        if not isinstance(
            baseline,
            CompanyState,
        ):
            raise TypeError(
                "compare_states() expects baseline "
                "to be a CompanyState."
            )

        if not isinstance(
            projected,
            CompanyState,
        ):
            raise TypeError(
                "compare_states() expects projected "
                "to be a CompanyState."
            )

        return {
            "baseline_version": baseline.version,
            "projected_version": projected.version,

            "baseline_label": baseline.label,
            "projected_label": projected.label,

            "drivers_changed": {
                "price": (
                    baseline.drivers.price,
                    projected.drivers.price,
                ),
                "volume": (
                    baseline.drivers.volume,
                    projected.drivers.volume,
                ),
                "variable_cost_per_unit": (
                    baseline.drivers.variable_cost_per_unit,
                    projected.drivers.variable_cost_per_unit,
                ),
                "fixed_opex": (
                    baseline.drivers.fixed_opex,
                    projected.drivers.fixed_opex,
                ),
                "depreciation": (
                    baseline.drivers.depreciation,
                    projected.drivers.depreciation,
                ),
            },

            "working_capital_changed": {
                "ar_days": (
                    baseline.working_capital.ar_days,
                    projected.working_capital.ar_days,
                ),
                "inventory_days": (
                    baseline.working_capital.inventory_days,
                    projected.working_capital.inventory_days,
                ),
                "ap_days": (
                    baseline.working_capital.ap_days,
                    projected.working_capital.ap_days,
                ),
            },

            "capital_structure_changed": {
                "wacc": (
                    baseline.capital_structure.wacc,
                    projected.capital_structure.wacc,
                ),
                "total_debt": (
                    baseline.capital_structure.total_debt,
                    projected.capital_structure.total_debt,
                ),
                "cost_of_debt": (
                    baseline.capital_structure.cost_of_debt,
                    projected.capital_structure.cost_of_debt,
                ),
                "tax_rate": (
                    baseline.capital_structure.tax_rate,
                    projected.capital_structure.tax_rate,
                ),
                "principal_payments": (
                    baseline.capital_structure.principal_payments,
                    projected.capital_structure.principal_payments,
                ),
            },
        }
