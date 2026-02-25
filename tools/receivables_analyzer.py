import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from decimal import Decimal, getcontext

# --- NPV ENGINE (UNTOUCHED) ---
def calculate_discount_npv_full(
    current_sales, extra_sales, discount_trial, prc_clients_take_disc,
    days_take_old, days_no_take_old, new_days_take, cogs, wacc, avg_days_suppliers
):
    getcontext().prec = 20
    i = wacc / 365 

    prc_no_take = 1 - prc_clients_take_disc
    avg_current_days = (prc_clients_take_disc * days_take_old) + (prc_no_take * days_no_take_old)
    current_receivables = current_sales * avg_current_days / 365

    total_sales = current_sales + extra_sales
    prcnt_new_policy = ((current_sales * prc_clients_take_disc) + extra_sales) / total_sales
    prcnt_old_policy = 1 - prcnt_new_policy

    new_avg_days = (prcnt_new_policy * new_days_take) + (prcnt_old_policy * days_no_take_old)
    new_receivables = total_sales * new_avg_days / 365
    free_capital = current_receivables - new_receivables

    inflow = (total_sales * prcnt_new_policy * (1 - discount_trial)) / ((1 + i) ** new_days_take)
    inflow += (total_sales * prcnt_old_policy) / ((1 + i) ** days_no_take_old)
    
    outflow = ((cogs / current_sales) * (extra_sales / current_sales) * current_sales) / ((1 + i) ** avg_days_suppliers)
    outflow += current_sales / ((1 + i) ** avg_current_days)
    
    npv = inflow - outflow

    return {
        "avg_current_days": float(avg_current_days),
        "new_avg_days": float(new_avg_days),
        "free_capital": float(free_capital),
        "npv": float(npv),
        "discount_cost": float(total_sales * prcnt_new_policy * discount_trial),
        "targeted_dso": float(days_take_old)
    }

def show_receivables_analyzer_ui():
    st.header("📊 Receivables Strategic Control (NPV Mode)")
    
    # 1. SEGMENTATION & TARGETING
    st.subheader("1. Portfolio Segmentation & Targeting")
    
    # SYNC ADDITION: Use global session state for base amounts if available
    base_sales = st.session_state.get('price', 0) * st.session_state.get('volume', 0)
    
    default_segments = [
        {"Cat": "A", "Amt": 300000.0, "Days": 60},
        {"Cat": "B", "Amt": 400000.0, "Days": 85},
        {"Cat": "C", "Amt": 550000.0, "Days": 115},
        {"Cat": "D", "Amt": 75000.0, "Days": 160},
    ]
    
    seg_data = []
    cols = st.columns([1, 2, 1])
    cols[0].write("**Target?**")
    cols[1].write("**Amount (€)**")
    cols[2].write("**Current Days**")
    
    for s in default_segments:
        c = st.columns([1, 2, 1])
        is_targeted = c[0].checkbox(f"Offer to {s['Cat']}", value=(s['Cat'] in ['C', 'D']), key=f"target_{s['Cat']}")
        amt = c[1].number_input(f"Amount {s['Cat']}", value=s['Amt'], key=f"amt_{s['Cat']}", label_visibility="collapsed")
        days = c[2].number_input(f"Days {s['Cat']}", value=s['Days'], key=f"day_{s['Cat']}", label_visibility="collapsed")
        seg_data.append({"Cat": s['Cat'], "Amount": amt, "Days": days, "Targeted": is_targeted})

    total_sales = sum(d["Amount"] for d in seg_data)
    targeted_sales = sum(d["Amount"] for d in seg_data if d["Targeted"])
    
    current_weighted_dso = sum(d["Amount"] * d["Days"] for d in seg_data) / total_sales if total_sales > 0 else 0
    targeted_weighted_dso = sum(d["Amount"] * d["Days"] for d in seg_data if d["Targeted"]) / targeted_sales if targeted_sales > 0 else 0

    st.markdown(f"**Total Portfolio:** € {total_sales:,.0f} | **Targeted Segment:** € {targeted_sales:,.0f}")

    # 2. NPV SIMULATION SETTINGS
    st.subheader("2. Targeted Discount Parameters")
    col1, col2 = st.columns(2)
    
    with col1:
        discount_val = st.slider("Cash Discount Offered (%)", 0.0, 5.0, 2.0, step=0.1) / 100
        new_days_target = st.number_input("Target Payment Days (for Discount)", value=10)
        # SYNC ADDITION: Pull WACC from sidebar state
        wacc = st.session_state.get('wacc', 0.15)
        
    with col2:
        take_rate_targeted = st.slider("% Acceptance within Targeted Segment", 0, 100, 60) / 100
        extra_sales_growth = st.number_input("Est. Sales Growth (%)", value=5.0) / 100
        # SYNC ADDITION: Pull Variable Cost from sidebar state
        vc = st.session_state.get('variable_cost', 0.0)
        vol = st.session_state.get('volume', 0)
        cogs_input = st.number_input("Total COGS (€)", value=float(vc * vol) if vc*vol > 0 else total_sales * 0.7)

    total_take_rate = (targeted_sales * take_rate_targeted) / total_sales if total_sales > 0 else 0

    res = calculate_discount_npv_full(
        current_sales=total_sales,
        extra_sales=total_sales * extra_sales_growth,
        discount_trial=discount_val,
        prc_clients_take_disc=total_take_rate,
        days_take_old=targeted_weighted_dso,
        days_no_take_old=current_weighted_dso,
        new_days_take=new_days_target,
        cogs=cogs_input,
        wacc=wacc,
        avg_days_suppliers=st.session_state.get('ap_days', 45) # SYNC ADDITION
    )

    # 3. RESULTS & SYNC BUTTON
    st.divider()
    r1, r2, r3 = st.columns(3)
    r1.metric("Net Present Value (NPV)", f"€ {res['npv']:,.2f}")
    r2.metric("Free Capital (Liquidity)", f"€ {res['free_capital']:,.0f}")
    r3.metric("New Portfolio DSO", f"{res['new_avg_days']:.1f} Days")

    # SYNC ADDITION: The Sync Button
    if st.button("🔄 Sync Results to Cash Cycle", use_container_width=True):
        st.session_state.ar_days = res['new_avg_days'] # Updates the global AR Days
        st.success(f"Global DSO updated to {res['new_avg_days']:.1f} days for all calculations!")

    if res['npv'] > 0:
        st.success(f"**Verdict:** Positive NPV. Capital benefit outweighs discount cost.")
    else:
        st.error(f"**Verdict:** Negative NPV. Strategy destroys value.")

    # 4. SENSITIVITY CHART
    st.subheader("NPV Sensitivity: Acceptance Rate vs Profitability")
    test_rates = [r/100 for r in range(0, 101, 10)]
    npvs = [calculate_discount_npv_full(total_sales, total_sales*extra_sales_growth, discount_val, 
            (targeted_sales*tr)/total_sales, targeted_weighted_dso, current_weighted_dso, 
            new_days_target, cogs_input, wacc, 45)['npv'] for tr in test_rates]
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=[r*100 for r in test_rates], y=npvs, mode='lines+markers', line=dict(color="#00CC96")))
    fig.add_hline(y=0, line_dash="dash", line_color="red")
    fig.update_layout(xaxis_title="Acceptance Rate in Targeted Segment (%)", yaxis_title="NPV (€)", template="plotly_dark")
    st.plotly_chart(fig, use_container_width=True)
