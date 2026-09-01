"""
Diagnostic engine for evaluating the true economic profitability of customer deals.
Accounts for working capital funding duration and capital financing costs (WACC).
"""


def calculate_deal_economics(
    revenue: float,
    cost: float,
    days_inv: float,
    days_ar: float,
    days_ap: float,
    wacc: float,
) -> dict:
    """
    Calculates the economic impact and financing drag of a specific deal.

    Assumptions:
        - Financing cost assumes COGS is fully funded during the cash gap period.
        - WACC is provided as a percentage (e.g. 8.0 for 8%).
    """
    revenue = max(0.0, float(revenue))
    cost = max(0.0, float(cost))
    days_inv = max(0.0, float(days_inv))
    days_ar = max(0.0, float(days_ar))
    days_ap = max(0.0, float(days_ap))
    wacc = max(0.0, float(wacc))

    # Cash Conversion Cycle / Funding Gap for this specific deal
    cash_gap = (days_inv + days_ar) - days_ap

    # Standard Accounting P&L Metrics
    accounting_profit = revenue - cost
    accounting_margin = (accounting_profit / revenue) if revenue > 0 else 0.0

    # Financing / Capital Drag Cost
    # Formula: Cost * (WACC %) * (Cash Gap / 365 days)
    financing_cost = cost * (wacc / 100.0) * (cash_gap / 365.0)

    # True Economic Profit & Margin
    economic_profit = accounting_profit - financing_cost
    economic_margin = (economic_profit / revenue) if revenue > 0 else 0.0

    return {
        "cash_gap": cash_gap,
        "accounting_profit": accounting_profit,
        "accounting_margin": accounting_margin,
        "financing_cost": financing_cost,
        "economic_profit": economic_profit,
        "economic_margin": economic_margin,
    }
