import streamlit as st
from decimal import Decimal, getcontext

# ========================
# --- CALCULATION LOGIC ---
# ========================
def calculate_discount_npv(
    current_sales,
    extra_sales,
    discount_trial,
    prc_clients_take_disc,
    days_curently_paying_clients_take_discount,
    days_curently_paying_clients_not_take_discount,
    new_days_payment_clients_take_disc,
    cogs,
    wacc,
    avg_days_pay_suppliers
):
    getcontext().prec = 20

    prc_clients_not_take_disc = 1 - prc_clients_take_disc
    avg_current_collection_days = (
        prc_clients_take_disc * days_curently_paying_clients_take_discount +
        prc_clients_not_take_disc * days_curently_paying_clients_not_take_discount
    )
    current_receivables = current_sales * avg_current_collection_days / 365

    total_sales = current_sales + extra_sales
    prcnt_new_policy = ((current_sales * prc_clients_take_disc) + extra_sales) / total_sales
    prcnt_old_policy = 1 - prcnt_new_policy

    new_avg_collection_period = (
        prcnt_new_policy * new_days_payment_clients_take_disc +
        prcnt_old_policy * days_curently_paying_clients_not_take_discount
    )
    new_receivables = total_sales * new_avg_collection_period / 365
    free_capital = current_receivables - new_receivables

    profit_from_extra_sales = extra_sales * (1 - cogs / current_sales)
    profit_from_free_capital = free_capital * wacc
    discount_cost = total_sales * prcnt_new_policy * discount_trial

    i = wacc / 365

    inflow = (
        total_sales * prcnt_new_policy * (1 - discount_trial) /
        ((1 + i) ** new_days_payment_clients_take_disc)
    )
    inflow += (
        total_sales * prcnt_old_policy /
        ((1 + i) ** days_curently_paying_clients_not_take_discount)
    )

    outflow = (
        (cogs / current_sales) * (extra_sales / current_sales) * current_sales /
        ((1 + i) ** avg_days_pay_suppliers)
    )
    outflow += current_sales / ((1 + i) ** avg_current_collection_days)

    npv = inflow - outflow

    max_discount = 1 - (
        (1 + i) ** (new_days_payment_clients_take_disc - days_curently_paying_clients_not_take_discount) * (
            (1 - 1 / prcnt_new_policy) + (
                (1 + i) ** (days_curently_paying_clients_not_take_discount - avg_current_collection_days) +
                (cogs / current_sales) * (extra_sales / current_sales) *
                (1 + i) ** (days_curently_paying_clients_not_take_discount - avg_days_pay_suppliers)
            ) / (prcnt_new_policy * (1 + extra_sales / current_sales))
        )
    )

    optimum_discount = (
        1 - ((1 + i) ** (new_days_payment_clients_take_disc - avg_current_collection_days))
    ) / 2

    return {
        "avg_current_collection_days": round(avg_current_collection_days, 2),
        "current_receivables": round(current_receivables, 2),
        "prcnt_new_policy": round(prcnt_new_policy, 4),
        "prcnt_old_policy": round(prcnt_old_policy, 4),
        "new_avg_collection_period": round(new_avg_collection_period, 2),
        "new_receivables": round(new_receivables, 2),
        "free_capital": round(free_capital, 2),
        "profit_from_extra_sales": round(profit_from_extra_sales, 2),
        "profit_from_free_capital": round(profit_from_free_capital, 2),
        "discount_cost": round(discount_cost, 2),
        "npv": round(npv, 2),
        "max_discount": round(max_discount * 100, 2),
        "optimum_discount": round(optimum_discount * 100, 2),
    }

# ========================
# --- STREAMLIT UI ---
# ========================
def show_discount_npv_ui():
    st.title("💳 Cash Discount – NPV Analysis")
    st.caption("Ανάλυση επιπτώσεων έκπτωσης με βάση την **παρούσα αξία (NPV)**.")

    with st.form("discount_npv_form"):
        st.subheader("📈 Sales Data")
        current_sales = st.number_input("Current Sales (€)", value=1000.0, step=100.0)
        extra_sales = st.number_input("Extra Sales from Discount (€)", value=250.0, step=50.0)
        cogs = st.number_input("COGS (€)", value=800.0, step=50.0)
        wacc = st.number_input("Capital Cost (WACC %)", value=20.0, step=0.1) / 100

        st.subheader("🎯 Discount & Customers")
        discount_trial = st.number_input("Proposed Discount (%)", value=2.0, step=0.1) / 100
        prc_clients_take_disc = st.number_input("% of Customers Taking Discount", value=40.0, step=1.0) / 100

        st.subheader("⏱️ Payment Terms")
        days_clients_take_discount = st.number_input("Payment Days (with discount)", value=60)
        days_clients_no_discount = st.number_input("Payment Days (without discount)", value=120)
        new_days_cash_payment = st.number_input("New Target Payment Days", value=10)
        avg_days_pay_suppliers = st.number_input("Average Supplier Payment Days", value=30)

        submitted = st.form_submit_button("📊 Calculate")

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
        r1.metric("Current Avg Collection Period (days)", results['avg_current_collection_days'])
        r2.metric("New Avg Collection Period (days)", results['new_avg_collection_period'])
        r3.metric("Released Capital (€)", f"{results['free_capital']:,.2f}")

        st.subheader("💰 Financial Impact")
        r4, r5, r6 = st.columns(3)
        r4.metric("Profit from Extra Sales (€)", f"{results['profit_from_extra_sales']:,.2f}")
        r5.metric("Profit from Released Capital (€)", f"{results['profit_from_free_capital']:,.2f}")
        r6.metric("Cost of Discount (€)", f"{results['discount_cost']:,.2f}")

        st.markdown("---")
        st.subheader("📌 Net Present Value (NPV)")
        npv_val = results["npv"]
        if npv_val > 0:
            st.success(f"✅ NPV: €{npv_val:,.2f} – Policy creates value")
        else:
            st.error(f"❌ NPV: €{npv_val:,.2f} – Policy destroys value")

        with st.expander("📉 Limits & Optimization"):
            st.write(f"Maximum Discount (NPV = 0): {results['max_discount']}%")
            st.write(f"Optimal Discount: {results['optimum_discount']}%")

if __name__ == "__main__":
    show_discount_npv_ui()
