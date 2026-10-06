from dataclasses import dataclass
from typing import List

import numpy_financial as npf


# ============================================================================
# 1. ASSUMPTIONS
# ============================================================================

@dataclass(frozen=True)
class ReplacementAssumptions:

    # New machine
    new_machine_cost: float
    new_machine_life: int
    annual_operating_cost_reduction: float
    new_machine_residual_pct: float = 0.05

    # Old machine
    old_machine_market_value: float = 0.0
    old_machine_book_value: float = 0.0
    old_machine_annual_depreciation: float = 0.0

    # What the old machine would be worth at the end of
    # the comparison period if we KEEP it.
    old_machine_terminal_value_if_kept: float = 0.0

    # Company
    increase_nwc: float = 0.0
    tax_rate: float = 0.0
    wacc: float = 0.0


# ============================================================================
# 2. YEAR
# ============================================================================

@dataclass(frozen=True)
class ReplacementYear:

    year: int

    operating_cost_savings: float

    new_depreciation: float
    old_depreciation: float
    depreciation_change: float

    tax_shield_from_depreciation: float
    after_tax_operating_savings: float

    terminal_value: float
    terminal_tax: float
    nwc_recovery: float

    incremental_cash_flow: float
    cumulative_cash_flow: float


# ============================================================================
# 3. RESULT
# ============================================================================

@dataclass(frozen=True)
class ReplacementResult:

    new_machine_residual_value: float
    new_machine_depreciable_base: float
    annual_new_depreciation: float

    after_tax_old_machine_sale_proceeds: float
    old_sale_tax_effect: float

    initial_incremental_outlay: float

    yearly_cash_flows: List[ReplacementYear]

    npv: float
    irr: float
    mirr: float
    payback_years: float


# ============================================================================
# 4. TAX ON ASSET SALE
# ============================================================================

def calculate_after_tax_sale_proceeds(
    sale_value: float,
    book_value: float,
    tax_rate: float,
) -> float:

    taxable_gain = sale_value - book_value

    tax = taxable_gain * tax_rate

    return sale_value - tax


# ============================================================================
# 5. PAYBACK
# ============================================================================

def calculate_payback(
    cash_flows: List[float],
) -> float:

    cumulative = 0.0

    for i, cash_flow in enumerate(cash_flows):

        previous = cumulative

        cumulative += cash_flow

        if cumulative >= 0:

            if i == 0:
                return 0.0

            if cash_flow == 0:
                return float(i)

            fraction = (
                -previous / cash_flow
            )

            return (i - 1) + fraction

    return float("inf")


# ============================================================================
# 6. CORE ENGINE
# ============================================================================

