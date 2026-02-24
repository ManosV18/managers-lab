import streamlit as st
import pandas as pd
from core.engine import compute_core_metrics

def run_stage3():
    st.header("🫁 Stage 3: Liquidity Collapse Timeline")
    st.caption("The Oxygen Monitor: Upfront WC Investment vs. Monthly Operational Flow.")

    m = compute_core_metrics()
    s = st.session_state

    # 1. INITIAL OXYGEN (Month 0)
    cash_after_wc = s.opening_cash_balance - m["total_wc_requirement"]

    # 2. MONTHLY NET FLOW
    monthly_structural = (s.fixed_cost + m["annual_debt_service"]) / 12
    monthly_contribution = (m["unit_contribution"] * s.volume) / 12
    monthly_net = monthly_contribution - monthly_structural

    # 3. TIMELINE
    timeline = []
    current_cash = cash_after_wc
    death_month = None

    for month in range(0, 37):
        timeline.append({"Month": month, "Cash Balance": current_cash})
        if current_cash <= 0 and death_month is None:
            death_month = month
        current_cash += monthly_net

    # 4. DASHBOARD
    st.divider()
    c1, c2, c3 = st.columns(3)
    c1.metric("Cash After WC", f"{cash_after_wc:,.0f} €")
    c2.metric("Monthly Net Flow", f"{monthly_net:,.0f} €")
    c3.metric("Runway", f"{death_month} Months" if death_month else "Stable")

    st.line_chart(pd.DataFrame(timeline).set_index("Month"))

    if death_month:
        st.error(f"💀 **Month of Death: {death_month}**.")
    
    if st.button("Next: Financing Intervention 💉", use_container_width=True):
        st.session_state.flow_step = 4
        st.rerun()
