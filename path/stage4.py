import streamlit as st
from core.engine import compute_core_metrics

def run_stage4():
    st.header("🏢 Stage 4: Sustainability & Survival Stress Test")
    st.caption("Strategic Audit: Evaluating structural durability against operational friction and debt obligations.")

    # 1. SYNC WITH CORE ENGINE
    metrics = compute_core_metrics()
    
    q_annual = st.session_state.get('volume', 0)
    liquidity_drain = st.session_state.get('liquidity_drain_annual', 0)

    st.info(f"🔗 **Core Engine Linked:** Volume: {q_annual:,.0f} units | Unit Contribution: {metrics['unit_contribution']:.2f} €")

    # 2. FIXED COSTS & DEBT INPUTS
    st.subheader("Annual Structural Obligations")
    col1, col2 = st.columns(2)
    
    with col1:
        st.session_state.fixed_cost = st.number_input(
            "Total Annual Operating Fixed Costs (€)", 
            min_value=0.0, 
            value=float(st.session_state.get('fixed_cost', 200000.0)),
            help="Includes Rent, Salaries, Admin, Insurance, and fixed Software costs.",
            key="fixed_cost_s4"
        )
        
    with col2:
        st.session_state.annual_loan_payment = st.number_input(
            "Annual Debt Service (Principal + Interest) (€)", 
            min_value=0.0, 
            value=float(st.session_state.get('annual_loan_payment', 12000.0)),
            help="The total cash outflow required to service bank debt annually.",
            key="debt_service_s4"
        )

    # 3. RE-COMPUTE AFTER INPUTS
    metrics = compute_core_metrics()
    surv_bep = metrics.get('survival_bep', 0)
    
    # 4. EXECUTIVE METRICS DISPLAY
    st.divider()
    res1, res2, res3 = st.columns(3)
    
    with res1:
        st.metric("Survival BEP (Units)", f"{surv_bep:,.0f}", 
                  help="The volume required to cover Fixed Costs + Debt Service + Working Capital Drain.")

    with res2:
        st.metric("Operating EBIT", f"{metrics['ebit']:,.0f} €", 
                  delta=f"Margin: {metrics['ebit_margin']:.1%}" if 'ebit_margin' in metrics else None)

    with res3:
        # Net profit after considering the cash 'trapped' in operations
        net_econ_profit = metrics['net_profit'] - liquidity_drain
        st.metric("Net Economic Profit", f"{metrics['net_profit']:,.0f} €", 
                  delta=f"-{liquidity_drain:,.0f} Cash Friction", delta_color="inverse",
                  help="Accounting Profit minus Cash tied up in Working Capital.")

    # 5. SURVIVAL ANALYSIS (Shock Test)
    st.divider()
    st.subheader("🔬 Structural Viability Analysis")
    
    # Visualization: Capacity vs Survival
    if surv_bep > 0:
        # Αντιστρέφουμε τη λογική: Δείχνουμε πόσο κοντά είμαστε στο 'γκρεμό'
        safety_margin_pct = ((q_annual - surv_bep) / q_annual) if q_annual > 0 else -1.0
        
        c1, c2 = st.columns([1, 3])
        c1.write("**Safety Margin**")
        c1.write(f"### {safety_margin_pct:.1%}")
        
        # ProgressBar: Red if below BEP, Green if above
        progress_val = min(max(q_annual / surv_bep, 0.0), 1.0) if surv_bep > 0 else 0
        st.progress(progress_val)
        
    

    # Cold Analysis Logic
    if q_annual < surv_bep:
        st.error(f"🔴 **Survival Alert:** The system is structurally non-viable at current volume. "
                 f"You are {surv_bep - q_annual:,.0f} units below the survival threshold. "
                 "The business is consuming its own capital to stay alive.")
    else:
        safety_buffer = q_annual - surv_bep
        st.success(f"🟢 **Operational Surplus:** System is stable. "
                   f"You can withstand a volume drop of {safety_buffer:,.0f} units ({safety_margin_pct:.1%}) "
                   "before the business fails to meet its cash obligations.")

    # Efficiency Assessment
    ebit = metrics.get('ebit', 0)
    if ebit > 0:
        friction_ratio = (liquidity_drain / ebit)
        if friction_ratio > 1.0:
             st.error(f"🚨 **Liquidity Trap:** Working Capital drain ({liquidity_drain:
