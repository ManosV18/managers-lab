import streamlit as st
import pandas as pd
from core.engine import compute_core_metrics

def run_stage3():
    st.header("🫁 Stage 3: Liquidity Collapse Timeline")
    st.caption("The Oxygen Monitor: Upfront WC Investment vs. Monthly Operational Flow.")

    # 1. Single Source of Truth από τον Engine
    m = compute_core_metrics()
    s = st.session_state

    # 2. INITIAL OXYGEN (Month 0)
    # Χρήση του διορθωμένου naming 'opening_cash' για αποφυγή KeyErrors
    cash_after_wc = s.get('opening_cash', 0.0) - m["total_wc_requirement"]

    # 3. MONTHLY NET FLOW (Cash Physics Logic)
    # Χρησιμοποιούμε το FCF του Engine που είναι ήδη καθαρό από WC διπλοεγγραφές
    monthly_net = m["fcf"] / 12

    # 4. TIMELINE GENERATION
    timeline = []
    current_cash = cash_after_wc
    death_month = None

    # Προσομοίωση 3 ετών (36 μήνες + Μήνας 0)
    for month in range(0, 37):
        timeline.append({"Month": month, "Cash Balance": current_cash})
        
        # Καταγραφή του Month of Death αν τα μετρητά μηδενιστούν
        if current_cash <= 0 and death_month is None:
            death_month = month
            
        current_cash += monthly_net

    # 5. DASHBOARD
    st.divider()
    c1, c2, c3 = st.columns(3)
    
    # Πόσο οξυγόνο έμεινε μετά το "πάγωμα" κεφαλαίου στο WC
    c1.metric("Cash After WC", f"{cash_after_wc:,.0f} €", help="Starting Cash minus Upfront Working Capital Investment")
    
    # Μηνιαία παραγωγή ή καύση μετρητών
    status_color = "normal" if monthly_net >= 0 else "inverse"
    c2.metric("Monthly Net Flow", f"{monthly_net:,.0f} €", delta="Surplus" if monthly_net >= 0 else "Burn", delta_color=status_color)
    
    # Runway σε μήνες
    runway_val = f"{death_month} Months" if death_month is not None else "Stable (∞)"
    c3.metric("Runway", runway_val, delta="CRITICAL" if death_month else "OK", delta_color="inverse" if death_month else "normal")

    # 6. VISUALIZATION
    st.subheader("📉 Cash Runway Projection")
    st.line_chart(pd.DataFrame(timeline).set_index("Month"))

    

    # 7. COLD ASSESSMENT
    if death_month is not None:
        if death_month == 0:
            st.error("💀 **Immediate Collapse:** Your Starting Cash is not enough even to cover the initial Working Capital requirement.")
        else:
            st.error(f"💀 **Month of Death: {death_month}**. Το σύστημα καταναλώνει τα αποθέματά του ταχύτερα από όσο τα αναπληρώνει.")
    elif monthly_net < 0:
        st.warning("⚠️ **Slow Erosion:** Survive the 3-year window, but long-term structural changes are needed as FCF is negative.")
    else:
        st.success("✅ **Structural Health:** Το μοντέλο παράγει πλεόνασμα οξυγόνου κάθε μήνα.")

    # NAVIGATION
    st.divider()
    if st.button("Next: Financing Intervention 💉", type="primary", use_container_width=True):
        st.session_state.flow_step = 4
        st.rerun()
