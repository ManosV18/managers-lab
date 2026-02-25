import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from decimal import Decimal, getcontext
from core.sync import sync_global_state

# --- NPV ENGINE (Strictly Aligned with discount_npv_logic.py) ---
def calculate_discount_npv_full(
    current_sales, extra_sales, discount_trial, prc_clients_take_disc,
    days_take_old, days_no_take_old, new_days_take, cogs, wacc, avg_days_suppliers
):
    getcontext().prec = 20
    
    # Μετατροπή σε Decimal για ακρίβεια
    current_sales = Decimal(str(current_sales))
    extra_sales = Decimal(str(extra_sales))
    discount_trial = Decimal(str(discount_trial))
    prc_clients_take_disc = Decimal(str(prc_clients_take_disc))
    days_take_old = Decimal(str(days_take_old))
    days_no_take_old = Decimal(str(days_no_take_old))
    new_days_take = Decimal(str(new_days_take))
    cogs = Decimal(str(cogs))
    wacc = Decimal(str(wacc))
    avg_days_suppliers = Decimal(str(avg_days_suppliers))
    
    i = wacc / Decimal('365')

    # Βασικοί Υπολογισμοί
    prc_no_take = 1 - prc_clients_take_disc
    avg_current_days = (prc_clients_take_disc * days_take_old) + (prc_no_take * days_no_take_old)
    current_receivables = current_sales * avg_current_days / Decimal('365')

    total_sales = current_sales + extra_sales
    prcnt_new_policy = ((current_sales * prc_clients_take_disc) + extra_sales) / total_sales
    prcnt_old_policy = 1 - prcnt_new_policy

    new_avg_days = (prcnt_new_policy * new_days_take) + (prcnt_old_policy * days_no_take_old)
    new_receivables = total_sales * new_avg_days / Decimal('365')
    free_capital = current_receivables - new_receivables

    # NPV Calculation (Inflow - Outflow)
    inflow = (total_sales * prcnt_new_policy * (1 - discount_trial)) / ((1 + i) ** new_days_take)
    inflow += (total_sales * prcnt_old_policy) / ((1 + i) ** days_no_take_old)
    
    # Outflow Logic (Strict Match)
    outflow = ((cogs / current_sales) * (extra_sales / current_sales) * current_sales) / ((1 + i) ** avg_days_suppliers)
    outflow += current_sales / ((1 + i) ** avg_current_days)
    
    npv = inflow - outflow

    # Limits Calculation (Max & Optimum)
    max_discount = 1 - (
        (1 + i) ** (new_days_take - days_no_take_old) * (
            (1 - 1 / prcnt_new_policy) + (
                (1 + i) ** (days_no_take_old - avg_current_days) +
                (cogs / current_sales) * (extra_sales / current_sales) * (1 + i) ** (days_no_take_old - avg_days_suppliers)
            ) / (prcnt_new_policy * (1 + extra_sales / current_sales))
        )
    )
    
    optimum_discount = (1 - ((1 + i) ** (new_days_take - avg_current_days))) / 2

    return {
        "avg_current_days": float(avg_current_days),
        "new_avg_days": float(new_avg_days),
        "free_capital": float(free_capital),
        "npv": float(npv),
        "max_discount": float(max_discount * 100),
        "optimum_discount": float(optimum_discount * 100),
        "discount_cost": float(total_sales * prcnt_new_policy * discount_trial)
    }

def show_receivables_analyzer_ui():
    st.header("📊 Receivables Strategic Control (NPV Mode)")
    
    m = sync_global_state()
    
    # 1. SEGMENTATION
    st.subheader("1. Portfolio Segmentation")
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
        is_targeted = c[0].checkbox(f"Offer to {s['Cat']}", value=(s['Cat'] in ['C', 'D']), key=f"tg_{s['Cat']}")
        amt = c[1].number_input(f"Amt {s['Cat']}", value=s['Amt'], key=f"am_{s['Cat']}", label_visibility="collapsed")
        days = c[2].number_input(f"Dys {s['Cat']}", value=s['Days'], key=f"dy_{s['Cat']}", label_visibility="collapsed")
        seg_data.append({"Cat": s['Cat'], "Amount": amt, "Days": days, "Targeted": is_targeted})

    total_sales = sum(d["Amount"] for d in seg_data)
    targeted_sales = sum(d["Amount"] for d in seg_data if d["Targeted"])
    current_weighted_dso = sum(d["Amount"] * d["Days"] for d in seg_data) / (total_sales if total_sales > 0 else 1)
    targeted_weighted_dso = sum(d["Amount"] * d["Days"] for d in seg_data if d["Targeted"]) / (targeted_sales if targeted_sales > 0 else 1)

    # 2. PARAMETERS
    st.subheader("2. Targeted Discount Parameters")
    col1, col2 = st.columns(2)
    with col1:
        discount_val = st.slider("Cash Discount (%)", 0.0, 5.0, 2.0, step=0.1, key="ra_d_val") / 100
        new_days_target = st.number_input("Target Days", value=10, key="ra_d_days")
        wacc = st.session_state.get('wacc', 0.10)
    with col2:
        take_rate_targeted = st.slider("% Acceptance (Targeted)", 0, 100, 60, key="ra_t_rate") / 100
        growth = st.number_input("Growth (%)", value=5.0, key="ra_g_val") / 100
        cogs_input = st.number_input("COGS (€)", value=total_sales * 0.7, key="ra_c_val")

    total_take_rate = (targeted_sales * take_rate_targeted) / (total_sales if total_sales > 0 else 1)

    res = calculate_discount_npv_full(
        total_sales, total_sales * growth, discount_val, total_take_rate,
        targeted_weighted_dso, current_weighted_dso, new_days_target, 
        cogs_input, wacc, st.session_state.get('ap_days', 45)
    )

    # 3. RESULTS
    st.divider()
    r1, r2, r3 = st.columns(3)
    r1.metric("NPV", f"€ {res['npv']:,.2f}")
    r2.metric("Max Discount", f"{res['max_discount']:.2f}%")
    r3.metric("Optimum Discount", f"{res['optimum_discount']:.2f}%")

    st.subheader("Liquidity & Cycle")
    l1, l2 = st.columns(2)
    l1.metric("Free Capital", f"€ {res['free_capital']:,.0f}")
    l2.metric("New Portfolio DSO", f"{res['new_avg_days']:.1f} Days")

    # 4. CHART
    st.subheader("NPV Sensitivity Analysis")
    test_rates = [r/100 for r in range(0, 101, 10)]
    npvs = [calculate_discount_npv_full(total_sales, total_sales*growth, discount_val, 
            (targeted_sales*tr)/(total_sales if total_sales > 0 else 1), targeted_weighted_dso, 
            current_weighted_dso, new_days_target, cogs_input, wacc, 45)['npv'] for tr in test_rates]
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=[r*100 for r in test_rates], y=npvs, mode='lines+markers', name="NPV Path"))
    fig.add_hline(y=0, line_dash="dash", line_color="red")
    fig.update_layout(xaxis_title="Acceptance Rate (%)", yaxis_title="NPV (€)", template="plotly_dark")
    st.plotly_chart(fig, use_container_width=True)

    if st.button("⬅️ Back to Library Hub", key="ra_final_back"):
        st.session_state.selected_tool = None
        st.rerun()
