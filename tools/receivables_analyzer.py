import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from decimal import Decimal, getcontext

# --- Η ΔΙΚΗ ΣΟΥ ΣΥΝΑΡΤΗΣΗ NPV (ΑΜΕΤΑΒΛΗΤΗ) ---
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
        "discount_cost": float(total_sales * prcnt_new_policy * discount_trial)
    }

# --- UI ΜΕ ΕΠΙΛΕΚΤΙΚΗ ΣΤΟΧΕΥΣΗ (Γ & Δ) ---
def show_receivables_analyzer_ui():
    st.header("📊 Receivables Strategic Control (NPV Mode)")
    
    st.subheader("1. Ανάλυση Πελατολογίου & Επιλογή Στόχων")
    
    default_segments = [
        {"Cat": "A", "Amt": 300000.0, "Days": 60},
        {"Cat": "B", "Amt": 400000.0, "Days": 85},
        {"Cat": "C", "Amt": 550000.0, "Days": 115},
        {"Cat": "D", "Amt": 75000.0, "Days": 160},
    ]
    
    seg_data = []
    # Πίνακας εισαγωγής
    cols = st.columns([1, 2, 1, 1])
    cols[0].write("**Target?**")
    cols[1].write("**Amount (€)**")
    cols[2].write("**Days**")
    
    for s in default_segments:
        c = st.columns([1, 2, 1, 1])
        # Default: Στοχεύουμε Γ και Δ
        is_targeted = c[0].checkbox(f"Offer to {s['Cat']}", value=(s['Cat'] in ['C', 'D']), key=f"target_{s['Cat']}")
        amt = c[1].number_input(f"Amt {s['Cat']}", value=s['Amt'], key=f"amt_{s['Cat']}", label_visibility="collapsed")
        days = c[2].number_input(f"Days {s['Cat']}", value=s['Days'], key=f"day_{s['Cat']}", label_visibility="collapsed")
        seg_data.append({"Cat": s['Cat'], "Amount": amt, "Days": days, "Targeted": is_targeted})

    # Υπολογισμοί για το NPV βάσει επιλογής
    total_sales = sum(d["Amount"] for d in seg_data)
    targeted_sales = sum(d["Amount"] for d in seg_data if d["Targeted"])
    
    # Μέσος όρος ημερών όλου του χαρτοφυλακίου (Current DSO)
    current_weighted_dso = sum(d["Amount"] * d["Days"] for d in seg_data) / total_sales if total_sales > 0 else 0
    
    # Μέσος όρος ημερών αυτών που στοχεύουμε (Targeted DSO)
    if targeted_sales > 0:
        targeted_weighted_dso = sum(d["Amount"] * d["Days"] for d in seg_data if d["Targeted"]) / targeted_sales
    else:
        targeted_weighted_dso = 0

    st.info(f"**Συνολικές Πωλήσεις:** € {total_sales:,.0f} | **Targeted Segment:** € {targeted_sales:,.0f} ({ (targeted_sales/total_sales)*100:.1f}%)")

    

    # 2. NPV SIMULATION
    st.subheader("2. NPV Simulation (Targeted Policy)")
    col1, col2 = st.columns(2)
    
    with col1:
        discount_val = st.slider("Προτεινόμενη Έκπτωση (%)", 0.0, 5.0, 2.0, step=0.1) / 100
        new_days_target = st.number_input("Νέος Στόχος Ημερών (για την έκπτωση)", value=10)
        wacc = st.session_state.get('wacc', 0.15)
        
    with col2:
        # Εδώ το take_rate αφορά ΜΟΝΟ το targeted segment
        take_rate_targeted = st.slider("% του targeted segment που αποδέχεται", 0, 100, 60) / 100
        extra_sales_growth = st.number_input("Εκτίμηση Αύξησης Πωλήσεων (%)", value=5.0) / 100
        cogs_input = st.number_input("Κόστος Πωληθέντων (COGS €)", value=total_sales * 0.7)

    # Προσαρμογή των παραμέτρων για τη συνάρτηση NPV
    # Το prc_clients_take_disc υπολογίζεται ως ποσοστό επί του συνόλου
    total_take_rate = (targeted_sales * take_rate_targeted) / total_sales if total_sales > 0 else 0

    res = calculate_discount_npv_full(
        current_sales=total_sales,
        extra_sales=total_sales * extra_sales_growth,
        discount_trial=discount_val,
        prc_clients_take_disc=total_take_rate,
        days_take_old=targeted_weighted_dso, # Οι ημέρες αυτών που θα πάρουν την έκπτωση
        days_no_take_old=current_weighted_dso, # Οι ημέρες των υπολοίπων
        new_days_take=new_days_target,
        cogs=cogs_input,
        wacc=wacc,
        avg_days_suppliers=45
    )

    # 3. ΑΠΟΤΕΛΕΣΜΑΤΑ
    st.divider()
    r1, r2, r3 = st.columns(3)
    r1.metric("NPV Πολιτικής", f"€ {res['npv']:,.2f}", delta="Value Created" if res['npv'] > 0 else "Value Loss")
    r2.metric("Free Cash Flow", f"€ {res['free_capital']:,.0f}")
    r3.metric("Νέο DSO (Σύνολο)", f"{res['new_avg_days']:.1f} ημέρες")

    st.subheader("📊 Ανάλυση Ευαισθησίας")
    # Γράφημα NPV vs Take Rate
    test_rates = [r/100 for r in range(0, 101, 10)]
    npvs = [calculate_discount_npv_full(total_sales, total_sales*extra_sales_growth, discount_val, 
            (targeted_sales*tr)/total_sales, targeted_weighted_dso, current_weighted_dso, 
            new_days_target, cogs_input, wacc, 45)['npv'] for tr in test_rates]
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=[r*100 for r in test_rates], y=npvs, mode='lines+markers', name="NPV Profile"))
    fig.add_hline(y=0, line_dash="dash", line_color="red")
    fig.update_layout(title="Επίδραση του Take Rate (εντός του Targeted Segment) στο NPV", template="plotly_dark")
    st.plotly_chart(fig, use_container_width=True)
