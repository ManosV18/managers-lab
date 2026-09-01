import pandas as pd


def calculate_salesperson_value(df: pd.DataFrame, wacc: float) -> pd.DataFrame:
    """Calculates funding gaps, locked capital, financing costs, people costs,

    and net economic contribution for each salesperson.

    Args:
        df: Input DataFrame with raw sales team data.
        wacc: Cost of capital percentage (e.g. 15.0 for 15%).

    Returns:
        Enriched DataFrame with calculated metrics and classifications.
    """
    if df.empty:
        return pd.DataFrame()

    result = df.copy()

    # Ensure numeric types
    numeric_cols = [
        "Annual Sales ($)",
        "Annual Gross Profit ($)",
        "Avg Customer Payment Days",
        "Inventory Days",
        "Supplier Credit Days",
        "Annual Salary + Commissions ($)",
        "Annual Expenses ($)",
    ]
    for col in numeric_cols:
        if col in result.columns:
            result[col] = pd.to_numeric(result[col], errors="coerce").fillna(0.0)

    # 1. Funding Gap Days (Cash Cycle)
    result["Funding Gap Days"] = (
        result["Inventory Days"]
        + result["Avg Customer Payment Days"]
        - result["Supplier Credit Days"]
    )

    # 2. Daily Sales and Capital Locked ($)
    result["Daily Sales ($)"] = result["Annual Sales ($)"] / 365.0
    result["Capital Locked ($)"] = (
        result["Daily Sales ($)"] * result["Funding Gap Days"]
    )

    # 3. Capital Cost ($)
    wacc_fraction = wacc / 100.0
    result["Capital Cost ($)"] = result["Capital Locked ($)"] * wacc_fraction

    # 4. Total People Cost ($)
    result["Total People Cost ($)"] = (
        result["Annual Salary + Commissions ($)"] + result["Annual Expenses ($)"]
    )

    # 5. Economic Contribution ($) [True Salesperson Contribution]
    result["Economic Contribution ($)"] = (
        result["Annual Gross Profit ($)"]
        - result["Capital Cost ($)"]
        - result["Total People Cost ($)"]
    )

    # 6. Contribution Margin %
    result["Contribution Margin %"] = 0.0
    nonzero_sales = result["Annual Sales ($)"] != 0
    result.loc[nonzero_sales, "Contribution Margin %"] = (
        result.loc[nonzero_sales, "Economic Contribution ($)"]
        / result.loc[nonzero_sales, "Annual Sales ($)"]
    ) * 100.0

    # 7. Classification
    def classify_salesperson(row):
        ec = row["Economic Contribution ($)"]
        fg = row["Funding Gap Days"]
        cm = row["Contribution Margin %"]

        if ec < 0:
            return "Value Destroyer"
        elif fg > 80:
            return "Cash Heavy"
        elif cm > 10:
            return "High Value"
        else:
            return "Stable"

    result["Classification"] = result.apply(classify_salesperson, axis=1)

    return result


def calculate_sales_team_metrics(df: pd.DataFrame) -> dict:
    """Aggregates portfolio summary metrics across the sales team."""
    if df.empty:
        return {
            "total_sales": 0.0,
            "total_gross_profit": 0.0,
            "capital_cost": 0.0,
            "economic_contribution": 0.0,
        }

    return {
        "total_sales": float(df["Annual Sales ($)"].sum()),
        "total_gross_profit": float(df["Annual Gross Profit ($)"].sum()),
        "capital_cost": float(df["Capital Cost ($)"].sum()),
        "economic_contribution": float(df["Economic Contribution ($)"].sum()),
    }


def calculate_released_capital(
    df: pd.DataFrame, reduction_days: float
) -> float:
    """Calculates total cash released across all salespeople when payment days

    are reduced.
    """
    if df.empty or reduction_days <= 0:
        return 0.0

    if "Daily Sales ($)" in df.columns:
        return float((df["Daily Sales ($)"] * reduction_days).sum())
    else:
        daily_sales = df["Annual Sales ($)"] / 365.0
        return float((daily_sales * reduction_days).sum())
