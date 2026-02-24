import streamlit as st
from core.engine import compute_core_metrics

def run_stage4():
    st.header("💉 Stage 4: Financing Intervention Lab")
    st.caption("Strategic Maneuvers: Testing liquidity injections and structural debt changes.")

    # 1. BASELINE SYNC (Single Source of Truth)
    m = compute_core_metrics()
    s = st.session_state
    
    # Baseline Runway Calculation
    monthly_net_baseline = m['fcf'] / 12
    initial_oxygen = s.get('opening_cash', 0.0) - m['total_wc_requirement']
    
    if monthly_net_baseline >= 0:
        initial_runway = 100.0  # Stable
    else:
        initial_runway = max(0.0, initial_oxygen / abs(monthly_net_baseline))

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
        factoring_fee = 0.03 
        
    # 3. CALCULATE IMPACT
    new_oxygen = initial_oxygen + injection
    
    # Factoring Impact
    ar_balance = (s.price * s.volume) * (s.ar_days / 365)
    cash_released = ar_balance * (factoring_pct / 100) * (1 - factoring_fee)
    new_oxygen += cash_released
    
    # Monthly Flow Impact
    new_monthly_net = (m['ocf'] - new_annual_payment) / 12
    
    # New Runway & Delta Calculation
    if new_monthly_net >= 0:
        new_runway_val = 100.0 # Stable
        display_runway = "∞ (Stable)"
    else:
        new_runway_val = max(0.0, new_oxygen / abs(new_monthly_net))
        display_runway = f"{new_runway_val:,.1f} Months"

    # --- ΠΡΟΣΘΗΚΗ: RUNWAY DELTA LOGIC ---
    # Υπολογίζουμε πόσους μήνες κερδίσαμε ή χάσαμε
    if initial_runway >= 100 and new_runway_val >= 100:
        runway_delta_text = "Maintained Stability"
    elif new_runway_val >= 100:
        runway_delta_text = "Achieved Stability"
    else:
        diff = new_runway_val - initial_runway
        runway_delta_text = f"{diff:+.1f} Months"

    # 4. RESULTS DASHBOARD
    st.divider()
    res1, res2 = st.columns(2)
    
    res1.metric("Baseline Runway", 
               f"{initial_runway:,.1f} Months" if initial_runway < 100 else "Stable")
    
    # Εδώ εμφανίζουμε το Runway Delta
    res2.metric("New Runway after Intervention", 
               display_runway, 
               delta=runway_delta_text, 
               delta_color="normal" if "Months" in runway_delta_text and (new_runway_val > initial_runway) else "off")

    # 5. COLD ANALYSIS
    st.subheader("🔬 Tactical Assessment")
    
    col_a, col_b = st.columns(2)
    with col_a:
        if injection > 0 or cash_released > 0:
            st.write(f"✅ **Liquidity Boost:** +{injection + cash_released:,.0f}€ immediate oxygen.")
        if new_annual_payment < s.annual_loan_payment:
            st.write(f"📉 **Flow Improvement:** +{(s.annual_loan_payment - new_annual_payment)/12:,.0f}€/month saved.")

    # 6. NAVIGATION
    st.divider()
    if st.button("Apply & Finalize Strategy 🏁", type="primary", use_container_width=True):
        s.opening_cash += (injection + cash_released)
        s.annual_loan_payment = new_annual_payment
        s.flow_step = 5
        st.rerun()
