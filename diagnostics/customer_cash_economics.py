from typing import Dict, Tuple

import pandas as pd


DAYS_IN_YEAR = 365
MAX_LIFETIME_YEARS = 15


# =========================================================
# CUSTOMER LIFETIME
# =========================================================

def calculate_expected_customer_lifespan(
    retention_rate_pct: float,
) -> float:
    """
    Estimate expected customer lifetime from annual retention.

    80% retention -> 1 / (1 - 0.80) = 5 years.

    The result is capped at 15 years for practical analysis.
    """
    retention_rate = float(retention_rate_pct) / 100.0

    if retention_rate >= 1.0:
        return float(MAX_LIFETIME_YEARS)

    if retention_rate <= 0.0:
        return 1.0

    lifespan = 1.0 / (1.0 - retention_rate)

    return min(
        float(lifespan),
        float(MAX_LIFETIME_YEARS),
    )


# =========================================================
# WORKING CAPITAL
# =========================================================

def calculate_customer_working_capital(
    annual_revenue: float,
    annual_gross_profit: float,
    payment_days: float,
    inventory_days: float,
    supplier_credit_days: float,
) -> Dict[str, float]:
    """
    Estimate customer-level working capital requirement.

    AR uses revenue.
    Inventory and AP use COGS.

    This is deliberately aligned with the company's
    working-capital logic rather than using revenue for
    every component.
    """

    revenue = max(float(annual_revenue), 0.0)
    gross_profit = max(float(annual_gross_profit), 0.0)

    cogs = max(
        revenue - gross_profit,
        0.0,
    )

    accounts_receivable = (
        revenue
        * max(float(payment_days), 0.0)
        / DAYS_IN_YEAR
    )

    inventory = (
        cogs
        * max(float(inventory_days), 0.0)
        / DAYS_IN_YEAR
    )

    accounts_payable = (
        cogs
        * max(float(supplier_credit_days), 0.0)
        / DAYS_IN_YEAR
    )

    working_capital = (
        accounts_receivable
        + inventory
        - accounts_payable
    )

    funding_gap_days = (
        float(inventory_days)
        + float(payment_days)
        - float(supplier_credit_days)
    )

    return {
        "cogs": float(cogs),
        "accounts_receivable": float(accounts_receivable),
        "inventory": float(inventory),
        "accounts_payable": float(accounts_payable),
        "working_capital": float(working_capital),
        "funding_gap_days": float(funding_gap_days),
    }


# =========================================================
# CURRENT CUSTOMER CASH ECONOMICS
# =========================================================

def calculate_customer_cash_cost(
    df: pd.DataFrame,
    wacc: float,
) -> pd.DataFrame:
    """
    Calculate current customer profitability and cash economics.

    `wacc` is expected as a percentage, e.g. 8.0 for 8%.
    """

    if df.empty:
        return df.copy()

    result = df.copy()

    result["Annual Revenue ($)"] = pd.to_numeric(
        result["Annual Revenue ($)"],
        errors="coerce",
    ).fillna(0.0)

    result["Annual Gross Profit ($)"] = pd.to_numeric(
        result["Annual Gross Profit ($)"],
        errors="coerce",
    ).fillna(0.0)

    result["Inventory Days"] = pd.to_numeric(
        result["Inventory Days"],
        errors="coerce",
    ).fillna(0.0)

    result["Customer Payment Days"] = pd.to_numeric(
        result["Customer Payment Days"],
        errors="coerce",
    ).fillna(0.0)

    result["Supplier Credit Days"] = pd.to_numeric(
        result["Supplier Credit Days"],
        errors="coerce",
    ).fillna(0.0)

    result["Funding Gap Days"] = (
        result["Inventory Days"]
        + result["Customer Payment Days"]
        - result["Supplier Credit Days"]
    )

    result["COGS ($)"] = (
        result["Annual Revenue ($)"]
        - result["Annual Gross Profit ($)"]
    ).clip(lower=0.0)

    result["Accounts Receivable ($)"] = (
        result["Annual Revenue ($)"]
        * result["Customer Payment Days"]
        / DAYS_IN_YEAR
    )

    result["Inventory ($)"] = (
        result["COGS ($)"]
        * result["Inventory Days"]
        / DAYS_IN_YEAR
    )

    result["Accounts Payable ($)"] = (
        result["COGS ($)"]
        * result["Supplier Credit Days"]
        / DAYS_IN_YEAR
    )

    result["Capital Locked ($)"] = (
        result["Accounts Receivable ($)"]
        + result["Inventory ($)"]
        - result["Accounts Payable ($)"]
    )

    result["Capital Cost ($)"] = (
        result["Capital Locked ($)"]
        * (float(wacc) / 100.0)
    )

    result["Economic Profit ($)"] = (
        result["Annual Gross Profit ($)"]
        - result["Capital Cost ($)"]
    )

    result["Economic Profit Margin %"] = 0.0

    revenue_positive = (
        result["Annual Revenue ($)"] != 0
    )

    result.loc[revenue_positive, "Economic Profit Margin %"] = (
        result.loc[
            revenue_positive,
            "Economic Profit ($)",
        ]
        / result.loc[
            revenue_positive,
            "Annual Revenue ($)",
        ]
        * 100.0
    )

    result["Classification"] = result.apply(
        classify_customer,
        axis=1,
    )

    return result


