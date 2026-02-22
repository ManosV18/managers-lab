import streamlit as st
from core.engine import compute_core_metrics

def run_stage4():
    st.header("🏢 Stage 4: Sustainability & Survival Stress Test")
    st.caption("Deep dive into the structural durability of the enterprise.")

    # 1. SYNC WITH CORE ENGINE
    metrics = compute_core_metrics()
    p = st.session_state.price
    vc = st.session_state.variable_cost
    q_annual = st.session_state.volume
    liquidity_drain = st.session_state.liquidity_drain_annual

    st.write(f"**🔗 Core Engine Data:** Annual Volume: {q_annual:,.0f} | Unit Margin: {metrics['unit_contribution']:.2f} €")

    # 2. FIXED COSTS & DEBT INPUTS (Updating Global State)
    st.subheader("Annual Structural Obligations")
    col1, col2 = st.columns(2)
    
    with col1:
        # Ενημερώνουμε το κεντρικό fixed_cost
        st.session_state.fixed_cost = st.number_input(
            "Total Annual Operating Fixed Costs (€)", 
            min_value=0.0, 
            value=float(st.session_state.fixed_cost),
            help="Rent, Salaries, Admin, Software"
        )
        
    with col2:
        # Ενημερώνουμε το Debt Service
        st.session_state.annual_loan_payment = st.number_input(
            "Annual Debt Service (Principal + Interest) (€)", 
            min_value=0.0, 
            value=float(st.session_state.annual_loan_payment)
        )

    # 3. RE-COMPUTE AFTER INPUTS
    metrics = compute_core_metrics()
    
    # 4. RESULTS DISPLAY (Executive Metrics)
    st.divider()
    res1, res2, res3 = st.columns(3)
    
    with res1:
        st.metric("Survival BEP (Units)", f"{metrics['survival_bep']:,.0f}")
        st.caption("Includes Fixed Costs + Debt + Liquidity Drain")

    with res2:
        st.metric("Operating EBIT", f"{metrics['ebit']:,.2f} €")
        st.caption("Before Debt & Liquidity Adjustments")

    with res3:
        # Το Net Profit εδώ υπολογίζεται από το Engine (EBIT - Interest - Liquidity)
        st.metric("Final Net Economic Profit", f"{metrics['net_profit']:,.2f} €", 
                  delta=f"-{liquidity_drain:,.0f} Liquidity Drain", delta_color="inverse")
        st.caption("True bottom line after cash friction")

    # 5. SURVIVAL ANALYSIS (Strategic Signal)
    st.divider()
    
    

    if q_annual < metrics['survival_bep']:
        st.error(f"🔴 **Survival Alert:** The system is structurally non-viable. You are {metrics['survival_bep'] - q_annual:,.0f} units short of the survival threshold.")
    else:
        safety_buffer = q_annual - metrics['survival_bep']
        st.success(f"🟢 **Operational Surplus:** System is stable. Safety buffer: {safety_buffer:,.0f} units ({ (safety_buffer/q_annual)*100:.1f}%).")

    # Risk Factor: Liquidity vs EBIT
    if metrics['ebit'] > 0:
        friction_ratio = (liquidity_drain / metrics['ebit']) * 100
        if friction_ratio > 20:
            st.warning(f"⚠️ **Efficiency Risk:** Cash friction (Working Capital) consumes {friction_ratio:.1f}% of operating profit.")

    # 6. NAVIGATION
    st.divider()
    nav1, nav2 = st.columns(2)
    with nav1:
        if st.button("⬅️ Back to CLV Analysis"):
            st.session_state.flow_step = 3
            st.rerun()
    with nav2:
        if st.button("Proceed to Strategic Synthesis (Stage 5) ➡️", type="primary"):
            st.session_state.flow_step = 5
            st.rerun()
