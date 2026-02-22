import streamlit as st
from decimal import Decimal, getcontext
import pandas as pd
from core.engine import compute_core_metrics

# --- CALCULATION LOGIC (Preserving your exact logic) ---
def calculate_discount_npv(current_sales, extra_sales, discount_trial, prc_clients_take_disc,
                           eff_take, eff_no_take, new_days_payment_clients_take_disc, 
                           cogs, wacc, avg_days_pay_suppliers):
    getcontext().prec = 20
    i = wacc / 365

    avg_current_collection_days = (prc_clients_take_disc * eff_take) + ((1 - prc_clients_take_disc) * eff_no_take)
    current_receivables = current_sales * avg_current_collection_days / 365

    total_sales = current_sales + extra_sales
    prcnt_new_policy = ((current_sales * prc_clients_take_disc) + extra_sales) / total_sales
    prcnt_old_policy = 1 - prcnt_new_policy

    new_avg_collection_period = (prcnt_new_policy * new_days_payment_clients_take_disc +
                                 prcnt_old_policy * eff_no_take)
    
    new_receivables = total_sales * new_avg_collection_period / 365
    free_capital = current_receivables - new_receivables

    profit_from_extra_sales = extra_sales * (1 - cogs / current_sales)
    profit_from_free_capital = free_capital * wacc
    discount_cost = total_sales * prcnt_new_policy * discount_trial

    inflow = (total_sales * prcnt_new_policy * (1 - discount_trial) / ((1 + i) ** new_days_payment_clients_take_disc))
    inflow += total_sales * prcnt_old_policy / ((1 + i) ** eff_no_take)

    outflow = ((cogs / current_sales) * (extra_sales / current_sales) * current_sales / ((1 + i) ** avg_days_pay_suppliers))
    outflow += current_sales / ((1 + i) ** avg_current_collection_days)

    npv = inflow - outflow

    # Thresholds
    max_discount = 1 - ((1 + i) ** (new_days_payment_clients_take_disc - eff_no_take) * (
        (1 - 1 / prcnt_new_policy) + ((1 + i) ** (eff_no_take - avg_current_collection_days) +
        (cogs / current_sales) * (extra_sales / current_sales) * (1 + i) ** (eff_no_take - avg_days_pay_suppliers)) / 
        (prcnt_new_policy * (1 + extra_sales / current_sales))
    ))
    optimum_discount = (1 - ((1 + i) ** (new_days_payment_clients_take_disc - avg_current_collection_days))) / 2

    return {
        "avg_current_collection_days": round(avg_current_collection_days, 2),
        "free_capital": round(free_capital, 2),
        "npv": round(npv, 2),
        "max_discount": round(max_discount * 100, 2),
        "optimum_discount": round(optimum_discount * 100, 2),
        "profit_from_free_capital": round(profit_from_free_capital, 2),
        "profit_from_extra_sales": round(profit_from_extra_sales, 2),
        "discount_cost": round(discount_cost, 2),
        "new_avg_collection_period": round(new_avg_collection_period, 2)
    }

def show_discount_npv_ui():
    st.header("💳 Cash Discount – Strategic NPV Analysis")
    
    # 1. FETCH DATA FROM ENGINE
    metrics = compute_core_metrics()
    base_sales = metrics['revenue']
    # COGS = Variable Costs total
    base_cogs = st.session_state.get('variable_cost', 0.0) * st.session_state.get('volume', 0)
    # WACC = Interest Rate + Risk Premium (e.g., 5%)
    base_wacc = st.session_state.get('interest_rate', 0.10) + 0.05

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("📈 Core Financials")
        current_sales = st.number_input("Current Annual Sales (€)", value=float(base_sales))
        extra_sales = st.number_input("Extra Sales from Discount (€)", value=current_sales * 0.1)
        cogs = st.number_input("Total COGS (€)", value=float(base_cogs))
        wacc = st.number_input("Cost of Capital / WACC (%)", value=float(base_wacc * 100)) / 100

    with col2:
        st.subheader("🎯 Discount Strategy")
        discount_trial = st.number_input("Proposed Discount (%)", value=2.0) / 100
        prc_clients_take_disc = st.number_input("% Revenue Expected to Take Discount", value=40.0) / 100
        new_days_cash_payment = st.number_input("Target Discount Days", value=10)
        avg_days_pay_suppliers = st.number_input("Supplier Payment Days", value=30)

    # ... [Το υπόλοιπο UI με το segmentation παραμένει ως έχει] ...
    st.divider()
    st.subheader("📊 Receivable Segmentation")
    s1, s2, s3 = st.columns(3)
    fast_pct = s1.number_input("Fast Payers (%)", value=30.0) / 100
    fast_dso = s1.number_input("Fast DSO (days)", value=45)
    med_pct = s2.number_input("Med Payers (%)", value=40.0) / 100
    med_dso = s2.number_input("Med DSO (days)", value=75)
    slow_pct = s3.number_input("Slow Payers (%)", value=30.0) / 100
    slow_dso = s3.number_input("Slow DSO (days)", value=120)

    if st.button("🚀 Calculate Policy Impact", use_container_width=True):
        # [Η λογική του allocation_mode παραμένει ίδια]
        segments = [{"pct": fast_pct, "dso": fast_dso}, {"pct": med_pct, "dso": med_dso}, {"pct": slow_pct, "dso": slow_dso}]
        remaining = prc_clients_take_disc
        weighted_take_dso = 0
        weighted_no_take_dso = 0
        for seg in segments:
            take = min(seg["pct"], remaining)
            weighted_take_dso += take * seg["dso"]
            weighted_no_take_dso += (seg["pct"] - take) * seg["dso"]
            remaining -= take

        eff_take = weighted_take_dso / prc_clients_take_disc if prc_clients_take_disc > 0 else 0
        eff_no_take = weighted_no_take_dso / (1 - prc_clients_take_disc) if prc_clients_take_disc < 1 else 0

        res = calculate_discount_npv(current_sales, extra_sales, discount_trial, prc_clients_take_disc, 
                                     eff_take, eff_no_take, new_days_cash_payment, cogs, wacc, avg_days_pay_suppliers)

        # RESULTS DISPLAY
        
        
        m1, m2, m3 = st.columns(3)
        m1.metric("DSO Shift", f"{res['avg_current_collection_days']} → {res['new_avg_collection_period']}", f"{res['new_avg_collection_period'] - res['avg_current_collection_days']:.1f} days")
        m2.metric("Cash Released", f"{res['free_capital']:,.2f} €")
        m3.metric("NPV Outcome", f"{res['npv']:,.2f} €", delta="Value Creation" if res['npv']>0 else "Value Loss")
        
        # ... [Το υπόλοιπο display των Gains/Costs και Threshold Analysis παραμένει ως έχει] ...
