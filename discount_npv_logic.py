import streamlit as st
from decimal import Decimal, getcontext

# --- CALCULATION LOGIC ---
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
    inflow += total_sales * prcnt_old_policy / ((1 + i) ** days_curently_paying_clients_not_take_discount)

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

    optimum_discount = (1 - ((1 + i) ** (new_days_payment_clients_take_disc - avg_current_collection_days))) / 2

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

# --- UI ---
def show_discount_npv_ui():
    st.title("💳 Cash Discount – Strategic NPV Analysis")

    # Default values για web
    master_sales = 1000
    master_cogs = 800
    master_wacc = 0.2

    with st.form("discount_npv_form"):
        col1, col2 = st.columns(2)

        with col1:
            st.subheader("📈 Sales Data")
            current_sales = st.number_input("Current Sales ($)", value=float(master_sales))
            extra_sales = st.number_input("Extra Sales from Discount ($)", value=250.0)
            cogs = st.number_input("Total COGS ($)", value=float(master_cogs))
            wacc = st.number_input("Capital Cost (WACC %)", value=master_wacc * 100) / 100

        with col2:
            st.subheader("🎯 Discount Strategy")
            discount_trial = st.number_input("Proposed Discount (%)", value=2.0) / 100
            prc_clients_take_disc = st.number_input("% of Revenue Taking Discount", value=40.0) / 100
            avg_days_pay_suppliers = st.number_input("Supplier Payment Days", value=30)

        st.subheader("📊 Revenue Segmentation")
        s1, s2, s3 = st.columns(3)

        with s1:
            fast_pct = st.number_input("Fast Payers (% Revenue)", value=30.0) / 100
            fast_dso = st.number_input("Fast DSO (days)", value=60)
        with s2:
            med_pct = st.number_input("Medium Payers (% Revenue)", value=40.0) / 100
            med_dso = st.number_input("Medium DSO (days)", value=90)
        with s3:
            slow_pct = st.number_input("Slow Payers (% Revenue)", value=30.0) / 100
            slow_dso = st.number_input("Slow DSO (days)", value=120)

        allocation_mode = st.radio(
            "Discount Targeting Strategy",
            ["Proportional", "Slow Payers First", "Fast Payers First"]
        )

        new_days_cash_payment = st.number_input("New Target Payment Days", value=10)
        submitted = st.form_submit_button("📊 Calculate Strategic NPV")

    if submitted:
        total_pct = fast_pct + med_pct + slow_pct
        if abs(total_pct - 1) > 0.01:
            st.error("Revenue segmentation must sum to 100%.")
            st.stop()

        uptake = prc_clients_take_disc

        segments = [
            {"pct": fast_pct, "dso": fast_dso},
            {"pct": med_pct, "dso": med_dso},
            {"pct": slow_pct, "dso": slow_dso},
        ]

        if allocation_mode == "Slow Payers First":
            segments.sort(key=lambda x: x["dso"], reverse=True)
        elif allocation_mode == "Fast Payers First":
            segments.sort(key=lambda x: x["dso"])

        remaining = uptake
        weighted_take_dso = 0
        weighted_no_take_dso = 0

        for seg in segments:
            take_from_seg = min(seg["pct"], remaining)
            not_take_from_seg = seg["pct"] - take_from_seg
            weighted_take_dso += take_from_seg * seg["dso"]
            weighted_no_take_dso += not_take_from_seg * seg["dso"]
            remaining -= take_from_seg

        effective_days_take = weighted_take_dso / uptake if uptake > 0 else 0
        effective_days_no_take = weighted_no_take_dso / (1 - uptake) if uptake < 1 else 0

        results = calculate_discount_npv(
            current_sales,
            extra_sales,
            discount_trial,
            uptake,
            effective_days_take,
            effective_days_no_take,
            new_days_cash_payment,
            cogs,
            wacc,
            avg_days_pay_suppliers
        )

        st.divider()
        st.subheader("📊 Policy Impact Analysis")
        r1, r2, r3 = st.columns(3)
        r1.metric("Current ACP", f"{results['avg_current_collection_days']} days")
        r2.metric("New ACP", f"{results['new_avg_collection_period']} days")
        r3.metric("Released Capital", f"${results['free_capital']:,.2f}")

        # Financial Impact
        st.divider()
        st.subheader("📊 Financial Impact")
        def colored_metric(label, value):
            color = "green" if value >= 0 else "red"
            st.markdown(f"""
                <div style="text-align:center; padding:10px; border-radius:5px; background-color:#f0f2f6;">
                    <h4>{label}</h4>
                    <h3 style="color:{color};">${value:,.2f}</h3>
                </div>
            """, unsafe_allow_html=True)

        col1, col2, col3 = st.columns(3)
        with col1:
            colored_metric("Profit from Extra Sales", results['profit_from_extra_sales'])
        with col2:
            colored_metric("Profit from Released Capital", results['profit_from_free_capital'])
        with col3:
            colored_metric("Cost of Discount", results['discount_cost'])

        # NPV
        st.divider()
        st.subheader("💰 Value Creation (NPV)")
        npv_val = results["npv"]
        if npv_val > 0:
            st.success(f"### Net Present Value: ${npv_val:,.2f}")
            st.write("✅ The discount policy creates value.")
        else:
            st.error(f"### Net Present Value: ${npv_val:,.2f}")
            st.write("❌ The discount policy destroys value.")

        with st.expander("📉 Optimization & Thresholds"):
            st.write(f"Maximum Sustainable Discount: {results['max_discount']}%")
            st.write(f"Mathematically Optimal Discount: {results['optimum_discount']}%")
