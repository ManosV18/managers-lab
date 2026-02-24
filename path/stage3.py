import streamlit as st
import pandas as pd
from core.engine import compute_core_metrics

def run_stage3():
    st.header("🫁 Stage 3: Liquidity Collapse Timeline")
    st.caption("The Oxygen Monitor: Upfront WC Investment vs. Monthly Operational Flow.")

    # 1. Single Source of Truth από τον Engine
    m = compute_core_metrics()
    s = st.session_state

    # 2. MONTHLY NET FLOW & INITIAL OXYGEN
    # Ορίζουμε το monthly_net από το FCF του Engine
    monthly_net = m["fcf"] / 12
    cash_after_wc = s.get('opening_cash', 0.0) - m["total_wc_requirement"]

    # 3. RUNWAY STOP LOGIC (Cold Stop)
    timeline = []
    current_cash = cash_after_wc
    death_month = None

    for month in range(0, 37):
        timeline.append({"Month": month, "Cash Balance": current_cash})
        
        if current_cash <= 0:
            death_month = month
            break # Σταματάμε το γράφημα στο μηδέν
            
        current_cash += monthly_net

    # 4. DASHBOARD (Equilibrium & Status)
    st.divider()
    c1, c2, c3 = st.columns(3)
    
    c1.metric("Cash After WC", f"{cash_after_wc:,.0f} €", help="Starting Cash minus Upfront WC")
    
    status_color = "normal" if monthly_net >= 0 else "inverse"
    c2.metric("Monthly Net Flow", f"{monthly_net:,.0f} €", delta="Surplus" if monthly_net >= 0 else "Burn", delta_color=status_color)
    
    # Advanced Runway Status Logic
    if death_month is not None:
        runway_val = f"{death_month} Months"
    elif monthly_net == 0:
        runway_val = "Equilibrium"
    else:
        runway_val = "Stable (∞)"
        
    c3.metric("Runway", runway_val, delta="CRITICAL" if death_month else "OK", delta_color="inverse" if death_month else "normal")

    # 5. VISUALIZATION
    st.subheader("📉 Cash Runway Projection")
    if len(timeline) > 1:
        st.line_chart(pd.DataFrame(timeline).set_index("Month"))
    else:
        st.error("Instant Collapse: No timeline to display.")

    

    # 6. COLD ASSESSMENT
    st.divider()
    if death_month is not None:
        if death_month == 0:
            st.error("💀 **Immediate Collapse:** Τα μετρητά έναρξης δεν καλύπτουν καν το απαιτούμενο Working Capital.")
        else:
            st.error(f"💀 **Month of Death: {death_month}**. Η επιχείρηση ξεμένει από οξυγόνο.")
    elif monthly_net < 0:
        st.warning("⚠️ **Slow Burn:** Αργή κατανάλωση κεφαλαίου. Χρειάζεται δομική παρέμβαση.")
    else:
        st.success("✅ **Structural Health:** Το μοντέλο είναι αυτοσυντηρούμενο.")

    # 7. NAVIGATION
    if st.button("Next: Financing Intervention 💉", type="primary", use_container_width=True):
        st.session_state.flow_step = 4
        st.rerun()
