import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from core.engine import compute_core_metrics

def show_inventory_manager():
    st.header("📦 Strategic Inventory Analyzer")
    st.info("Note: For Cash Cycle calculations, weighting is performed strictly by Value (€).")
    
    # 1. SEGMENTATION DATA ENTRY
    st.subheader("1. ERP Inventory Data")
    
    # Pre-defined segments for ease of use
    default_segments = [
        {"label": "Fast Moving", "val": 300000.0, "days": 30},
        {"label": "Standard Flow", "val": 400000.0, "days": 45},
        {"label": "Slow Moving", "val": 200000.0, "days": 75},
        {"label": "Obsolete/Dead Stock", "val": 50000.0, "days": 180},
    ]

    inventory_data = []
    cols = st.columns([2, 2, 1])
    cols[0].write("**Segment Description**")
    cols[1].write("**Total Value (€)**")
    cols[2].write("**Inventory Days**")

    for i, cat in enumerate(default_segments):
        c = st.columns([2, 2, 1])
        name = c[0].text_input(f"Name {i}", cat['label'], key=f"inv_n_{i}", label_visibility="collapsed")
        val = c[1].number_input(f"Value {i}", value=cat['val'], key=f"inv_v_{i}", label_visibility="collapsed")
        days = c[2].number_input(f"Days {i}", value=cat['days'], key=f"inv_d_{i}", label_visibility="collapsed")
        inventory_data.append({"Category": name, "Value": val, "Days": days})

    # 2. STRATEGIC WEIGHTING (BY VALUE)
    df = pd.DataFrame(inventory_data)
    total_val = df["Value"].sum()
    
    # Weighted Average DSI - The critical input for Cash Cycle
    weighted_dsi = (df["Value"] * df["Days"]).sum() / total_val if total_val > 0 else 0
    
    # Save to session_state to be picked up by Cash Cycle Tool
    st.session_state.global_inventory_dsi = weighted_dsi
    st.session_state.inventory_value = total_val

    st.divider()

    # 3. OUTPUT METRICS
    m1, m2, m3 = st.columns(3)
    m1.metric("Total Inventory Value", f"€ {total_val:,.0f}")
    m2.metric("Weighted Avg DSI", f"{weighted_dsi:.1f} Days", help="This value is used in Cash Cycle calculations.")
    m3.metric("Capital Pressure Index", f"{(weighted_dsi/365*100):.1f}%", help="Percentage of the year capital is trapped.")

    

    # 4. PARETO IMPACT (VALUE x DAYS)
    st.subheader("2. Financial Friction (Pareto Analysis)")
    df["Financial_Friction"] = df["Value"] * df["Days"]
    df["Friction_Share"] = (df["Financial_Friction"] / df["Financial_Friction"].sum() * 100) if total_val > 0 else 0
    
    fig = go.Figure(go.Bar(
        x=df["Category"],
        y=df["Friction_Share"],
        marker_color=['#EF553B' if x == df["Friction_Share"].max() else '#00CC96' for x in df["Friction_Share"]],
        text=[f"{x:.1f}%" for x in df["Friction_Share"]],
        textposition='auto',
    ))
    fig.update_layout(title="Capital Pressure Share by Segment", template="plotly_dark", yaxis_title="% Contribution to Cash Delay")
    st.plotly_chart(fig, use_container_width=True)

    # 5. CASH CYCLE INTEGRATION STATUS
    st.subheader("3. Integration Status")
    if 'global_inventory_dsi' in st.session_state:
        st.success(f"✔️ Weighted DSI ({weighted_dsi:.1f} days) is now linked to the Cash Cycle Calculator.")
    
    # Cold Analytical Insight
    wacc = compute_core_metrics().get('wacc', 0.15)
    annual_cost = total_val * wacc
    st.warning(f"**Strategic Note:** Holding this inventory costs **€ {annual_cost:,.2f}** per year in capital cost alone. Reducing the DSI by 10 days would improve NPV by approximately **€ {(total_val/365 * 10 * wacc):,.2f}**.")

if __name__ == "__main__":
    show_inventory_manager()
