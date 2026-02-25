import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from core.sync import sync_global_state

def calculate_excel_total_cost(q, M, kf, r, unit_price, storage_costs_monthly, insurance_monthly, interest_rate):
    # Μετατροπή μηνιαίων σε ετήσια βάσει Excel
    total_storage = storage_costs_monthly * 12
    total_insurance = insurance_monthly * 12
    
    # Κόστος Παραγγελιών (KF)
    ordering_cost = (M / q) * kf
    
    # Κόστος Αποθήκευσης & Τόκων (KL)
    # Βασίζεται στη μέση αξία αποθέματος (q/2) * (τιμή + κόστος συντήρησης)
    inventory_value_avg = (q / 2) * unit_price * (1 - r)
    holding_cost = inventory_value_avg * interest_rate + (total_storage + total_insurance) * (q / M)
    
    return ordering_cost + holding_cost

def show_inventory_manager():
    st.header("📦 Strategic Inventory & Cost Optimizer")
    
    tab1, tab2 = st.tabs(["Inventory Dashboard", "Total Cost Simulation (Excel Model)"])
    
    with tab1:
        # Εδώ παραμένει ο κώδικας για το Segmentation που φτιάξαμε πριν
        st.subheader("Inventory Segmentation & Cash Impact")
        # ... (Ο κώδικας με τα Fast/Slow Moving όπως τον έχουμε ορίσει)

    with tab2:
        st.subheader("📈 Total Cost Optimization (Excel Logic)")
        col1, col2 = st.columns(2)
        
        with col1:
            M = st.number_input("Annual Demand (M)", value=10000)
            unit_p = st.number_input("Unit Price (q)", value=30.0)
            kf = st.number_input("Order Cost (kf)", value=600.0)
            r_disc = st.number_input("Discount % (r)", value=0.0) / 100
        
        with col2:
            storage_m = st.number_input("Monthly Storage/Rent", value=600.0)
            insurance_m = st.number_input("Monthly Insurance", value=150.0)
            interest = st.number_input("Annual Interest Rate", value=5.0) / 100

        # Simulation Logic
        q_min = 100
        q_max = 2000
        q_steps = np.arange(q_min, q_max, 10)
        costs = [calculate_excel_total_cost(q, M, kf, r_disc, unit_p, storage_m, insurance_m, interest) for q in q_steps]
        
        optimal_q = q_steps[np.argmin(costs)]
        min_cost = min(costs)

        st.divider()
        st.success(f"🎯 **Optimal Order Quantity (Q): {int(optimal_q)} units** at Min Cost: **€{min_cost:,.2f}**")

        # Charting
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=list(q_steps), y=costs, name="Total Cost Curve", line=dict(color="#00CC96", width=3)))
        fig.add_vline(x=optimal_q, line_dash="dash", line_color="orange", annotation_text="OPTIMAL Q")
        
        fig.update_layout(template="plotly_dark", xaxis_title="Order Quantity (q)", yaxis_title="Total Procurement Cost (€)")
        st.plotly_chart(fig, use_container_width=True)

    if st.button("⬅️ Back to Library"):
        st.session_state.selected_tool = None
        st.rerun()
