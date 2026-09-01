def calculate_deal_economics(
    revenue,
    cost,
    days_inv,
    days_ar,
    days_ap,
    wacc,
):
    """
    Calculates the economic impact of a customer deal.

    Returns:
        cash_gap
        accounting_profit
        financing_cost
        economic_profit
        accounting_margin
        economic_margin
    """

    revenue = float(revenue)
    cost = float(cost)
    days_inv = float(days_inv)
    days_ar = float(days_ar)
    days_ap = float(days_ap)
    wacc = float(wacc)

    cash_gap = (days_inv + days_ar) - days_ap

    accounting_profit = revenue - cost

    financing_cost = (
        cost
        * (wacc / 100)
        * (cash_gap / 365)
    )

    economic_profit = accounting_profit - financing_cost

    accounting_margin = (
        accounting_profit / revenue
        if revenue > 0
        else 0
    )

    economic_margin = (
        economic_profit / revenue
        if revenue > 0
        else 0
    )

    return {
        "cash_gap": cash_gap,
        "accounting_profit": accounting_profit,
        "financing_cost": financing_cost,
        "economic_profit": economic_profit,
        "accounting_margin": accounting_margin,
        "economic_margin": economic_margin,
    }
