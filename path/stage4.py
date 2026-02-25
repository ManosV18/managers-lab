import streamlit as st
from core.sync import sync_global_state

def run_stage4():
    st.header("💉 Stage 4: Financing Intervention Lab")
    st.caption("Strategic Maneuvers: Real-time Liquidity & Structural Debt Impact.")
    st.divider()

    # 1. BASELINE SYNC
    m = sync_global_state()
    s = st.session_state
    
    # Baseline Metrics (Current State)
    initial_monthly_net = (m['ocf'] - s.annual_loan_payment) / 12
    initial_oxygen = s.get('opening_cash', 0.0) - m['wc_requirement']
    
    if initial_monthly_net >= 0:
        initial_runway = 100.0
    else:
        initial_runway = max(0.0, initial_oxygen / abs(initial_monthly_net))

    # 2. INTERVENTION CONTROLS
    st.subheader("Simulate Strategic Interventions")
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 🟢 Equity Injection")
        injection = st.number_input("Direct Cash Infusion (€)", min_value=0, value=0, step=5000)
        
        st.markdown("### 🟡 Debt Restructuring")
        new_annual_payment = st.number_input(
            "New Annual Debt Service (€)", 
            min_value=0.0, 
            value=float(s.annual_loan_payment),
            help="Negotiate lower installments or longer duration."
        )

    with col2:
        st.markdown("### 🔵 AR Factoring (WC Release)")
        factoring_pct = st.slider("Factor portion of Accounts Receivable (%)", 0, 100, 0)
        factoring_fee = 0.03 # 3% fee standard
        
    # 3. IMPACT CALCULATION
    # A. Equity
    sim_opening_cash = s.opening_cash + injection
    
    # B. AR Factoring Release
    # Cash released = (AR balance * % factored) - fees
    ar_balance = m.get('accounts_receivable', (s.price * s.volume) * (s.ar_days / 365))
    cash_released_wc = ar_balance * (factoring_pct / 100) * (1 - factoring_fee)
    
    # C. New Liquidity Position
    sim_wc_requirement = m['wc_requirement'] - (ar_balance * (factoring_pct / 100))
    sim_oxygen = sim_opening_cash - sim_wc_requirement + (cash_released_wc - (ar_balance * (factoring_pct / 100)))
    
    # D. New Monthly Flow
    sim_monthly_net = (m['ocf'] - new_annual_payment) / 12
    
    # E. New Runway calculation
    if sim_monthly_net >= 0:
        new_runway_val = 100.0
        display_runway = "Stable (∞)"
    else:
        new_runway_val = max(0.0, sim_oxygen / abs(sim_monthly_net))
        display_runway = f"{new_runway_val:,.1f} Months"

    # 4. SHOW Δ RUNWAY (The Executive Insight)
    st.divider()
    res1, res2 = st.columns(2)
    
    res1.metric("Baseline Runway", 
               f"{initial_runway:,.1f} Mo" if initial_runway < 100 else "Stable")
    
    # Delta Logic
    if initial_runway >= 100 and new_runway_val >= 100:
        delta_text = "Maintained"
    elif new_runway_val >= 100:
        delta_text = "Achieved Stability ✅"
    else:
        diff = new_runway_val - initial_runway
        delta_text = f"{diff:+.1f} Months"

    res2.metric("Projected Runway", 
               display_runway, 
               delta=delta_text, 
               delta_color="normal" if new_runway_val > initial_runway else "off")

    

    # 5. LOCK & PERSIST
    st.info(f"**Impact Summary:** Total Cash unlocked: {injection + cash_released_wc:,.0f}€ | Monthly Burn Change: {((s.annual_loan_payment - new_annual_payment)/12):,.0f}€")

    if st.button("Apply & Lock Financing 🏁", type="primary", use_container_width=True):
        # Update session state with the new structural reality
        st.session_state.opening_cash = sim_opening_cash + cash_released_wc
        st.session_state.annual_loan_payment = new_annual_payment
        st.session_state.flow_step = 5
        st.rerun()

    if st.button("⬅️ Back to Stage 3", use_container_width=True):
        st.session_state.flow_step = 3
        st.rerun()
