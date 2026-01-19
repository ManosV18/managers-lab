import streamlit as st
from discount_npv_logic import calculate_discount_npv
from utils import format_number_gr, format_percentage_gr

def show_discount_npv_ui():
    st.title("💳 Cash Discount – NPV Analysis")
    st.caption(
        "Evaluate the impact of cash discounts considering the **time value of money**."
    )

    # ===== Input Data =====
    st.header("🔢 Input Data")

    with st.form("discount_npv_form"):
        st.subheader("📈 Sales")
        current_sales = st.number_input(
            "Current Sales (€)", value=1000.0, step=100.0
        )
        st.caption("Total revenue from current sales.")

        extra_sales = st.number_input(
            "Extra Sales from Discount (€)", value=250.0, step=50.0
        )
        st.caption("Expected additional revenue if the discount is offered.")

        st.subheader("🎯 Discount & Customers")
        discount_trial = st.number_input(
            "Proposed Discount (%)", value=2.0, step=0.1
        ) / 100
        st.caption("Percentage discount offered to eligible customers.")

        prc_clients_take_disc = st.number_input(
            "Percentage of Customers Taking Discount (%)", value=40.0, step=1.0
        ) / 100
        st.caption("Share of customers expected to accept the discount.")

        st.subheader("⏱️ Payment Terms")
        days_clients_take_discount = st.number_input(
            "Payment Days (with discount)", value=60
        )
        st.caption("Average days for customers who take the discount to pay.")

        days_clients_no_discount = st.number_input(
            "Payment Days (without discount)", value=120
        )
        st.caption("Average days for customers who do not take the discount.")

        new_days_cash_payment = st.number_input(
            "New Cash Payment Days (for discount)", value=10
        )
        st.caption("Targeted days for immediate cash payment when discount is applied.")

        st.subheader("💸 Costs & Financing")
        cogs = st.number_input("COGS (€)", value=800.0)
        st.caption("Cost of goods sold related to the sales volume.")

        wacc = st.number_input("Capital Cost (WACC %)", value=20.0, step=0.1) / 100
        st.caption("Weighted Average Cost of Capital (annual rate).")

        avg_days_pay_suppliers = st.number_input(
            "Average Supplier Payment Days", value=30
        )
        st.caption("Average days your company takes to pay suppliers.")

        # Submit button
        submitted = st.form_submit_button("📊 Calculate")

    # ===== Results =====
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
        r1.metric("Current Avg Collection Period (ACP)", f"{results['avg_current_collection_days']} days")
        r2.metric("New Avg Collection Period", f"{results['new_avg_collection_period']} days")
        r3.metric("Released Capital", format_number_gr(results['free_capital']))
        st.caption(
            "Changes in receivables and freed-up capital due to the discount policy."
        )

        st.subheader("💰 Financial Impact")
        r4, r5, r6 = st.columns(3)
        r4.metric("Profit from Extra Sales", format_number_gr(results['profit_from_extra_sales']))
        r5.metric("Profit from Released Capital", format_number_gr(results['profit_from_free_capital']))
        r6.metric("Cost of Discount", format_number_gr(results['discount_cost']))
        st.caption(
            "Evaluate additional profit and costs arising from the discount policy."
        )

        st.markdown("---")
        st.metric("📌 Net Present Value (NPV)", format_number_gr(results["npv"]))
        st.caption(
            "NPV considers both additional profits and the time value of money, showing the net value created by the discount."
        )

        if results["npv"] > 0:
            st.success("✅ Discount policy creates value")
        else:
            st.error("❌ Discount policy destroys value")

        with st.expander("📉 Limits & Optimization"):
            st.write(f"Maximum Discount (NPV = 0): {format_percentage_gr(results['max_discount'])}")
            st.write(f"Optimal Discount: {format_percentage_gr(results['optimum_discount'])}")
            st.caption(
                "Max Discount: highest discount before NPV turns negative.\n"
                "Optimal Discount: best discount considering sales increase and capital costs."
            )
