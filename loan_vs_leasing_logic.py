import streamlit as st
import numpy_financial as npf

# ===== Financial Functions =====
def pmt(rate, nper, pv, fv=0, when=0):
    """Compute monthly payment for a loan or lease."""
    return -npf.pmt(rate, nper, pv, fv, when)

def calculate_final_burden(
    loan_rate, wc_rate, duration_years, property_value,
    loan_financing_percent, leasing_financing_percent,
    add_expenses_loan, add_expenses_leasing, residual_value_leasing,
    depreciation_years, tax_rate, pay_when
):
    months = 12
    n_months = duration_years * months

    # Acquisition costs
    acquisition_cost_loan = property_value + add_expenses_loan
    acquisition_cost_lease = property_value + add_expenses_leasing

    # Working capital loans
    wc_loan = property_value - (property_value * loan_financing_percent) + add_expenses_loan
    wc_lease = property_value - (property_value * leasing_financing_percent) + add_expenses_leasing

    # Monthly payments
    monthly_loan = pmt(loan_rate / months, n_months, property_value * loan_financing_percent, 0, pay_when)
    monthly_lease = pmt(loan_rate / months, n_months, property_value * leasing_financing_percent, 0, pay_when)
    monthly_wc_loan = pmt(wc_rate / months, n_months, wc_loan, 0, pay_when)
    monthly_wc_lease = pmt(wc_rate / months, n_months, wc_lease, 0, pay_when)

    total_monthly_loan = monthly_loan + monthly_wc_loan
    total_monthly_lease = monthly_lease + monthly_wc_lease

    # Total interest
    total_interest_loan = (total_monthly_loan * n_months) - property_value
    total_interest_lease = (total_monthly_lease * n_months) - property_value

    # Total cost
    total_cost_loan = total_interest_loan + property_value
    total_cost_lease = total_interest_lease + property_value

    # Depreciation
    depreciation_loan = acquisition_cost_loan / depreciation_years * duration_years
    depreciation_lease = (acquisition_cost_lease / duration_years * duration_years) + residual_value_leasing

    # Deductible expenses
    deductible_loan = total_interest_loan + depreciation_loan
    deductible_lease = (monthly_wc_lease * n_months - wc_lease) + depreciation_lease

    # Tax benefits
    tax_benefit_loan = deductible_loan * tax_rate
    tax_benefit_lease = deductible_lease * tax_rate

    # Final burden
    final_loan = total_cost_loan - tax_benefit_loan
    final_lease = total_cost_lease - tax_benefit_lease

    return round(final_loan), round(final_lease)

# ===== Streamlit UI =====
def loan_vs_leasing_ui():
    st.title("🏦 Loan vs Leasing Analysis")
    st.markdown(
        "Compare the **total financial burden** of acquiring an asset via **loan** or **leasing**. "
        "Includes interest, working capital, depreciation, and tax effects."
    )

    with st.form("loan_vs_leasing_form"):
        # ----- Inputs -----
        col1, col2 = st.columns(2)

        with col1:
            property_value = st.number_input(
                "🏠 Asset Value (€)",
                value=1_000_000.0,
                step=10_000.0,
                help="Purchase price of the asset (e.g., machinery, vehicle, equipment)."
            )
            loan_financing_percent = st.number_input(
                "💰 Loan Financing (%)",
                min_value=0.0, max_value=100.0,
                value=70.0,
                help="Percentage of asset financed via bank loan."
            )
            leasing_financing_percent = st.number_input(
                "💸 Leasing Financing (%)",
                min_value=0.0, max_value=100.0,
                value=100.0,
                help="Percentage of asset financed via leasing."
            )
            duration_years = st.number_input(
                "⏳ Duration (years)",
                min_value=1, value=5,
                help="Contract duration in years."
            )
            pay_when = st.selectbox(
                "📅 Payment Timing",
                options=["End of Period", "Beginning of Period"],
                help="Choose if payments are made at the end or beginning of each period."
            )
            pay_when_val = 0 if pay_when == "End of Period" else 1

        with col2:
            loan_rate = st.number_input(
                "🏦 Loan Interest Rate (%)", value=6.0,
                help="Annual interest rate on the loan."
            )
            wc_rate = st.number_input(
                "💳 Working Capital Rate (%)", value=10.0,
                help="Cost of financing required working capital."
            )
            add_expenses_loan = st.number_input(
                "🧾 Additional Loan Expenses (€)", value=10_000.0,
                help="Upfront fees or administrative costs for the loan."
            )
            add_expenses_leasing = st.number_input(
                "🧾 Additional Leasing Expenses (€)", value=5_000.0,
                help="Upfront fees or administrative costs for the lease."
            )
            residual_value_leasing = st.number_input(
                "🔄 Residual Value (Leasing, €)", value=100_000.0,
                help="Estimated value of the asset at the end of the lease period."
            )
            depreciation_years = st.number_input(
                "📉 Depreciation Period (years)", min_value=1, value=10,
                help="Years to depreciate the asset for tax purposes."
            )
            tax_rate = st.number_input(
                "🏦 Tax Rate (%)", value=24.0,
                help="Corporate income tax rate for tax benefit calculations."
            ) / 100

        submitted = st.form_submit_button("🔍 Calculate")

    # ----- Results -----
    if submitted:
        final_loan, final_lease = calculate_final_burden(
            loan_rate/100, wc_rate/100, duration_years, property_value,
            loan_financing_percent/100, leasing_financing_percent/100,
            add_expenses_loan, add_expenses_leasing, residual_value_leasing,
            depreciation_years, tax_rate, pay_when_val
        )

        st.markdown("---")
        st.subheader("📊 Results")
        col1, col2 = st.columns(2)
        col1.metric("🏦 Total Burden with Loan", f"€ {final_loan:,}")
        col2.metric("💸 Total Burden with Leasing", f"€ {final_lease:,}")

        st.caption(
            "This tool shows the **overall financial cost** of acquiring an asset via loan vs leasing, "
            "including interest, working capital, depreciation, and tax benefits. "
            "Use it to make the most cost-efficient financing decision."
        )
