import streamlit as st


def calculate_metrics(price, volume, variable_cost, fixed_cost, wacc, tax_rate,
                      ar_days, inv_days, ap_days, annual_debt_service, opening_cash):

    # ----- P&L -----
    unit_contribution = price - variable_cost
    revenue = price * volume
    total_vc = variable_cost * volume

    contribution_margin = unit_contribution * volume
    ebit = contribution_margin - fixed_cost

    # ----- Taxes -----
    tax_payment = max(0, ebit * tax_rate)

    # ----- Cash Flow -----
    ocf = ebit - tax_payment
    fcf = ocf - annual_debt_service

    # ----- Working Capital (365 base) -----
    daily_revenue = revenue / 365 if revenue > 0 else 0
    daily_variable_cost = total_vc / 365 if total_vc > 0 else 0

    accounts_receivable = daily_revenue * ar_days
    inventory_val = daily_variable_cost * inv_days
    accounts_payable = daily_variable_cost * ap_days

    wc_requirement = accounts_receivable + inventory_val - accounts_payable

    # ----- Liquidity -----
    net_cash_position = opening_cash - wc_requirement

    # ----- Survival -----
    monthly_net = fcf / 12

    if monthly_net >= 0:
        runway = 100.0
    else:
        runway = max(0.0, net_cash_position / abs(monthly_net))

    # ----- Break Even -----
    bep_units = (fixed_cost + annual_debt_service) / unit_contribution if unit_contribution > 0 else 0

    return {
        "unit_contribution": unit_contribution,
        "contribution_margin": contribution_margin,
        "contribution_ratio": unit_contribution / price if price > 0 else 0,

        "revenue": revenue,
        "ebit": ebit,

        "ocf": ocf,
        "fcf": fcf,

        "ccc": ar_days + inv_days - ap_days,

        "accounts_receivable": accounts_receivable,
        "wc_requirement": wc_requirement,

        "net_cash_position": net_cash_position,
        "runway_months": runway,

        "cash_wall": fixed_cost + annual_debt_service,

        "bep_units": bep_units
    }


def lock_baseline():
    """Activates the engine by locking the initial parameters."""
    st.session_state.baseline_locked = True


def sync_global_state():
    """
    Gatekeeper: Collects sidebar inputs and runs the engine
    only when baseline is locked.
    """

    s = st.session_state

    if not s.get("baseline_locked", False):
        st.error("🚨 Baseline not defined. Lock the baseline first.")
        st.stop()

    params = {
        "price": float(s.get("price", 0.0)),
        "volume": float(s.get("volume", 0.0)),
        "variable_cost": float(s.get("variable_cost", 0.0)),
        "fixed_cost": float(s.get("fixed_cost", 0.0)),
        "wacc": float(s.get("wacc", 0.15)),
        "tax_rate": float(s.get("tax_rate", 0.22)),
        "ar_days": float(s.get("ar_days", 0.0)),
        "inv_days": float(s.get("inventory_days", 0.0)),
        "ap_days": float(s.get("ap_days", 0.0)),
        "annual_debt_service": float(s.get("annual_debt_service", 0.0)),
        "opening_cash": float(s.get("opening_cash", 0.0))
    }

    return calculate_metrics(**params)
