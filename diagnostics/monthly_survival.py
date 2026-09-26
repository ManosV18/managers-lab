from __future__ import annotations

from typing import Any, Dict, Optional


# =========================================================
# MONTHLY CASH SURVIVAL DIAGNOSTIC
# =========================================================

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
    Monthly Cash Coverage / Survival diagnostic.

    Uses the same receivables and supplier-payment timing logic
    as Cash Management.

    The diagnostic itself does not create an independent cash model.
    It delegates monthly cash timing to:

        ui.cash_management_lab.build_monthly_cash_coverage()

    Legacy parameters cash_collection_pct and past_collections
    are retained only for backward compatibility with older callers.
    They are NOT used as the source of monthly cash timing.
    """

    # =====================================================
    # SHARED CASH TIMING ENGINE
    # =====================================================

    from ui.cash_management_lab import (
        build_monthly_cash_coverage,
    )

    # =====================================================
    # STATE SELECTION
    # =====================================================

    state = (
        projected_state
        if projected_state is not None
        else baseline_state
    )

    drivers = state.drivers
    capital = state.capital_structure

    # =====================================================
    # CANONICAL BASELINE VALUES
    # =====================================================

    default_price = float(
        drivers.price
    )

    default_vc = float(
        drivers.variable_cost_per_unit
    )

    default_monthly_volume = (
        float(drivers.volume)
        / 12.0
        * (float(season_factor) / 100.0)
    )

    default_monthly_fixed_cost = (
        float(drivers.fixed_opex)
        / 12.0
    )

    default_monthly_debt_service = (
        float(capital.annual_debt_service)
        / 12.0
    )

    # =====================================================
    # SIMULATION OVERRIDES
    # =====================================================

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

    volume = (
        float(sim_volume)
        if sim_volume is not None
        else default_monthly_volume
    )

    # =====================================================
    # BASIC SCENARIO VALUES
    # =====================================================

    sales_amount = (
        volume
        * price
    )

    purchases_amount = (
        volume
        * variable_cost
    )

    # =====================================================
    # SHARED CASH MANAGEMENT TIMING
    # =====================================================

    if cash_timing is None:
        cash_timing = build_monthly_cash_coverage(
            baseline_state=baseline_state,
            sales_amount=sales_amount,
            purchases_amount=purchases_amount,
            monthly_opex=monthly_fixed_costs,
            monthly_debt=monthly_debt_service,
        )
    
    if not cash_timing.get("valid", False):
        raise ValueError(
            cash_timing.get(
                "error",
                "Unable to build monthly cash timing.",
            )
        )

    # =====================================================
    # CASH RECEIPTS
    # =====================================================

    existing_ar_cash_in = float(
        cash_timing.get(
            "existing_ar_receipts",
            0.0,
        )
    )

    current_sales_cash_in = float(
        cash_timing.get(
            "new_sales_receipts",
            0.0,
        )
    )

    total_monthly_cash_in = (
        existing_ar_cash_in
        + current_sales_cash_in
    )

    # =====================================================
    # CASH PAYMENTS
    # =====================================================

    existing_ap_cash_out = float(
        cash_timing.get(
            "existing_ap_payments",
            0.0,
        )
    )

    current_purchase_cash_out = float(
        cash_timing.get(
            "new_purchase_payments",
            0.0,
        )
    )

    supplier_cash_out = (
        existing_ap_cash_out
        + current_purchase_cash_out
    )

    # =====================================================
    # TOTAL CASH OUTFLOW
    # =====================================================

    total_cash_outflow = (
        supplier_cash_out
        + monthly_fixed_costs
        + monthly_debt_service
    )

    # =====================================================
    # CASH GAP
    # =====================================================

    cash_gap = (
        total_monthly_cash_in
        - total_cash_outflow
    )

    # =====================================================
    # INCREMENTAL CASH ECONOMICS
    # =====================================================

    collection_profile = cash_timing.get(
        "collection_profile"
    )

    ar_days = float(
        cash_timing.get(
            "ar_days",
            0.0,
        )
    )

    ap_days = float(
        cash_timing.get(
            "ap_days",
            0.0,
        )
    )

    # Cash actually received from one additional unit
    # sold this month.
    cash_revenue_per_unit = (
        current_sales_cash_in / volume
        if volume > 0
        else 0.0
    )

    # Cash actually paid to suppliers for one additional
    # unit purchased this month.
    cash_purchase_cost_per_unit = (
        current_purchase_cash_out / volume
        if volume > 0
        else 0.0
    )

    cash_contribution_per_unit = (
        cash_revenue_per_unit
        - cash_purchase_cost_per_unit
    )

    # =====================================================
    # CASH BREAK-EVEN
    # =====================================================

    fixed_cash_obligations = (
        monthly_fixed_costs
        + monthly_debt_service
        + existing_ap_cash_out
        - existing_ar_cash_in
    )

    if cash_contribution_per_unit <= 0:

        cash_bep = None

    elif fixed_cash_obligations <= 0:

        cash_bep = 0.0

    else:

        cash_bep = (
            fixed_cash_obligations
            / cash_contribution_per_unit
        )

    # =====================================================
    # UNIT GAP
    # =====================================================

    if cash_bep is None:

        unit_gap = None

    else:

        unit_gap = (
            volume
            - cash_bep
        )

    # =====================================================
    # STATUS & INTERPRETATION
    # =====================================================

    if cash_contribution_per_unit <= 0:

        status = "Negative Cash Contribution"

        interpretation = (
            "Cash received from an additional unit this month "
            "does not cover the supplier cash payment associated "
            "with that unit under the current timing assumptions."
        )

    elif cash_gap < 0:

        status = "Shortfall"

        interpretation = (
            f"Monthly cash shortfall of "
            f"€{abs(cash_gap):,.0f}. "
            "Expected cash receipts are insufficient to cover "
            "supplier payments, operating expenses and debt service."
        )

    else:

        status = "Covered"

        interpretation = (
            f"Monthly cash obligations are covered with a "
            f"projected surplus of €{cash_gap:,.0f}."
        )


# =====================================================
# RESULT
# =====================================================

return {
    "state_version": getattr(
        state,
        "version",
        None,
    ),

    # =================================================
    # SCENARIO
    # =================================================

    "price": price,
    "variable_cost": variable_cost,
    "volume": volume,
    "sales_amount": sales_amount,
    "purchases_amount": purchases_amount,

    # =================================================
    # FIXED CASH OBLIGATIONS
    # =================================================

    "monthly_fixed_costs": monthly_fixed_costs,
    "monthly_debt_service": monthly_debt_service,

    # =================================================
    # SHARED CASH TIMING
    # =================================================

    "ar_days": ar_days,
    "ap_days": ap_days,
    "collection_profile": collection_profile,

    # =================================================
    # EXISTING BALANCES
    # =================================================

    "opening_ar": cash_timing.get(
        "opening_ar",
        0.0,
    ),

    "opening_ap": cash_timing.get(
        "opening_ap",
        0.0,
    ),

    # =================================================
    # CASH RECEIPTS
    # =================================================

    "existing_ar_cash_in": existing_ar_cash_in,

    "current_sales_cash_in": current_sales_cash_in,

    "total_monthly_cash_in": total_monthly_cash_in,

    # Compatibility names expected by
    # Monthly Survival UI
    "existing_ar_receipts": existing_ar_cash_in,

    "new_sales_receipts": current_sales_cash_in,

    # =================================================
    # SUPPLIER CASH PAYMENTS
    # =================================================

    "existing_ap_cash_out": existing_ap_cash_out,

    "current_purchase_cash_out": current_purchase_cash_out,

    "supplier_cash_out": supplier_cash_out,

    # Compatibility names expected by
    # Monthly Survival UI
    "existing_ap_payments": existing_ap_cash_out,

    "new_purchase_payments": current_purchase_cash_out,

    # =================================================
    # TOTAL CASH
    # =================================================

    "total_cash_outflow": total_cash_outflow,

    "cash_gap": cash_gap,

    # =================================================
    # INCREMENTAL CASH ECONOMICS
    # =================================================

    "cash_revenue_per_unit": cash_revenue_per_unit,

    "cash_purchase_cost_per_unit": (
        cash_purchase_cost_per_unit
    ),

    "cash_contribution_per_unit": (
        cash_contribution_per_unit
    ),

    # =================================================
    # CASH BREAK-EVEN
    # =================================================

    "cash_bep": cash_bep,

    "unit_gap": unit_gap,

    # =================================================
    # STATUS
    # =================================================

    "status": status,

    "interpretation": interpretation,

    # =================================================
    # BACKWARD COMPATIBILITY
    # =================================================

    "cash_collection_pct": (
        float(cash_collection_pct)
        if cash_collection_pct is not None
        else None
    ),

    "past_collections": (
        float(past_collections)
        if past_collections is not None
        else None
    ),
}

        # =================================================
        # BACKWARD-COMPATIBLE FIELDS
        # =================================================
        #
        # These remain so older parts of the application
        # do not break, but they are no longer the source
        # of the calculation.
        #

        "cash_collection_pct": (
            float(cash_collection_pct)
            if cash_collection_pct is not None
            else None
        ),

        "past_collections": (
            float(past_collections)
            if past_collections is not None
            else None
        ),
    }
