from __future__ import annotations

from typing import Any, Dict, Optional


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
    cash_timing: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """
    Monthly Cash Coverage diagnostic.

    Important V2 rule:
    Cash timing is owned by Cash Management.

    This diagnostic keeps the scenario controls
    (price, variable cost, fixed costs, debt and volume),
    but does not create an independent collection/payables model.

    cash_timing should normally come from:
        ui.cash_management_lab.build_monthly_cash_coverage()

    The legacy cash_collection_pct and past_collections arguments
    are retained only for compatibility with older callers.
    They are NOT used when cash_timing is supplied.
    """

    state = (
        projected_state
        if projected_state is not None
        else baseline_state
    )

    drivers = state.drivers
    capital = state.capital_structure

    default_price = float(
        drivers.price
    )

    default_vc = float(
        drivers.variable_cost_per_unit
    )

    default_monthly_volume = (
        float(drivers.volume)
        / 12.0
        * (
            float(season_factor)
            / 100.0
        )
    )

    default_monthly_fixed_cost = (
        float(drivers.fixed_opex)
        / 12.0
    )

    default_monthly_debt_service = (
        float(capital.annual_debt_service)
        / 12.0
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
        else default_monthly_debt
    )

    volume = (
        float(sim_volume)
        if sim_volume is not None
        else default_monthly_volume
    )

    volume = max(
        0.0,
        volume,
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

    monthly_sales = (
        volume
        * price
    )

    monthly_purchases = (
        volume
        * variable_cost
    )

    # -----------------------------------------------------
    # CASH TIMING
    # -----------------------------------------------------

    if cash_timing is None:

        # Compatibility fallback.
        #
        # This should only be reached by an older caller that
        # has not yet been connected to Cash Management.
        #
        # The normal V2 UI always supplies cash_timing.

        collection_pct = (
            20.0
            if cash_collection_pct is None
            else max(
                0.0,
                min(
                    100.0,
                    float(cash_collection_pct),
                ),
            )
        )

        previous_collections = (
            0.0
            if past_collections is None
            else max(
                0.0,
                float(past_collections),
            )
        )

        current_sales_cash_in = (
            monthly_sales
            * collection_pct
            / 100.0
        )

        total_monthly_cash_in = (
            current_sales_cash_in
            + previous_collections
        )

        total_supplier_payments = (
            monthly_purchases
        )

        existing_ar_receipts = (
            previous_collections
        )

        new_sales_receipts = (
            current_sales_cash_in
        )

        existing_ap_payments = 0.0
        new_purchase_payments = (
            total_supplier_payments
        )

        ar_timing_source = (
            "Legacy compatibility assumption"
        )

        ap_days = None

    else:

        if not cash_timing.get(
            "valid",
            False,
        ):

            return {
                "valid": False,
                "reason": cash_timing.get(
                    "reason",
                    "Cash timing calculation is invalid.",
                ),
            }

        existing_ar_receipts = float(
            cash_timing.get(
                "existing_ar_receipts",
                0.0,
            )
        )

        new_sales_receipts = float(
            cash_timing.get(
                "new_sales_receipts",
                0.0,
            )
        )

        total_monthly_cash_in = float(
            cash_timing.get(
                "total_cash_receipts",
                0.0,
            )
        )

        existing_ap_payments = float(
            cash_timing.get(
                "existing_ap_payments",
                0.0,
            )
        )

        new_purchase_payments = float(
            cash_timing.get(
                "new_purchase_payments",
                0.0,
            )
        )

        total_supplier_payments = float(
            cash_timing.get(
                "total_supplier_payments",
                0.0,
            )
        )

        ar_timing_source = cash_timing.get(
            "ar_timing_source",
            "Cash Management",
        )

        ap_days = cash_timing.get(
            "ap_days"
        )

    # -----------------------------------------------------
    # CASH OUTFLOW
    # -----------------------------------------------------

    total_cash_outflow = (
        total_supplier_payments
        + monthly_fixed_costs
        + monthly_debt_service
    )

    cash_gap = (
        total_monthly_cash_in
        - total_cash_outflow
    )

    # -----------------------------------------------------
    # CASH CONTRIBUTION
    #
    # This is deliberately kept as a diagnostic metric,
    # but it is now based on actual current-month cash
    # generated by the timing layer.
    # -----------------------------------------------------

    current_sales_cash_in = (
        new_sales_receipts
    )

    cash_revenue_per_unit = (
        current_sales_cash_in / volume
        if volume > 0
        else 0.0
    )

    new_purchase_cash_out = (
        new_purchase_payments
    )

    cash_variable_cost_per_unit = (
        new_purchase_cash_out / volume
        if volume > 0
        else 0.0
    )

    cash_contribution_per_unit = (
        cash_revenue_per_unit
        - cash_variable_cost_per_unit
    )

    # -----------------------------------------------------
    # CASH BREAK-EVEN
    # -----------------------------------------------------

    fixed_cash_obligations = (
        monthly_fixed_costs
        + monthly_debt_service
        + existing_ap_payments
        - existing_ar_receipts
    )

    if cash_contribution_per_unit <= 0:

        cash_bep = None

    else:

        cash_bep = (
            max(
                0.0,
                fixed_cash_obligations,
            )
            / cash_contribution_per_unit
        )

    unit_gap = (
        volume - cash_bep
        if cash_bep is not None
        else None
    )

    # -----------------------------------------------------
    # STATUS
    # -----------------------------------------------------

    if cash_contribution_per_unit <= 0:

        status = (
            "Negative Cash Contribution"
        )

        interpretation = (
            "Cash generated by the current month's "
            "sales is insufficient, after current-month "
            "purchase cash payments, to generate a "
            "positive cash contribution."
        )

    elif cash_gap < 0:

        status = "Shortfall"

        interpretation = (
            f"Monthly cash shortfall of "
            f"€{abs(cash_gap):,.0f}. "
            "Cash receipts arriving this month are "
            "insufficient to cover supplier payments "
            "and other modeled cash obligations."
        )

    else:

        status = "Covered"

        interpretation = (
            f"Monthly cash obligations are covered "
            f"with a projected surplus of "
            f"€{cash_gap:,.0f}."
        )

    return {
        "valid": True,

        "state_version": getattr(
            state,
            "version",
            None,
        ),

        "price": price,
        "variable_cost": variable_cost,
        "volume": volume,

        "monthly_sales": monthly_sales,
        "monthly_purchases": monthly_purchases,

        "monthly_fixed_costs": monthly_fixed_costs,
        "monthly_debt_service": monthly_debt_service,

        "existing_ar_receipts": existing_ar_receipts,
        "new_sales_receipts": new_sales_receipts,
        "current_sales_cash_in": current_sales_cash_in,
        "total_monthly_cash_in": total_monthly_cash_in,

        "existing_ap_payments": existing_ap_payments,
        "new_purchase_payments": new_purchase_payments,
        "total_supplier_payments": total_supplier_payments,

        "total_cash_outflow": total_cash_outflow,
        "cash_gap": cash_gap,

        "cash_revenue_per_unit": cash_revenue_per_unit,
        "cash_variable_cost_per_unit": (
            cash_variable_cost_per_unit
        ),
        "cash_contribution_per_unit": (
            cash_contribution_per_unit
        ),

        "cash_bep": cash_bep,
        "unit_gap": unit_gap,

        "ar_timing_source": ar_timing_source,
        "ap_days": ap_days,

        "status": status,
        "interpretation": interpretation,
    }
