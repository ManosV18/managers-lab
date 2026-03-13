import streamlit as st
import plotly.graph_objects as go

def show_wc_optimizer():
    st.title("🔄 Working Capital & Cash Velocity")
    s = st.session_state
    m = s.get("metrics", {})

    st.subheader("💰 Capital Tied Up")
    c1, c2, c3 = st.columns(3)
    c1.metric("Receivables", f"€{m.get('receivables_euro', 0):,.0f}")
    c2.metric("Inventory", f"€{m.get('inventory_euro', 0):,.0f}")
    c3.metric("Payables", f"€{m.get('payables_euro', 0):,.0f}", delta_color="inverse")

    st.divider()

    col_a, col_b = st.columns(2)
    
    with col_a:
        st.subheader("🏗️ NWC Structure")
        labels = ['Receivables', 'Inventory', 'Payables (Negative)']
        values = [m.get('receivables_euro', 0), m.get('inventory_euro', 0), -m.get('payables_euro', 0)]
        
        fig = go.Figure(go.Bar(x=labels, y=values, marker_color=['#3b82f6', '#10b981', '#ef4444']))
        fig.update_layout(title="Net Working Capital Components", template="plotly_dark")
        st.plotly_chart(fig, use_container_width=True)

    with col_b:
        st.subheader("📉 Leverage & Runway")
        dol = m.get('dol', 0)
        runway = m.get('runway_months', 0)
        
        # DOL Interpretation
        st.write(f"**Degree of Operating Leverage (DOL):** {dol:.2f}")
        if dol > 5: st.error("⚠️ High Risk: Small drop in sales will wipe out profit.")
        elif dol > 3: st.warning("🟡 Volatile: Significant profit swings expected.")
        else: st.success("✅ Stable: Cost structure is resilient.")
        
        st.divider()
        
        st.write(f"**Cash Runway:** {f'{runway:.1f} months' if runway != float('inf') else '∞'}")
        if runway < 6: st.error("🚨 Critical: Cash exhaustion in less than 6 months.")
        elif runway < 12: st.warning("⚠️ Tight: Capital injection or WC optimization needed.")
