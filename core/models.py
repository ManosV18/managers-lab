from dataclasses import dataclass

# =========================================================

# OPERATIONAL DRIVERS

# =========================================================

@dataclass(frozen=True)
class OperationalDrivers:
"""
Core operating data of the company.

```
These values represent the company's reported/current
operating position and the business drivers used by
downstream decision tools.

Nothing is calculated here.
"""

revenue: float
price: float
volume: float
variable_cost_per_unit: float
fixed_opex: float
fixed_assets: float
depreciation: float
target_profit_goal: float
opening_cash: float
```

# =========================================================

# REPORTED FINANCIALS

# =========================================================

@dataclass(frozen=True)
class ReportedFinancials:
"""
Financial figures reported/provided by the user.

```
These are baseline facts supplied by the company.

They are NOT calculated from the operational drivers.
"""

ebit: float
ebt: float
tax: float
net_profit: float
```

# =========================================================

# CAPITAL STRUCTURE

# =========================================================

@dataclass(frozen=True)
class CapitalStructure:
"""
Financing and capital structure data.

```
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
```

# =========================================================

# WORKING CAPITAL POLICY

# =========================================================

@dataclass(frozen=True)
class WorkingCapitalPolicy:
"""
Working capital operating policy.
"""

```
ar_days: float
inventory_days: float
ap_days: float
```

# =========================================================

# COMPANY STATE

# =========================================================

@dataclass(frozen=True)
class CompanyState:
"""
Immutable representation of the company's state.

```
The CompanyState is the canonical contract shared by:

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
    Diagnostics / Control Tower

Baseline values are supplied by the user.

No financial metric is calculated while creating
the baseline.
"""

version: int
created_at: str
label: str

drivers: OperationalDrivers
reported_financials: ReportedFinancials
capital_structure: CapitalStructure
working_capital: WorkingCapitalPolicy
