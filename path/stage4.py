import streamlit as st
from core.engine import compute_core_metrics

def run_stage4():
    st.header("🏢 Stage 4: Sustainability & Survival Stress Test")
    st.caption("Strategic Audit: Evaluating structural durability against operational friction.")

    # 1. SYNC WITH CORE ENGINE
    # Καλούμε τον engine για να έχουμε τα τελευταία δεδομένα από τα προηγούμενα στάδια
    metrics = compute_core_metrics()
    
    q_annual = st.session_state.get('volume', 0)
    liquidity_drain = st.session_state.get('liquidity_drain_annual', 0)

    st.info(f"🔗 **Core Engine Linked:** Annual Volume: {q_annual:,.0f} units | Unit Margin: {metrics['unit_contribution']:.2f} €")

    # 2. FIXED COSTS & DEBT INPUTS (Updating Global State)
    st.subheader("Annual Structural Obligations")
    col1, col2 = st.columns(2)
    
    with col1:
        # Ενημερώνουμε το κεντρικό fixed_cost - Συγχρονισμένο με Stage 0 & 1
        st.session_state.fixed_cost = st.number_input(
            "Total Annual Operating Fixed Costs (€)", 
            min_value=0.0, 
            value=float(st.session_state.get('fixed_cost', 200000.0)),
            help="Rent, Salaries, Admin, Software"
        )
        
    with col2:
        # Ενημερώνουμε το Debt Service (Το κεφάλαιο + τόκοι που πρέπει να πληρωθούν μετρητά)
        st.session_state.annual_loan_payment = st.number_input(
            "Annual Debt Service (Principal + Interest) (€)", 
            min_value=0.0, 
            value=float(st.session_state.get('annual_loan_payment', 12000.0))
        )

    # 3. RE-COMPUTE AFTER INPUTS
    metrics = compute_core_metrics()
    surv_bep = metrics.get('survival_bep', 0)
    
    # 4. RESULTS DISPLAY (Executive Metrics)
    st.divider()
    res1, res2, res3 = st.columns(3)
    
    with res1:
        st.metric("Survival BEP (Units)", f"{surv_bep:,.0f}")
        st.caption("Covers: Fixed + Debt + WC Drain")

    with res2:
        st.metric("Operating EBIT", f"{metrics['ebit']:,.0f} €")
        st.caption("Core Operating Performance")

    with res3:
        # True bottom line after accounting for taxes and the cash needed for working capital
        st.metric("Net Economic Profit", f"{metrics['net_profit']:,.0f} €", 
                  delta=f"-{liquidity_drain:,.0f} Cash Friction", delta_color="inverse")
        st.caption("Net after Tax & Liquidity Drain")

    # 5. SURVIVAL ANALYSIS (Strategic Signals)
    st.divider()
    
    # Οπτικοποίηση του Stress Test
    if surv_bep > 0:
        utilization = q_annual / surv_bep
        st.write(f"**Survival Capacity Utilization: {utilization:.1%}**")
        st.progress(min(utilization, 1.0))
    
    

    if q_annual < surv_bep:
        st.error(f"🔴 **Survival Alert:** The system is structurally non-viable at current volume. "
                 f"You are {surv_bep - q_annual:,.0f} units below the survival threshold.")
    else:
        safety_buffer = q_annual - surv_bep
        buffer_pct = (safety_buffer / q_annual) * 100 if q_annual > 0 else 0
        st.success(f"🟢 **Operational Surplus:** System is stable. "
                   f"Safety buffer: {safety_buffer:,.0f} units ({buffer_pct:.1f}%).")

    # Risk Factor: Liquidity vs EBIT (Cold Analysis)
    ebit = metrics.get('ebit', 0)
    if ebit > 0:
        friction_ratio = (liquidity_drain / ebit) * 100
        if friction_ratio > 30:
            st.warning(f"⚠️ **Efficiency Risk:** Cash friction (Working Capital) consumes {friction_ratio:.1f}% of operating profit. "
                       f"The business is 'cash-heavy' despite being profitable.")
        elif friction_ratio > 100:
             st.error("🚨 **Liquidity Trap:** Working Capital needs exceed total EBIT. The business is growing into a cash hole.")

    # 6. NAVIGATION
    st.divider()
    nav1, nav2 = st.columns(2)
    with nav1:
        if st.button("⬅️ Back to CLV Analysis", use_container_width=True):
            st.session_state.flow_step = 3
            st.rerun()
    with nav2:
        if st.button("Proceed to Strategic Synthesis (Stage 5) ➡️", type="primary", use_container_width=True):
            st.session_state.flow_step = 5
            st.rerun()
