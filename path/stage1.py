import streamlit as st
from core.engine import compute_core_metrics

def run_stage1():
    st.header("🧱 Stage 1: Static Survival Threshold")
    st.caption("Analytical Focus: The 'Cash Wall' vs. Unit Contribution.")

    metrics = compute_core_metrics()
    s = st.session_state

    if metrics['is_non_viable']:
    st.error("🚨 **SYSTEMIC COLLAPSE:** Your Variable Cost exceeds your Price. The business loses money with every unit sold. Survival is mathematically impossible at any volume.")
else:
    st.metric("Survival BEP", f"{metrics['survival_bep']:,.0f} Units")
    # 1. Calculation of the Cash Wall
    # Το WC Requirement θεωρείται upfront κεφάλαιο που πρέπει να 'κλειδωθεί'
    cash_wall = s.fixed_cost + s.annual_loan_payment + metrics['total_wc_requirement']
    unit_cont = metrics['unit_contribution']
    
    survival_bep = cash_wall / unit_cont if unit_cont > 0 else float('inf')

    # 2. Visualizing the Challenge
    st.divider()
    c1, c2, c3 = st.columns(3)
    
    c1.metric("The Cash Wall", f"{cash_wall:,.0f} €", help="FC + Debt Service + WC Requirement")
    c2.metric("The Ladder (Unit Cont.)", f"{unit_cont:,.2f} €")
    c3.metric("Survival BEP", f"{survival_bep:,.0f} Units")

    # 3. Gap Analysis
    gap = survival_bep - s.volume
    st.subheader("📏 The Survival Gap")
    
    if gap > 0:
        st.error(f"🚨 **Structural Deficit:** You are {gap:,.0f} units below the Cash Survival Wall.")
        st.progress(min(s.volume / survival_bep, 1.0))
    else:
        st.success(f"🟢 **Structural Surplus:** You are {abs(gap):,.0f} units above the Survival Wall.")
        st.progress(1.0)

    # 4. Cold Insight
    st.info(f"""
    **Cold Reality Insight:** To cover your fixed obligations and the cash 'trapped' in operations, 
    every unit you sell contributes {unit_cont:,.2f}€. 
    You need to reach **{survival_bep:,.0f} units** just to maintain 0 net cash flow.
    """)

    # Navigation
    if st.button("Next: Volume Shock Simulation 📉", use_container_width=True):
        st.session_state.flow_step = 2
        st.rerun()
