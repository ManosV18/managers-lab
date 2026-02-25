import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from decimal import Decimal, getcontext
from core.sync import sync_global_state

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

    # NPV Calculation
    inflow = (total_sales * prcnt_new_policy * (1 - discount_trial)) / ((1 + i) ** new_days_take)
    inflow += (total_sales * prcnt_old_policy) / ((1 + i) ** days_no_take_old)
    
    outflow = (cogs * (extra_sales / (current_sales if current_sales != 0 else 1))) / ((1 + i) ** avg_days_suppliers)
    outflow += current_sales / ((1 + i) ** avg_current_days)
    
    npv = float(inflow - outflow)

    return {
        "new_avg_days": float(new_avg_days),
        "free_capital": float(free_capital),
        "npv": npv
    }

def show_receivables_analyzer_ui():
    st.header("📊 Receivables Strategic Control")
    m = sync_global_state()
    
    # Inputs
    col1, col2 = st.columns(2)
    with col1:
        total_sales = st.number_input("Current Annual Sales (€)", value=1000000.0)
        cogs = st.number_input("Total COGS (€)", value=700000.0)
    with col2:
        discount_val = st.slider("Cash Discount (%)", 0.0, 5.0, 2.0) / 100
        new_days = st.number_input("Target Days", value=10)

    # Core Execution
    res = calculate_discount_npv_full(
        total_sales, total_sales*0.05, discount_val, 0.6, 
        90, 90, new_days, cogs, 0.15, 45
    )

    st.metric("Strategy NPV", f"€ {res['npv']:,.2f}")
    
    if st.button("Back to Library"):
        st.session_state.selected_tool = None
        st.rerun()
