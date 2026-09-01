import streamlit as st
import plotly.graph_objects as go

def show_inventory_manager():
    st.header("📦 Is Your Inventory Helping Your Business, or Trapping Your Cash?")
    st.info(
        "Inventory feels safe because it helps you avoid running out of stock.\n\n"
        "But too much inventory quietly locks cash that your business could use to grow, reduce debt or improve liquidity.\n\n"
        "This tool shows:\n"
        "• How much cash is tied up in inventory\n"
        "• How quickly inventory turns into sales\n"
        "• How much cash you could release by improving inventory management\n"
    )
    
    s = st.session_state

    # 1. FETCH LINKED DATA
    volume       = float(s.get('volume', 12000))
    vc           = float(s.get('variable_cost', 100.0))
    fixed_assets = float(s.get('fixed_assets', 800000.0))
    depreciation = float(s.get('depreciation', 50000.0))
    annual_cogs  = volume * vc

    if not s.get('baseline_locked', False) or volume == 0:
        st.warning("🔒 Please lock a valid Baseline in Home first to sync Fixed Assets & COGS.")
        return

    # 2. INVENTORY INPUTS
    st.subheader("1. How Much Cash Is Locked in Inventory?")
    col1, col2 = st.columns(2)

    b_inv = int(s.get('inv_days', 75))

    with col1:
        inv_days = st.slider(
            "Inventory Holding Days (DIO) - How many days your cash stays trapped before inventory is sold.",
            1,
            365,
            b_inv,
            key=f"inv_mgr_{b_inv}"
        )
        s.inv_days = inv_days  # write back to global state

    avg_inventory_val  = (inv_days / 365) * annual_cogs
    inventory_turnover = 365 / inv_days if inv_days > 0 else 0

    with col2:
        st.metric("Cash Tied Up in Inventory", f"${avg_inventory_val:,.0f}")
        st.metric("How Many Times Inventory Recycles Each Year", f"{inventory_turnover:.1f}x / Year")

    st.divider()

    # 3. ASSET DRAG ANALYSIS
    st.subheader("2. The Hidden Cost of Inventory That Moves Too Slowly")

    asset_utilization_ratio = avg_inventory_val / fixed_assets if fixed_assets > 0 else 0
    annual_asset_drag        = asset_utilization_ratio * depreciation

    c1, c2 = st.columns(2)
    with c1:
        st.progress(min(asset_utilization_ratio, 1.0))
        st.caption(f"Almost {asset_utilization_ratio:.0%} of the capital invested in your business is tied up in inventory.")

    with c2:
        st.metric("Estimated Annual Cost of Holding Inventory", f"${annual_asset_drag:,.0f}",
                  help="The estimated annual depreciation and asset cost tied up in unsold stock.")
        st.info(f"💡 Every 10 days of DIO reduction releases "
                f"**${(10/365)*annual_cogs:,.0f}** in cash flow.")

    # 4. VISUALIZATION
    fig = go.Figure(data=[go.Pie(
        labels=['Cash Invested in Productive Assets', 'Cash Tied Up in Inventory'],
        values=[max(0, fixed_assets - avg_inventory_val), avg_inventory_val],
        hole=0.5,
        marker_colors=['#1E3A8A', '#ef4444']
    )])
    fig.update_layout(title="Where Your Business Capital Is Invested", height=350, template="plotly_dark")
    st.plotly_chart(fig, use_container_width=True)

    # 5. STRATEGIC VERDICT
    st.divider()
    if inventory_turnover < 6:
        st.error("🚨 **Too much cash is tied up in inventory.** This reduces liquidity and limits the cash available for growth, debt repayment or new opportunities.")
    elif inventory_turnover > 12:
        st.success("✅ **Inventory is moving efficiently.** Your business is converting inventory back into cash quickly.")
    else:
        st.warning("⚠️ **Your inventory levels appear reasonable.** Keep monitoring inventory days to avoid unnecessary cash being tied up in stock.")

    # 6. EXPLANATION SECTION
    st.divider()
    with st.expander("💡 Why does this matter?"):
        st.write(
            "Inventory is not just products sitting on shelves.\n\n"
            "It is cash that has already left your bank account.\n\n"
            "Until those products are sold, that cash cannot be used to:\n"
            "• Pay suppliers\n"
            "• Reduce debt\n"
            "• Invest in growth\n"
            "• Handle unexpected opportunities\n\n"
            "Lower inventory does not always mean selling more.\n\n"
            "Sometimes it simply means getting your cash back faster."
        )

    # 7. NAVIGATION
    st.divider()
    if st.button("⬅️ Back to Hub", use_container_width=True):
        s.flow_step = "home"
        st.rerun()

