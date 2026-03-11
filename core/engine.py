def calculate_metrics(price, volume, variable_cost, fixed_cost,
                      ar_days, inv_days, ap_days,
                      annual_debt_service, opening_cash,
                      target_profit=0.0):
    unit_contribution = price - variable_cost
    revenue = price * volume
    total_vc = variable_cost * volume

    # 365-Day Logic [2026-02-18]
    daily_rev = revenue / 365 if revenue > 0 else 0
    daily_costs = (total_vc + fixed_cost) / 365 if (total_vc + fixed_cost) > 0 else 0

    wc_req = (daily_rev * ar_days) + (daily_costs * inv_days) - (daily_costs * ap_days)
    net_cash = opening_cash - wc_req

    cash_wall = fixed_cost + annual_debt_service + target_profit
    bep_units = cash_wall / unit_contribution if unit_contribution > 0 else None

    return {
        "unit_contribution": unit_contribution,
        "revenue": revenue,
        "ebit": (unit_contribution * volume) - fixed_cost,
        "bep_units": bep_units,
        "net_cash_position": net_cash,
        "ccc": ar_days + inv_days - ap_days
    }
