import streamlit as st
from discount_npv_logic import calculate_discount_npv
from utils import format_number_gr, format_percentage_gr

def show_discount_npv_ui():
    st.header("💳 Cash Discount – NPV Analysis")
    st.caption("Evaluation of a discount policy considering the time value of money")

    # ---------- INPUTS ----------
    with st.form("discount_npv_form"):
        st.subheader("📈 Sales")
        col1, col2 = st.columns(2)

        with col1:
            current_sales = st.number_input("Current Sales (€)", value=1000.0, step=100.0)
            extra_sales = st.number_input("Extra Sales from Discount (€)", value=250.0, step=50.0)

        with col2:
            discount_trial = st.number_input("Proposed Discount (%)", value=2.0, step=0.1) / 100
            prc_clients_take_disc = st.number_input(
                "% of Customers Accepting Discount", value=40.0
            ) / 100

        st.subheader("⏱️ Credit Terms")
        col3, col4 = st.columns(2)

        with col3:
            days_clients_take_discount = st.number_input(
                "Payment Days (with discount)", value=60
            )
            new_days_cash_payment = st.number_input(
                "New Cash Payment Days", value=10
            )

        with col4:
            days_clients_no_discount = st.number_input(
                "Payment Days (without discount)", value=120
            )
            avg_days_pay_suppliers = st.number_input(
                "Average Supplier Payment Days", value=30
            )

        st.subheader("💸 Capital Cost")
        col5, col6 = st.columns(2)

        with col5:
            cogs = st.number_input("COGS (€)", value=800.0)

        with col6:
            wacc = st.number_input("Capital Cost (WACC %)", value=20.0) / 100

        submitted = st.form_submit_button("📊 Calculate")

    # ---------- RESULTS ----------
    if submitted:
        results = calculate_discount_npv(
            current_sales,
            extra_sales,
            discount_trial,
            prc_clients_take_disc,
            days_clients_take_discount,
            days_clients_no_discount,
            new_days_cash_payment,
            cogs,
            wacc,
            avg_days_pay_suppliers
        )

        st.markdown("---")
        st.subheader("📊 Collection Cycle")

        r1, r2, r3 = st.columns(3)
        r1.metric("Current ACP", f"{results['avg_current_collection_days']} days")
        r2.metric("New ACP", f"{results['new_avg_collection_period']} days")
        r3.metric("Released Capital", format_number_gr(results['free_capital']))

        st.subheader("💰 Financial Impact")
        r4, r5, r6 = st.columns(3)
        r4.metric("Profit from Sales", format_number_gr(results['profit_from_extra_sales']))
        r5.metric("Profit from Capital", format_number_gr(results['profit_from_free_capital']))
        r6.metric("Discount Cost", format_number_gr(results['discount_cost']))

        st.markdown("---")
        st.metric("📌 Net Present Value (NPV)", format_number_gr(results["npv"]))

        if results["npv"] > 0:
            st.success("✅ The discount policy creates value")
        else:
            st.error("❌ The discount policy destroys value")

        with st.expander("📉 Limits & Optimization"):
            st.write(f"Maximum Discount (NPV = 0): {format_percentage_gr(results['max_discount'])}")
            st.write(f"Optimal Discount: {format_percentage_gr(results['optimum_discount'])}")
