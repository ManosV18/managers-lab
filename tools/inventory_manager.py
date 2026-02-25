import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from core.engine import compute_core_metrics

def show_inventory_manager():
    st.header("📦 Inventory Strategic Control & Segmentation")
    st.info("Analyze inventory efficiency by segment and calculate the cost of trapped capital.")

    # 1. FETCH GLOBAL METRICS
    metrics = compute_core_metrics()
    wacc = metrics.get('wacc', 0.15)
    
    # Get COGS from session state
    v = st.session_state.get('volume', 0)
    vc = st.session_state.get('variable_cost', 0.0)
    annual_cogs = v * vc

    # 2. INVENTORY SEGMENTATION (A-D or by Type)
    st.subheader("1. Inventory Portfolio Segmentation")
    
    default_segments = [
        {"Type": "Raw Materials", "Value": annual_cogs * 0.05, "Days": 30},
        {"Type": "Work in Progress", "Value": annual_cogs * 0.03, "Days": 15},
        {"Type": "Finished Goods (Fast)", "Value": annual_cogs * 0.07, "Days": 45},
        {"Type": "Finished Goods (Slow/Obsolete)", "Value": annual_cogs * 0.02, "Days": 180},
    ]

    seg_data = []
    cols = st.columns([2, 2, 1])
    cols[0].write("**Inventory Category**")
    cols[1].write("**Current Value (€)**")
    cols[2].write("**Days in Stock (DSI)**")

    for i, s in enumerate(default_segments):
        c = st.columns([2, 2, 1])
        name = c[0].text_input(f"Cat {i}", s['Type'], key=f"inv_n_{i}", label_visibility="collapsed")
        val = c[1].number_input(f"Val {i}", value=float(s['Value']), key=f"inv_v_{i}", label_visibility="collapsed")
        days = c[2].number_input(f"Days {i}", value=int(s['Days']), key=f"inv_d_{i}", label_visibility="collapsed")
        seg_data.append({"Category": name, "Value": val, "Days": days})

    # Global Calculations from Segmentation
    total_inventory_value = sum(d["Value"] for d in seg_data)
    
    # Weighted Average Days Sales in Inventory (DSI)
    if total_inventory_value > 0:
        weighted_dsi = sum(d["Value"] * d["Days"] for d in seg_data) / total_inventory_value
    else:
        weighted_dsi = 0
    
    inventory_turnover = annual_cogs / total_inventory_value if total_inventory_value > 0 else 0

    st.divider()
    
    # 3. EFFICIENCY METRICS
    m1, m2, m3 = st.columns(3)
    m1.metric("Total Inventory Value", f"€ {total_inventory_value:,.2f}")
    m2.metric("Weighted Avg DSI", f"{weighted_dsi:.1f} Days")
    m3.metric("Inventory Turnover", f"{inventory_turnover:.2f}x")

    

    # 4. FINANCIAL CARRYING COST (The "Bleed" Rate)
    st.subheader("2. Carrying Cost Analysis (WACC Based)")
    
    col_l, col_r = st.columns(2)
    other_holding_costs = col_l.slider("Additional Holding Costs % (Storage, Insurance, Obsolescence)", 0.0, 20.0, 5.0) / 100
    total_carrying_rate = wacc + other_holding_costs
    
    annual_carrying_cost = total_inventory_value * total_carrying_rate
    daily_bleed = annual_carrying_cost / 365

    st.warning(f"**Financial Bleed:** Your inventory is costing you **€ {daily_bleed:,.2f} per day** in interest and holding expenses.")

    # 5. OPTIMIZATION SIMULATOR
    st.subheader("3. Strategic Optimization Simulator")
    
    target_reduction = st.slider("Target Inventory Reduction (%)", 0, 50, 15)
    
    cash_released = total_inventory_value * (target_reduction / 100)
    annual_savings = cash_released * total_carrying_rate
    
    st.success(f"""
        **Optimization Result:**
        - **Cash Released to Balance Sheet:** € {cash_released:,.2f}
        - **Permanent Annual Cost Savings:** € {annual_savings:,.2f}
        - **New Target DSI:** {weighted_dsi * (1 - target_reduction/100):.1f} Days
    """)

    # Visual Chart: Value Distribution
    fig = go.Figure(data=[go.Pie(labels=[d["Category"] for d in seg_data], 
                                 values=[d["Value"] for d in seg_data], 
                                 hole=.4,
                                 marker_colors=["#00CC96", "#636EFA", "#EF553B", "#AB63FA"])])
    fig.update_layout(title="Inventory Value Distribution", template="plotly_dark", height=400)
    st.plotly_chart(fig, use_container_width=True)
