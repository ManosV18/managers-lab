import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from core.engine import compute_core_metrics

def show_inventory_manager():
    st.header("📦 Strategic Inventory Analyzer")
    
    # Warning for Cash Cycle Integration
    st.warning("⚠️ **Important:** While you can track Quantity for logistics, the **Cash Cycle** requires **Total Value (€)** to calculate financial impact correctly.")
    
    # 1. SEGMENTATION DATA ENTRY
    st.subheader("1. Inventory Data Input")
    
    # Expanded segments to include Quantity
    default_segments = [
        {"label": "Fast Moving", "val": 300000.0, "qty": 5000, "days": 30},
        {"label": "Standard Flow", "val": 400000.0, "qty": 2500, "days": 45},
        {"label": "Slow Moving", "val": 200000.0, "qty": 800, "days": 75},
        {"label": "Obsolete/Dead Stock", "val": 50000.0, "qty": 200, "days": 180},
    ]

    inventory_data = []
    # Grid Layout for 4 columns
    cols = st.columns([2, 1.5, 1, 1])
    cols[0].write("**Category**")
    cols[1].write("**Total Value (€)**")
    cols[2].write("**Quantity**")
    cols[3].write("**Days**")

    for i, cat in enumerate(default_segments):
        c = st.columns([2, 1.5, 1, 1])
        name = c[0].text_input(f"Name {i}", cat['label'], key=f"inv_n_{i}", label_visibility="collapsed")
        val = c[1].number_input(f"Value {i}", value=cat['val'], key=f"inv_v_{i}", label_visibility="collapsed")
        qty = c[2].number_input(f"Qty {i}", value=cat['qty'], key=f"inv_q_{i}", label_visibility="collapsed")
        days = c[3].number_input(f"Days {i}", value=cat['days'], key=f"inv_d_{i}", label_visibility="collapsed")
        inventory_data.append({"Category": name, "Value": val, "Quantity": qty, "Days": days})

    # 2. STRATEGIC CALCULATIONS
    df = pd.DataFrame(inventory_data)
    total_val = df["Value"].sum()
    total_qty = df["Quantity"].sum()
    
    # Weighted Average DSI (Weighted by VALUE for Finance)
    weighted_dsi = (df["Value"] * df["Days"]).sum() / total_val if total_val > 0 else 0
    
    # Save to session_state for Cash Cycle Tool
    st.session_state.global_inventory_dsi = weighted_dsi
    st.session_state.inventory_value = total_val

    st.divider()

    # 3. EXECUTIVE METRICS
    m1, m2, m3 = st.columns(3)
    m1.metric("Total Inventory Value", f"€ {total_val:,.0f}")
    m2.metric("Weighted Avg DSI", f"{weighted_dsi:.1f} Days")
    m3.metric("Total Items", f"{total_qty:,.0f} units")

    

    # 4. PARETO: VALUE VS QUANTITY ANALYSIS
    st.subheader("2. Strategic Pareto: Value vs. Volume")
    
    fig = go.Figure()
    # Bars for Value
    fig.add_trace(go.Bar(name='Value (€)', x=df["Category"], y=df["Value"], marker_color='#636EFA'))
    # Line for Days (Secondary Axis)
    fig.add_trace(go.Scatter(name='DSI (Days)', x=df["Category"], y=df["Days"], yaxis="y2", line=dict(color='#EF553B', width=3)))

    fig.update_layout(
        title="Inventory Concentration Analysis",
        template="plotly_dark",
        yaxis=dict(title="Total Value (€)"),
        yaxis2=dict(title="Days in Stock", overlaying='y', side='right'),
        legend=dict(x=0, y=1.1, orientation="h")
    )
    st.plotly_chart(fig, use_container_width=True)

    # 5. INTEGRATION STATUS
    st.subheader("3. System Integration")
    if total_val > 0:
        st.success(f"✔️ **Cash Cycle Synced:** The weighted DSI of **{weighted_dsi:.1f} days** is now available for global calculations.")
    else:
        st.error("❌ **Incomplete Data:** Please enter Value (€) to enable Cash Cycle calculations.")

    # Cold Insight on Liquidity
    wacc = compute_core_metrics().get('wacc', 0.15)
    daily_bleed = (total_val * wacc) / 365
    st.markdown(f"> **Analytical Note:** Every day this inventory sits on the shelf, it consumes **€ {daily_bleed:,.2f}** in capital cost. The highest friction is caused by segments with high Value × Days.")

if __name__ == "__main__":
    show_inventory_manager()
