import streamlit as st

def format_number(value):
    return f"€ {value:,.0f}"

def loan_vs_leasing_ui():
    st.header("📊 Loan vs Leasing Comparison")
    st.caption(
        "Compare **total after-tax financial burden** between Loan and Leasing "
        "including financing, working capital, depreciation and tax effects."
    )

    with st.form("loan_vs_leasing_form"):
        st.subheader("🔢 Input Parameters")
        col1, col2 = st.columns(2)

        with col1:
            loan_rate = st.number_input("Loan Interest Rate (%)", value=6.0) / 100
            wc_rate = st.number_input("Working Capital Interest Rate (%)", value=8.0) / 100
            duration_years = st.number_input("Duration (years)", min_value=1, value=15)

            pay_when = st.radio(
                "Payment Timing",
                ["End of Period", "Beginning of Period"]
            )
            pay_when = 1 if pay_when == "Beginning of Period" else 0

            tax_rate = st.number_input("Corporate Tax Rate (%)", value=35.0) / 100

        with col2:
            property_value = st.number_input("Property Market Value (€)", value=250_000.0)
            loan_financing = st.number_input("Loan Financing (%)", value=70.0) / 100
            leasing_financing = st.number_input("Leasing Financing (%)", value=100.0) / 100
            add_expenses_loan = st.number_input("Additional Acquisition Costs (Loan €)", value=35_000.0)
            add_expenses_leasing = st.number_input("Additional Acquisition Costs (Leasing €)", value=30_000.0)
            residual_value = st.number_input("Leasing Residual Value (€)", value=3_530.0)
            depreciation_years = st.number_input("Depreciation Period (years)", value=30)

        submitted = st.form_submit_button("📉 Calculate")

    if submitted:
        final_loan, final_leasing = calculate_final_burden(
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
            pay_when
        )

        st.markdown("---")
        st.subheader("📊 Results")

        c1, c2 = st.columns(2)
        c1.metric("Total Cost – Loan", format_number(final_loan))
        c2.metric("Total Cost – Leasing", format_number(final_leasing))

        if final_loan < final_leasing:
            st.success("✅ Loan is financially preferable.")
        else:
            st.success("✅ Leasing is financially preferable.")