def classify_customer(row: pd.Series) -> str:
    if row["Economic Profit ($)"] < 0:
        return "Capital Destructive"

    if row["Funding Gap Days"] > 90:
        return "Cash Heavy"

    if row["Economic Profit Margin %"] > 15:
        return "High Quality"

    return "Stable"


# =========================================================
# CUSTOMER ECONOMIC NPV
# =========================================================

def calculate_customer_npv(
    annual_revenue: float,
    annual_gross_profit: float,
    customer_specific_annual_costs: float,
    cac: float,
    retention_rate_pct: float,
    discount_rate_pct: float,
    payment_days: float,
    inventory_days: float,
    supplier_credit_days: float,
    lifetime_years: int,
) -> Dict:
    """
    Calculate discounted customer economic cash flow.

    Year 0:
        - CAC
        - initial working-capital requirement

    Each future year:
        customer contribution
        - / + change in expected working capital
        weighted by customer survival probability.

    Working capital is released as expected customer survival
    declines. This avoids treating working capital as a permanent
    expense.

    No terminal value is assumed.
    """

    revenue = max(float(annual_revenue), 0.0)
    gross_profit = max(float(annual_gross_profit), 0.0)
    direct_costs = max(
        float(customer_specific_annual_costs),
        0.0,
    )
    acquisition_cost = max(float(cac), 0.0)

    retention = min(
        max(float(retention_rate_pct) / 100.0, 0.0),
        1.0,
    )

    discount_rate = max(
        float(discount_rate_pct) / 100.0,
        0.0,
    )

    lifetime = max(
        int(lifetime_years),
        1,
    )

    wc = calculate_customer_working_capital(
        annual_revenue=revenue,
        annual_gross_profit=gross_profit,
        payment_days=payment_days,
        inventory_days=inventory_days,
        supplier_credit_days=supplier_credit_days,
    )

    initial_nwc = wc["working_capital"]

    annual_customer_contribution = (
        gross_profit
        - direct_costs
    )

    # -----------------------------------------------------
    # YEAR 0
    # -----------------------------------------------------

    initial_investment = (
        acquisition_cost
        + initial_nwc
    )

    cumulative_npv = -initial_investment

    yearly_data = [
        {
            "Year": 0,
            "Survival_Probability": 1.0,
            "Customer_Contribution": 0.0,
            "Working_Capital_Investment": float(
                initial_nwc
            ),
            "Net_Cash_Flow": -float(
                initial_investment
            ),
            "Discounted_Cash_Flow": -float(
                initial_investment
            ),
            "Cumulative_NPV": float(
                cumulative_npv
            ),
        }
    ]

    payback_year = None

    # -----------------------------------------------------
    # FUTURE YEARS
    # -----------------------------------------------------

    for year in range(1, lifetime + 1):

        survival_probability = (
            retention ** (year - 1)
        )

        next_survival_probability = (
            retention ** year
        )

        expected_contribution = (
            annual_customer_contribution
            * survival_probability
        )

        # Expected NWC at beginning/end of year.
        nwc_begin = (
            initial_nwc
            * survival_probability
        )

        nwc_end = (
            initial_nwc
            * next_survival_probability
        )

        # If expected NWC falls, cash is released.
        working_capital_cash_impact = (
            nwc_begin - nwc_end
        )

        net_cash_flow = (
            expected_contribution
            + working_capital_cash_impact
        )

        discounted_cash_flow = (
            net_cash_flow
            / ((1.0 + discount_rate) ** year)
        )

        cumulative_npv += discounted_cash_flow

        yearly_data.append(
            {
                "Year": year,
                "Survival_Probability": float(
                    survival_probability
                ),
                "Customer_Contribution": float(
                    expected_contribution
                ),
                "Working_Capital_Investment": float(
                    -working_capital_cash_impact
                ),
                "Net_Cash_Flow": float(
                    net_cash_flow
                ),
                "Discounted_Cash_Flow": float(
                    discounted_cash_flow
                ),
                "Cumulative_NPV": float(
                    cumulative_npv
                ),
            }
        )

        if (
            cumulative_npv >= 0
            and payback_year is None
        ):
            payback_year = year

    return {
        "npv": float(cumulative_npv),
        "payback_year": payback_year,
        "expected_lifespan_years": calculate_expected_customer_lifespan(
            retention_rate_pct
        ),
        "annual_customer_contribution": float(
            annual_customer_contribution
        ),
        "initial_working_capital": float(
            initial_nwc
        ),
        "initial_investment": float(
            initial_investment
        ),
        "working_capital": wc,
        "yearly_data": yearly_data,
    }


