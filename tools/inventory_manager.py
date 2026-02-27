import streamlit as st
import pandas as pd
import math
import numpy as np
import plotly.graph_objects as go
from core.sync import sync_global_state

def show_inventory_manager():
    # 1. SYNC WITH GLOBAL BASELINE
    metrics = sync_global_state()
    s = st.session_state
    
    # Auto-fetch from Stage 0 (Direct Excel-style Integration)
    # Unit Price (q) from Stage 0 variable costs
    sys_unit_p = float(s.get('variable_cost', 30.0))
    # Annual Needs (M) derived from Volume
    sys_m = float(s.get('volume', 10000.0))
    # Interest Rate linked to WACC or specific lending rate
    sys_interest = float(s.get('wacc', 0.05))

    st.title("📦 Strategic Inventory Optimizer")
    st.info("EOQ Logic: Balancing Ordering Costs vs. Holding Costs to maximize liquidity.")

    # 2. DATA ENTRY SECTION
    st.subheader("1. Input Parameters")
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 🔒 Locked Baseline Constants")
        M = st.number_input("Annual Needs (M)", value=sys_m, disabled=True, format="%.2f")
        unit_p = st.number_input("Unit Price (q)", value=sys_unit_p, disabled=True, format="%.2f")
        interest_rate = st.number_input("Annual Cost of Capital (%)", value=sys_interest * 100, disabled=True) / 100
        
    with col2:
        st.markdown("### ⚙️ Operational Variables")
        kf = st.number_input("Cost per Order (kf)", value=600.0, format="%.2f", help="Administrative and shipping costs per order.")
        r_disc = st.number_input("Supplier Discount % (r)", value=0.0, step=0.1) / 100
        storage_m = st.number_input("Monthly Storage/Rent (€)", value=600.0, format="%.2f")
        insurance_m = st.number_input("Monthly Insurance (€)", value=150.0, format="%.2f")

    # 3. CALCULATION ENGINE (365-day context)
    annual_overheads = (storage_m + insurance_m) * 12
    # The overhead ratio is critical for the KL (Holding Cost) calculation
    overhead_ratio = annual_overheads / (M * unit_p) if (M * unit_p) > 0 else 0

    # EOQ Formula Implementation
    if r_disc == 0:
        q_opt = math.sqrt((2 * M * kf) / (unit_p * (interest_rate + overhead_ratio)))
    else:
        q_opt = math.sqrt((2 * M * kf) / (unit_p * (overhead_ratio + (1 - r_disc) * interest_rate)))

    num_orders = M / q_opt if q_opt > 0 else 0
    days_between_orders = 365 / num_orders if num_orders > 0 else 0

    # 4. OUTPUT DASHBOARD
    st.divider()
    st.subheader("2. Optimization Results")
    
    m1, m2, m3 = st.columns(3)
    m1.metric("Optimal Order Quantity (EOQ)", f"{q_opt:,.0f} units")
    m2.metric("Orders per Year", f"{num_orders:,.1f}")
    m3.metric("Order Every", f"{days_between_orders:,.0f} Days")

    # 5. COST BREAKDOWN
    st.subheader("3. Audit Trail & Annual Cost Breakdown")
    
    KF = (M / q_opt) * kf if q_opt > 0 else 0
    KL = (q_opt / 2) * unit_p * (overhead_ratio + (1 - r_disc) * interest_rate)
    
    audit_df = pd.DataFrame({
        "Cost Component": ["Total Ordering Costs (KF)", "Total Holding Costs (KL)", "Total Inventory Logistics Cost"],
        "Annual Result (€)": [f"{KF:,.2f}", f"{KL:,.2f}", f"{(KF + KL):,.2f}"]
    })
    st.table(audit_df)

    # 6. VISUALIZATION
    
    st.subheader("4. Cost Sensitivity Curve")
    q_range = np.linspace(q_opt * 0.3, q_opt * 2.5, 100)
    kf_curve = [(M / q) * kf for q in q_range]
    kl_curve = [(q / 2) * unit_p * (overhead_ratio + (1 - r_disc) * interest_rate) for q in q_range]
    total_curve = [f + l for f, l in zip(kf_curve, kl_curve)]

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=q_range, y=total_curve, name="Total Annual Cost", line=dict(color="#00CC96", width=4)))
    fig.add_trace(go.Scatter(x=q_range, y=kf_curve, name="Ordering Cost (Decreasing)", line=dict(dash="dash", color="cyan")))
    fig.add_trace(go.Scatter(x=q_range, y=kl_curve, name="Holding Cost (Increasing)", line=dict(dash="dash", color="magenta")))
    
    fig.add_vline(x=q_opt, line_dash="dot", line_color="orange", annotation_text="EOQ POINT")
    fig.update_layout(template="plotly_dark", xaxis_title="Order Quantity (Units)", yaxis_title="Cost (€)")
    st.plotly_chart(fig, use_container_width=True)

    # 7. SYNC TO GLOBAL STATE (Updating DIO)
    st.divider()
    if st.button("🚀 Sync Inventory Policy with Global Strategy", type="primary", use_container_width=True):
        # Update Days Inventory Outstanding (DIO) based on EOQ
        # Average Inventory = q_opt / 2. DIO = (Avg Inv / M) * 365
        new_dio = ((q_opt / 2) / M) * 365 if M > 0 else 0
        st.session_state.inventory_days = int(new_dio)
        st.success(f"Global Baseline Updated: Inventory Days (DIO) set to {int(new_dio)} based on EOQ.")
        st.rerun()

    if st.button("⬅️ Back to Library"):
        st.session_state.selected_tool = None
        st.rerun()