def evaluate_replacement(
    assumptions: ReplacementAssumptions,
) -> ReplacementResult:

    tax_rate = max(
        0.0,
        min(1.0, assumptions.tax_rate),
    )

    wacc = max(
        -0.999999,
        assumptions.wacc,
    )

    life = max(
        1,
        int(assumptions.new_machine_life),
    )

    # ========================================================================
    # NEW MACHINE DEPRECIATION
    # ========================================================================

    residual_value = (
        assumptions.new_machine_cost
        * assumptions.new_machine_residual_pct
    )

    residual_value = max(
        0.0,
        residual_value,
    )

    depreciable_base = max(
        0.0,
        assumptions.new_machine_cost
        - residual_value,
    )

    # Straight-line depreciation
    annual_new_depreciation = (
        depreciable_base / life
    )

    # ========================================================================
    # OLD MACHINE SALE
    # ========================================================================

    after_tax_old_sale_proceeds = (
        calculate_after_tax_sale_proceeds(
            sale_value=assumptions.old_machine_market_value,
            book_value=assumptions.old_machine_book_value,
            tax_rate=tax_rate,
        )
    )

    old_sale_tax_effect = (
        after_tax_old_sale_proceeds
        - assumptions.old_machine_market_value
    )

    # ========================================================================
    # INITIAL INCREMENTAL OUTLAY
    # ========================================================================

    initial_outlay = (
        -assumptions.new_machine_cost
        + after_tax_old_sale_proceeds
        - assumptions.increase_nwc
    )

    cash_flows = [
        initial_outlay
    ]

    yearly_results = []

    cumulative_cash_flow = initial_outlay

    # ========================================================================
    # YEAR 1 ... N
    # ========================================================================

    for year in range(
        1,
        life + 1,
    ):

        old_depreciation = (
            assumptions.old_machine_annual_depreciation
        )

        depreciation_change = (
            annual_new_depreciation
            - old_depreciation
        )

        # Tax shield can be positive or negative.
        depreciation_tax_shield = (
            depreciation_change
            * tax_rate
        )

        # Operating cost reduction is an economic saving.
        after_tax_operating_savings = (
            assumptions.annual_operating_cost_reduction
            * (1.0 - tax_rate)
        )

        terminal_value = 0.0
        terminal_tax = 0.0
        nwc_recovery = 0.0

        # ====================================================================
        # TERMINAL YEAR
        # ====================================================================

        if year == life:

            terminal_value = (
                residual_value
            )

            # Because straight-line depreciation ends
            # at the residual value, book value equals
            # residual value at the end of the useful life.
            terminal_book_value = residual_value

            terminal_tax = (
                terminal_value
                - terminal_book_value
            ) * tax_rate

            nwc_recovery = (
                assumptions.increase_nwc
            )

        # ====================================================================
        # INCREMENTAL CASH FLOW
        # ====================================================================

        incremental_cash_flow = (
            after_tax_operating_savings
            + depreciation_tax_shield
            + terminal_value
            - terminal_tax
            + nwc_recovery
        )

        cumulative_cash_flow += (
            incremental_cash_flow
        )

        cash_flows.append(
            incremental_cash_flow
        )

        yearly_results.append(
            ReplacementYear(
                year=year,
                operating_cost_savings=(
                    assumptions
                    .annual_operating_cost_reduction
                ),
                new_depreciation=(
                    annual_new_depreciation
                ),
                old_depreciation=(
                    old_depreciation
                ),
                depreciation_change=(
                    depreciation_change
                ),
                tax_shield_from_depreciation=(
                    depreciation_tax_shield
                ),
                after_tax_operating_savings=(
                    after_tax_operating_savings
                ),
                terminal_value=(
                    terminal_value
                ),
                terminal_tax=(
                    terminal_tax
                ),
                nwc_recovery=(
                    nwc_recovery
                ),
                incremental_cash_flow=(
                    incremental_cash_flow
                ),
                cumulative_cash_flow=(
                    cumulative_cash_flow
                ),
            )
        )

    # =========================================================================
    # RETURN METRICS
    # =========================================================================

    npv = float(
        npf.npv(
            wacc,
            cash_flows,
        )
    )

    try:

        irr = float(
            npf.irr(
                cash_flows,
            )
        )

        if irr != irr:
            irr = 0.0

    except Exception:

        irr = 0.0

    try:

        mirr = float(
            npf.mirr(
                cash_flows,
                wacc,
                wacc,
            )
        )

        if mirr != mirr:
            mirr = 0.0

    except Exception:

        mirr = 0.0

    payback = calculate_payback(
        cash_flows
    )

    return ReplacementResult(
        new_machine_residual_value=(
            residual_value
        ),
        new_machine_depreciable_base=(
            depreciable_base
        ),
        annual_new_depreciation=(
            annual_new_depreciation
        ),
        after_tax_old_machine_sale_proceeds=(
            after_tax_old_sale_proceeds
        ),
        old_sale_tax_effect=(
            old_sale_tax_effect
        ),
        initial_incremental_outlay=(
            initial_outlay
        ),
        yearly_cash_flows=(
            yearly_results
        ),
        npv=npv,
        irr=irr,
        mirr=mirr,
        payback_years=payback,
    )
