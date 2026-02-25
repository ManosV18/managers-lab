import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go

def calculate_excel_logic(q_order, M, kf, r_disc, unit_price, storage_monthly, insurance_monthly, interest_rate):
    # 1. Κόστος Εμπορεύματος (KV)
    KV = M * unit_price * (1 - r_disc)
    
    # 2. Σταθερό Κόστος Προμηθειών (KF)
    # Φόρμουλα Excel: (M/q) * kf
    KF = (M / q_order) * kf
    
    # 3. Κόστος Αποθήκευσης και Τόκων (KL)
    # Excel Logic: (q/2 * unit_price * (1-r) * interest) + (Storage_Annual + Insurance_Annual) * (q/M)
    annual_storage = storage_monthly * 12
    annual_insurance = insurance_monthly * 12
    
    inventory_hold_cost = (q_order / 2) * unit_price * (1 - r_disc) * interest_rate
    overhead_impact = (annual_storage + annual_insurance) * (q_order / M)
    KL = inventory_hold_cost + overhead_impact
    
    # 4. Συνολικό Κόστος (K) - Σύμφωνα με το Excel είναι KF + KL (το KV είναι το κόστος αγοράς)
    K = KF + KL
    
    return {
        "q": q_order,
        "KF": float(KF),
        "KL": float(KL),
        "KV": float(KV),
        "K_Total": float(K)
    }

def show_inventory_manager():
    st.title("📦 Strategic Inventory & Cost Optimizer")
    
    # Inputs Section
    st.subheader("1. Excel Parameters Input")
    col1, col2 = st.columns(2)
    
    with col1:
        M = st.number_input("Annual Needs (M)", value=10000.0, step=100.0)
        unit_q = st.number_input("Unit Price (q)", value=30.0, step=1.0)
        kf_val = st.number_input("Order Cost per Order (kf)", value=600.0, step=10.0)
        r_val = st.number_input("Discount % (r)", value=0.0, step=0.1) / 100
    
    with col2:
        st_m = st.number_input("Monthly Storage Costs", value=600.0, step=50.0)
        ins_m = st.number_input("Monthly Insurance", value=150.0, step=10.0)
        int_rate = st.number_input("Annual Interest Rate (%)", value=5.0, step=0.5) / 100
        q_selected = st.slider("Select Order Quantity (q) for Detail Analysis", 100, 5000, 2230)

    # 2. Detailed Calculation Table (The "Boss" View)
    res_detail = calculate_excel_logic(q_selected, M, kf_val, r_val, unit_q, st_m, ins_m, int_rate)
    
    st.subheader("2. Detailed Step-by-Step Calculation (Audit)")
    
    audit_data = {
        "Description": [
            "Order Quantity (q)",
            "Fixed Ordering Costs (KF)",
            "Holding & Interest Costs (KL)",
            "Total Procurement Cost (K = KF + KL)",
            "Inventory Purchase Cost (KV)"
        ],
        "Formula": [
            "Input",
            "(M/q) * kf",
            "(q/2 * unit_price * (1-r) * interest) + (Overheads * q/M)",
            "KF + KL",
            "M * unit_price * (1-r)"
        ],
        "Result (€)": [
            f"{res_detail['q']}",
            f"{res_detail['KF']:,.2f}",
            f"{res_detail['KL']:,.2f}",
            f"{res_detail['K_Total']:,.2f}",
            f"{res_detail['KV']:,.2f}"
        ]
    }
    st.table(pd.DataFrame(audit_data))

    # 3. Simulation for Optimal Point
    q_range = np.arange(500, 5001, 10)
    sim_results = [calculate_excel_logic(q, M, kf_val, r_val, unit_q, st_m, ins_m, int_rate) for q in q_range]
    
    costs_total = [r['K_Total'] for r in sim_results]
    best_idx = np.argmin(costs_total)
    best_q = q_range[best_idx]
    best_cost = costs_total[best_idx]

    st.divider()
    st.success(f"🎯 **Optimal Result:** Order **{int(best_q)} units** to minimize total costs at **€{best_cost:,.2f}**")

    # 4. Optimization Chart
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=list(q_range), y=costs_total, name="Total Cost (K)", line=dict(color="#00CC96", width=3)))
    fig.add_trace(go.Scatter(x=list(q_range), y=[r['KF'] for r in sim_results], name="Ordering Cost (KF)", line=dict(dash='dash')))
    fig.add_trace(go.Scatter(x=list(q_range), y=[r['KL'] for r in sim_results], name="Holding Cost (KL)", line=dict(dash='dash')))
    
    fig.add_vline(x=best_q, line_dash="dot", line_color="orange", annotation_text="Optimal Q")
    
    fig.update_layout(template="plotly_dark", xaxis_title="Order Quantity (q)", yaxis_title="Cost (€)", height=500)
    st.plotly_chart(fig, use_container_width=True)

    if st.button("⬅️ Back to Library Hub"):
        st.session_state.selected_tool = None
        st.rerun()
