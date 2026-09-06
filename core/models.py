from dataclasses import dataclass
from typing import Optional


# =========================================================
# OPERATIONAL DRIVERS
# =========================================================

@dataclass(frozen=True)
class OperationalDrivers:
    """
    Core operating assumptions of the company.

    These fields represent the operating baseline and preserve
    the information used by the legacy Managers Lab tools.
    """

    price: float
    volume: float
    variable_cost_per_unit: float
    fixed_opex: float
    fixed_assets: float
    depreciation: float
    target_profit_goal: float
    opening_cash: float


# =========================================================
# CAPITAL STRUCTURE
# =========================================================

@dataclass(frozen=True)
class CapitalStructure:
    """
    Financing and capital structure assumptions.

    All rates are stored internally as decimals.

    Example:
        0.08 = 8%
    """

    wacc: float
    total_debt: float
    equity: float
    cost_of_debt: float
    annual_cash_interest_paid: float
    annual_debt_service: float
    principal_payments: float
    tax_rate: float


# =========================================================
# WORKING CAPITAL POLICY
# =========================================================

@dataclass(frozen=True)
class WorkingCapitalPolicy:
    """
    Working capital operating policy.
    """

    ar_days: float
    inventory_days: float
    ap_days: float


# =========================================================
# COMPANY STATE
# =========================================================

@dataclass(frozen=True)
class CompanyState:
    """
    Immutable representation of the company's state.

    This object is the central state contract used by:

        Baseline
            ↓
        Decision
            ↓
        Decision Engine / Runner
            ↓
        Projected CompanyState
            ↓
        Financial Engine
            ↓
        Control Tower

    The CompanyState intentionally preserves the broader
    Managers Lab baseline data so downstream Decision Labs
    can use the required fields.
    """

    version: int
    created_at: str
    label: str

    drivers: OperationalDrivers
    capital_structure: CapitalStructure
    working_capital: WorkingCapitalPolicy
