from dataclasses import dataclass
from typing import Dict, Any


# =========================================================
# DECISION
# =========================================================

@dataclass(frozen=True)
class Decision:
    """
    Canonical business Decision.

    A Decision is a declarative description of a
    management action.

    It does NOT:
        - modify CompanyState
        - execute itself
        - calculate financial impact
        - resolve conflicts
        - manage scenarios

    Execution is handled exclusively by:

        Decision
            ↓
        DecisionPlan
            ↓
        DecisionRunner.run_many()
            ↓
        Projected CompanyState
    """

    id: str
    name: str
    description: str
    category: str
    changes: Dict[str, Any]

    # =====================================================
    # VALIDATION
    # =====================================================

    def __post_init__(self) -> None:

        if not isinstance(self.id, str):
            raise TypeError(
                "Decision id must be a string."
            )

        if not self.id.strip():
            raise ValueError(
                "Decision id cannot be empty."
            )

        if not isinstance(self.name, str):
            raise TypeError(
                "Decision name must be a string."
            )

        if not self.name.strip():
            raise ValueError(
                "Decision name cannot be empty."
            )

        if not isinstance(
            self.description,
            str,
        ):
            raise TypeError(
                "Decision description must be a string."
            )

        if not isinstance(
            self.category,
            str,
        ):
            raise TypeError(
                "Decision category must be a string."
            )

        if not self.category.strip():
            raise ValueError(
                "Decision category cannot be empty."
            )

        if not isinstance(
            self.changes,
            dict,
        ):
            raise TypeError(
                "Decision changes must be a dictionary."
            )


# =========================================================
# DECISION FACTORY
# =========================================================

