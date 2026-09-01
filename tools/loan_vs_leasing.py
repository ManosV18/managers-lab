# tools/loan_vs_leasing.py

import streamlit as st
import plotly.graph_objects as go

from core.financial_engine import FinancialEngine


# =========================================================
# FORMATTING
# =========================================================

def format_number_gr(value):
    return f"{value:,.0f}"


# =========================================================
# EXISTING FINANCING CALCULATION
# =========================================================

def pmt_basic(rate, nper, pv, fv=0, when=0):

    if rate == 0:
        return -(pv + fv) / nper

    factor = (1 + rate) ** nper

    payment = (
        pv * rate * factor
    ) / (factor - 1)

    if when == 1:
        payment = payment / (1 + rate)

    return payment


def calculate_final_burden(
    loan_rate,
    wc_rate,
    duration_years,
    property_value,
    loan_financing_percent,
    leasing_financing_percent,
    add_expenses_loan,
    add_expenses_leasing,
    residual_value_leasing,
    depreciation_years,
    tax_rate,
    pay_when,
):

    months = 12
    n_months = duration_years * months

    acquisition_cost_loan = (
        property_value
        + add_expenses_loan
    )

    acquisition_cost_lease = (
        property_value
        + add_expenses_leasing
    )

    wc_loan = (
        property_value
        - property_value * loan_financing_percent
        + add_expenses_loan
    )

    wc_lease = (
        property_value
        - property_value * leasing_financing_percent
        + add_expenses_leasing
    )

    monthly_loan = pmt_basic(
        loan_rate / months,
        n_months,
        property_value * loan_financing_percent,
        0,
        pay_when,
    )

    monthly_lease = pmt_basic(
        loan_rate / months,
        n_months,
        property_value * leasing_financing_percent,
        0,
        pay_when,
    )

    monthly_wc_loan = pmt_basic(
        wc_rate / months,
        n_months,
        wc_loan,
        0,
        pay_when,
    )

    monthly_wc_lease = pmt_basic(
        wc_rate / months,
        n_months,
        wc_lease,
        0,
        pay_when,
    )

    total_monthly_loan = (
        monthly_loan
        + monthly_wc_loan
    )

    total_monthly_lease = (
        monthly_lease
        + monthly_wc_lease
    )

    total_interest_loan = (
        total_monthly_loan * n_months
    ) - property_value

    total_interest_lease = (
        total_monthly_lease * n_months
    ) - property_value

    total_cost_loan = (
        total_interest_loan
        + property_value
    )

    total_cost_lease = (
        total_interest_lease
        + property_value
    )

    depreciation_loan = (
        acquisition_cost_loan
        / depreciation_years
        * duration_years
    )

    depreciation_lease = (
        acquisition_cost_lease
        / duration_years
        * duration_years
    ) + residual_value_leasing

    deductible_loan = (
        total_interest_loan
        + depreciation_loan
    )

    deductible_lease = (
        monthly_wc_lease * n_months
        - wc_lease
        + depreciation_lease
    )

    tax_benefit_loan = (
        deductible_loan * tax_rate
    )

    tax_benefit_lease = (
        deductible_lease * tax_rate
    )

    final_loan = (
        total_cost_loan
        - tax_benefit_loan
    )

    final_lease = (
        total_cost_lease
        - tax_benefit_lease
    )

    return (
        round(final_loan),
        round(final_lease),
        total_monthly_loan,
        total_monthly_lease,
    )


# =========================================================
# BASELINE FINANCIALS
# =========================================================

def get_baseline_financials(
    baseline_state,
):

    return FinancialEngine.calculate_statements(
        baseline_state
    )


# =========================================================
# DECISION LAB
# =========================================================

