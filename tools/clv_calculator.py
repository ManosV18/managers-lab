from typing import Dict, List, Optional, Tuple


def calculate_expected_customer_lifespan(
    retention_rate_pct: float,
) -> float:
    """
    Estimate expected customer relationship duration
    from annual retention rate.

    Example:
        80% retention -> 1 / (1 - 0.80) = 5 years
    """
    retention_rate = retention_rate_pct / 100.0

    if retention_rate >= 1.0:
        return 15.0

    if retention_rate <= 0:
        return 1.0

    churn_rate = 1.0 - retention_rate

    return 1.0 / churn_rate


def calculate_clv(
    purchases: float,
    margin_per_order: float,
    retention_years: int,
    discount_rate_pct: float,
    retention_rate_pct: float,
    realization_rate: float,
    cac: float,
) -> Tuple[List[Dict[str, float]], float, Optional[int]]:
    """
    Calculate NPV Customer Lifetime Value year by year.

    Returns:
        yearly_data
        final_npv
        payback_year
    """
    discount_rate = discount_rate_pct / 100.0
    retention_rate = retention_rate_pct / 100.0

    cumulative_npv = -float(cac)

    yearly_data = []
    payback_year = None

    annual_margin = (
        float(purchases)
        * float(margin_per_order)
        * float(realization_rate)
    )

    for year in range(1, int(retention_years) + 1):
        survival_probability = retention_rate ** (year - 1)

        annual_cash_flow = (
            annual_margin
            * survival_probability
        )

        discounted_cash_flow = (
            annual_cash_flow
            / ((1.0 + discount_rate) ** year)
        )

        cumulative_npv += discounted_cash_flow

        yearly_data.append(
            {
                "Year": year,
                "Annual_Cash_Flow": float(
                    annual_cash_flow
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

    return (
        yearly_data,
        cumulative_npv,
        payback_year,
    )


def calculate_customer_unit_economics(
    price: float,
    variable_cost: float,
    purchases_per_year: float,
    units_per_purchase: float,
    retention_rate_pct: float,
) -> Dict[str, float]:
    """
    Calculate basic annual customer economics.
    """
    unit_contribution = (
        price - variable_cost
    )

    annual_units = (
        purchases_per_year
        * units_per_purchase
    )

    annual_revenue = (
        annual_units * price
    )

    annual_margin = (
        annual_units
        * unit_contribution
    )

    expected_lifespan = (
        calculate_expected_customer_lifespan(
            retention_rate_pct
        )
    )

    return {
        "unit_contribution": unit_contribution,
        "annual_units": annual_units,
        "annual_revenue": annual_revenue,
        "annual_margin": annual_margin,
        "expected_lifespan_years": expected_lifespan,
    }


def calculate_ltv_cac_ratio(
    clv: float,
    cac: float,
) -> float:
    """
    Calculate LTV / CAC ratio.

    CLV already includes the initial CAC deduction,
    therefore CAC is added back before calculating
    the traditional LTV/CAC ratio.
    """
    if cac <= 0:
        return 0.0

    gross_customer_value = clv + cac

    return gross_customer_value / cac


def classify_ltv_cac_ratio(
    ratio: float,
) -> str:
    """
    Classify customer unit economics.
    """
    if ratio < 1.0:
        return "Value Destruction"

    if ratio < 3.0:
        return "Sustainable / Vulnerable"

    return "Strong / Scalable"


def calculate_portfolio_value(
    customer_clv: float,
    num_customers: int,
) -> float:
    """
    Calculate total portfolio NPV.
    """
    return customer_clv * num_customers


def calculate_total_cac(
    cac_per_customer: float,
    num_customers: int,
) -> float:
    """
    Calculate total customer acquisition investment.
    """
    return cac_per_customer * num_customers


def calculate_clv_scenario_comparison(
    scenario_a: Dict,
    scenario_b: Dict,
    num_customers: int,
) -> Dict:
    """
    Compare two customer economics scenarios.
    """
    clv_a = scenario_a["clv"]
    clv_b = scenario_b["clv"]

    portfolio_a = calculate_portfolio_value(
        clv_a,
        num_customers,
    )

    portfolio_b = calculate_portfolio_value(
        clv_b,
        num_customers,
    )

    incremental_value = (
        portfolio_b - portfolio_a
    )

    retention_improvement = (
        scenario_b["retention_rate"]
        - scenario_a["retention_rate"]
    )

    return {
        "clv_current": clv_a,
        "clv_target": clv_b,
        "portfolio_value_current": portfolio_a,
        "portfolio_value_target": portfolio_b,
        "incremental_portfolio_value": incremental_value,
        "retention_improvement_pct_points": retention_improvement,
    }


def calculate_customer_value_analysis(
    price: float,
    variable_cost: float,
    scenario_a: Dict,
    scenario_b: Dict,
    discount_rate_pct: float,
    realization_rate: float,
    horizon_years: int,
    num_customers: int,
) -> Dict:
    """
    Complete Customer Economics / CLV analysis.

    This is the main calculation entry point for
    the Customer Economics Lab.
    """
    unit_contribution = (
        price - variable_cost
    )

    economics_a = calculate_customer_unit_economics(
        price=price,
        variable_cost=variable_cost,
        purchases_per_year=scenario_a[
            "purchases"
        ],
        units_per_purchase=scenario_a[
            "units_per_purchase"
        ],
        retention_rate_pct=scenario_a[
            "retention_rate"
        ],
    )

    economics_b = calculate_customer_unit_economics(
        price=price,
        variable_cost=variable_cost,
        purchases_per_year=scenario_b[
            "purchases"
        ],
        units_per_purchase=scenario_b[
            "units_per_purchase"
        ],
        retention_rate_pct=scenario_b[
            "retention_rate"
        ],
    )

    yearly_a, clv_a, payback_a = calculate_clv(
        purchases=scenario_a["purchases"],
        margin_per_order=(
            unit_contribution
            * scenario_a["units_per_purchase"]
        ),
        retention_years=int(horizon_years),
        discount_rate_pct=discount_rate_pct,
        retention_rate_pct=scenario_a[
            "retention_rate"
        ],
        realization_rate=realization_rate,
        cac=scenario_a["cac"],
    )

    yearly_b, clv_b, payback_b = calculate_clv(
        purchases=scenario_b["purchases"],
        margin_per_order=(
            unit_contribution
            * scenario_b["units_per_purchase"]
        ),
        retention_years=int(horizon_years),
        discount_rate_pct=discount_rate_pct,
        retention_rate_pct=scenario_b[
            "retention_rate"
        ],
        realization_rate=realization_rate,
        cac=scenario_b["cac"],
    )

    portfolio_a = calculate_portfolio_value(
        clv_a,
        num_customers,
    )

    portfolio_b = calculate_portfolio_value(
        clv_b,
        num_customers,
    )

    total_cac_a = calculate_total_cac(
        scenario_a["cac"],
        num_customers,
    )

    total_cac_b = calculate_total_cac(
        scenario_b["cac"],
        num_customers,
    )

    ratio_a = calculate_ltv_cac_ratio(
        clv_a,
        scenario_a["cac"],
    )

    ratio_b = calculate_ltv_cac_ratio(
        clv_b,
        scenario_b["cac"],
    )

    return {
        "unit_contribution": unit_contribution,

        "scenario_a": {
            "economics": economics_a,
            "yearly_data": yearly_a,
            "clv": clv_a,
            "portfolio_value": portfolio_a,
            "total_cac": total_cac_a,
            "ltv_cac_ratio": ratio_a,
            "classification": classify_ltv_cac_ratio(
                ratio_a
            ),
            "payback_year": payback_a,
        },

        "scenario_b": {
            "economics": economics_b,
            "yearly_data": yearly_b,
            "clv": clv_b,
            "portfolio_value": portfolio_b,
            "total_cac": total_cac_b,
            "ltv_cac_ratio": ratio_b,
            "classification": classify_ltv_cac_ratio(
                ratio_b
            ),
            "payback_year": payback_b,
        },

        "incremental_value": (
            portfolio_b - portfolio_a
        ),

        "retention_improvement": (
            scenario_b["retention_rate"]
            - scenario_a["retention_rate"]
        ),
    }
