import streamlit as st

from diagnostics.stress_test import (
    calculate_stress_scenario,
)


# =========================================================
# BASELINE HELPERS
# =========================================================

def _get_operational_drivers(baseline_state):
    return baseline_state.drivers


def _get_capital_structure(baseline_state):
    return baseline_state.capital_structure


def _get_working_capital(baseline_state):
    return baseline_state.working_capital


# =========================================================
# FORMATTING
# =========================================================

def _euro(value):
    return f"€{float(value):,.0f}"


def _pct(value):
    return f"{float(value):+.1f}%"


# =========================================================
# MAIN LAB
# =========================================================

def render_stress_test_lab(
    baseline_state,
):
    """
    Stress Test Simulator.

    The tool evaluates hypothetical financial pressure
    against the locked CompanyState.

    It does NOT modify the baseline.
    """

    st.title("🛡️ Stress Test Simulator")

    st.markdown(
        """
        **What happens if the business comes under pressure?**

        Test revenue pressure, variable-cost increases and
        customer collection delays without changing the
        locked company baseline.
        """
    )

    st.info(
        """
        This is a **what-if analysis**.

        The locked baseline remains unchanged.
        Every stress scenario is evaluated against the same
        starting company position.
        """
    )

    # =====================================================
    # BASELINE
    # =====================================================

    drivers = _get_operational_drivers(
        baseline_state
    )

    capital = _get_capital_structure(
        baseline_state
    )

    working_capital = _get_working_capital(
        baseline_state
    )

    price = float(
        drivers.price
    )

    volume = float(
        drivers.volume
    )

    variable_cost = float(
        drivers.variable_cost_per_unit
    )

    fixed_opex = float(
        drivers.fixed_opex
    )

    depreciation = float(
        drivers.depreciation
    )

    opening_cash = float(
        drivers.opening_cash
    )

    annual_interest = float(
        capital.annual_cash_interest_paid
    )

    annual_debt_service = float(
        capital.annual_debt_service
    )

    tax_rate = float(
        capital.tax_rate
    )

    ar_days = float(
        working_capital.ar_days
    )

    revenue = (
        price * volume
    )

    # =====================================================
    # BASELINE SNAPSHOT
    # =====================================================

    st.subheader(
        "🔒 Locked Company Baseline"
    )

    c1, c2, c3, c4 = st.columns(4)

    c1.metric(
        "Revenue",
        _euro(revenue),
    )

    c2.metric(
        "Variable Cost / Unit",
        _euro(variable_cost),
    )

    c3.metric(
        "Opening Cash",
        _euro(opening_cash),
    )

    c4.metric(
        "Receivable Days",
        f"{ar_days:.0f} days",
    )

    st.divider()

    # =====================================================
    # STRESS SCENARIO
    # =====================================================

    st.subheader(
        "🎛️ What If?"
    )

    col1, col2, col3 = st.columns(3)

    with col1:

        revenue_shock_pct = st.slider(
            "Revenue Change (%)",
            min_value=-60,
            max_value=20,
            value=-25,
            step=5,
            help=(
                "Change in total revenue. "
                "This does not automatically change physical sales volume."
            ),
        )

    with col2:

        variable_cost_shock_pct = st.slider(
            "Variable Cost Increase (%)",
            min_value=0,
            max_value=50,
            value=10,
            step=5,
            help=(
                "Percentage increase in variable cost per unit."
            ),
        )

    with col3:

        collection_delay_days = st.slider(
            "Additional Collection Delay (Days)",
            min_value=0,
            max_value=120,
            value=30,
            step=5,
            help=(
                "Additional days before customers pay."
            ),
        )

    # =====================================================
    # CALCULATE
    # =====================================================

    result = calculate_stress_scenario(
        revenue=revenue,
        variable_cost=variable_cost,
        volume=volume,
        fixed_opex=fixed_opex,
        depreciation=depreciation,
        annual_interest=annual_interest,
        annual_debt_service=annual_debt_service,
        opening_cash=opening_cash,
        tax_rate=tax_rate,
        ar_days=ar_days,
        revenue_shock_pct=revenue_shock_pct,
        variable_cost_shock_pct=(
            variable_cost_shock_pct
        ),
        collection_delay_days=(
            collection_delay_days
        ),
    )

    # =====================================================
    # EXECUTIVE RESULT
    # =====================================================

    st.divider()

    st.subheader(
        "📊 Scenario Impact"
    )

    c1, c2, c3, c4 = st.columns(4)

    c1.metric(
        "Revenue",
        _euro(
            result["scenario_revenue"]
        ),
        delta=_euro(
            result["revenue_change"]
        ),
    )

    c2.metric(
        "EBIT",
        _euro(
            result["scenario_ebit"]
        ),
        delta=_euro(
            result["ebit_change"]
        ),
    )

    c3.metric(
        "Net Profit",
        _euro(
            result["scenario_net_profit"]
        ),
        delta=_euro(
            result["net_profit_change"]
        ),
    )

    c4.metric(
        "Cash",
        _euro(
            result["scenario_cash"]
        ),
        delta=_euro(
            result["cash_change"]
        ),
    )

    # =====================================================
    # COLLECTION IMPACT
    # =====================================================

    st.divider()

    st.subheader(
        "💧 Cash Collection Impact"
    )

    c1, c2, c3 = st.columns(3)

    c1.metric(
        "Baseline Receivable Days",
        f"{result['baseline_ar_days']:.0f}",
    )

    c2.metric(
        "Scenario Receivable Days",
        f"{result['scenario_ar_days']:.0f}",
        delta=f"+{collection_delay_days:.0f}",
    )

    c3.metric(
        "Additional Cash Locked",
        _euro(
            result["additional_receivables"]
        ),
    )

    # =====================================================
    # INTERPRETATION
    # =====================================================

    st.divider()

    st.subheader(
        "🔍 What does this mean?"
    )

    if (
        result["scenario_net_profit"] < 0
        and result["scenario_cash"] < 0
    ):

        st.error(
            """
            **Severe financial pressure**

            Under this scenario the business becomes both
            loss-making and cash-negative.
            """
        )

    elif result["scenario_net_profit"] < 0:

        st.warning(
            """
            **Profitability pressure**

            The business becomes loss-making under this
            scenario, although the modeled cash position
            remains positive.
            """
        )

    elif result["scenario_cash"] < 0:

        st.warning(
            """
            **Liquidity pressure**

            The business remains profitable, but the
            modeled cash position becomes negative.

            This is an important distinction:
            profitability has not necessarily failed;
            liquidity has.
            """
        )

    else:

        st.success(
            """
            **Business remains financially resilient**

            Under the selected stress assumptions, the
            business remains profitable and the modeled
            cash position remains positive.
            """
        )

    # =====================================================
    # DRIVER EXPLANATION
    # =====================================================

    with st.expander(
        "🔎 Why did the result change?",
        expanded=True,
    ):

        if revenue_shock_pct != 0:

            st.markdown(
                f"""
                **Revenue:** {_pct(revenue_shock_pct)}

                Revenue changes by
                **{_euro(result["revenue_change"])}**
                versus the locked baseline.
                """
            )

        if variable_cost_shock_pct != 0:

            st.markdown(
                f"""
                **Variable cost:** +{variable_cost_shock_pct:.0f}%

                Total variable cost changes by
                **{_euro(result["variable_cost_change"])}**.
                """
            )

        if collection_delay_days > 0:

            st.markdown(
                f"""
                **Collections:** +{collection_delay_days:.0f} days

                Approximately
                **{_euro(result["additional_receivables"])}**
                of additional cash becomes tied up in receivables.
                """
            )

    # =====================================================
    # BASELINE PROTECTION
    # =====================================================

    st.divider()

    st.caption(
        "🔒 The locked baseline has not been changed. "
        "This scenario exists only for analysis."
    )
