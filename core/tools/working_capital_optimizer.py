import streamlit as st
import plotly.graph_objects as go

def show_wc_optimizer():
    st.title("🔄 Working Capital & Cash Velocity")
    
    # Έλεγχος αν υπάρχουν δεδομένα
    if not st.session_state.get("baseline_locked"):
        st.warning("⚠️ Παρακαλώ 'κλειδώστε' το Baseline στην αρχική σελίδα για να εμφανιστούν τα δεδομένα.")
        return

    s = st.session_state
    m = s.get("metrics", {})

    # 1. FETCH METRICS (Με default τιμή 0.1 για να μην κρασάρουν τα γραφήματα αν είναι όλα μηδέν)
    receivables = m.get('receivables_euro', 0.0)
    inventory = m.get('inventory_euro', 0.0)
    payables = m.get('payables_euro', 0.0)
    nwc = receivables + inventory - payables

    # 2. TOP KPI PANEL
    st.subheader("💰 Capital Tied Up")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Receivables", f"€{receivables:,.0f}")
    c2.metric("Inventory", f"€{inventory:,.0f}")
    c3.metric("Payables", f"€{payables:,.0f}")
    c4.metric("Net Working Capital", f"€{nwc:,.0f}")

    st.divider()

    if receivables == 0 and inventory == 0:
        st.info("ℹ️ Δεν βρέθηκαν δεδομένα Working Capital. Ελέγξτε αν ο Τζίρος ή οι Ημέρες (AR/Inventory) είναι πάνω από το μηδέν.")
    else:
        col_a, col_b = st.columns(2)
        
        with col_a:
            st.subheader("🏗️ Working Capital Structure")
            labels = ['Receivables', 'Inventory', 'Payables']
            values = [receivables, inventory, payables]
            colors = ['#3b82f6', '#10b981', '#ef4444']
            
            fig = go.Figure(go.Bar(
                x=labels, 
                y=values, 
                marker_color=colors,
                text=[f"€{v:,.0f}" for v in values],
                textposition='auto'
            ))
            fig.update_layout(title="Working Capital Components (€)", template="plotly_dark", height=400)
            st.plotly_chart(fig, use_container_width=True)

        with col_b:
            st.subheader("📉 Risk & Runway Analysis")
            
            # DOL
            dol = m.get('dol', 0)
            st.write(f"**Degree of Operating Leverage (DOL):** `{dol:.2f}`")
            if dol > 5: st.error("🚨 **High Risk**: Υψηλή ευαισθησία κέρδους.")
            elif dol > 1: st.success("✅ **Stable**: Κανονική λειτουργική μόχλευση.")
            
            st.divider()
            
            # RUNWAY
            runway = m.get('runway_months', 0)
            if runway == float("inf"):
                st.success("✅ **Positive Cash Flow**: Δεν υπάρχει Burn Rate.")
            elif runway < 6:
                st.error(f"🚨 **Critical**: Τα μετρητά τελειώνουν σε {runway:.1f} μήνες.")
            else:
                st.info(f"🟢 **Runway**: {runway:.1f} μήνες επιβίωσης.")

    # Δυναμικό Insight
    if m.get('revenue', 0) > 0:
        daily_rev = m.get('revenue') / 365
        st.info(f"💡 **Strategy:** Αν μειώσεις τις ημέρες είσπραξης (AR) κατά 10 μέρες, θα απελευθερώσεις **€{daily_rev*10:,.0f}** άμεσα στην τράπεζα.")
