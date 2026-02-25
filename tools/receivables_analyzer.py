import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from decimal import Decimal, getcontext
from core.sync import sync_global_state

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
        "discount_cost": float(total_sales * prcnt_new_policy * discount_
