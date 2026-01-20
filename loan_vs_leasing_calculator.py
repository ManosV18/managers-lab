import streamlit as st
from loan_vs_leasing_logic import calculate_loan_vs_leasing_breakdown


def format_number(value):
    return f"€ {value:,.0f}"


def loan_vs_leasing_ui():
    st.header("📊 Loan vs Leasing – Financial Comparison")

    st.subheader("🔢 Input Parameters")
    col1, col2 = st.columns(2)

    with col1:
        loan_rate = st.number_input("Loan Interest Rate (%)", value=6.0) / 100
        wc_rate = st.number_input("Working Capital Interest Rate (%)", value=8.0) / 100
        duration_years = st.number_input("Duration (years)", min_value=1, value=15)
        payment_timing = st.radio("Payment Timing", ["Beginning of Period", "End of Period"])
        pay_when = 1 if payment_timing == "Beginning of Period" else 0
        tax_rate = st.number_input("Corporate Tax Rate (%)", value=35.0) / 100

    with col2:
        property_value = st.number_input("Property Market Value (€)", value=250_000.0)
        loan_financing = st.number_input("Loan Financing (%)", value=70.0) / 100
        leasing_financing = st.number_input("Leasing Financing (%)", value=100.0) / 100
        add_expenses_loan = st.number_input("Additional Acquisition Costs (Loan €)", value=35_000.0)
        add_expenses_leasing = st.number_input("Additional Acquisition Costs (Leasing €)", value=30_000.0)
        residual_value = st.number_input("Leasing Residual Value (€)", value=3_530.0)
        depreciation_years = st.number_input("Depreciation Period (years)", value=30)

    results = calculate_loan_vs_leasing_breakdown(
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

    st.subheader("📉 Financial Breakdown")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### 🏦 Loan")
        for k, v in results["loan"].items():
            st.write(f"**{k}:** {format_number(v)}")

    with col2:
        st.markdown("### 🧾 Leasing")
        for k, v in results["leasing"].items():
            st.write(f"**{k}:** {format_number(v)}")

    st.divider()

    if results["loan"]["Final Financial Burden"] < results["leasing"]["Final Financial Burden"]:
        st.success("✅ Loan is the financially preferable option.")
    else:
        st.success("✅ Leasing is the financially preferable option.")
