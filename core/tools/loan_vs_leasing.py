import streamlit as st

def format_number_gr(value):
    """Formats numbers with a thousands separator."""
    return f"{value:,.0f}"

def pmt_basic(rate, nper, pv, fv=0, when=0):
    """Calculates the monthly payment (PMT) without external libraries."""
    if rate == 0:
        return -(pv + fv) / nper
    factor = (1 + rate)**nper
    payment = (pv * rate * factor) / (factor - 1)
    if when == 1:
        payment = payment / (1 + rate)
    return payment

def calculate_final_burden(
    loan_rate, wc_rate, duration_years, property_value,
    loan_financing_percent, leasing_financing_percent,
    add_expenses_loan, add_expenses_leasing,
    residual_value_leasing, depreciation_years,
    tax_rate, pay_when
):
    """Calculates the total financial burden for both options."""
    months = 12
    n_months = duration_years * months

    # 1. Working Capital (The cash you must 'sacrifice' or borrow for upfront costs)
    wc_loan = property_value - (property_value * loan_financing_percent) + add_expenses_loan
    wc_lease = property_value - (property_value * leasing_financing_percent) + add_expenses_leasing

    # 2. Monthly Payments
    monthly_loan = pmt_basic(loan_rate / months, n_months, property_value * loan_financing_percent, 0, pay_when)
    monthly_lease = pmt_basic(loan_rate / months, n_months, property_value * leasing_financing_percent, 0, pay_when)
    
    # WC cost (Interest-only approach to capture capital cost)
    monthly_wc_loan = pmt_basic(wc_rate / months, n_months, wc_loan, 0, pay_when)
    monthly_wc_lease = pmt_basic(wc_rate / months, n_months, wc_lease, 0, pay_when)

    total_monthly_loan = monthly_loan + monthly_wc_loan
    total_monthly_lease = monthly_lease + monthly_wc_lease

    # 3. Total Interest Cost
    total_interest_loan = (total_monthly_loan * n_months) - property_value
    total_interest_lease = (total_monthly_lease * n_months) - property_value

    # 4. Tax Shield (Interest + Depreciation)
    # Acquisition costs are depreciated
    acq_loan = property_value + add_expenses_loan
    depreciation_total_loan = (acq_loan / depreciation_years) * duration_years
    
    # Leasing usually allows full rent deduction or combined interest/depreciation
    # Simplified here to match analytical logic of interest + depreciation shield
    tax_benefit_loan = (total_interest_loan + depreciation_total_loan) * tax_rate
    tax_benefit_lease = (total_interest_lease + (property_value / duration_years * duration_years)) * tax_rate

    # 5. Final Net Burden
    final_loan = (total_monthly_loan * n_months) - tax_benefit_loan
    final_lease = (total_monthly_lease * n_months) - tax_benefit_lease + residual_value_leasing

    return round(final_loan), round(final_lease)

def loan_vs_leasing_ui():
    st.header("📊 Loan vs Leasing Comparison")
    st.info("Analytical comparison of total financial burden considering Tax Shields, Interest, and Capital Costs.")

    st.subheader("🔢 Input Parameters")
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("**Financing Terms**")
        loan_rate = st.number_input("Standard Interest Rate (%)", value=6.0) / 100
        wc_rate = st.number_input("Opportunity Cost of Capital (%)", value=8.0, help="The rate used for upfront capital tied up.") / 100
        duration_years = st.number_input("Analysis Horizon (Years)", value=15)
        tax_rate = st.number_input("Corporate Tax Rate (%)", value=22.0) / 100

    with col2:
        st.markdown("**Investment Details**")
        property_value = st.number_input("Investment Value (€)", value=250000.0)
        loan_financing = st.slider("Loan Financing (%)", 0, 100, 70) / 100
        leasing_financing = st.slider("Leasing Financing (%)", 0, 100, 100) / 100
        residual_value = st.number_input("Leasing Residual Value (€)", value=3500.0)
        depreciation_years = st.number_input("Asset Useful Life (Years)", value=30)

    # Calculation Execution
    final_loan, final_leasing = calculate_final_burden(
        loan_rate, wc_rate, duration_years, property_value, 
        loan_financing, leasing_financing, 35000.0, 30000.0, 
        residual_value, depreciation_years, tax_rate, 0
    )

    st.divider()

    # RESULTS DASHBOARD
    st.subheader("📉 Financial Verdict")
    m1, m2 = st.columns(2)
    m1.metric("Total Loan Net Burden", f"€ {format_number_gr(final_loan)}")
    m2.metric("Total Leasing Net Burden", f"€ {format_number_gr(final_leasing)}")

    # Visualizing the Tax Shield impact
    

    st.subheader("💡 Strategic Analytical Verdict")
    diff = abs(final_loan - final_leasing)
    cheaper = "Loan" if final_loan < final_leasing else "Leasing"
    
    st.success(f"**{cheaper}** is the mathematically superior choice, offering a net advantage of **€ {format_number_gr(diff)}** over {duration_years} years.")
    
    with st.expander("🔍 Methodology Breakdown"):
        st.markdown(f"""
        1. **Capital Opportunity Cost**: Calculates the cost of the funds you provide upfront (own participation).
        2. **Tax Shield**: Evaluates the deductible interest and depreciation based on a {tax_rate*100:.0f}% rate.
        3. **Net Burden**: (Total Payments + Residual) - (Tax Savings).
        """)

    if st.button("⬅️ Back to Library"):
        st.session_state.selected_tool = None
        st.rerun()
