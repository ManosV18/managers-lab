import streamlit as st
import pandas as pd
import plotly.graph_objects as go

def run_inventory_manager():
    st.header("📦 Industrial Inventory & Asset Productivity")
    st.info("Strategic Audit: Linking Inventory Turnover to Asset Depreciation and Capital Efficiency.")

    s = st.session_state
    if not s.get('baseline_locked', False):
        st.warning("🔒 Please lock Baseline in Home to sync Fixed Assets & Depreciation.")
        return

    # 1. FETCH LINKED DATA (The McKinsey Connection)
    volume = float(s.get('volume', 15000))
    vc = float(s.get('variable_cost', 90.0))
    fixed_assets = float(s.get('fixed_assets', 800000.0))
    depreciation = float(s.get('depreciation', 50000.0))
    annual_cogs = volume * vc
    
    # 2. INVENTORY INPUTS
    st.subheader("1. Inventory Dynamics")
    col1, col2 = st.columns(2)
    
    with col1:
        inv_days = st.slider("Inventory Holding Days (DIO)", 1, 365, int(s.get('inv_days', 60)))
        s.inv_days = inv_days # Sync back to global
        
    # Calculated metrics
    avg_inventory_val = (inv_days / 365) * annual_cogs
    inventory_turnover = 365 / inv_days if inv_days > 0 else 0
    
    with col2:
        st.metric("Avg. Inventory Value", f"${avg_inventory_val:,.0f}")
        st.metric("Inventory Turnover", f"{inventory_turnover:.1f}x / Year")

    st.divider()

    # 3. THE "ASSET DRAG" ANALYSIS (Linking Depreciation)
    st.subheader("2. The Hidden Cost: Asset Drag")
    
    # Logic: Πόσο μέρος των παγίων "δουλεύει" μόνο για την αποθήκη;
    # Αν το στοκ είναι το 20% των παγίων, τότε το 20% των αποσβέσεων "καίγεται" σε αποθέματα.
    asset_utilization_ratio = avg_inventory_val / fixed_assets if fixed_assets > 0 else 0
    annual_asset_drag = asset_utilization_ratio * depreciation
    
    c1, c2 = st.columns(2)
    with c1:
        st.write(f"**Fixed Assets Base:** ${fixed_assets:,.0f}")
        st.write(f"**Annual Depreciation:** ${depreciation:,.0f}")
        st.progress(min(asset_utilization_ratio, 1.0))
        st.caption(f"Inventory represents {asset_utilization_ratio:.1%} of Fixed Asset value.")

    with c2:
        st.metric("Annual Asset Drag", f"${annual_asset_drag:,.0f}", 
                  help="The portion of your machinery's depreciation that is 'locked' in unsold stock.")
        st.info(f"💡 Reducing DIO by 10 days releases **${(10/365)*annual_cogs:,.0f}** in cash.")

    # 4. VISUALIZATION: THE LIQUIDITY VS ASSET UTILIZATION
    
    
    labels = ['Active Assets', 'Inventory Drag']
    values = [fixed_assets - avg_inventory_val, avg_inventory_val]
    
    fig = go.Figure(data=[go.Pie(labels=labels, values=values, hole=.5, marker_colors=['#1E3A8A', '#ef4444'])])
    fig.update_layout(title="Capital Allocation: Fixed Assets vs Inventory", height=350)
    st.plotly_chart(fig, use_container_width=True)

    # 5. STRATEGIC VERDICT
    st.divider()
    if inventory_turnover < 6:
        st.error("🚨 **Verdict: Low Capital Velocity.** Your inventory is moving too slowly compared to your asset base. You are depreciating equipment to build stock, not cash.")
    elif inventory_turnover > 12:
        st.success("✅ **Verdict: Lean Operation.** High turnover indicates efficient use of assets. Minimal 'Asset Drag' detected.")
    else:
        st.warning("⚠️ **Verdict: Balanced.** Normal industrial rotation, but monitor holding costs.")

    # 6. NAVIGATION
    if st.button("⬅️ Return to Hub", use_container_width=True):
        s.flow_step = "home"
        st.rerun()
