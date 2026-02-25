import streamlit as st
import pandas as pd
from core.sync import sync_global_state

def run_stage3():
    st.header("🫁 Stage 3: Liquidity Collapse Timeline")
    st.caption("The Oxygen Monitor: Upfront WC Investment vs. Monthly Operational Flow.")
    st.divider()

    # 1. FETCH REAL-TIME PHYSICS
    m = sync_global_state()
    s = st.session_state

    # Liquidity Physics:
    # monthly_net = (OCF - Debt Service) / 12
    # Safe retrieval of session state values annual_loan = s.get('annual_loan_payment', 0.0) ocf = m.get('ocf', 0.0)  monthly_net = (ocf - annual_loan) / 12
    
    # Net Initial Cash = Opening Cash - Working Capital Lock
    # Χρησιμοποιούμε το max(0, ...) για να μην ξεκινάμε με αρνητικά αν δεν έχουμε λεφτά
    cash_after_wc = s.opening_cash - m["wc_requirement"]

    # 2. RUNWAY CALCULATION
    timeline = []
    current_cash = cash_after_wc
    death_month = None

    for month in range(0, 37):
        timeline.append({"Month": month, "Cash Balance": float(current_cash)})
        if current_cash <= 0 and death_month is None:
            death_month = month
        current_cash += monthly_net

    # 3. EXECUTIVE DASHBOARD
    c1, c2, c3 = st.columns(3)
    c1.metric("Cash After WC Lock", f"{cash_after_wc:,.0f} €")
    
    status = "Surplus" if monthly_net >= 0 else "Burn"
    c2.metric("Monthly Net Flow", f"{monthly_net:,.0f} €", delta=status, delta_color="normal" if monthly_net >= 0 else "inverse")
    
    if monthly_net >= 0:
        runway_val = "Stable (∞)"
        delta_label = "No Depletion"
    else:
        runway_val = f"{death_month} Months" if death_month is not None else ">36 Months"
        delta_label = "Critical" if (death_month and death_month < 6) else "Monitoring"
    
    c3.metric("Survival Runway", runway_val, delta=delta_label, delta_color="inverse" if monthly_net < 0 else "normal")

    # 4. VISUALIZATION
    st.subheader("📉 Cash Runway Projection")
    df_timeline = pd.DataFrame(timeline).set_index("Month")
    st.line_chart(df_timeline)

    # 5. MANAGERIAL VERDICT
    st.divider()
    if death_month is not None:
        st.error(f"💀 **TERMINAL ALERT:** Liquidity exhaustion predicted in **Month {death_month}**.")
    elif monthly_net < 0:
        st.warning("⚠️ **CONTROLLED BURN:** Cash reserves cover more than 36 months.")
    else:
        st.success("✅ **LIQUIDITY SURPLUS:** The system is self-sustaining.")

    # 6. NAVIGATION
    st.divider()
    col_prev, col_next = st.columns(2)
    with col_prev:
        if st.button("⬅️ Back to Stage 2", use_container_width=True):
            st.session_state.flow_step = "stage2" # Χρήση string για συνέπεια
            st.rerun()
    with col_next:
        if st.button("Next: Financing Intervention 💉", type="primary", use_container_width=True):
            st.session_state.flow_step = "stage4"
            st.rerun()
