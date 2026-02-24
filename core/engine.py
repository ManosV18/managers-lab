import streamlit as st

def compute_core_metrics():
    """
    Central Engine: calculates P&L, Cash Flow, Working Capital, FCF, and Survival Horizon
    All annual, single-period, defaults included (no extra user input required)
    """

    # ─── 1. Fetch inputs safely ────────────────────────────────
    s = st.session_state

    # Revenue & Volume
    price = s.get('price', 30.0)
    volume = s.get('volume', 10000)
    variable_cost = s.get('variable_cost', 15.0)
    fixed_cost = s.get('fixed_cost', 50000.0)

    # Financing
    debt = s.get('debt', 20000.0)
    interest_rate = s.get('interest_rate', 0.05)
    wacc = s.get('wacc', 0.12)
    tax_rate = s.get('tax_rate', 0.22)
    annual_loan_payment = s.get('annual_loan_payment', 12000.0)

    # Working Capital
    ar_days = s.get('ar_days', 45)
    inventory_days = s.get('inventory_days', 60)
    payables_days = s.get('payables_days', 30)
    slow_moving_factor = s.get('slow_moving_factor', 0.2)

    # ─── 2. Derived Unit Metrics ───────────────────────────────
    unit_contribution = price - variable_cost
    revenue = price * volume
    cogs = variable_cost * volume

    # EBIT
    operating_ebit = (unit_contribution * volume) - fixed_cost

    # Interest & Taxes
    interest_expense = debt * interest_rate
    ebt = operating_ebit - interest_expense
    tax_amount = max(0, ebt * tax_rate)
    net_profit = ebt - tax_amount

    # ─── 3. Synthetic Previous Period (no user input) ────────
    previous_sales = revenue  # single-period model
    previous_cogs = cogs
    previous_receivables = previous_sales * (ar_days / 365)
    previous_inventory = previous_cogs * (inventory_days / 365)
    previous_payables = previous_cogs * (payables_days / 365)
    previous_nwc = previous_receivables + previous_inventory - previous_payables

    # Current Working Capital
    current_receivables = revenue * (ar_days / 365)
    current_inventory = cogs * (inventory_days / 365)
    current_payables = cogs * (payables_days / 365)
    working_capital_current = current_receivables + current_inventory - current_payables

    # WC friction from slow-moving stock
    inventory_friction = (inventory_days / 365) * cogs * slow_moving_factor
    liquidity_drain_annual = working_capital_current + inventory_friction
    s['liquidity_drain_annual'] = liquidity_drain_annual

    # ─── 4. Free Cash Flow ─────────────────────────────────────
    opening_cash = 0.05 * revenue
    change_in_wc = working_capital_current - previous_nwc
    fcf = net_profit - change_in_wc
    ending_cash = opening_cash + fcf

    # ─── 5. Break-Even Calculations ───────────────────────────
    operating_bep = fixed_cost / unit_contribution if unit_contribution > 0 else 0
    total_fixed_burden = fixed_cost + interest_expense + liquidity_drain_annual
    survival_bep = total_fixed_burden / unit_contribution if unit_contribution > 0 else 0

    # ─── 6. Cash Survival Horizon ─────────────────────────────
    if fcf < 0:
        cash_survival_horizon = opening_cash / abs(fcf)
    else:
        cash_survival_horizon = float('inf')

    # ─── 7. Store / Return ────────────────────────────────────
    return {
        "unit_contribution": unit_contribution,
        "revenue": revenue,
        "cogs": cogs,
        "ebit": operating_ebit,
        "ebt": ebt,
        "tax_amount": tax_amount,
        "net_profit": net_profit,
        "operating_bep": operating_bep,
        "survival_bep": survival_bep,
        "wacc": wacc,
        "interest_rate": interest_rate,
        "tax_rate": tax_rate,
        "working_capital_current": working_capital_current,
        "liquidity_drain_annual": liquidity_drain_annual,
        "opening_cash": opening_cash,
        "fcf": fcf,
        "ending_cash": ending_cash,
        "cash_survival_horizon": cash_survival_horizon
    }