class DecisionFactory:
    """
    Factory for creating canonical Decision objects.

    Factory methods describe business intent only.

    They do NOT execute decisions.

    Execution is handled by DecisionRunner.
    """

    # =====================================================
    # GENERIC CREATE
    # =====================================================

    @classmethod
    def create(
        cls,
        *,
        decision_id: str,
        name: str,
        description: str,
        category: str,
        changes: Dict[str, Any],
    ) -> Decision:

        return Decision(
            id=decision_id,
            name=name,
            description=description,
            category=category,
            changes=dict(changes),
        )

    # =====================================================
    # PRICE CHANGE
    # =====================================================

    @classmethod
    def price_change(
        cls,
        *,
        decision_id: str,
        target_price: float,
    ) -> Decision:

        return cls.create(
            decision_id=decision_id,
            name=f"Price Change → € {target_price:,.2f}",
            description=(
                f"Change selling price to "
                f"€ {target_price:,.2f} per unit."
            ),
            category="pricing",
            changes={
                "price": float(target_price),
            },
        )
    
    # =====================================================
    # VOLUME CHANGE
    # =====================================================

    @classmethod
    def volume_change(
        cls,
        *,
        decision_id: str,
        target_volume: float,
    ) -> Decision:

        return cls.create(
            decision_id=decision_id,
            name=f"Volume Change → {target_volume:,.0f}",
            description=(
                f"Change sales volume to "
                f"{target_volume:,.0f} units."
            ),
            category="sales",
            changes={
                "volume": float(target_volume),
            },
        )
    
    # =====================================================
    # VARIABLE COST CHANGE
    # =====================================================

    @classmethod
    def variable_cost_change(
        cls,
        *,
        decision_id: str,
        target_variable_cost: float,
    ) -> Decision:

        return cls.create(
            decision_id=decision_id,
            name=(
                "Variable Cost Change → "
                f"€ {target_variable_cost:,.2f}"
            ),
            description=(
                "Change variable cost per unit."
            ),
            category="cost",
            changes={
                "variable_cost_per_unit": float(
                    target_variable_cost
                ),
            },
        )

    # =====================================================
    # FIXED OPEX CHANGE
    # =====================================================

    @classmethod
    def fixed_opex_change(
        cls,
        *,
        decision_id: str,
        target_fixed_opex: float,
    ) -> Decision:

        return cls.create(
            decision_id=decision_id,
            name=(
                "Fixed OPEX Change → "
                f"€ {target_fixed_opex:,.0f}"
            ),
            description=(
                "Change annual fixed operating expenses."
            ),
            category="cost",
            changes={
                "fixed_opex": float(
                    target_fixed_opex
                ),
            },
        )

    # =====================================================
    # AR DAYS
    # =====================================================

    @classmethod
    def ar_days_change(
        cls,
        *,
        decision_id: str,
        target_ar_days: float,
    ) -> Decision:

        return cls.create(
            decision_id=decision_id,
            name=f"AR Days → {target_ar_days:.0f}",
            description=(
                "Change accounts receivable days."
            ),
            category="working_capital",
            changes={
                "ar_days": float(
                    target_ar_days
                ),
            },
        )

    # =====================================================
    # INVENTORY DAYS
    # =====================================================

    @classmethod
    def inventory_days_change(
        cls,
        *,
        decision_id: str,
        target_inventory_days: float,
    ) -> Decision:

        return cls.create(
            decision_id=decision_id,
            name=(
                f"Inventory Days → "
                f"{target_inventory_days:.0f}"
            ),
            description=(
                "Change inventory holding days."
            ),
            category="working_capital",
            changes={
                "inventory_days": float(
                    target_inventory_days
                ),
            },
        )

    # =====================================================
    # AP DAYS
    # =====================================================

    @classmethod
    def ap_days_change(
        cls,
        *,
        decision_id: str,
        target_ap_days: float,
    ) -> Decision:

        return cls.create(
            decision_id=decision_id,
            name=f"AP Days → {target_ap_days:.0f}",
            description=(
                "Change accounts payable days."
            ),
            category="working_capital",
            changes={
                "ap_days": float(
                    target_ap_days
                ),
            },
        )

    # =====================================================
    # WACC CHANGE
    # =====================================================

    @classmethod
    def wacc_change(
        cls,
        *,
        decision_id: str,
        target_wacc: float,
    ) -> Decision:

        return cls.create(
            decision_id=decision_id,
            name=f"WACC → {target_wacc:.2%}",
            description=(
                f"Change WACC to "
                f"{target_wacc:.2%}."
            ),
            category="capital_structure",
            changes={
                "wacc": float(
                    target_wacc
                ),
            },
        )

    # =====================================================
    # DEBT CHANGE
    # =====================================================

    @classmethod
    def debt_change(
        cls,
        *,
        decision_id: str,
        target_debt: float,
    ) -> Decision:

        return cls.create(
            decision_id=decision_id,
            name=f"Debt → € {target_debt:,.0f}",
            description=(
                "Change total debt."
            ),
            category="capital_structure",
            changes={
                "total_debt": float(
                    target_debt
                ),
            },
        )

    # =====================================================
    # COST OF DEBT CHANGE
    # =====================================================

    @classmethod
    def cost_of_debt_change(
        cls,
        *,
        decision_id: str,
        target_cost_of_debt: float,
    ) -> Decision:

        return cls.create(
            decision_id=decision_id,
            name=(
                "Cost of Debt → "
                f"{target_cost_of_debt:.2%}"
            ),
            description=(
                "Change the cost of debt."
            ),
            category="capital_structure",
            changes={
                "cost_of_debt": float(
                    target_cost_of_debt
                ),
            },
        )

    # =========================================================
    # ANNUAL INTEREST EXPENSE CHANGE
    # =========================================================

    @classmethod
    def annual_interest_change(
        cls,
        *,
        decision_id: str,
        target_annual_interest: float,
    ) -> Decision:

        return cls.create(
            decision_id=decision_id,
            name=(
                "Annual Interest Expense → "
                f"€ {target_annual_interest:,.0f}"
            ),
            description=(
                "Change annual interest expense."
            ),
            category="capital_structure",
            changes={
                "annual_cash_interest_paid": float(
                    target_annual_interest
                ),
            },
        )

    # =====================================================
    # PRINCIPAL PAYMENTS CHANGE
    # =====================================================

    @classmethod
    def principal_payments_change(
        cls,
        *,
        decision_id: str,
        target_principal_payments: float,
    ) -> Decision:

        return cls.create(
            decision_id=decision_id,
            name=(
                "Principal Payments → "
                f"€ {target_principal_payments:,.0f}"
            ),
            description=(
                "Change annual principal payments."
            ),
            category="capital_structure",
            changes={
                "principal_payments": float(
                    target_principal_payments
                ),
            },
        )
