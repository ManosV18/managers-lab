import streamlit as st
import pandas as pd
import math
import numpy as np
import plotly.graph_objects as go

def calculate_eoq_excel(M, kf, unit_price, r_disc, storage_monthly, insurance_monthly, interest_rate):
    # Μετατροπή σε ετήσια βάση για να συμβαδίζουν οι μονάδες
    annual_storage = storage_monthly * 12
    annual_insurance = insurance_monthly * 12
    
    # Ο τύπος σου από το Excel (C32=r, C30=M, C31=kf, C29=unit_price, C41=interest, C42=fixed_costs_ratio)
    # Στο Excel σου το C42 φαίνεται να είναι το (Annual Storage + Insurance) / M
    fixed_overhead_unit = (annual_storage + annual_insurance) / M
    
    if r_disc == 0:
        # SQRT((2 * M * kf) / (unit_price * (interest_rate + fixed_overhead_unit)))
        q_opt = math.sqrt((2 * M * kf) / (unit_price * (interest_rate + fixed_overhead_unit)))
    else:
        # SQRT((2 * M * kf) / (unit_price * (fixed_overhead_unit + (1 - r_disc) * interest_rate)))
        q_opt = math.sqrt((2 * M * kf) / (unit_price * (fixed_overhead_unit + (1 - r_disc) * interest_rate)))
    
    return q_opt

def show_inventory_manager():
    st.title("📦 Strategic Inventory Optimizer (EOQ Model)")
    
    st.subheader("1. Parameters from Excel (inv.xlsx)")
    col1, col2 = st.columns(2)
    
    with col1:
        M = st.number_input("Annual Needs (M)", value=10000.0)
        unit_p = st.number_input("Unit Price (q)", value=30.0)
        kf = st.number_input("Order Cost (kf)", value=600.0)
    with col2:
        r = st.number_input("Discount % (r)", value=0.0) / 100
        storage = st.number_input("Monthly Storage", value=600.0)
        insurance = st.number_input("Monthly Insurance", value=150.0)
        interest = st.number_input("Annual Interest Rate (%)", value=5.0) / 100

    # 2. Calculation using your exact IF formula
    q_opt = calculate_eoq_excel(M, kf, unit_p, r, storage, insurance, interest)
    
    # 3. Validation Audit (Detailed Costing for the Optimal Q)
    # KF = (M/q) * kf
    kf_total = (M / q_opt) * kf
    # KL = (q/2 * unit_p * (1-r) * interest) + (Annual_Overheads * q/M)
    annual_overheads = (storage + insurance) * 12
    kl_total = (q_opt / 2 * unit_p * (1 - r) * interest) + (annual_overheads * q_opt / M)
    total_k = kf_total + kl_total

    st.divider()
    
    # Executive Results
    res_col1, res_col2, res_col3 = st.columns(3)
    res_col1.metric("Optimal Order Quantity (q)", f"{int(q_opt)} units")
    res_col2.metric("Min Total Cost (K)", f"€ {total_k:,.2f}")
    res_col3.metric("Annual Order Freq", f"{M/q_opt:.1f} orders")

    # 4. Detailed Audit Table
    st.subheader("2. Detailed Audit Trail (Validation)")
    audit_df = pd.DataFrame({
        "Metric": ["Fixed Ordering Cost (KF)", "Holding & Interest (KL)", "Total Cost (K)"],
        "Excel Formula Logic": ["(M/q)*kf", "(q/2*u*i) + (OH*q/M)", "KF + KL"],
        "Value (€)": [f"{kf_total:,.2f}", f"{kl_total:,.2f}", f"{total_k:,.2f}"]
    })
    st.table(audit_df)

    # 5. Sensitivity Analysis Chart
    st.subheader("3. Cost Trade-off Visualization")
    q_range = np.arange(max(100, int(q_opt*0.5)), int(q_opt*2), 10)
    
    kf_curve = [(M / q) * kf for q in q_range]
    kl_curve = [(q / 2 * unit_p * (1 - r) * interest) + (annual_overheads * q / M) for q in q_range]
    total_curve = [f + l for f, l in zip(kf_curve, kl_curve)]

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=list(q_range), y=total_curve, name="Total Cost (K)", line=dict(color="gold", width=4)))
    fig.add_trace(go.Scatter(x=list(q_range), y=kf_curve, name="Ordering Cost (KF)", line=dict(color="cyan", dash="dash")))
    fig.add_trace(go.Scatter(x=list(q_range), y=kl_curve, name="Holding Cost (KL)", line=dict(color="magenta", dash="dash")))
    
    fig.add_vline(x=q_opt, line_dash="dot", line_color="white", annotation_text="EOQ Point")
    fig.update_layout(template="plotly_dark", xaxis_title="Order Quantity", yaxis_title="Annual Cost (€)")
    st.plotly_chart(fig, use_container_width=True)

    if st.button("⬅️ Back to Library"):
        st.session_state.selected_tool = None
        st.rerun()
