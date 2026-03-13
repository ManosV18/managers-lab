import streamlit as st
import plotly.graph_objects as go

def show_wc_optimizer():
    st.title("🔄 Working Capital & Cash Velocity")
    s = st.session_state
    m = s.get("metrics", {})

    # 1. FETCH METRICS
    receivables = m.get('receivables_euro', 0)
    inventory = m.get('inventory_euro', 0)
    payables = m.get('payables_euro', 0)
    nwc = receivables + inventory - payables

    # 2. TOP KPI PANEL
    st.subheader("💰 Capital Tied Up")
    c1, c2, c3, c4 = st.columns(4)
    
    c1.metric("Receivables", f"€{receivables:,.0f}")
    c2.metric("Inventory", f"€{inventory:,.0f}")
    c3.metric("Payables", f"€{payables:,.0f}", delta_color="inverse")
    c4.metric("Net Working Capital", f"€{nwc:,.0f}", help="Receivables + Inventory - Payables")

    st.divider()

    col_a, col_b = st.columns(2)
    
    with col_a:
        st.subheader("🏗️ Working Capital Structure")
        # Visualizing components (Payables as positive value but distinct color)
        labels = ['Receivables', 'Inventory', 'Payables']
        values = [receivables, inventory, payables]
        colors = ['#3b82f6', '#10b981', '#ef4444'] # Blue, Green, Red
        
        fig = go.Figure(go.Bar(
            x=labels, 
            y=values, 
            marker_color=colors,
            text=[f"€{v:,.0f}" for v in values],
            textposition='auto'
        ))
        fig.update_layout(
            title="Working Capital Components", 
            template="plotly_dark",
            height=400,
            showlegend=False
        )
        st.plotly_chart(fig, use_container_width=True)

    with col_b:
        st.subheader("📉 Risk & Runway Analysis")
        
        # OPERATING LEVERAGE (DOL)
        dol = m.get('dol', 0)
        st.write(f"**Degree of Operating Leverage (DOL):** `{dol:.2f}`")
        if dol > 5: 
            st.error("🚨 **High Risk**: Small revenue drops will severely impact profit.")
        elif dol > 3: 
            st.warning("⚠️ **Volatile**: High sensitivity to sales volume changes.")
        else: 
            st.success("✅ **Stable**: Resilient cost structure.")
        
        st.divider()
        
        # CASH RUNWAY (Safety Fix Included)
        runway = m.get('runway_months', 0)
        
        if runway == float("inf"):
            st.success("✅ **Positive Cash Generation**: No burn rate detected.")
            runway_display = "∞"
        else:
            runway_display = f"{runway:.1f} months"
            if runway < 6:
                st.error(f"🚨 **Critical**: Cash exhaustion in {runway_display}.")
            elif runway < 12:
                st.warning(f"⚠️ **Tight**: Capital injection or WC optimization needed.")
            else:
                st.success(f"🟢 **Comfortable**: Liquidity horizon is {runway_display}.")

    # 3. ACTIONABLE INSIGHTS
    st.info(f"💡 **Insight:** Reducing Receivables Days by just 5 days would unlock approximately **€{(m.get('revenue',0)/365)*5:,.0f}** in immediate cash.")
