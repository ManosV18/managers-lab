from typing import Optional, Dict


def calculate_pricing_threshold(
    price: float,
    variable_cost: float,
    volume: float,
    fixed_cost: float,
    price_cut_pct: float,
) -> Optional[Dict[str, float]]:
    """
    Pricing Threshold Diagnostic.

    Answers:

        After a proposed price reduction,
        how much revenue can the business afford to lose
        while still covering its fixed costs?

    The diagnostic does NOT create or modify a Decision.
    It only analyses the economics of a proposed pricing change.

    Inputs
    ------
    price:
        Current selling price per unit.

    variable_cost:
        Current variable cost per unit.

    volume:
        Current annual sales volume.

    fixed_cost:
        Current annual fixed costs.

    price_cut_pct:
        Proposed price reduction in percentage terms.

        Example:
            10.0 = 10% price reduction

    Returns
    -------
    Dictionary containing the baseline economics,
    post-price-cut economics and maximum tolerable
    revenue loss.

    Returns None when the economics are invalid.
    """

    # -----------------------------------------------------
    # INPUT VALIDATION
    # -----------------------------------------------------

    if price <= 0:
        return None

    if variable_cost < 0:
        return None

    if volume <= 0:
        return None

    if fixed_cost < 0:
        return None

    price_cut = abs(price_cut_pct) / 100.0

    if price_cut >= 1.0:
        return None

    # -----------------------------------------------------
    # BASELINE ECONOMICS
    # -----------------------------------------------------

    current_revenue = price * volume

    current_contribution_per_unit = (
        price - variable_cost
    )

    if current_contribution_per_unit <= 0:
        return None

    current_contribution = (
        current_contribution_per_unit * volume
    )

    current_contribution_margin_pct = (
        current_contribution_per_unit / price
    ) * 100.0

    current_operating_profit = (
        current_contribution - fixed_cost
    )

    # -----------------------------------------------------
    # PRICE AFTER PROPOSED REDUCTION
    # -----------------------------------------------------

    new_price = (
        price * (1.0 - price_cut)
    )

    new_contribution_per_unit = (
        new_price - variable_cost
    )

    # Price reduction cannot be supported if
    # contribution per unit becomes zero or negative.
    if new_contribution_per_unit <= 0:
        return None

    new_contribution_margin_pct = (
        new_contribution_per_unit / new_price
    ) * 100.0

    # -----------------------------------------------------
    # FIXED-COST COVERAGE THRESHOLD
    # -----------------------------------------------------

    # Minimum sales volume required after the
    # price reduction to cover fixed costs.

    required_volume = (
        fixed_cost
        / new_contribution_per_unit
    )

    # Revenue generated at that minimum volume.
    threshold_revenue = (
        required_volume * new_price
    )

    # -----------------------------------------------------
    # MAXIMUM REVENUE LOSS
    # -----------------------------------------------------

    maximum_revenue_loss_pct = (
        1.0
        - threshold_revenue / current_revenue
    ) * 100.0

    # If the baseline itself does not generate enough
    # contribution to cover fixed costs, there is no
    # positive revenue-loss cushion.
    maximum_revenue_loss_pct = max(
        0.0,
        maximum_revenue_loss_pct,
    )

    # -----------------------------------------------------
    # REVENUE LOSS IN EURO
    # -----------------------------------------------------

    maximum_revenue_loss = (
        current_revenue
        * maximum_revenue_loss_pct
        / 100.0
    )

    # -----------------------------------------------------
    # RETURN DIAGNOSTIC RESULT
    # -----------------------------------------------------

    return {
        "current_revenue": current_revenue,

        "current_contribution": (
            current_contribution
        ),

        "current_contribution_margin_pct": (
            current_contribution_margin_pct
        ),

        "current_operating_profit": (
            current_operating_profit
        ),

        "price_cut_pct": (
            price_cut_pct
        ),

        "price_after_cut": (
            new_price
        ),

        "new_contribution_per_unit": (
            new_contribution_per_unit
        ),

        "new_contribution_margin_pct": (
            new_contribution_margin_pct
        ),

        "required_volume_at_threshold": (
            required_volume
        ),

        "threshold_revenue": (
            threshold_revenue
        ),

        "maximum_revenue_loss_pct": (
            maximum_revenue_loss_pct
        ),

        "maximum_revenue_loss": (
            maximum_revenue_loss
        ),
    }
