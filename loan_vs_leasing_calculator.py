import streamlit as st
import numpy_financial as npf

# --- Payment function wrapper ---
def pmt(rate, nper, pv, fv=0, when=0):
    return -npf.pmt(rate, nper, pv, fv, when)

# --- Calculation logic ---
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
    pay_when
):
    months = 12
    n_months = duration_years * months

    # Acquisition costs
    acquisition_cost_loan = property_value + add_expenses_loan
    acquisition_cost_lease = property_value + add_expenses_leasing

    # Working capital financing
    wc_loan = property_value - (property_value * loan_financing_percent) + add_expenses_loan
    wc_lease = property_value - (property_value * leasing_financing_percent) + add_expenses_leasing

    # Monthly payments
    monthly_loan = pmt(loan_rate / months, n_months, property_value * loan_financing_percent, 0, pay_when)
    monthly_lease = pmt(loan_rate / months, n_months, property_value * leasing_financing_percent, 0, pay_when)
    monthly_wc_loan = pmt(wc_rate / months, n_months, wc_loan, 0, pay_when)
    monthly_wc_lease = pmt(wc_rate / months, n_months, wc_lease, 0, pay_when)

    # Total monthly burden
    total_monthly_loan = monthly_loan + monthly_wc_loan
    total_monthly_lease = monthly_lease + monthly_wc_lease

    # Total interest
    total_interest_loan = (total_monthly_loan * n_months) - property_value
    total_interest_lease = (total_monthly_lease * n_months) - property_value

    # Total cost over project
    total_cost_loan = total_interest_loan + property_value
    total_cost_lease = total_interest_lease + property_value

    # Depreciation
    depreciation_loan = acquisition_cost_loan / depreciation_years * duration_years
    depreciation_lease = (acquisition_cost_lease / duration_years * duration_years) + residual_value_leasing

    # Deductible expenses
    deductible_loan = total_interest_loan + depreciation_loan
    deductible_lease = (monthly_wc_lease * n_months - wc_lease) + depreciation_lease

    # Tax benefit
    tax_benefit_loan = deductible_loan * tax_rate
    tax_benefit_lease = deductible_lease * tax_rate

    # Final burden
    final_loan = total_cost_loan - tax_benefit_loan
    final_lease = total_cost_lease - tax_benefit_lease

    return round(final_loan), round(final_lease)

# --- UI ---
def loan_vs_leasing_ui():
    st.title("🏦 Loan vs Leasing Comparison")
    st.caption(
        "Compare the total financial burden of financing an asset via **loan or leasing**, "
        "taking into account interest, working capital, depreciation, and tax effects."
    )

    with st.form("loan_lease_form"):
        st.subheader("🔢 Input Parameters")

        col1, col2 = st.columns(2)
        with col1:
            loan_rate = st.number_input("Loan Interest Rate (%)", value=6.0)
            wc_rate = st.number_input("Working Capital Interest Rate (%)", value=8.0)
            duration_years = st.number_input("Duration (years)", value=15, min_value=1)
            pay_when_option = st.radio("Payment Timing", ["Beginning of Period", "End of Period"])
            pay_when = 1 if pay_when_option == "Beginning of Period" else 0
            tax_rate = st.number_input("Corporate Tax Rate (%)", value=35.0) / 100

        with col2:
            property_value = st.number_input("Property Market Value (€)", value=250_000.0, step=1_000.0)
            loan_financing_percent = st.number_input("Loan Financing (%)", value=70.0) / 100
            leasing_financing_percent = st.number_input("Leasing Financing (%)", value=100.0) / 100
            add_expenses_loan = st.number_input("Additional Acquisition Costs (Loan €)", value=35_000.0, step=100.0)
            add_expenses_leasing = st.number_input("Additional Acquisition Costs (Leasing €)", value=30_000.0, step=100.0)
            residual_value_leasing = st.number_input("Leasing Residual Value (€)", value=3_530.0)
            depreciation_years = st.number_input("Depreciation Period (years)", value=30, min_value=1)

        submitted = st.form_submit_button("📊 Calculate")

    if submitted:
        final_loan, final_lease = calculate_final_burden(
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
            pay_when
        )

        st.markdown("---")
        st.subheader("📉 Results")

        col3, col4 = st.columns(2)
        col3.metric("📌 Total Cost – Loan", f"€ {final_loan:,}".replace(",", "."))
        col4.metric("📌 Total Cost – Leasing", f"€ {final_lease:,}".replace(",", "."))

        st.caption("✅ The option with the lower total cost is financially preferable.")
