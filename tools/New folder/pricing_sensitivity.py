from typing import Optional, Sequence, Tuple


def calculate_volume_loss_threshold(
    price: float,
    variable_cost: float,
    price_cut_pct: float,
) -> Optional[float]:
    """
    Maximum allowable volume loss (%) after a price reduction
    while maintaining the same contribution profit.
    """

    if price <= 0:
        return None

    contribution_margin = price - variable_cost

    if contribution_margin <= 0:
        return None

    margin_pct = contribution_margin / price
    cut = abs(price_cut_pct) / 100.0

    if cut >= margin_pct:
        return None

    return (cut / margin_pct) * 100.0


def calculate_required_volume_change(
    current_price: float,
    variable_cost: float,
    price_change_pct: float,
) -> Optional[float]:
    """
    Required volume change (%) to maintain the same contribution profit
    after a price change.

    Positive result:
        Required volume increase.

    Negative result:
        Allowable volume loss.
    """

    if current_price <= 0:
        return None

    current_cm = current_price - variable_cost

    if current_cm <= 0:
        return None

    new_price = current_price * (
        1.0 + price_change_pct / 100.0
    )

    new_cm = new_price - variable_cost

    if new_cm <= 0:
        return None

    return (current_cm / new_cm - 1.0) * 100.0


def calculate_cross_sell_impact(
    main_price: float,
    price_decrease_pct: float,
    profit_main: float,
    complement_data: Sequence[Tuple[float, float]],
) -> Tuple[Optional[float], float]:
    """
    Calculates the additional sales volume required to compensate
    for a price reduction when complementary products generate
    additional expected profit.

    complement_data:
        Sequence of (profit_per_complement, purchase_probability).

    Returns:
        (
            required_volume_increase_pct,
            expected_complement_profit
        )
    """

    if main_price <= 0:
        return None, 0.0

    expected_complement_profit = sum(
        profit * probability
        for profit, probability in complement_data
    )

    total_profit_per_main_unit = (
        profit_main + expected_complement_profit
    )

    denominator = (
        total_profit_per_main_unit / main_price
    ) + price_decrease_pct

    if denominator == 0:
        return None, expected_complement_profit

    required_increase = (
        -price_decrease_pct / denominator
    )

    return (
        required_increase * 100.0,
        expected_complement_profit,
    )


def calculate_max_drop(
    old_price: float,
    price_inc_pct: float,
    profit_per_unit: float,
    substitute_data: Sequence[Tuple[float, float]],
) -> Optional[float]:
    """
    Calculates the maximum acceptable volume drop (%) after a
    price increase, taking substitute economics into account.

    substitute_data:
        Sequence of
        (profit_per_substitute, switching_probability).

    price_inc_pct:
        Decimal percentage change.
        Example: 0.10 = +10%.
    """

    if old_price <= 0:
        return None

    weighted_sub_profit = sum(
        profit * probability
        for profit, probability in substitute_data
    )

    denominator = (
        (profit_per_unit - weighted_sub_profit) / old_price
    ) + price_inc_pct

    if denominator == 0:
        return 0.0

    numerator = -price_inc_pct

    return (numerator / denominator) * 100.0
