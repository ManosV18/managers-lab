import streamlit as st
import plotly.graph_objects as go
from decimal import Decimal, getcontext

def calculate_discount_npv_full(
    current_sales, extra_sales, discount_trial, prc_clients_take_disc,
    days_take_old, days_no_take_old, new_days_take, cogs, wacc, avg_days_suppliers
):
    # Set precision for financial accuracy
    getcontext().prec = 20
    i = wacc / 365 # Daily Discount Rate (WACC based)

    # --- 1. CURRENT STATE ANALYSIS ---
    prc_no_take = 1 - prc_clients_take_disc
    avg_current_days = (prc_clients_take_disc * days_take_old) + (prc_no_take * days_no_take_old)
    current_receivables = current_sales * avg_current_days / 365

    # --- 2. NEW POLICY STATE ANALYSIS ---
    total_sales = current_sales + extra_sales
    # Percentage of total sales that will now take the discount
    prcnt_new_policy = ((current_sales * prc_clients_take_disc) + extra_sales) / total_sales
    prcnt_old_policy = 1 - prcnt_new_policy

    new_avg_days = (prcnt_new_policy * new_days_take) + (prcnt_old_policy * days_no_take_old)
    new_receivables = total_sales * new_avg_days / 365
    free_capital = current_receivables - new_receivables

    # --- 3. COLD FINANCIAL CALCULATIONS (STRICT NPV) ---
    # Inflow: Discounted value of collections under the new policy
    inflow = (total_sales * prcnt_new_policy * (1 - discount_trial)) / ((1 + i) ** new_days_take)
    inflow += (total_sales * prcnt_old_policy) / ((1 + i) ** days_no_take_old)

    # Outflow: Discounted value of cost and original collection state
    # PV of cost for extra sales
    outflow = ((cogs / current_sales) * (extra_sales / current_sales) * current_sales) / ((1 + i) ** avg_days_suppliers)
    # PV of the current collection cycle
    outflow += current_sales / ((1 + i) ** avg_current_days)

    npv = inflow - outflow

    # --- 4. STRATEGIC THRESHOLDS (MAX & OPTIMUM) ---
    # Formula for Break-even Discount Rate
    max_discount = 1 - (
        (1 + i) ** (new_days_take - days_no_take_old) * (
            (1 - 1 / prcnt_new_policy) + (
                (1 + i) ** (days_no_take_old - avg_current_days) +
                (cogs / current_sales) * (extra_sales / current_sales) * (1 + i) ** (days_no_take_old - avg_days_suppliers)
            ) / (prcnt_new_policy * (1 + (extra_sales / current_sales)))
        )
    )

    # Optimum discount based on money cost and collection gap
    optimum_discount = (1 - ((1 + i) ** (new_days_take - avg_current_days))) / 2

    # Additional metrics for display
    profit_extra_sales = extra_sales * (1 - cogs / current_sales)
    discount_cost = total_sales * prcnt_new_policy * discount_trial

    return {
        "avg_current_days": float(avg_current_days),
        "current_receivables": float(current_receivables),
        "new_avg_days": float(new_avg_days),
        "new_receivables": float(new_receivables),
        "free_capital": float(free_capital),
        "npv": float(npv),
        "max_discount": float(max_discount * 100),
        "optimum_discount": float(abs(optimum_discount * 100)),
        "profit_extra_sales": float(profit_extra_sales),
        "discount_cost": float(discount_cost),
        "prcnt_new_policy": float(prcnt_new_policy * 100)
    }

def show_receivables_analyzer_ui():
    st.title("📈 Strategic Receivables & NPV Analyzer")
    st.markdown("---")

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Current Sales Data")
        curr_sales = st.number_input("Current Annual Sales (€)", value=1000000.0)
        cogs = st.number_input("Cost of Goods Sold (COGS €)", value=700000.0)
        wacc = st.number_input("WACC (%)", value=15.0) / 100
        suppliers_days = st.number_input("Supplier Payment Days", value=45)

    with col2:
        st.subheader("Discount Policy Inputs")
        extra_sales = st.number_input("Est. Extra Sales (€)", value=100000.0)
        disc_trial = st.number_input("Proposed Discount (%)", value=2.0) / 100
        take_rate = st.number_input("% Current Clients taking Discount", value=40.0) / 100
        
    st.divider()
    
    col3, col4 = st.columns(2)
    with col3:
        st.subheader("Collection Timing (Days)")
        days_take_old = st.number_input("Days (Current takers)", value=60)
        days_no_take_old = st.number_input("Days (Non-takers)", value=120)
        new_days_take = st.number_input("New Payment Target (Cash)", value=10)

    # Run the Engine
    res = calculate_discount_npv_full(
        curr_sales, extra_sales, disc_trial, take_rate,
        days_take_old, days_no_take_old, new_days_take, cogs, wacc, suppliers_days
    )

    # --- RESULTS DISPLAY ---
    st.divider()
    m1, m2, m3 = st.columns(3)
    m1.metric("Net NPV", f"€ {res['npv']:,.2f}", delta="Value Created" if res['npv'] > 0 else "Value Destroyed")
    m2.metric("Cash Released", f"€ {res['free_capital']:,.0f}")
    m3.metric("New Avg DSO", f"{res['new_avg_days']:.1f} Days")

    with st.expander("🔍 View Detailed Analytical Breakdown"):
        st.write(f"**Current Receivables:** € {res['current_receivables']:,.2f}")
        st.write(f"**New Receivables:** € {res['new_receivables']:,.2f}")
        st.write(f"**Gross Profit from Extra Sales:** € {res['profit_extra_sales']:,.2f}")
        st.write(f"**Nominal Discount Cost:** € {res['discount_cost']:,.2f}")
        st.write(f"**Clients under New Policy:** {res['prcnt_new_policy']:.1f}%")

    st.subheader("🧠 Strategic Thresholds")
    c_max, c_opt = st.columns(2)
    c_max.info(f"**Max Sustainable Discount:** {res['max_discount']:.2f}%")
    c_opt.success(f"**Optimum Financial Discount:** {res['optimum_discount']:.2f}%")

    # Visualizing NPV Sensitivity
    st.subheader("Sensitivity Analysis: Discount % vs NPV")
    test_discounts = [d/100 for d in range(0, 105, 5)] # 0% to 10%
    npv_trend = [calculate_discount_npv_full(curr_sales, extra_sales, d, take_rate, 
                days_take_old, days_no_take_old, new_days_take, cogs, wacc, suppliers_days)['npv'] for d in test_discounts]
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=[d*100 for d in test_discounts], y=npv_trend, name="NPV Profile", line=dict(color="#00CC96", width=3)))
    fig.add_hline(y=0, line_dash="dash", line_color="red")
    fig.update_layout(template="plotly_dark", xaxis_title="Discount (%)", yaxis_title="NPV (€)")
    st.plotly_chart(fig, use_container_width=True)

if __name__ == "__main__":
    show_receivables_analyzer_ui()
