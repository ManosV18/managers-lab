import streamlit as st
import pandas as pd
import math
import numpy as np
import plotly.graph_objects as go

def show_inventory_manager():
    st.title("📦 Strategic Inventory Optimizer")
    st.info("Direct Excel Integration: Validation for Best Quantity and Order Frequency.")

    # 1. DATA ENTRY SECTION (Aligned with Excel Cells)
    st.subheader("1. Input Parameters")
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**Core Order Data**")
        M = st.number_input("Annual Needs (M) - [C30]", value=10000.0, format="%.2f")
        kf = st.number_input("Order Cost (kf) - [C31]", value=600.0, format="%.2f")
        unit_p = st.number_input("Unit Price (q) - [C29]", value=30.0, format="%.2f")
        r_disc = st.number_input("Discount % (r) - [C32]", value=0.0, step=0.1) / 100

    with col2:
        st.markdown("**Holding & Capital Costs**")
        storage_m = st.number_input("Monthly Storage/Rent", value=600.0, format="%.2f")
        insurance_m = st.number_input("Monthly Insurance", value=150.0, format="%.2f")
        interest_rate = st.number_input("Annual Interest Rate (%) - [C41]", value=5.0, step=0.1) / 100

    # 2. CALCULATION ENGINE (The exact IF logic)
    # C42 Calculation: Total Overheads / (M * Unit Price)
    annual_overheads = (storage_m + insurance_m) * 12
    overhead_ratio = annual_overheads / (M * unit_p)

    # Applying the user formula
    if r_disc == 0:
        q_opt = math.sqrt((2 * M * kf) / (unit_p * (interest_rate + overhead_ratio)))
    else:
        q_opt = math.sqrt((2 * M * kf) / (unit_p * (overhead_ratio + (1 - r_disc) * interest_rate)))

    num_orders = M / q_opt if q_opt > 0 else 0

    # 3. OUTPUT DASHBOARD
    st.divider()
    st.subheader("2. Optimization Results")
    
    m1, m2, m3 = st.columns(3)
    m1.metric("Best Quantity (q)", f"{q_opt:,.4f}")
    m2.metric("Orders per Year", f"{num_orders:,.4f}")
    m3.metric("Overhead Ratio (C42)", f"{overhead_ratio:.6f}")

    # 4. AUDIT TABLE (Step-by-Step validation)
    st.subheader("3. Audit Trail & Cost Breakdown")
    
    # Calculate costs at optimal point
    KF = (M / q_opt) * kf
    KL = (q_opt / 2) * unit_p * (overhead_ratio + (1 - r_disc) * interest_rate)
    
    audit_df = pd.DataFrame({
        "Component": ["Ordering Cost (KF)", "Holding Cost (KL)", "Total Annual Cost (K)"],
        "Excel Result (€)": [f"{KF:,.4f}", f"{KL:,.4f}", f"{(KF + KL):,.4f}"],
        "Formula Logic": ["(M/q)*kf", "(q/2)*u*(C42+(1-r)*i)", "KF + KL"]
    })
    st.table(audit_df)

    # 5. VISUALIZATION
    st.subheader("4. Cost Sensitivity Curve")
    q_range = np.linspace(q_opt * 0.4, q_opt * 1.8, 100)
    kf_curve = [(M / q) * kf for q in q_range]
    kl_curve = [(q / 2) * unit_p * (overhead_ratio + (1 - r_disc) * interest_rate) for q in q_range]
    total_curve = [f + l for f, l in zip(kf_curve, kl_curve)]

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=q_range, y=total_curve, name="Total Cost", line=dict(color="#00CC96", width=3)))
    fig.add_trace(go.Scatter(x=q_range, y=kf_curve, name="Ordering Cost", line=dict(dash="dash", color="cyan")))
    fig.add_trace(go.Scatter(x=q_range, y=kl_curve, name="Holding Cost", line=dict(dash="dash", color="magenta")))
    
    fig.add_vline(x=q_opt, line_dash="dot", line_color="orange", annotation_text="EOQ Point")
    fig.update_layout(template="plotly_dark", xaxis_title="Order Quantity (q)", yaxis_title="Annual Cost (€)")
    st.plotly_chart(fig, use_container_width=True)

    if st.button("⬅️ Back to Library"):
        st.session_state.selected_tool = None
        st.rerun()
