import streamlit as st
import pandas as pd
import plotly.graph_objects as go

def show_inventory_manager(): # Διορθωμένο όνομα για τον Router
    st.header("📦 Industrial Inventory & Asset Productivity")
    st.info("Strategic Audit: Linking Inventory Turnover to Asset Depreciation and Capital Efficiency.")

    s = st.session_state
    
    # 1. FETCH LINKED DATA (The McKinsey Connection)
    # Τραβάμε τα 16-20 βασικά νούμερα από το Home
    volume = float(s.get('volume', 0))
    vc = float(s.get('variable_cost', 0.0))
    fixed_assets = float(s.get('fixed_assets', 0.0))
    depreciation = float(s.get('depreciation', 0.0))
    annual_cogs = volume * vc
    
    if not s.get('baseline_locked', False) or volume == 0:
        st.warning("🔒 Please lock a valid Baseline in Home first to sync Fixed Assets & COGS.")
        return

    # 2. INVENTORY INPUTS
    st.subheader("1. Inventory Dynamics")
    col1, col2 = st.columns(2)
    
    with col1:
        # Χρησιμοποιούμε 365 ημέρες βάσει οδηγίας [2026-02-18]
        inv_days = st.slider("Inventory Holding Days (DIO)", 1, 365, int(s.get('inv_days', 60)))
        s.inv_days = inv_days # Ενημέρωση του Global State
        
    # Calculated metrics
    avg_inventory_val = (inv_days / 365) * annual_cogs
    inventory_turnover = 365 / inv_days if inv_days > 0 else 0
    
    with col2:
        st.metric("Avg. Inventory Value", f"${avg_inventory_val:,.0f}")
        st.metric("Inventory Turnover", f"{inventory_turnover:.1f}x / Year")

    st.divider()

    # 3. THE "ASSET DRAG" ANALYSIS (Linking Depreciation)
    st.subheader("2. The Hidden Cost: Asset Drag")
    
    # Υπολογισμός: Πόσο μέρος των αποσβέσεων "δεσμεύεται" στο απόθεμα
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
        st.info(f"💡 Every 10 days of DIO reduction releases **${(10/365)*annual_cogs:,.0f}** in cash flow.")

    # 4. VISUALIZATION
    labels = ['Productive Assets', 'Inventory Drag']
    values = [max(0, fixed_assets - avg_inventory_val), avg_inventory_val]
    
    fig = go.Figure(data=[go.Pie(labels=labels, values=values, hole=.5, 
                                 marker_colors=['#1E3A8A', '#ef4444'])])
    fig.update_layout(title="Capital Allocation Profile", height=350, template="plotly_white")
    st.plotly_chart(fig, use_container_width=True)

    # 5. STRATEGIC VERDICT
    st.divider()
    if inventory_turnover < 6:
        st.error("🚨 **Verdict: Low Capital Velocity.** You are depreciating equipment to build stock, not cash. High Risk of Obsolescence.")
    elif inventory_turnover > 12:
        st.success("✅ **Verdict: Lean Operation.** Minimal Asset Drag. High ROIC potential due to rapid capital recycling.")
    else:
        st.warning("⚠️ **Verdict: Balanced.** Monitor if 'Asset Drag' exceeds 15% of total depreciation.")

    # 6. NAVIGATION
    if st.button("⬅️ Return to Control Tower", use_container_width=True):
        s.flow_step = "home"
        st.rerun()
