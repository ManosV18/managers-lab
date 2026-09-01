from typing import Optional, Sequence, Tuple


def calculate_substitute_price_increase_impact(
    current_price: float,
    price_increase_pct: float,
    current_profit_per_unit: float,
    substitute_data: Sequence[Tuple[float, float]],
) -> Optional[dict]:
    """
    Estimate the financial resilience of a price increase when some
    customers may switch to substitute products.

    substitute_data:
        Sequence of (profit_per_substitute, switching_probability).

    switching_probability is expressed as a decimal:
        0.15 = 15%

    The diagnostic estimates the expected profit lost through
    substitution and compares it with the additional contribution
    created by the higher price.
    """

    if current_price <= 0:
        return None

    if current_profit_per_unit < 0:
        return None

    price_increase = price_increase_pct / 100.0

    if price_increase <= 0:
        return {
            "price_after_increase": current_price,
            "additional_profit_per_unit": 0.0,
            "expected_substitute_profit": 0.0,
            "expected_profit_gap": 0.0,
            "break_even_switching_rate": None,
            "resilience_status": "No price increase",
        }

    new_price = (
        current_price
        * (1.0 + price_increase)
    )

    new_main_profit = (
        current_profit_per_unit
        + current_price * price_increase
    )

    weighted_substitute_profit = sum(
        float(profit) * float(probability)
        for profit, probability in substitute_data
    )

    additional_profit_per_unit = (
        new_main_profit
        - current_profit_per_unit
    )

    expected_profit_gap = (
        additional_profit_per_unit
        - weighted_substitute_profit
    )

    substitute_profit_loss_per_switch = (
        current_profit_per_unit
        - weighted_substitute_profit
    )

    if substitute_profit_loss_per_switch > 0:
        break_even_switching_rate = (
            additional_profit_per_unit
            / substitute_profit_loss_per_switch
            * 100.0
        )
    else:
        break_even_switching_rate = None

    if expected_profit_gap > 0:
        resilience_status = "Resilient"
    elif expected_profit_gap == 0:
        resilience_status = "At Threshold"
    else:
        resilience_status = "Vulnerable"

    return {
        "price_after_increase": new_price,
        "additional_profit_per_unit": additional_profit_per_unit,
        "expected_substitute_profit": weighted_substitute_profit,
        "expected_profit_gap": expected_profit_gap,
        "break_even_switching_rate": break_even_switching_rate,
        "resilience_status": resilience_status,
    }
