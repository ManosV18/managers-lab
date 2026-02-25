import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from decimal import Decimal, getcontext

# --- YOUR ORIGINAL NPV ENGINE (UNTOUCHED) ---
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

    # Inflow/Outflow logic based on your strict Excel formulas
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

# --- UI WITH SELECTIVE TARGETING ---
def show_receivables_analyzer_ui():
    st.header("📊 Receivables Strategic Control (NPV Mode)")
    
    st.subheader("1. Portfolio Segmentation & Targeting")
    st.info("Select specific segments to receive the cash discount offer (Default: C & D).")
    
    # Pre-defined segments based on your data
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
        # Option to only target C and D
        is_targeted = c[0].checkbox(f"Offer to {s['Cat']}", value=(s['Cat'] in ['C', 'D']), key=f"target_{s['Cat']}")
        amt = c[1].number_input(f"Amount {s['Cat']}", value=s['Amt'], key=f"amt_{s['Cat']}", label_visibility="collapsed")
        days = c[2].number_input(f"Days {s['Cat']}", value=s['Days'], key=f"day_{s['Cat']}", label_visibility="collapsed")
        seg_data.append({"
