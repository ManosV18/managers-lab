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
    """Calculates the 15-year total financial burden for both options."""
    months = 12
    n_months = duration_years * months

    # 1. Acquisition Costs
    acquisition_cost_loan = property_value + add_expenses_loan
    acquisition_cost_lease = property_value + add_expenses_leasing

    # 2. Working Capital Loans (Required to cover own participation and expenses)
    wc_loan = property_value - (property_value * loan_financing_percent) + add_expenses_loan
    wc_lease = property_value - (property_value * leasing_financing_percent) + add_expenses_leasing

    # 3. Monthly Payments (Calculated using the basic PMT function)
    monthly_loan = pmt_basic(loan_rate / months, n_months, property_value * loan_financing_percent, 0, pay_when)
    monthly_lease = pmt_basic(loan_rate / months, n_months, property_value * leasing_financing_percent, 0, pay_when)
    monthly_wc_loan = pmt_basic(wc_rate / months, n_months, wc_loan, 0, pay_when)
    monthly_wc_lease = pmt_basic(wc_rate / months, n_months, wc_lease, 0, pay_when)

    # 4. Total Monthly Obligations
    total_monthly_loan = monthly_loan + monthly_wc_loan
    total_monthly_lease = monthly_lease + monthly_wc_lease

    # 5. Interest Components
    total_interest_loan = (total_monthly_loan * n_months) - property_value
    total_interest_lease = (total_monthly_lease * n_months) - property_value

    # 6. Total 15-year Gross Cost
    total_cost_loan = total_interest_loan + property_value
    total_cost_lease = total_interest_lease + property_value

    # 7. Depreciation
    depreciation_loan = acquisition_cost_loan / depreciation_years * duration_years
    depreciation_lease = (acquisition_cost_lease / duration_years * duration_years) + residual_value_leasing

    # 8. Deductible Expenses (Tax Shield components)
    deductible_loan = total_interest_loan + depreciation_loan
    deductible_lease = (monthly_wc_lease * n_months - wc_lease) + depreciation_lease

    # 9. Tax Benefits
    tax_benefit_loan = deductible_loan * tax_rate
    tax_benefit_lease = deductible_lease * tax_rate

    # 10. Final Net Burden
    final_loan = total_cost_loan - tax_benefit_loan
    final_lease = total_cost_lease - tax_benefit_lease

    return round(final_loan), round(final_lease)

def loan_vs_leasing_ui():
    st.header("📊 Loan vs Leasing Comparison")
    st.info("Analytical comparison of the total financial burden considering tax shields and financing structures.")

    st.subheader("🔢 Input Data")
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("**Financing Terms**")
        loan_rate = st.number_input("Loan Interest Rate (%)", value=6.0) / 100
        wc_rate = st.number_input("Working Capital Interest Rate (%)", value=8.0) / 100
        duration_years = st.number_input("Duration (Years)", value=15)
        pay_timing = st.radio("Payment Timing", ["Beginning of Month", "End of Month"])
        pay_when = 1 if pay_timing == "Beginning of Month" else 0
        tax_rate = st.number_input("Corporate Tax Rate (%)", value=35.0) / 100

    with col2:
        st.markdown("**Investment Details**")
        property_value = st.number_input("Property Commercial Value ($)", value=250000.0)
        loan_financing = st.number_input("Loan Financing (%)", value=70.0) / 100
        leasing_financing = st.number_input("Leasing Financing (%)", value=100.0) / 100
        add_expenses_loan = st.number_input("Acquisition Expenses (Loan)", value=35000.0)
        add_expenses_leasing = st.number_input("Acquisition Expenses (Leasing)", value=30000.0)
        residual_value = st.number_input("Leasing Residual Value ($)", value=3530.0)
        depreciation_years = st.number_input("Depreciation Period (Years)", value=30)

    st.divider()

    # Calculation Execution
    final_loan, final_leasing = calculate_final_burden(
        loan_rate, wc_rate, duration_years, property_value, 
        loan_financing, leasing_financing, add_expenses_loan, 
        add_expenses_leasing, residual_value, depreciation_years, 
        tax_rate, pay_when
    )

    st.subheader("📉 Financial Verdict")
    m1, m2 = st.columns(2)
    m1.metric("Total Loan Burden", f"$ {format_number_gr(final_loan)}")
    m2.metric("Total Leasing Burden", f"$ {format_number_gr(final_leasing)}")

    # Visual Comparison Chart
    

    st.write("---")
    
    # Analytical Logic Explanation
    with st.expander("🔍 Analysis Explanation"):
        st.markdown(f"""
        **Methodology:**
        1. **Working Capital (WC):** The tool calculates the interest cost for the capital you must provide upfront (Difference in financing + expenses).
        2. **Tax Shield:** It calculates the total interest and depreciation deductible from your taxable income over the {duration_years}-year period.
        3. **Net Burden:** Final Burden = (Principal + Total Interest) - (Tax Savings).
        """)
        
        if final_loan < final_leasing:
            st.success(f"**Loan** is more cost-effective by **$ {format_number_gr(final_leasing - final_loan)}**.")
        else:
            st.success(f"**Leasing** is more cost-effective by **$ {format_number_gr(final_loan - final_leasing)}**.")

    # Navigation (Ευθυγραμμισμένο με το νέο app.py)
    st.divider()
    if st.button("⬅️ Back to Control Tower", use_container_width=True):
        st.session_state.flow_step = "home"
        st.session_state.selected_tool = None
        st.rerun()
    
