import streamlit as st
import pandas as pd
import math
import numpy as np
import plotly.graph_objects as go

def show_inventory_manager():
    st.title("📦 Strategic Inventory & Cost Optimizer")
    st.info("Direct Excel Formula Integration (Wilson-Albright Logic)")

    # 1. INPUT SECTION
    with st.sidebar:
        st.header("Excel Parameters (C-Cells)")
        M = st.number_input("Annual Needs (M) [C30]", value=10000.0)
        kf = st.number_input("Order Cost (kf) [C31]", value=600.0)
        unit_p = st.number_input("Unit Price (q) [C29]", value=30.0)
        r_disc = st.number_input("Discount % (r) [C32]", value=0.0) / 100
        
        st.subheader("Overheads & Capital")
        storage_m = st.number_input("Monthly Storage", value=600.0)
        insurance_m = st.number_input("Monthly Insurance", value=150.0)
        interest_rate = st.number_input("Interest Rate (%) [C41]", value=5.0) / 100

    # 2. CALCULATION ENGINE (Exact User Formula)
    # C42 = (Annual Storage + Insurance) / (M * Unit_Price)
    annual_overheads = (storage_m + insurance_m) * 12
    overhead_ratio = annual_overheads / (M * unit_p) # C42 logic

    # The IF Formula provided by user
    if r_disc == 0:
        # SQRT((2*C30*C31)/(C29*(C41+C42)))
        q_opt = math.sqrt((2 * M * kf) / (unit_p * (interest_rate + overhead_ratio)))
    else:
        # SQRT((2*C30*C31)/(C29*(C42+(1-C32)*C41)))
        q_opt = math.sqrt((2 * M * kf) / (unit_p * (overhead_ratio + (1 - r_disc) * interest_rate)))

    num_orders = M / q_opt if q_opt > 0 else 0

    # 3. DASHBOARD METRICS
    st.subheader("1. Strategic Results")
    c1, c2, c3 = st.columns(3)
    c1.metric("Best Quantity (q)", f"{q_opt:,.4f}")
    c2.metric("Orders per Year", f"{num_orders:,.4f}")
    c3.metric("Annual Overheads", f"€{annual_overheads:,.0f}")

    # 4. AUDIT TRAIL (For the "Boss" View)
    st.subheader("2. Formula Audit Table")
    audit_data = {
        "Variable": ["M (Annual Needs)", "kf (Order Cost)", "C41 (Interest)", "C42 (Overhead Ratio)"],
        "Value": [f"{M:,.0f}", f"{kf:,.2f}", f"{interest_rate:.4f}", f"{overhead_ratio:.4f}"]
    }
    st.table(pd.DataFrame(audit_data))

    # 5. COST BREAKDOWN
    st.subheader("3. Total Cost Analysis")
    # KF = (M/q)*kf
    # KL = (q/2) * unit_p * (overhead_ratio + (1-r)*interest_rate)
    KF = (M / q_opt) * kf
    KL = (q_opt / 2) * unit_p * (overhead_ratio + (1 - r_disc) * interest_rate)
    
    col_a, col_b = st.columns(2)
    col_a.write(f"**Annual Ordering Cost (KF):** €{KF:,.2f}")
    col_b.write(f"**Annual Holding Cost (KL):** €{KL:,.2f}")
    
    # 6. VISUALIZATION
    q_range = np.linspace(q_opt*0.5, q_opt*2, 100)
    kf_curve = [(M / q) * kf for q in q_range]
    kl_curve = [(q / 2) * unit_p * (overhead_ratio + (1 - r_disc) * interest_rate) for q in q_range]
    total_curve = [f + l for f, l in zip(kf_curve, kl_curve)]

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=q_range, y=total_curve, name="Total Cost (K)", line=dict(color="gold", width=4)))
    fig.add_trace(go.Scatter(x=q_range, y=kf_curve, name="Ordering (KF)", line=dict(dash="dash")))
    fig.add_trace(go.Scatter(x=q_range, y=kl_curve, name="Holding (KL)", line=dict(dash="dash")))
    fig.update_layout(template="plotly_dark", xaxis_title="Order Quantity", yaxis_title="€")
    st.plotly_chart(fig, use_container_width=True)

    if st.button("⬅️ Back to Library"):
        st.session_state.selected_tool = None
        st.rerun()
