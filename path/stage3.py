import streamlit as st
import pandas as pd
from core.engine import compute_core_metrics

def run_stage3():
    st.header("🫁 Stage 3: Liquidity Collapse Timeline")
    st.caption("The Oxygen Monitor: Monthly cash burn and the 'Month of Death' analysis.")

    metrics = compute_core_metrics()
    s = st.session_state

    # 1. Monthly Engine Logic
    # Starting Cash - Upfront WC Investment
    starting_oxygen = s.opening_cash_balance - metrics['total_wc_requirement']
    
    monthly_structural_drain = (s.fixed_cost + s.annual_loan_payment) / 12
    monthly_contribution = (metrics['unit_contribution'] * s.volume) / 12
    monthly_net_flow = monthly_contribution - monthly_structural_drain

    # 2. Timeline Logic
    timeline = []
    current_cash = starting_oxygen
    death_month = None

    for m in range(0, 37): # 3-year projection
        timeline.append({"Month": m, "Cash Balance": current_cash})
        if current_cash <= 0 and death_month is None:
            death_month = m
        current_cash += monthly_net_flow

    # 3. Visualization & KPIs
    st.divider()
    col1, col2, col3 = st.columns(3)
    col1.metric("Starting Oxygen", f"{starting_oxygen:,.0f} €")
    col2.metric("Monthly Net Flow", f"{monthly_net_flow:,.0f} €")
    
    runway = death_month if death_month is not None else "∞"
    col3.metric("Runway (Months)", f"{runway}")

    st.line_chart(pd.DataFrame(timeline).set_index("Month"))
    
    

    if death_month:
        st.error(f"🚨 **Critical Alert:** Cash depletion predicted in Month {death_month}.")
    else:
        st.success("✅ **Self-Sustaining Model:** No collapse predicted within 36 months.")

    st.divider()
    if st.button("Next: Financing Interventions 💉", type="primary", use_container_width=True):
        st.session_state.flow_step = 4
        st.rerun()
