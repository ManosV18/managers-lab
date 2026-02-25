import streamlit as st
import plotly.graph_objects as go
from decimal import Decimal, getcontext

# --- NPV LOGIC ENGINE ---
def calculate_discount_npv(
    current_sales, extra_sales, discount_trial, prc_clients_take_disc,
    days_curently_paying_clients_take_discount, days_curently_paying_clients_not_take_discount,
    new_days_payment_clients_take_disc, cogs, wacc, avg_days_pay_suppliers
):
    getcontext().prec = 20
    
    # Conversion to float for logic handling
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
    
    # Outflow strictly following your provided logic
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
                (cogs / current_sales) * (extra_sales / current_sales) * (1 + i) ** (days_curently_paying_clients_not_take_discount - avg_days_pay_suppliers)
            ) / (prcnt_new_policy * (1 + extra_sales / current_sales))
        )
    )

    optimum_discount = (1 - ((1 + i) ** (new_days_payment_clients_take_disc - avg_current_collection_days))) / 2

    return {
        "avg_current_collection_days": round(float(avg_current_collection_days), 2),
        "current_receivables": round(float(current_receivables), 2),
        "new_avg_collection_period": round(float(new_avg_collection_period), 2),
        "new_receivables": round(float(new_receivables), 2),
        "free_capital": round(float(free_capital), 2),
        "profit_from_extra_sales": round(float(profit_from_extra_sales), 2),
        "profit_from_free_capital": round(float(profit_from_free_capital), 2),
        "discount_cost": round(float(discount_cost), 2),
        "npv": round(float(npv), 2),
        "max_discount": round(float(max_discount * 100), 2),
        "optimum_discount": round(float(optimum_discount * 100), 2),
    }

def show_receivables_analyzer_ui():
    st.title("📊 Cash Discount Performance Analysis (NPV)")
    
    # Try to fetch global data if available
    g_sales = st.session_state.get('annual_revenue', 1000000.0)
    g_cogs = st.session_state.get('total_cogs', 800000.0)
    g_wacc = st.session_state.get('wacc', 20.0) / 100 if st.session_state.get('wacc') else 0.20
    g_ap = st.session_state.get('ap_days', 30)

    with st.form("discount_npv_form"):
        col1, col2 = st.columns(2)

        with col1:
            st.subheader("Sales & Terms")
            current_sales = st.number_input("Current Sales (€)", value=float(g_sales), step=1000.0)
            extra_sales = st.number_input("Extra Sales due to Discount (€)", value=current_sales*0.1, step=500.0)
            discount_trial = st.number_input("Proposed Discount (%)", value=2.0, step=0.1) / 100
            prc_clients_take_disc = st.number_input("% Clients Accepting Discount", value=40.0, step=1.0) / 100
            days_clients_take_discount = st.number_input("Current Days (for those who will take it)", value=60, step=1)

        with col2:
            st.subheader("Financial & Operations")
            days_clients_no_discount = st.number_input("Current Days (for those who won't take it)", value=120, step=1)
            new_days_cash_payment = st.number_input("New Payment Days (for Discount)", value=10, step=1)
            cogs = st.number_input("Cost of Goods Sold (COGS €)", value=float(g_cogs), step=1000.0)
            wacc = st.number_input("Cost of Capital (WACC %)", value=float(g_wacc * 100), step=0.1) / 100
            avg_days_pay_suppliers = st.number_input("Avg. Supplier Payment Days", value=int(g_ap), step=1)

        submitted = st.form_submit_button("Calculate Analytical Results", use_container_width=True)

    if submitted:
        res = calculate_discount_npv(
            current_sales, extra_sales, discount_trial, prc_clients_take_disc,
            days_clients_take_discount, days_clients_no_discount,
            new_days_cash_payment, cogs, wacc, avg_days_pay_suppliers
        )

        # Main Metrics
        st.divider()
        m1, m2, m3 = st.columns(3)
        m1.metric("Net Present Value (NPV)", f"€ {res['npv']:,.2f}")
        m2.metric("Max Discount (BEP)", f"{res['max_discount']}%")
        m3.metric("Optimum Discount", f"{res['optimum_discount']}%")

        # Detailed Analysis
        st.subheader("Detailed Breakdown")
        col_a, col_b = st.columns(2)
        
        with col_a:
            st.write(f"**Current DSO:** {res['avg_current_collection_days']} days")
            st.write(f"**New Targeted DSO:** {res['new_avg_collection_period']} days")
            st.write(f"**Free Capital:** € {res['free_capital']:,.2f}")
        
        with col_b:
            st.write(f"**Profit from Growth:** € {res['profit_from_extra_sales']:,.2f}")
            st.write(f"**Liquidity Benefit:** € {res['profit_from_free_capital']:,.2f}")
            st.write(f"**Total Discount Cost:** € {res['discount_cost']:,.2f}")

        # Sensitivity Chart
        st.subheader("NPV Sensitivity: Acceptance vs Profit")
        test_rates = [r/100 for r in range(0, 101, 10)]
        npv_values = [calculate_discount_npv(current_sales, extra_sales, discount_trial, tr,
                      days_clients_take_discount, days_clients_no_discount,
                      new_days_cash_payment, cogs, wacc, avg_days_pay_suppliers)['npv'] for tr in test_rates]
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=[r*100 for r in test_rates], y=npv_values, mode='lines+markers', line=dict(color="#00CC96")))
        fig.add_hline(y=0, line_dash="dash", line_color="red")
        fig.update_layout(template="plotly_dark", xaxis_title="Acceptance Rate (%)", yaxis_title="NPV (€)")
        st.plotly_chart(fig, use_container_width=True)

    st.divider()
    if st.button("⬅️ Back to Library Hub"):
        st.session_state.selected_tool = None
        st.rerun()