# =========================================================
# BREAK-EVEN
# =========================================================

def calculate_max_cac(
    annual_revenue: float,
    annual_gross_profit: float,
    customer_specific_annual_costs: float,
    retention_rate_pct: float,
    discount_rate_pct: float,
    payment_days: float,
    inventory_days: float,
    supplier_credit_days: float,
    lifetime_years: int,
) -> float:
    """
    Maximum CAC that produces NPV = 0.
    """

    result = calculate_customer_npv(
        annual_revenue=annual_revenue,
        annual_gross_profit=annual_gross_profit,
        customer_specific_annual_costs=customer_specific_annual_costs,
        cac=0.0,
        retention_rate_pct=retention_rate_pct,
        discount_rate_pct=discount_rate_pct,
        payment_days=payment_days,
        inventory_days=inventory_days,
        supplier_credit_days=supplier_credit_days,
        lifetime_years=lifetime_years,
    )

    return max(
        float(result["npv"]),
        0.0,
    )


def calculate_break_even_gross_profit(
    annual_revenue: float,
    customer_specific_annual_costs: float,
    cac: float,
    retention_rate_pct: float,
    discount_rate_pct: float,
    payment_days: float,
    inventory_days: float,
    supplier_credit_days: float,
    lifetime_years: int,
) -> float:
    """
    Solve for the minimum annual gross profit that produces NPV = 0.

    Uses binary search because working capital itself depends on COGS.
    """

    revenue = max(float(annual_revenue), 0.0)

    if revenue <= 0:
        return 0.0

    low = 0.0
    high = revenue

    npv_at_high = calculate_customer_npv(
        annual_revenue=revenue,
        annual_gross_profit=high,
        customer_specific_annual_costs=customer_specific_annual_costs,
        cac=cac,
        retention_rate_pct=retention_rate_pct,
        discount_rate_pct=discount_rate_pct,
        payment_days=payment_days,
        inventory_days=inventory_days,
        supplier_credit_days=supplier_credit_days,
        lifetime_years=lifetime_years,
    )["npv"]

    if npv_at_high < 0:
        return revenue

    for _ in range(60):
        mid = (low + high) / 2.0

        npv = calculate_customer_npv(
            annual_revenue=revenue,
            annual_gross_profit=mid,
            customer_specific_annual_costs=customer_specific_annual_costs,
            cac=cac,
            retention_rate_pct=retention_rate_pct,
            discount_rate_pct=discount_rate_pct,
            payment_days=payment_days,
            inventory_days=inventory_days,
            supplier_credit_days=supplier_credit_days,
            lifetime_years=lifetime_years,
        )["npv"]

        if npv >= 0:
            high = mid
        else:
            low = mid

    return float(high)


def calculate_break_even_lifetime(
    annual_revenue: float,
    annual_gross_profit: float,
    customer_specific_annual_costs: float,
    cac: float,
    retention_rate_pct: float,
    discount_rate_pct: float,
    payment_days: float,
    inventory_days: float,
    supplier_credit_days: float,
    max_years: int = MAX_LIFETIME_YEARS,
) -> int | None:
    """
    Find the minimum analysis lifetime producing NPV >= 0.
    """

    for years in range(1, max_years + 1):

        npv = calculate_customer_npv(
            annual_revenue=annual_revenue,
            annual_gross_profit=annual_gross_profit,
            customer_specific_annual_costs=customer_specific_annual_costs,
            cac=cac,
            retention_rate_pct=retention_rate_pct,
            discount_rate_pct=discount_rate_pct,
            payment_days=payment_days,
            inventory_days=inventory_days,
            supplier_credit_days=supplier_credit_days,
            lifetime_years=years,
        )["npv"]

        if npv >= 0:
            return years

    return None


# =========================================================
# PORTFOLIO / EXISTING DIAGNOSTIC HELPERS
# =========================================================

def calculate_customer_portfolio_metrics(
    df: pd.DataFrame,
) -> Dict[str, float]:

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

    if df.empty:
        return (
            pd.Series(dtype=object),
            pd.Series(dtype=object),
        )

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

    if df.empty or reduction_days <= 0:
        return 0.0

    released_capital = (
        df["Annual Revenue ($)"]
        / DAYS_IN_YEAR
        * float(reduction_days)
    ).sum()

    return float(released_capital)
