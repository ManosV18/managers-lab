import streamlit as st
from core.engine import compute_core_metrics

def run_stage4():
    st.header("💉 Stage 4: Financing Intervention Lab")
    st.caption("Strategic Maneuvers: Testing liquidity injections and structural debt changes.")

    # 1. BASELINE SYNC
    metrics = compute_core_metrics()
    s = st.session_state
    
    # Αποθήκευση του αρχικού runway για σύγκριση
    monthly_structural = (s.fixed_cost + s.annual_loan_payment) / 12
    monthly_contribution = (metrics['unit_contribution'] * s.volume) / 12
    monthly_net = monthly_contribution - monthly_structural
    
    initial_oxygen = s.opening_cash_balance - metrics['total_wc_requirement']
    initial_runway = initial_oxygen / abs(monthly_net) if monthly_net < 0 else 100

    # 2. INTERVENTION CONTROLS
    st.subheader("Choose Your Intervention")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 🟢 Equity Injection")
        injection = st.number_input("Direct Cash Infusion (€)", min_value=0, value=0, step=5000)
        
        st.markdown("### 🟡 Debt Restructuring")
        new_annual_payment = st.number_input(
            "New Annual Debt Service (€)", 
            min_value=0.0, 
            value=float(s.annual_loan_payment),
            help="Lowering this extends runway but may increase long-term interest."
        )

    with col2:
        st.markdown("### 🔵 AR Factoring (WC Release)")
        factoring_pct = st.slider("Factor portion of Accounts Receivable (%)", 0, 100, 0)
        factoring_fee = 0.03 # 3% fee on factored amount
        
    # 3. CALCULATE IMPACT
    # Impact of Equity
    new_oxygen = initial_oxygen + injection
    
    # Impact of Factoring (Immediate Cash Release)
    ar_balance = (s.price * s.volume) * (s.ar_days / 365)
    cash_released = ar_balance * (factoring_pct / 100) * (1 - factoring_fee)
    new_oxygen += cash_released
    
    # Impact of Debt Restructuring on Monthly Net Flow
    new_monthly_structural = (s.fixed_cost + new_annual_payment) / 12
    new_monthly_net = monthly_contribution - new_monthly_structural
    
    # New Runway Calculation
    if new_monthly_net >= 0:
        new_runway = "∞ (Stable)"
    else:
        new_runway = f"{max(0.0, new_oxygen / abs(new_monthly_net)):,.1f} Months"

    # 4. RESULTS DASHBOARD
    st.divider()
    res1, res2 = st.columns(2)
    
    res1.metric("Current Runway", f"{initial_runway:,.1f} Months" if initial_runway < 100 else "Stable")
    res2.metric("New Runway after Intervention", new_runway, 
               delta=f"{injection + cash_released:,.0f}€ Liquidity Boost", delta_color="normal")

    # 5. COLD ANALYSIS
    st.subheader("🔬 Tactical Assessment")
    
    if injection > 0:
        st.write(f"✔️ **Equity:** Adding {injection:,.0f}€ buys you linear time but doesn't fix the underlying burn.")
    
    if factoring_pct > 0:
        st.write(f"⚡ **Factoring:** Immediate release of {cash_released:,.0f}€ from your own invoices. High speed, high cost.")

    if new_annual_payment < s.annual_loan_payment:
        st.write(f"📉 **Restructuring:** Lowering debt service by {(s.annual_loan_payment - new_annual_payment)/12:,.0f}€/month reduces the 'bleed' rate.")

    

    # 6. NAVIGATION
    st.divider()
    if st.button("Final Stage: Strategic Recovery 🏁", type="primary", use_container_width=True):
        # Ενημερώνουμε το state με τις αλλαγές αν ο χρήστης θέλει να τις κρατήσει
        s.opening_cash_balance += injection + cash_released
        s.annual_loan_payment = new_annual_payment
        st.session_state.flow_step = 5
        st.rerun()
