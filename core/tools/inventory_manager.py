import streamlit as st
import pandas as pd
import math
import numpy as np
import plotly.graph_objects as go

def show_inventory_manager():
    st.header("📦 Strategic Inventory Optimizer")
    st.info("Analytical EOQ Model: Balancing Ordering Costs against Capital Holding Costs.")

    # 1. DATA ENTRY SECTION
    # Σύνδεση με το παγκόσμιο WACC και τα AR Days (ως proxy για inventory days αν χρειαστεί)
    s = st.session_state
    sys_wacc = float(s.get('wacc', 0.15))
    sys_revenue = float(s.get('price', 100) * s.get('volume', 1000))

    st.subheader("1. Input Parameters")
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**Supply Chain Data**")
        # Χρησιμοποιούμε το Volume από το κεντρικό Dashboard ως default Demand
        M = st.number_input("Annual Demand (Units)", value=float(s.get('volume', 10000.0)), format="%.2f")
        kf = st.number_input("Cost per Order ($)", value=600.0, format="%.2f")
        unit_p = st.number_input("Unit Purchase Price ($)", value=float(s.get('variable_cost', 30.0)), format="%.2f")
        r_disc = st.number_input("Discount % (r)", value=0.0, step=0.1) / 100

    with col2:
        st.markdown("**Carrying Costs**")
        storage_m = st.number_input("Monthly Storage/Rent ($)", value=600.0, format="%.2f")
        insurance_m = st.number_input("Monthly Insurance ($)", value=150.0, format="%.2f")
        # Το WACC έρχεται αυτόματα από το WACC Optimizer
        interest_rate = st.number_input("Annual WACC/Interest (%)", value=sys_wacc * 100, step=0.1) / 100

    # 2. CALCULATION ENGINE (Analytical Approach)
    annual_overheads = (storage_m + insurance_m) * 12
    # Overhead ratio relative to total inventory value
    overhead_ratio = annual_overheads / (M * unit_p) if M > 0 else 0

    # EOQ Formula 
    if r_disc == 0:
        q_opt = math.sqrt((2 * M * kf) / (unit_p * (interest_rate + overhead_ratio)))
    else:
        q_opt = math.sqrt((2 * M * kf) / (unit_p * (overhead_ratio + (1 - r_disc) * interest_rate)))

    num_orders = M / q_opt if q_opt > 0 else 0

    # 3. OUTPUT DASHBOARD
    st.divider()
    st.subheader("2. Optimization Results")
    
    m1, m2, m3 = st.columns(3)
    m1.metric("Economic Order Quantity (q)", f"{q_opt:,.0f} Units")
    m2.metric("Orders per Year", f"{num_orders:,.2f}")
    m3.metric("Holding Cost Ratio", f"{overhead_ratio:.4%}")

    # 4. AUDIT TABLE (Financial Breakdown)
    st.subheader("3. Annual Cost Breakdown")
    
    KF = (M / q_opt) * kf if q_opt > 0 else 0
    KL = (q_opt / 2) * unit_p * (overhead_ratio + (1 - r_disc) * interest_rate)
    
    audit_df = pd.DataFrame({
        "Cost Component": ["Total Ordering Costs (Fixed)", "Total Holding Costs (Variable)", "Total Optimization Cost"],
        "Annual Amount ($)": [f"$ {KF:,.2f}", f"$ {KL:,.2f}", f"$ {(KF + KL):,.2f}"]
    })
    st.table(audit_df)

    # 5. VISUALIZATION (Sensitivity Curve)
    st.subheader("4. Cost Sensitivity Curve")
    
    if q_opt > 0:
        q_range = np.linspace(q_opt * 0.3, q_opt * 2.5, 100)
        kf_curve = [(M / q) * kf for q in q_range]
        kl_curve = [(q / 2) * unit_p * (overhead_ratio + (1 - r_disc) * interest_rate) for q in q_range]
        total_curve = [f + l for f, l in zip(kf_curve, kl_curve)]

        fig = go.Figure()
        fig.add_trace(go.Scatter(x=q_range, y=total_curve, name="Total Annual Cost", line=dict(color="#1E3A8A", width=4)))
        fig.add_trace(go.Scatter(x=q_range, y=kf_curve, name="Ordering Cost", line=dict(dash="dot", color="#64748b")))
        fig.add_trace(go.Scatter(x=q_range, y=kl_curve, name="Holding Cost", line=dict(dash="dot", color="#ef4444")))
        
        fig.add_vline(x=q_opt, line_dash="dash", line_color="orange", annotation_text="Optimal (EOQ)")
        fig.update_layout(height=400, template="plotly_dark", xaxis_title="Order Quantity (Units)", yaxis_title="Annual Cost ($)", margin=dict(l=20, r=20, t=20, b=20))
        st.plotly_chart(fig, use_container_width=True)

    # 6. VERDICT
    st.subheader("💡 Strategic Verdict")
    st.success(f"To minimize value destruction, the system should place **{num_orders:.1f} orders** per year of **{q_opt:,.0f} units** each.")

    # 7. NAVIGATION (Συγχρονισμένο με το app.py)
    st.divider()
    if st.button("⬅️ Back to Control Tower", use_container_width=True):
        st.session_state.flow_step = "home"
        st.session_state.selected_tool = None
        st.rerun()
