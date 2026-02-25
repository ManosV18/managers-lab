import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from core.engine import compute_core_metrics

def show_inventory_manager():
    st.header("📦 Strategic Inventory Analyzer")
    st.markdown("---")
    
    # 1. CORE LOGIC: USER-DEFINED SEGMENTATION
    st.subheader("1. Inventory Segments (Data from ERP)")
    st.write("Input the inventory value and collection days for each category as reported in your accounting system.")

    # User choice for sorting/evaluation
    eval_basis = st.radio("Evaluation Basis:", ["By Value (€)", "By Quantity / Volume"], horizontal=True)

    # Categories based on your input
    categories = [
        {"label": "Fast Moving (e.g. 30 days)", "val": 300000.0, "days": 30},
        {"label": "Standard Flow (e.g. 45 days)", "val": 400000.0, "days": 45},
        {"label": "Slow Flow (e.g. 70 days)", "val": 200000.0, "days": 70},
        {"label": "Non-Moving/Obsolete (e.g. 170 days)", "val": 50000.0, "days": 170},
    ]

    inventory_data = []
    cols = st.columns([2, 2, 1])
    cols[0].write("**Segment Description**")
    cols[1].write(f"**Total {eval_basis}**")
    cols[2].write("**Days in Stock**")

    for i, cat in enumerate(categories):
        c = st.columns([2, 2, 1])
        name = c[0].text_input(f"Name {i}", cat['label'], key=f"inv_name_{i}", label_visibility="collapsed")
        val = c[1].number_input(f"Value {i}", value=cat['val'], key=f"inv_val_{i}", label_visibility="collapsed")
        days = c[2].number_input(f"Days {i}", value=cat['days'], key=f"inv_days_{i}", label_visibility="collapsed")
        inventory_data.append({"Category": name, "Value": val, "Days": days})

    # 2. STRATEGIC CALCULATIONS
    df = pd.DataFrame(inventory_data)
    total_val = df["Value"].sum()
    
    # Weighted Average DSO (DSI) - This is the "Master Average" you mentioned
    weighted_dsi = (df["Value"] * df["Days"]).sum() / total_val if total_val > 0 else 0
    
    # Pareto Logic: Find which segment "hurts" most (Value * Days)
    df["Financial_Impact"] = df["Value"] * df["Days"]
    df["Impact_Share"] = (df["Financial_Impact"] / df["Financial_Impact"].sum() * 100) if total_val > 0 else 0
    
    st.divider()

    # 3. EXECUTIVE DASHBOARD
    m1, m2, m3 = st.columns(3)
    m1.metric(f"Total Portfolio ({eval_basis})", f"{total_val:,.0f}")
    m2.metric("Weighted Average DSI", f"{weighted_dsi:.1f} Days")
    m3.metric("Critical Segment", df.loc[df['Impact_Share'].idxmax()]['Category'] if total_val > 0 else "N/A")

    # Save to session state for use in other functions/tools
    st.session_state.global_inventory_dsi = weighted_dsi
    st.session_state.global_inventory_value = total_val

    # 4. PARETO VISUALIZATION (Which segment traps most capital?)
    st.subheader("2. Financial Impact Analysis (Pareto)")
    
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=df["Category"],
        y=df["Impact_Share"],
        marker_color=['#EF553B' if x == df["Impact_Share"].max() else '#636EFA' for x in df["Impact_Share"]],
        text=[f"{x:.1f}%" for x in df["Impact_Share"]],
        textposition='auto',
    ))
    
    fig.update_layout(
        title=f"Percentage of Capital Pressure by Segment ({eval_basis} × Days)",
        xaxis_title="Inventory Segment",
        yaxis_title="% of Financial Pressure",
        template="plotly_dark",
        height=400
    )
    st.plotly_chart(fig, use_container_width=True)

    

    # 5. COLD ANALYTICAL VERDICT
    st.subheader("3. Analytical Verdict")
    wacc = compute_core_metrics().get('wacc', 0.15)
    daily_cost = (total_val * wacc) / 365
    
    st.warning(f"""
        **Insight:** Your weighted average DSI of **{weighted_dsi:.1f} days** represents a daily opportunity cost of **€ {daily_cost:,.2f}**. 
        The **{df.loc[df['Impact_Share'].idxmax()]['Category']}** segment is your primary source of cash flow friction, responsible for **{df['Impact_Share'].max():.1f}%** of your inventory-related capital pressure.
    """)

if __name__ == "__main__":
    show_inventory_manager()
