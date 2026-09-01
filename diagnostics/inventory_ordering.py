import math
from typing import Optional, Dict


# =========================================================
# INVENTORY ORDERING DIAGNOSTIC
# =========================================================
#
# Read-only analytical engine.
#
# This diagnostic analyzes one inventory item at a time and
# calculates the Economic Order Quantity (EOQ), inventory
# costs and average working capital tied up in inventory.
#
# It does not create or modify CompanyState.
# It does not modify the locked baseline.
#
# =========================================================


def calculate_inventory_metrics(
    unit_price: float,
    annual_demand: float,
    ordering_cost: float,
    discount_pct: float,
    insurance_pm: float,
    annual_interest_rate: float,
    months: float,
    maintenance_pm: float,
) -> Optional[Dict[str, float]]:
    """
    Calculate EOQ and inventory economics.

    Parameters
    ----------
    unit_price:
        Purchase price per inventory unit before discount.

    annual_demand:
        Total demand during the analysis period.

    ordering_cost:
        Fixed cost incurred for each order.

    discount_pct:
        Supplier discount expressed as a decimal.

        Example:
            0.05 = 5%

    insurance_pm:
        Monthly insurance and handling cost.

    annual_interest_rate:
        Annual cost of capital expressed as a decimal.

        Example:
            0.08 = 8%

    months:
        Analysis period in months.

    maintenance_pm:
        Monthly warehouse operating cost.

    Returns
    -------
    Dictionary containing EOQ and inventory economics,
    or None when the inputs cannot produce a valid result.
    """

    unit_price = float(unit_price)
    annual_demand = float(annual_demand)
    ordering_cost = float(ordering_cost)
    discount_pct = float(discount_pct)
    insurance_pm = float(insurance_pm)
    annual_interest_rate = float(annual_interest_rate)
    months = float(months)
    maintenance_pm = float(maintenance_pm)

    # -----------------------------------------------------
    # INPUT VALIDATION
    # -----------------------------------------------------

    if annual_demand <= 0:
        return None

    if unit_price <= 0:
        return None

    if ordering_cost < 0:
        return None

    if months <= 0:
        return None

    if discount_pct < 0 or discount_pct >= 1:
        return None

    if annual_interest_rate < 0:
        return None

    if insurance_pm < 0:
        return None

    if maintenance_pm < 0:
        return None

    # -----------------------------------------------------
    # 1. DISCOUNTED PURCHASE PRICE
    # -----------------------------------------------------

    discounted_price = (
        unit_price * (1.0 - discount_pct)
    )

    # -----------------------------------------------------
    # 2. COST OF CAPITAL FOR THE ANALYSIS PERIOD
    # -----------------------------------------------------

    interest_pct = (
        annual_interest_rate * (months / 12.0)
    )

    # -----------------------------------------------------
    # 3. PURCHASE COST
    # -----------------------------------------------------

    purchase_cost = (
        discounted_price * annual_demand
    )

    # -----------------------------------------------------
    # 4. STORAGE AND MAINTENANCE COSTS
    # -----------------------------------------------------

    maintenance_total = (
        maintenance_pm * months
    )

    insurance_total = (
        insurance_pm * months
    )

    # -----------------------------------------------------
    # 5. STORAGE COST RATE
    # -----------------------------------------------------

    base_purchase_cost = (
        unit_price * annual_demand
    )

    if base_purchase_cost <= 0:
        return None

    storage_pct = (
        maintenance_total + insurance_total
    ) / base_purchase_cost

    # -----------------------------------------------------
    # 6. CARRYING RATE
    # -----------------------------------------------------

    if discount_pct > 0:
        carrying_rate = (
            storage_pct
            + (1.0 - discount_pct) * interest_pct
        )
    else:
        carrying_rate = (
            interest_pct + storage_pct
        )

    if carrying_rate <= 0:
        return None

    # -----------------------------------------------------
    # 7. ECONOMIC ORDER QUANTITY
    # -----------------------------------------------------

    eoq = math.sqrt(
        (
            2.0
            * annual_demand
            * ordering_cost
        )
        /
        (
            unit_price
            * carrying_rate
        )
    )

    if eoq <= 0:
        return None

    # -----------------------------------------------------
    # 8. NUMBER OF ORDERS
    # -----------------------------------------------------

    orders = (
        annual_demand / eoq
    )

    # -----------------------------------------------------
    # 9. TOTAL ORDERING COST
    # -----------------------------------------------------

    total_ordering_cost = (
        orders * ordering_cost
    )

    # -----------------------------------------------------
    # 10. TOTAL HOLDING COST
    # -----------------------------------------------------

    total_holding_cost = (
        carrying_rate
        * (eoq / 2.0)
        * unit_price
    )

    # -----------------------------------------------------
    # 11. TOTAL OPERATING COST
    # -----------------------------------------------------

    operating_cost = (
        total_ordering_cost
        + total_holding_cost
    )

    # -----------------------------------------------------
    # 12. TOTAL INVENTORY COST
    # -----------------------------------------------------

    total_cost = (
        purchase_cost
        + operating_cost
    )

    # -----------------------------------------------------
    # 13. AVERAGE CAPITAL TIED UP
    # -----------------------------------------------------

    capital_tied_up = (
        (eoq / 2.0)
        * discounted_price
    )

    # -----------------------------------------------------
    # RETURN RESULTS
    # -----------------------------------------------------

    return {
        "eoq": eoq,
        "orders": orders,

        "purchase_cost": purchase_cost,
        "ordering_cost": total_ordering_cost,
        "holding_cost": total_holding_cost,
        "operating_cost": operating_cost,
        "total_cost": total_cost,

        "interest_pct": interest_pct,
        "storage_pct": storage_pct,
        "carrying_rate": carrying_rate,

        "capital_tied_up": capital_tied_up,
        "discounted_price": discounted_price,
    }
