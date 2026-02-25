import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from core.sync import sync_global_state

def calculate_excel_logic(q_order, M, kf, r_disc, unit_price, storage_monthly, insurance_monthly, interest_rate):
    # Πιστότητα στο Excel inv.xlsx
    # Σταθερό Κόστος Προμηθειών (KF) = (M/q) * kf
    KF = (M / q_order) * kf
    
    # Κόστος Αποθήκευσης και Τόκων (KL)
    # Excel Logic: (q/2 * unit_price * (1-r) * interest) + (Storage_Annual + Insurance_Annual) * (q/M)
    annual_storage = storage_monthly * 12
    annual_insurance = insurance_monthly * 12
    
    inventory_hold_cost = (q_order / 2) * unit_price * (1 - r_disc) * interest_rate
    overhead_impact = (annual_storage + annual_insurance) * (q_order / M)
    KL = inventory_hold_cost + overhead_impact
    
    total_cost = KF + KL
    return float(total_cost), float(KF), float(KL)

def show_inventory_manager():
    st.header("📦 Strategic Inventory Analyzer")
    
    tab1, tab2 = st.tabs(["📊 Inventory Dashboard", "📈 Excel Optimization (inv.xlsx)"])
    
    with tab1:
        st.subheader("Inventory Segmentation")
        # Εδώ το Dashboard που "δεν εμφάνιζε τίποτα" - Διορθώθηκε η ροή
        default_segments = [
            {"label": "Fast Moving", "val": 300000.0, "qty": 5000, "days": 30},
            {"label": "Standard Flow", "val": 400000.0, "qty": 2500, "days": 45},
            {"label": "Slow Moving", "val": 200000.0, "qty": 800, "days": 75},
            {"label": "Obsolete", "val": 50000.0, "qty": 200, "days": 180},
        ]
        
        inventory_data = []
        c_header = st.columns([2, 1.5, 1, 1])
        c_header[0].write("**Category**")
        c_header[1].write("**Value (€)**")
        c_header[2].write("**Qty**")
        c_header[3].write("**Days**")

        for i, cat in enumerate(default_segments):
            c = st.columns([2, 1.5, 1, 1])
            name = c[0].text_input(f"Cat {i}", cat['label'], key=f"inv_n_{i}", label_visibility="collapsed")
            val = c[1].number_input(f"Val {i}", value=cat['val'], key=f"inv_v_{i}", label_visibility="collapsed")
            qty = c[2].number_input(f"Qty {i}", value=cat['qty'], key=f"inv_q_{i}", label_visibility="collapsed")
            days = c[3].number_input(f"Day {i}", value=cat['days'], key=f"inv_d_{i}", label_visibility="collapsed")
            inventory_data.append({"Category": name, "Value": val, "Quantity": qty, "Days": days})

        df = pd.DataFrame(inventory_data)
        total_v = df["Value"].sum()
        w_dsi = (df["Value"] * df["Days"]).sum() / total_v if total_v > 0 else 0
        
        st.divider()
        m1, m2 = st.columns(2)
        m1.metric("Total Value", f"€ {total_v:,.0f}")
        m2.metric("Weighted DSI", f"{w_dsi:.1f} Days")

    with tab2:
        st.subheader("Excel Model Simulation")
        c1, c2 = st.columns(2)
        with c1:
            M = st.number_input("Annual Needs (M)", value=10000)
            unit_q = st.number_input("Unit Price (q)", value=30.0)
            kf_val = st.number_input("Order Cost (kf)", value=600.0)
            r_val = st.number_input("Discount % (r)", value=0.0) / 100
        with c2:
            st_m = st.number_input("Monthly Storage", value=600.0)
            ins_m = st.number_input("Monthly Insurance", value=150.0)
            int_rate = st.number_input("Interest Rate", value=5.0) / 100

        # Simulation for Optimal q
        q_test = np.arange(100, 5000, 10)
        results = [calculate_excel_logic(q, M, unit_q, r_val, unit_q, st_m, ins_m, int_rate) for q in q_test]
        total_costs = [res[0] for res in results]
        
        best_idx = np.argmin(total_costs)
        best_q = q_test[best_idx]
        best_total = total_costs[best_idx]

        st.success(f"🎯 Optimal Q: {best_q} units | Min Total Cost: €{best_total:,.2f}")
        
        # Chart
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=list(q_test), y=total_costs, name="Total Cost", line=dict(color="#00CC96")))
        fig.update_layout(template="plotly_dark", xaxis_title="Order Quantity (q)", yaxis_title="Total Cost (€)")
        st.plotly_chart(fig, use_container_width=True)

    if st.button("⬅️ Back to Library", key="inv_final_back"):
        st.session_state.selected_tool = None
        st.rerun()
