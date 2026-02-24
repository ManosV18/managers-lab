import streamlit as st
import pandas as pd
from core.engine import compute_core_metrics

def run_stage3():
    st.header("🫁 Stage 3: Liquidity Collapse Timeline")
    st.caption("The Oxygen Monitor: Upfront WC Investment vs. Monthly Operational Flow.")

    m = compute_core_metrics()
    s = st.session_state

    # 1. Liquidity Physics Refinement
    # monthly_net = (OCF - Debt Service) / 12 -> Pure Liquidity Flow
    monthly_net = (m["ocf"] - s.annual_loan_payment) / 12
    cash_after_wc = s.get('opening_cash', 0.0) - m["total_wc_requirement"]

    # 2. Runway Stop Logic (Cold Stop)
    timeline = []
    current_cash = cash_after_wc
    death_month = None

    for month in range(0, 37):
        timeline.append({"Month": month, "Cash Balance": current_cash})
        if current_cash <= 0:
            death_month = month
            break 
        current_cash += monthly_net

    # 3. Dashboard
    st.divider()
    c1, c2, c3 = st.columns(3)
    c1.metric("Cash After WC", f"{cash_after_wc:,.0f} €")
    
    # Equilibrium vs Burn vs Surplus
    status = "Burn" if monthly_net < 0 else "Surplus"
    c2.metric("Monthly Net Flow", f"{monthly_net:,.0f} €", delta=status, delta_color="normal" if monthly_net >= 0 else "inverse")
    
    # Runway Labeling Logic
    if death_month is not None: runway_val = f"{death_month} Months"
    elif monthly_net == 0: runway_val = "Equilibrium"
    else: runway_val = "Stable (∞)"
    
    c3.metric("Runway Status", runway_val, delta="Critical" if death_month else "OK", delta_color="inverse" if death_month else "normal")

    # 4. Visualization
    st.subheader("📉 Cash Runway Projection")
    if len(timeline) > 1:
        st.line_chart(pd.DataFrame(timeline).set_index("Month"))

    

    if death_month is not None:
        st.error(f"💀 **Month of Death: {death_month}**. Liquidity exhausted.")
    
    st.divider()
    if st.button("Next: Financing Intervention 💉", type="primary", use_container_width=True):
        st.session_state.flow_step = 4
        st.rerun()
