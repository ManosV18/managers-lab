from __future__ import annotations

from typing import Dict, Any, Optional


# =========================================================
# MONTHLY CASH SURVIVAL DIAGNOSTIC
# =========================================================

def calculate_monthly_survival(
    baseline_state: Any,
    projected_state: Optional[Any] = None,
    season_factor: float = 100.0,
    cash_collection_pct: float = 20.0,
    past_collections: float = 0.0,
    sim_price: Optional[float] = None,
    sim_vc: Optional[float] = None,
    sim_fc: Optional[float] = None,
    sim_debt: Optional[float] = None,
    sim_volume: Optional[float] = None,
) -> Dict[str, Any]:
    """
    Diagnostic logic for Monthly Cash Coverage / Survival Analysis.
    Reads canonical fields from CompanyState.
    """

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
    # CANONICAL BASELINE / STATE VALUES
    # =====================================================
    default_price = float(drivers.price)
    default_vc = float(drivers.variable_cost_per_unit)

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

    collection_pct = max(
        0.0,
        min(100.0, float(cash_collection_pct)),
    )

    past_collections = max(
        0.0,
        float(past_collections),
    )

    # =====================================================
    # MONTHLY CASH OUTFLOW & INFLOW
    # =====================================================
    total_variable_costs = volume * variable_cost
    total_cash_outflow = (
        monthly_fixed_costs
        + monthly_debt_service
        + total_variable_costs
    )

    current_sales_cash_in = (
        volume
        * price
        * (collection_pct / 100.0)
    )

    total_monthly_cash_in = (
        current_sales_cash_in
        + past_collections
    )

    # =====================================================
    # CASH CONTRIBUTION
    # =====================================================
    cash_revenue_per_unit = (
        price
        * (collection_pct / 100.0)
    )

    cash_contribution_per_unit = (
        cash_revenue_per_unit
        - variable_cost
    )

    # =====================================================
    # CASH BREAK-EVEN
    # =====================================================
    fixed_cash_obligations = monthly_fixed_costs + monthly_debt_service

    if cash_contribution_per_unit <= 0:
        cash_bep = None
    else:
        net_fixed_cash_needed = fixed_cash_obligations - past_collections
        if net_fixed_cash_needed <= 0:
            cash_bep = 0.0
        else:
            cash_bep = net_fixed_cash_needed / cash_contribution_per_unit

    # =====================================================
    # CASH GAP & BUFFER IN UNITS
    # =====================================================
    cash_gap = (
        total_monthly_cash_in
        - total_cash_outflow
    )

    unit_gap = (volume - cash_bep) if cash_bep is not None else None

    # =====================================================
    # STATUS & INTERPRETATION
    # =====================================================
    if cash_contribution_per_unit <= 0:
        status = "Negative Cash Contribution"
        interpretation = (
            "Cash collected per unit is insufficient to cover variable cost per unit. "
            "Increasing sales under these collection terms may worsen short-term cash pressure."
        )
    elif cash_gap < 0:
        status = "Shortfall"
        interpretation = (
            f"Monthly cash shortfall of €{abs(cash_gap):,.0f}. "
            "Expected cash inflows are insufficient to cover modeled monthly cash obligations."
        )
    else:
        status = "Covered"
        interpretation = (
            f"Monthly cash obligations are covered with a projected surplus of €{cash_gap:,.0f}."
        )

    # =====================================================
    # RESULT
    # =====================================================
    return {
        "state_version": getattr(state, "version", None),
        "price": price,
        "variable_cost": variable_cost,
        "volume": volume,
        "monthly_fixed_costs": monthly_fixed_costs,
        "monthly_debt_service": monthly_debt_service,
        "cash_collection_pct": collection_pct,
        "past_collections": past_collections,
        "current_sales_cash_in": current_sales_cash_in,
        "total_monthly_cash_in": total_monthly_cash_in,
        "total_cash_outflow": total_cash_outflow,
        "cash_revenue_per_unit": cash_revenue_per_unit,
        "cash_contribution_per_unit": cash_contribution_per_unit,
        "cash_bep": cash_bep,
        "unit_gap": unit_gap,
        "cash_gap": cash_gap,
        "status": status,
        "interpretation": interpretation,
    }