def render_loan_vs_leasing_lab(
    baseline_state,
):

    st.header("🏦 Loan vs Leasing Lab")

    st.info(
        """
        Compare a new Loan or Leasing decision and see
        its economic consequence for the company.

        The locked baseline is not changed.
        """
    )

    # =====================================================
    # BASELINE
    # =====================================================

    baseline_financials = (
        get_baseline_financials(
            baseline_state
        )
    )

    baseline_is = (
        baseline_financials.income_statement
    )

    baseline_fcfe = (
        baseline_financials.fcfe
    )

    baseline_profit = (
        baseline_is.net_profit
    )

    # =====================================================
    # INPUTS
    # =====================================================

    st.subheader("Financing Terms")

    col1, col2 = st.columns(2)

    with col1:

        loan_rate = (
            st.number_input(
                "Loan Interest Rate (%)",
                value=6.0,
            )
            / 100
        )

        wc_rate = (
            st.number_input(
                "Working Capital Interest Rate (%)",
                value=8.0,
            )
            / 100
        )

        duration_years = st.number_input(
            "Duration (Years)",
            value=15,
            min_value=1,
        )

        pay_timing = st.radio(
            "Payment Timing",
            [
                "Beginning of Month",
                "End of Month",
            ],
        )

        pay_when = (
            1
            if pay_timing == "Beginning of Month"
            else 0
        )

        tax_rate = (
            st.number_input(
                "Corporate Tax Rate (%)",
                value=float(
                    baseline_state
                    .capital_structure
                    .tax_rate
                    * 100
                ),
            )
            / 100
        )

    with col2:

        st.subheader("Investment Details")

        property_value = st.number_input(
            "Property Commercial Value (€)",
            value=250000.0,
        )

        loan_financing = (
            st.number_input(
                "Loan Financing (%)",
                value=70.0,
            )
            / 100
        )

        leasing_financing = (
            st.number_input(
                "Leasing Financing (%)",
                value=100.0,
            )
            / 100
        )

        add_expenses_loan = st.number_input(
            "Acquisition Expenses — Loan (€)",
            value=35000.0,
        )

        add_expenses_leasing = st.number_input(
            "Acquisition Expenses — Leasing (€)",
            value=30000.0,
        )

        residual_value = st.number_input(
            "Leasing Residual Value (€)",
            value=3530.0,
        )

        depreciation_years = st.number_input(
            "Depreciation Period (Years)",
            value=30,
            min_value=1,
        )

    st.divider()

    # =====================================================
    # FINANCING CALCULATION
    # =====================================================

    (
        final_loan,
        final_leasing,
        monthly_loan,
        monthly_lease,
    ) = calculate_final_burden(
        loan_rate,
        wc_rate,
        duration_years,
        property_value,
        loan_financing,
        leasing_financing,
        add_expenses_loan,
        add_expenses_leasing,
        residual_value,
        depreciation_years,
        tax_rate,
        pay_when,
    )

    annual_payment_loan = (
        abs(monthly_loan) * 12
    )

    annual_payment_lease = (
        abs(monthly_lease) * 12
    )

    # =====================================================
    # YEAR-1 ECONOMIC CONSEQUENCE
    # =====================================================

    loan_profit_impact = (
        baseline_profit
        - annual_payment_loan
    )

    lease_profit_impact = (
        baseline_profit
        - annual_payment_lease
    )

    loan_cash_impact = (
        baseline_fcfe
        - annual_payment_loan
    )

    lease_cash_impact = (
        baseline_fcfe
        - annual_payment_lease
    )

    # =====================================================
    # FINANCING COMPARISON
    # =====================================================

    st.subheader("📊 Financing Comparison")

    m1, m2 = st.columns(2)

    m1.metric(
        "Loan — Net Financing Burden",
        f"€{format_number_gr(final_loan)}",
    )

    m2.metric(
        "Leasing — Net Financing Burden",
        f"€{format_number_gr(final_leasing)}",
    )

    fig = go.Figure(
        go.Bar(
            x=[
                "Loan",
                "Leasing",
            ],
            y=[
                final_loan,
                final_leasing,
            ],
            text=[
                f"€{format_number_gr(final_loan)}",
                f"€{format_number_gr(final_leasing)}",
            ],
            textposition="auto",
        )
    )

    fig.update_layout(
        height=300,
        yaxis_title="Total Financing Burden (€)",
    )

    st.plotly_chart(
        fig,
        use_container_width=True,
    )

    # =====================================================
    # YEAR-1 CONSEQUENCE
    # =====================================================

    st.divider()

    st.subheader(
        "📅 First-Year Economic Consequence"
    )

    c1, c2 = st.columns(2)

    with c1:

        st.markdown("### 🏦 Loan")

        st.metric(
            "Total Annual Financing Payment",
            f"€{annual_payment_loan:,.0f}",
        )

        st.metric(
            "Illustrative Net Profit",
            f"€{loan_profit_impact:,.0f}",
            delta=(
                f"€{loan_profit_impact - baseline_profit:,.0f}"
            ),
        )

        st.metric(
            "Illustrative Cash Flow",
            f"€{loan_cash_impact:,.0f}",
            delta=(
                f"€{loan_cash_impact - baseline_fcfe:,.0f}"
            ),
        )

    with c2:

        st.markdown("### 📄 Leasing")

        st.metric(
            "Total Annual Leasing Payment",
            f"€{annual_payment_lease:,.0f}",
        )

        st.metric(
            "Illustrative Net Profit",
            f"€{lease_profit_impact:,.0f}",
            delta=(
                f"€{lease_profit_impact - baseline_profit:,.0f}"
            ),
        )

        st.metric(
            "Illustrative Cash Flow",
            f"€{lease_cash_impact:,.0f}",
            delta=(
                f"€{lease_cash_impact - baseline_fcfe:,.0f}"
            ),
        )

    # =====================================================
    # DECISION SELECTION
    # =====================================================

    st.divider()

    st.subheader(
        "🎯 Select the financing decision"
    )

    selected_option = st.radio(
        "Choose one option",
        [
            "No financing decision",
            "Loan",
            "Leasing",
        ],
        horizontal=True,
    )

    if selected_option == "No financing decision":

        st.caption(
            "No Decision will be added to the Decision Plan."
        )

        return

    if selected_option == "Loan":

        annual_payment = annual_payment_loan
        final_burden = final_loan
        profit_after = loan_profit_impact
        cash_after = loan_cash_impact

    else:

        annual_payment = annual_payment_lease
        final_burden = final_leasing
        profit_after = lease_profit_impact
        cash_after = lease_cash_impact

    st.success(
        f"Selected decision: **{selected_option}**"
    )

    st.metric(
        "Total Annual Financing Payment",
        f"€{annual_payment:,.0f}",
    )

    st.metric(
        "Total Financing Burden",
        f"€{final_burden:,.0f}",
    )

    # =====================================================
    # DECISION PREVIEW
    # =====================================================

    st.session_state.loan_leasing_decision_preview = {

        "decision_type": "loan_vs_leasing",

        "selected_option": selected_option,

        "annual_payment": annual_payment,

        "final_burden": final_burden,

        "year_1_profit_before_decision": baseline_profit,

        "year_1_profit_after_decision": profit_after,

        "year_1_cash_before_decision": baseline_fcfe,

        "year_1_cash_after_decision": cash_after,

        "baseline_version": baseline_state.version,

        "financing_inputs": {
            "loan_rate": loan_rate,
            "wc_rate": wc_rate,
            "duration_years": duration_years,
            "property_value": property_value,
            "loan_financing_percent": loan_financing,
            "leasing_financing_percent": leasing_financing,
            "add_expenses_loan": add_expenses_loan,
            "add_expenses_leasing": add_expenses_leasing,
            "residual_value_leasing": residual_value,
            "depreciation_years": depreciation_years,
            "tax_rate": tax_rate,
            "pay_when": pay_when,
        },
    }

    st.success(
        """
        Financing decision prepared.

        The selected Loan/Leasing option is ready for the
        Decision Manager / Control Tower integration.
        """
    )
