import streamlit as st
import pandas as pd
from core.engine import compute_core_metrics

def run_stage3():
    st.header("🫁 Stage 3: Liquidity Collapse Timeline")
    st.caption("Oxygen Monitor: Upfront WC Investment vs. Monthly Operational Flow.")

    m = compute_core_metrics()
    s = st.session_state

    # 1. INITIAL OXYGEN (Month 0)
    # Αφαιρούμε το WC upfront από το Opening Cash
    starting_cash = s.opening_cash_balance
    wc_investment = m["total_wc_requirement"]
    cash_after_wc = starting_cash - wc_investment

    # 2. MONTHLY NET FLOW
    monthly_fixed = s.fixed_cost / 12
    monthly_debt = m["annual_debt_service"] / 12
    monthly_contribution = (m["unit_contribution"] * s.volume) / 12
    
    monthly_net = monthly_contribution - monthly_fixed - monthly_debt

    # 3. TIMELINE GENERATION
    timeline = []
    current_cash = cash_after_wc
    death_month = None

    for month in range(0, 37): # 36 Months + Month 0
        timeline.append({"Month": month, "Cash Balance": current_cash})
        if current_cash <= 0 and death_month is None:
            death_month = month
        current_cash += monthly_net

    df = pd.DataFrame(timeline)

    # 4. DASHBOARD
    st.divider()
    c1, c2, c3 = st.columns(3)
    c1.metric("Cash After WC", f"{cash_after_wc:,.0f} €", help="Starting Cash minus Upfront WC")
    c2.metric("Monthly Net Flow", f"{monthly_net:,.0f} €")
    
    runway_label = f"{death_month} Months" if death_month else "Stable"
    c3.metric("Runway", runway_label, delta="CRITICAL" if death_month else "OK", delta_color="inverse" if death_month else "normal")

    st.subheader("📉 Liquidity Projection")
    st.line_chart(df.set_index("Month"))

    # 5. COLD ASSESSMENT
    if death_month:
        st.error(f"💀 **Month of Death: {death_month}**. The upfront WC investment depletes resources that the monthly flow cannot replenish in time.")
    elif monthly_net < 0:
        st.warning("⚠️ **Slow Burn:** You survived the WC impact, but monthly structural costs are slowly eroding your cash.")
    else:
        st.success("✅ **Self-Sustaining:** The system has survived the upfront friction and generates monthly oxygen.")

    st.divider()
    if st.button("Next: Financing Intervention 💉", type="primary", use_container_width=True):
        st.session_state.flow_step = 4
        st.rerun()
