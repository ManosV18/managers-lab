import streamlit as st
import plotly.graph_objects as go

def show_wc_optimizer():
    st.title("🔄 Working Capital & Cash Velocity")
    
    if not st.session_state.get("baseline_locked"):
        st.warning("⚠️ Please 'Lock Baseline' on the home page to enable the analysis.")
        return

    s = st.session_state
    m = s.get("metrics", {})

    # 1. FETCH METRICS (Διόρθωση των keys βάσει του engine.py)
    receivables = m.get('ar_value', 0.0)
    inventory = m.get('inv_value', 0.0)
    payables = m.get('ap_value', 0.0)
    
    # Το NWC υπολογίζεται ήδη στον engine, αλλά μπορούμε να το πάρουμε και από εκεί
    nwc = m.get('net_working_capital', 0.0)
    roic = m.get('roic', 0.0)
    invested_cap = m.get('invested_capital', 0.0)

    # 2. TOP KPI PANEL
    st.subheader("💰 Capital Efficiency")
    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("Receivables", f"${receivables:,.0f}")
    c2.metric("Inventory", f"${inventory:,.0f}")
    c3.metric("Payables", f"${payables:,.0f}")
    c4.metric("Invested Cap", f"${invested_cap:,.0f}") 
    c5.metric("ROIC", f"{roic*100:.1f}%") 

    st.divider()

    # Έλεγχος αν υπάρχουν δεδομένα (αν receivables + inventory είναι 0, κάτι λείπει)
    if receivables == 0 and inventory == 0:
        st.info("ℹ️ No Working Capital data found. Check your Revenue or Days (AR/Inventory) inputs on Home.")
    else:
        col_a, col_b = st.columns(2)
        
        with col_a:
            st.subheader("🏗️ Working Capital Structure")
            labels = ['Receivables (AR)', 'Inventory', 'Payables (AP)']
            values = [receivables, inventory, payables]
            colors = ['#3b82f6', '#10b981', '#ef4444']
            
            fig = go.Figure(go.Bar(
                x=labels, 
                y=values, 
                marker_color=colors,
                text=[f"${v:,.0f}" for v in values],
                textposition='auto'
            ))
            fig.update_layout(title="Working Capital Components ($)", template="plotly_dark", height=400)
            st.plotly_chart(fig, use_container_width=True)

        with col_b:
            st.subheader("📉 Risk & Runway Analysis")
            
            dol = m.get('dol', 0)
            st.write(f"**Degree of Operating Leverage (DOL):** `{dol:.2f}`")
            if dol > 5: 
                st.error("🚨 **High Risk**: High profit sensitivity to sales volume fluctuations.")
            elif dol > 1: 
                st.success("✅ **Stable**: Normal operating leverage.")
            
            st.divider()
            
            # Διόρθωση για το Runway
            runway = m.get('runway_months', 0)
            if runway == float("inf") or runway > 100:
                st.success("✅ **Positive Cash Flow**: No Burn Rate detected.")
            elif runway < 6:
                st.error(f"🚨 **Critical**: Cash exhaustion in {runway:.1f} months.")
            else:
                st.info(f"🟢 **Cash Runway**: {runway:.1f} months of survival.")

    # 3. STRATEGIC INSIGHT (365-day logic)
    if m.get('revenue', 0) > 0:
        daily_rev = m.get('revenue') / 365
        st.info(f"💡 **Strategy:** If you reduce your collection days (AR) by 10 days, you will unlock **${daily_rev*10:,.0f}** in immediate liquidity.")

    # 4. NAVIGATION
    if st.button("⬅️ Back to Hub", use_container_width=True):
        s.flow_step = "home"
        st.rerun()
