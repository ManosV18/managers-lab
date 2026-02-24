import streamlit as st
from core.engine import compute_core_metrics

def run_stage4():
    st.header("💉 Stage 4: Financing Intervention Lab")
    st.caption("Strategic Maneuvers: Liquidity Injections & Debt Optimization.")

    m = compute_core_metrics()
    s = st.session_state
    
    # 1. Baseline Sync
    initial_monthly_net = (m['ocf'] - s.annual_loan_payment) / 12
    initial_oxygen = s.get('opening_cash', 0.0) - m['total_wc_requirement']
    initial_runway = initial_oxygen / abs(initial_monthly_net) if initial_monthly_net < 0 else 100.0

    # 2. Controls
    col1, col2 = st.columns(2)
    with col1:
        injection = st.number_input("Equity Injection (€)", min_value=0, value=0, step=5000)
        new_annual_payment = st.number_input("New Annual Debt Service (€)", min_value=0.0, value=float(s.annual_loan_payment))
    with col2:
        factoring_pct = st.slider("AR Factoring (%)", 0, 100, 0)
        factoring_fee = 0.03
        
    # 3. Impact Calculation
    # Equity injection
    sim_opening_cash = s.opening_cash + injection
    # Factoring release
    ar_balance = (s.price * s.volume) * (s.ar_days / 365)
    cash_released_wc = ar_balance * (factoring_pct / 100) * (1 - factoring_fee)
    
    sim_wc_requirement = m['total_wc_requirement'] - cash_released_wc
    sim_oxygen = sim_opening_cash - sim_wc_requirement
    sim_monthly_net = (m['ocf'] - new_annual_payment) / 12
    
    # 4. Runway Delta
    new_runway_val = sim_oxygen / abs(sim_monthly_net) if sim_monthly_net < 0 else 100.0
    
    st.divider()
    res1, res2 = st.columns(2)
    res1.metric("Baseline Runway", f"{initial_runway:,.1f} Mo" if initial_runway < 100 else "Stable")
    
    # Delta Logic
    diff = new_runway_val - initial_runway
    delta_text = f"{diff:+.1f} Months" if new_runway_val < 100 else "Achieved Stability"
    res2.metric("New Runway", f"{new_runway_val:,.1f} Mo" if new_runway_val < 100 else "Stable", delta=delta_text)

    # 5. Clean State Persistence (Refinement: Cleaner Normalization)
    if st.button("Apply & Lock Interventions 🏁", type="primary", use_container_width=True):
        # s.opening_cash reflects the new structural cash position
        s.opening_cash = sim_opening_cash + cash_released_wc
        s.annual_loan_payment = new_annual_payment
        s.flow_step = 5
        st.rerun()
