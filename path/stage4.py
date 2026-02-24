import streamlit as st
from core.engine import compute_core_metrics

def run_stage4():
    st.header("💉 Stage 4: Financing Intervention Lab")
    st.caption("Strategic Maneuvers: Testing liquidity injections and structural debt changes.")

    # 1. BASELINE SYNC (Single Source of Truth)
    m = compute_core_metrics()
    s = st.session_state
    
    # Υπολογισμός αρχικού Runway (Baseline) πριν τις νέες παρεμβάσεις
    # Χρησιμοποιούμε το FCF/12 για το monthly burn rate
    monthly_net_baseline = m['fcf'] / 12
    initial_oxygen = s.get('opening_cash', 0.0) - m['total_wc_requirement']
    
    if monthly_net_baseline >= 0:
        initial_runway = 100 # Stable
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
        factoring_fee = 0.03 # 3% fee on factored amount
        
    # 3. CALCULATE IMPACT
    # Impact of Equity: Αυξάνει το αρχικό οξυγόνο
    new_oxygen = initial_oxygen + injection
    
    # Impact of Factoring: Immediate Cash Release (από το τρέχον AR balance)
    ar_balance = (s.price * s.volume) * (s.ar_days / 365)
    cash_released = ar_balance * (factoring_pct / 100) * (1 - factoring_fee)
    new_oxygen += cash_released
    
    # Impact of Debt Restructuring: Αλλάζει το Monthly Net Flow (μειώνει το bleed)
    # Χρησιμοποιούμε το OCF (Operating Cash Flow) και αφαιρούμε το νέο Debt Service
    new_monthly_net = (m['ocf'] - new_annual_payment) / 12
    
    # New Runway Calculation
    if new_monthly_net >= 0:
        new_runway_val = "∞ (Stable)"
        runway_is_stable = True
    else:
        calc_runway = max(0.0, new_oxygen / abs(new_monthly_net))
        new_runway_val = f"{calc_runway:,.1f} Months"
        runway_is_stable = False

    # 4. RESULTS DASHBOARD
    st.divider()
    res1, res2 = st.columns(2)
    
    res1.metric("Baseline Runway", f"{initial_runway:,.1f} Months" if initial_runway < 100 else "Stable")
    
    delta_val = f"{injection + cash_released:,.0f}€ Liquidity Boost"
    res2.metric("New Runway after Intervention", new_runway_val, 
                delta=delta_val, delta_color="normal")

    # 5. COLD ANALYSIS
    st.subheader("🔬 Tactical Assessment")
    
    
    
    if injection > 0:
        st.write(f"✔️ **Equity Injection:** Προσθέτεις {injection:,.0f}€ στο 'Month 0', αγοράζοντας χρόνο χωρίς να επιβαρύνεις το P&L.")
    
    if factoring_pct > 0:
        st.write(f"⚡ **Factoring:** Απελευθερώνεις {cash_released:,.0f}€ από τις απαιτήσεις σου. Βελτιώνει το 'Month 0' αλλά μειώνει ελαφρώς το μελλοντικό margin λόγω fee.")

    if new_annual_payment < s.annual_loan_payment:
        reduction = (s.annual_loan_payment - new_annual_payment) / 12
        st.write(f"📉 **Debt Restructuring:** Μειώνεις το μηνιαίο bleed κατά {reduction:,.0f}€. Αυτό είναι το πιο ισχυρό εργαλείο για δομική επιβίωση.")

    # 6. NAVIGATION
    st.divider()
    if st.button("Apply & Finalize Strategy 🏁", type="primary", use_container_width=True):
        # Ενημερώνουμε το state με τις νέες "πολεμικές" παραμέτρους
        s.opening_cash += (injection + cash_released)
        s.annual_loan_payment = new_annual_payment
        s.flow_step = 5
        st.rerun()
