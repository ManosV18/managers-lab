from typing import Dict, Tuple
import pandas as pd


DAYS_IN_YEAR = 365

"""
Customer Economics Diagnostic

Analyzes the economic quality of individual customers
and the customer portfolio.

This diagnostic is read-only.

It does not create or modify decisions.
It operates on company/customer data and returns
diagnostic results for management interpretation.
"""

def calculate_customer_cash_cost(
    df: pd.DataFrame,
    wacc: float,
) -> pd.DataFrame:
    """
    Calculate cash consumption and economic profitability
    for each customer.

    Required columns:
        Customer
        Annual Revenue ($)
        Annual Gross Profit ($)
        Inventory Days
        Customer Payment Days
        Supplier Credit Days

    Returns:
        DataFrame containing calculated customer economics.
    """

    if df.empty:
        return df.copy()

    result = df.copy()

    # --------------------------------------------------
    # CASH CYCLE
    # --------------------------------------------------

    result["Funding Gap Days"] = (
        result["Inventory Days"]
        + result["Customer Payment Days"]
        - result["Supplier Credit Days"]
    )

    # --------------------------------------------------
    # DAILY REVENUE
    # --------------------------------------------------

    result["Daily Revenue ($)"] = (
        result["Annual Revenue ($)"] / DAYS_IN_YEAR
    )

    # --------------------------------------------------
    # CAPITAL LOCKED
    # --------------------------------------------------

    result["Capital Locked ($)"] = (
        result["Daily Revenue ($)"]
        * result["Funding Gap Days"]
    )

    # --------------------------------------------------
    # COST OF CAPITAL
    # --------------------------------------------------

    result["Capital Cost ($)"] = (
        result["Capital Locked ($)"]
        * (float(wacc) / 100.0)
    )

    # --------------------------------------------------
    # ECONOMIC PROFIT
    # --------------------------------------------------

    result["Economic Profit ($)"] = (
        result["Annual Gross Profit ($)"]
        - result["Capital Cost ($)"]
    )

    # --------------------------------------------------
    # ECONOMIC PROFIT MARGIN
    # --------------------------------------------------

    result["Economic Profit Margin %"] = 0.0

    revenue_positive = result["Annual Revenue ($)"] != 0

    result.loc[revenue_positive, "Economic Profit Margin %"] = (
        result.loc[revenue_positive, "Economic Profit ($)"]
        / result.loc[revenue_positive, "Annual Revenue ($)"]
        * 100.0
    )

    # --------------------------------------------------
    # CUSTOMER CLASSIFICATION
    # --------------------------------------------------

    result["Classification"] = result.apply(
        classify_customer,
        axis=1,
    )

    return result


def classify_customer(row: pd.Series) -> str:
    """
    Classify a customer according to economic profitability
    and cash-cycle characteristics.
    """

    if row["Economic Profit ($)"] < 0:
        return "Capital Destructive"

    if row["Funding Gap Days"] > 90:
        return "Cash Heavy"

    if row["Economic Profit Margin %"] > 15:
        return "High Quality"

    return "Stable"


def calculate_customer_portfolio_metrics(
    df: pd.DataFrame,
) -> Dict[str, float]:
    """
    Calculate aggregate portfolio-level customer economics.
    """

    if df.empty:
        return {
            "annual_revenue": 0.0,
            "cash_tied_up": 0.0,
            "capital_cost": 0.0,
            "economic_profit": 0.0,
        }

    return {
        "annual_revenue": float(
            df["Annual Revenue ($)"].sum()
        ),
        "cash_tied_up": float(
            df["Capital Locked ($)"].sum()
        ),
        "capital_cost": float(
            df["Capital Cost ($)"].sum()
        ),
        "economic_profit": float(
            df["Economic Profit ($)"].sum()
        ),
    }


def identify_customer_extremes(
    df: pd.DataFrame,
) -> Tuple[pd.Series, pd.Series]:
    """
    Identify the customer with the lowest and highest
    economic profit.

    Returns:
        (worst_customer, best_customer)
    """

    if df.empty:
        return pd.Series(dtype=object), pd.Series(dtype=object)

    worst = df.loc[
        df["Economic Profit ($)"].idxmin()
    ]

    best = df.loc[
        df["Economic Profit ($)"].idxmax()
    ]

    return worst, best


def calculate_released_capital(
    df: pd.DataFrame,
    reduction_days: float,
) -> float:
    """
    Estimate cash released if customer payment days
    are reduced by a given number of days.
    """

    if df.empty or reduction_days <= 0:
        return 0.0

    released_capital = (
        df["Daily Revenue ($)"]
        * float(reduction_days)
    ).sum()

    return float(released_capital)
