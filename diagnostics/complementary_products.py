from typing import Optional, Sequence, Tuple


def calculate_complementary_product_impact(
    main_price: float,
    price_decrease_pct: float,
    main_profit_per_unit: float,
    complement_data: Sequence[Tuple[float, float]],
) -> Optional[dict]:
    """
    Estimate how complementary-product profit can offset the
    contribution lost from a price reduction on the main product.

    complement_data:
        Sequence of (profit_per_complement, purchase_probability).

    purchase_probability is expressed as a decimal:
        0.20 = 20%

    Returns a read-only diagnostic result.
    """

    if main_price <= 0:
        return None

    if main_profit_per_unit < 0:
        return None

    price_cut = abs(price_decrease_pct) / 100.0

    if price_cut <= 0:
        return {
            "price_after_cut": main_price,
            "expected_complement_profit": 0.0,
            "main_profit_loss_per_unit": 0.0,
            "combined_profit_per_unit": main_profit_per_unit,
            "required_recovery_pct": 0.0,
            "recovery_coverage_pct": 0.0,
        }

    expected_complement_profit = sum(
        float(profit) * float(probability)
        for profit, probability in complement_data
    )

    main_profit_loss_per_unit = (
        main_profit_per_unit * price_cut
    )

    combined_profit_per_unit = (
        main_profit_per_unit
        + expected_complement_profit
    )

    if main_profit_loss_per_unit <= 0:
        required_recovery_pct = 0.0
    else:
        required_recovery_pct = (
            main_profit_loss_per_unit
            / combined_profit_per_unit
            * 100.0
            if combined_profit_per_unit > 0
            else None
        )

    recovery_coverage_pct = (
        expected_complement_profit
        / main_profit_loss_per_unit
        * 100.0
        if main_profit_loss_per_unit > 0
        else 0.0
    )

    return {
        "price_after_cut": main_price * (1.0 - price_cut),
        "expected_complement_profit": expected_complement_profit,
        "main_profit_loss_per_unit": main_profit_loss_per_unit,
        "combined_profit_per_unit": combined_profit_per_unit,
        "required_recovery_pct": required_recovery_pct,
        "recovery_coverage_pct": recovery_coverage_pct,
    }
