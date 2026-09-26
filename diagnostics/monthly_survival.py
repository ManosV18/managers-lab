import pandas as pd
import streamlit as st
import plotly.graph_objects as go

from diagnostics.monthly_survival import (
    calculate_monthly_survival,
)


def calculate_monthly_survival(
    baseline_state: Any,
    projected_state: Optional[Any] = None,
    season_factor: float = 100.0,
    cash_collection_pct: Optional[float] = None,
    past_collections: Optional[float] = None,
    sim_price: Optional[float] = None,
    sim_vc: Optional[float] = None,
    sim_fc: Optional[float] = None,
    sim_debt: Optional[float] = None,
    sim_volume: Optional[float] = None,
) -> Dict[str, Any]:
    """
    Monthly Cash Coverage diagnostic.

    V2 architecture:
        Monthly Cash Coverage does NOT create its own
        receivables / payables timing model.

        It delegates cash timing to:
            ui.cash_management_lab.build_monthly_cash_coverage

    Scenario controls remain local to this diagnostic:
        - price
        - variable cost
        - volume
        - fixed costs
        - debt service
        - seasonality

    Cash timing comes from the same Cash Management logic
    used by the six-month cash plan.
    """

    # -----------------------------------------------------
    # STATE
    # -----------------------------------------------------

    state = (
        projected_state
        if projected_state is not None
        else baseline_state
    )

    if state is None:
        raise ValueError(
            "A baseline_state or projected_state is required."
        )

    drivers = state.drivers
    capital = state.capital_structure

    # -----------------------------------------------------
    # CANONICAL BASELINE VALUES
    # -----------------------------------------------------

    default_price = float(
        drivers.price
    )

    default_vc = float(
        drivers.variable_cost_per_unit
    )

    default_monthly_volume = (
        float(drivers.volume)
        / 12.0
    )

    default_monthly_fixed_cost = (
        float(drivers.fixed_opex)
        / 12.0
    )

    default_monthly_debt_service = (
        float(
            capital.annual_debt_service
        )
        / 12.0
    )

    # -----------------------------------------------------
    # SCENARIO VALUES
    # -----------------------------------------------------

    season_factor = max(
        0.0,
        float(season_factor),
    )

    price = (
        float(sim_price)
        if sim_price is not None
        else default_price
    )

    variable_cost = (
        float(sim_vc)
        if sim_vc is not None
        else default_vc
    )

    monthly_fixed_costs = (
        float(sim_fc)
        if sim_fc is not None
        else default_monthly_fixed_cost
    )

    monthly_debt_service = (
        float(sim_debt)
        if sim_debt is not None
        else default_monthly_debt_service
    )

    if sim_volume is not None:

        volume = float(
            sim_volume
        )

    else:

        volume = (
            default_monthly_volume
            * season_factor
            / 100.0
        )

    price = max(
        0.0,
        price,
    )

    variable_cost = max(
        0.0,
        variable_cost,
    )

    monthly_fixed_costs = max(
        0.0,
        monthly_fixed_costs,
    )

    monthly_debt_service = max(
        0.0,
        monthly_debt_service,
    )

    volume = max(
        0.0,
        volume,
    )

    # -----------------------------------------------------
    # SCENARIO SALES / PURCHASES
    # -----------------------------------------------------

    monthly_sales = (
        volume * price
    )

    monthly_purchases = (
        volume * variable_cost
    )

    # -----------------------------------------------------
    # SHARED CASH MANAGEMENT TIMING
    # -----------------------------------------------------

    # Imported here rather than at module level to avoid
    # creating unnecessary import coupling during app load.
    from ui.cash_management_lab import (
        build_monthly_cash_coverage,
    )

    cash_timing = (
        build_monthly_cash_coverage(
            baseline_state=baseline_state,
            sales_amount=monthly_sales,
            purchases_amount=monthly_purchases,
            monthly_opex=monthly_fixed_costs,
            monthly_debt=monthly_debt_service,
        )
    )

    if cash_timing is None:

        raise ValueError(
            "Cash Management timing could not be calculated."
        )

    if not cash_timing.get(
        "valid",
        False,
    ):

        raise ValueError(
            cash_timing.get(
                "reason",
                "Cash Management timing assumptions are invalid.",
            )
        )

    # -----------------------------------------------------
    # CASH FLOWS
    # -----------------------------------------------------

    current_sales_cash_in = float(
        cash_timing[
            "new_sales_receipts"
        ]
    )

    existing_ar_cash_in = float(
        cash_timing[
            "existing_ar_receipts"
        ]
    )

    total_monthly_cash_in = float(
        cash_timing[
            "cash_receipts"
        ]
    )

    current_purchase_cash_out = float(
        cash_timing[
            "new_purchase_payments"
        ]
    )

    existing_ap_cash_out = float(
        cash_timing[
            "existing_ap_payments"
        ]
    )

    supplier_cash_out = float(
        cash_timing[
            "supplier_payments"
        ]
    )

    total_cash_outflow = (
        supplier_cash_out
        + monthly_fixed_costs
        + monthly_debt_service
    )

    cash_gap = (
        total_monthly_cash_in
        - total_cash_outflow
    )

    # -----------------------------------------------------
    # CASH CONTRIBUTION
    # -----------------------------------------------------
    #
    # This is deliberately different from the old model.
    #
    # We no longer say:
    #
    #     cash collected per unit - variable cost
    #
    # because variable cost is not necessarily paid
    # immediately.
    #
    # Instead we calculate the actual month-1 cash effect
    # of the scenario through the shared AR/AP timing.
    #

    current_sales_cash_in_per_unit = (
        current_sales_cash_in / volume
        if volume > 0
        else 0.0
    )

    current_purchase_cash_out_per_unit = (
        current_purchase_cash_out / volume
        if volume > 0
        else 0.0
    )

    cash_contribution_per_unit = (
        current_sales_cash_in_per_unit
        - current_purchase_cash_out_per_unit
    )

    # -----------------------------------------------------
    # CASH BREAK-EVEN
    # -----------------------------------------------------
    #
    # Existing AR/AP receipts/payments are fixed for the
    # scenario. We calculate the incremental cash needed
    # from the current month's sales cohort.
    #

    fixed_cash_obligations = (
        monthly_fixed_costs
        + monthly_debt_service
        + existing_ap_cash_out
        - existing_ar_cash_in
    )

    incremental_cash_contribution_per_unit = (
        price
        * (
            current_sales_cash_in / monthly_sales
            if monthly_sales > 0
            else 0.0
        )
        - variable_cost
        * (
            current_purchase_cash_out / monthly_purchases
            if monthly_purchases > 0
            else 0.0
        )
    )

    if (
        incremental_cash_contribution_per_unit
        <= 0
    ):

        cash_bep = None

    else:

        cash_bep = (
            max(
                0.0,
                fixed_cash_obligations,
            )
            / incremental_cash_contribution_per_unit
        )

    unit_gap = (
        volume - cash_bep
        if cash_bep is not None
        else None
    )

    # -----------------------------------------------------
    # STATUS
    # -----------------------------------------------------

    if (
        incremental_cash_contribution_per_unit
        <= 0
    ):

        status = (
            "Negative Incremental Cash Contribution"
        )

        interpretation = (
            "Under the current Receivables and Supplier "
            "timing assumptions, an additional unit does not "
            "generate positive cash contribution in this month."
        )

    elif cash_gap < 0:

        status = "Shortfall"

        interpretation = (
            f"Monthly cash shortfall of "
            f"€{abs(cash_gap):,.0f}. "
            "Expected cash receipts are insufficient to cover "
            "supplier payments and fixed cash obligations "
            "under the current timing assumptions."
        )

    else:

        status = "Covered"

        interpretation = (
            f"Monthly cash obligations are covered with "
            f"a projected surplus of €{cash_gap:,.0f}."
        )

    # -----------------------------------------------------
    # RETURN
    # -----------------------------------------------------

    return {
        "state_version": getattr(
            state,
            "version",
            None,
        ),

        # Scenario economics.
        "price": price,
        "variable_cost": variable_cost,
        "volume": volume,
        "monthly_sales": monthly_sales,
        "monthly_purchases": monthly_purchases,

        # Cash timing.
        "current_sales_cash_in": current_sales_cash_in,
        "existing_ar_cash_in": existing_ar_cash_in,
        "total_monthly_cash_in": total_monthly_cash_in,

        "current_purchase_cash_out": current_purchase_cash_out,
        "existing_ap_cash_out": existing_ap_cash_out,
        "supplier_cash_out": supplier_cash_out,

        "monthly_fixed_costs": monthly_fixed_costs,
        "monthly_debt_service": monthly_debt_service,

        "total_cash_outflow": total_cash_outflow,
        "cash_gap": cash_gap,

        # Timing diagnostics.
        "ar_days": cash_timing[
            "ar_days"
        ],
        "ap_days": cash_timing[
            "ap_days"
        ],
        "collection_profile": cash_timing[
            "collection_profile"
        ],

        # Contribution / BEP.
        "cash_revenue_per_unit": (
            current_sales_cash_in_per_unit
        ),
        "cash_purchase_cost_per_unit": (
            current_purchase_cash_out_per_unit
        ),
        "cash_contribution_per_unit": (
            cash_contribution_per_unit
        ),
        "incremental_cash_contribution_per_unit": (
            incremental_cash_contribution_per_unit
        ),
        "fixed_cash_obligations": (
            fixed_cash_obligations
        ),
        "cash_bep": cash_bep,
        "unit_gap": unit_gap,

        # Status.
        "status": status,
        "interpretation": interpretation,

        # Full shared timing result.
        "cash_timing": cash_timing,

        # Backward-compatible fields.
        #
        # These are retained so older UI code does not
        # immediately fail, but they are no longer the
        # source of the cash calculation.
        "cash_collection_pct": (
            (
                current_sales_cash_in
                / monthly_sales
                * 100.0
            )
            if monthly_sales > 0
            else 0.0
        ),
        "past_collections": (
            existing_ar_cash_in
        ),
    }
