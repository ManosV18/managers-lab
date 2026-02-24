import streamlit as st
from core.engine import compute_core_metrics

def run_stage4():
    st.header("🏢 Stage 4: Sustainability & Survival Stress Test")
    st.caption("Strategic Audit: Evaluating structural durability against operational friction.")

    # 1. SYNC WITH CORE ENGINE
    metrics = compute_core_metrics()
    
    q_annual = st.session_state.get('volume', 0)
    liquidity_drain = st.session_state.get('liquidity_drain_annual', 0)
    unit_contribution = metrics.get('unit_contribution', 0)

    st.info(f"🔗 **Core Engine Linked:** Volume: {q_annual:,.0f} units | Unit Contribution: {unit_contribution:,.2f} €")

    # 2. FIXED COSTS & DEBT INPUTS
    st.subheader("Annual Structural Obligations")
    col1, col2 = st.columns(2)
    
    with col1:
        st.session_state.fixed_cost = st.number_input(
            "Total Annual Operating Fixed Costs (€)", 
            min_value=0.0, 
            value=float(st.session_state.get('fixed_cost', 200000.0)),
            key="fixed_cost_s4"
        )
        
    with col2:
        st.session_state.annual_loan_payment = st.number_input(
            "Annual Debt Service (Principal + Interest) (€)", 
            min_value=0.0, 
            value=float(st.session_state.get('annual_loan_payment', 12000.0)),
            key="debt_service_s4"
        )

    # 3. RE-COMPUTE AFTER INPUTS
    metrics = compute_core_metrics()
    surv_bep = metrics.get('survival_bep', 0)
    ebit = metrics.get('ebit', 0)
    net_profit = metrics.get('net_profit', 0)
    
    # 4. EXECUTIVE METRICS DISPLAY
    st.divider()
    res1, res2, res3 = st.columns(3)
    
    res1.metric("Survival BEP (Units)", f"{surv_bep:,.0f}")
    res2.metric("Operating EBIT", f"{ebit:,.0f} €")
    
    # Προ-υπολογισμός για το delta του Net Economic Profit
    net_econ_profit = net_profit - liquidity_drain
    friction_label = f"-{liquidity_drain:,.0f} Cash Friction"
    res3.metric("Net Economic Profit", f"{net_econ_profit:,.0f} €", delta=friction_label, delta_color="inverse")

    # 5. SURVIVAL ANALYSIS (Shock Test)
    st.divider()
    st.subheader("🔬 Structural Viability Analysis")
    
    # Υπολογισμοί εκτός f-strings για ασφάλεια
    if q_annual > 0:
        safety_margin_val = (q_annual - surv_bep) / q_annual
    else:
        safety_margin_val = -1.0
        
    margin_text = f"{safety_margin_val:.1%}"
    
    if surv_bep > 0:
        c1, c2 = st.columns([1, 3])
        c1.write("**Safety Margin**")
        c1.write(f"### {margin_text}")
        
        progress_val = min(max(q_annual / surv_bep, 0.0), 1.0)
        st.progress(progress_val)

    # Cold Analysis Messages
    if q_annual < surv_bep:
        gap = surv_bep - q_annual
        st.error(f"🔴 **Survival Alert:** The system is structurally non-viable. You are {gap:,.0f} units below threshold.")
    else:
        buffer = q_annual - surv_bep
        st.success(f"🟢 **Operational Surplus:** System is stable. Safety buffer: {buffer:,.0f} units ({margin_text}).")

    # Friction Analysis
    if ebit > 0:
        friction_ratio = liquidity_drain / ebit
        friction_pct_text = f"{friction_ratio:.1%}"
        if friction_ratio > 1.0:
             st.error(f"🚨 **Liquidity Trap:** Working Capital drain exceeds EBIT. Friction: {friction_pct_text}")
        elif friction_ratio > 0.4:
            st.warning(f"⚠️ **Cash Intensive:** {friction_pct_text} of profit is tied up in liquidity.")

    # 6. NAVIGATION
    st.divider()
    nav1, nav2 = st.columns(2)
    with nav1:
        if st.button("⬅️ Back to CLV Analysis", use_container_width=True):
            st.session_state.flow_step = 3
            st.rerun()
    with nav2:
        if st.button("Final Stage: Strategic Synthesis ➡️", type="primary", use_container_width=True):
            st.session_state.flow_step = 5
            st.rerun()
