from typing import Dict


def calculate_stress_scenario(
    revenue: float,
    variable_cost: float,
    volume: float,
    fixed_opex: float,
    depreciation: float,
    annual_interest: float,
    annual_debt_service: float,
    opening_cash: float,
    tax_rate: float,
    ar_days: float,
    revenue_shock_pct: float = 0.0,
    variable_cost_shock_pct: float = 0.0,
    collection_delay_days: float = 0.0,
) -> Dict[str, float]:
    """
    Calculate the financial impact of a stress scenario.

    The locked baseline is never modified.

    revenue_shock_pct:
        Percentage change in total revenue.
        Example: -25 means revenue falls by 25%.

    variable_cost_shock_pct:
        Percentage increase in variable cost per unit.
        Example: 10 means unit variable cost increases by 10%.

    collection_delay_days:
        Additional customer collection delay in days.

    Returns baseline, scenario and impact metrics.
    """

    revenue = float(revenue)
    variable_cost = float(variable_cost)
    volume = float(volume)
    fixed_opex = float(fixed_opex)
    depreciation = float(depreciation)
    annual_interest = float(annual_interest)
    annual_debt_service = float(annual_debt_service)
    opening_cash = float(opening_cash)
    tax_rate = float(tax_rate)
    ar_days = float(ar_days)

    # =====================================================
    # BASELINE
    # =====================================================

    baseline_unit_vc = variable_cost

    baseline_variable_cost_total = (
        baseline_unit_vc * volume
    )

    baseline_ebit = (
        revenue
        - baseline_variable_cost_total
        - fixed_opex
        - depreciation
    )

    baseline_ebt = (
        baseline_ebit
        - annual_interest
    )

    baseline_tax = (
        max(0.0, baseline_ebt * tax_rate)
    )

    baseline_net_profit = (
        baseline_ebt
        - baseline_tax
    )

    baseline_daily_revenue = (
        revenue / 365.0
        if revenue > 0
        else 0.0
    )

    # =====================================================
    # SCENARIO
    # =====================================================

    scenario_revenue = (
        revenue
        * (1.0 + revenue_shock_pct / 100.0)
    )

    scenario_unit_vc = (
        variable_cost
        * (1.0 + variable_cost_shock_pct / 100.0)
    )

    # We deliberately do NOT change volume here.
    #
    # The user asked:
    #
    # "What happens if revenue falls?"
    #
    # not:
    #
    # "What happens if physical sales volume falls?"

    scenario_variable_cost_total = (
        scenario_unit_vc * volume
    )

    scenario_ebit = (
        scenario_revenue
        - scenario_variable_cost_total
        - fixed_opex
        - depreciation
    )

    scenario_ebt = (
        scenario_ebit
        - annual_interest
    )

    scenario_tax = (
        max(0.0, scenario_ebt * tax_rate)
    )

    scenario_net_profit = (
        scenario_ebt
        - scenario_tax
    )

    # =====================================================
    # CASH / COLLECTION IMPACT
    # =====================================================

    additional_receivables = (
        max(0.0, scenario_revenue)
        / 365.0
        * collection_delay_days
    )

    scenario_cash = (
        opening_cash
        - additional_receivables
    )

    # Approximate annual cash generation after debt service.
    annual_cash_generation = (
        scenario_net_profit
        + depreciation
        - (
            annual_debt_service
            - annual_interest
        )
    )

    scenario_cash_after_operations = (
        scenario_cash
        + annual_cash_generation
    )

    # =====================================================
    # IMPACT
    # =====================================================

    revenue_change = (
        scenario_revenue - revenue
    )

    variable_cost_change = (
        scenario_variable_cost_total
        - baseline_variable_cost_total
    )

    ebit_change = (
        scenario_ebit - baseline_ebit
    )

    net_profit_change = (
        scenario_net_profit
        - baseline_net_profit
    )

    cash_change = (
        scenario_cash_after_operations
        - (
            opening_cash
            + baseline_net_profit
            + depreciation
            - (
                annual_debt_service
                - annual_interest
            )
        )
    )

    return {
        # Baseline
        "baseline_revenue": revenue,
        "baseline_variable_cost": baseline_variable_cost_total,
        "baseline_ebit": baseline_ebit,
        "baseline_net_profit": baseline_net_profit,
        "baseline_cash": opening_cash,

        # Scenario
        "scenario_revenue": scenario_revenue,
        "scenario_unit_variable_cost": scenario_unit_vc,
        "scenario_variable_cost": scenario_variable_cost_total,
        "scenario_ebit": scenario_ebit,
        "scenario_net_profit": scenario_net_profit,
        "scenario_cash": scenario_cash_after_operations,

        # Impact
        "revenue_change": revenue_change,
        "variable_cost_change": variable_cost_change,
        "ebit_change": ebit_change,
        "net_profit_change": net_profit_change,
        "cash_change": cash_change,
        "additional_receivables": additional_receivables,

        # Stress assumptions
        "revenue_shock_pct": revenue_shock_pct,
        "variable_cost_shock_pct": variable_cost_shock_pct,
        "collection_delay_days": collection_delay_days,
        "baseline_ar_days": ar_days,
        "scenario_ar_days": ar_days + collection_delay_days,
    }
