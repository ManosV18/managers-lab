import streamlit as st
from core.engine import compute_core_metrics

def run_stage4():
    st.header("💉 Stage 4: Financing Intervention Lab")
    st.caption("Strategic Maneuvers: Real-time Liquidity & Structural Debt Impact.")

    # 1. BASELINE SYNC (Single Source of Truth)
    m = compute_core_metrics()
    s = st.session_state
    
    # Baseline Metrics (Πριν την παρέμβαση)
    initial_monthly_net = m['fcf'] / 12
    initial_wc_req = m['total_wc_requirement']
    initial_oxygen = s.get('opening_cash', 0.0) - initial_wc_req
    
    if initial_monthly_net >= 0:
        initial_runway = 100.0
    else:
        initial_runway = max(0.0, initial_oxygen / abs(initial_monthly_net))

    # 2. INTERVENTION CONTROLS (Real-time Inputs)
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
            help="Reduces monthly bleed but may extend debt duration."
        )

    with col2:
        st.markdown("### 🔵 AR Factoring (WC Optimization)")
        factoring_pct = st.slider("Factor portion of Accounts Receivable (%)", 0, 100, 0)
        factoring_fee = 0.03 
        
    # 3. EXECUTIVE CALCULATION LOGIC
    # A. Equity: Αυξάνει το opening_cash
    sim_opening_cash = s.opening_cash + injection
    
    # B. AR Factoring: Μειώνει το total_wc_requirement (απελευθερώνει μετρητά)
    ar_balance = (s.price * s.volume) * (s.ar_days / 365)
    cash_released_from_wc = ar_balance * (factoring_pct / 100) * (1 - factoring_fee)
    sim_wc_requirement = initial_wc_req - cash_released_from_wc
    
    # C. New Oxygen (Month 0)
    sim_oxygen = sim_opening_cash - sim_wc_requirement
    
    # D. New Monthly Flow (Debt impact)
    sim_monthly_net = (m['ocf'] - new_annual_payment) / 12
    
    # E. New Runway calculation
    if sim_monthly_net >= 0:
        new_runway_val = 100.0
        display_runway = "∞ (Stable)"
    else:
        new_runway_val = max(0.0, sim_oxygen / abs(sim_monthly_net))
        display_runway = f"{new_runway_val:,.1f} Months"

    # 4. SHOW Δ RUNWAY (The Executive Insight)
    st.divider()
    res1, res2 = st.columns(2)
    
    res1.metric("Baseline Runway", 
               f"{initial_runway:,.1f} Months" if initial_runway < 100 else "Stable")
    
    # Delta Logic
    if initial_runway >= 100 and new_runway_val >= 100:
        delta_text = "Maintained Stability"
    elif new_runway_val >= 100:
        delta_text = "Achieved Stability ✅"
    else:
        diff = new_runway_val - initial_runway
        delta_text = f"{diff:+.1f} Months"

    res2.metric("Projected Runway", 
               display_runway, 
               delta=delta_text, 
               delta_color="normal" if new_runway_val > initial_runway else "off")

    # 5. REAL-TIME IMPACT ANALYSIS
    st.info(f"""
    **Executive Summary of Intervention:**
    * **Liquidity Injection:** +{injection:,.0f}€
    * **WC Released via Factoring:** +{cash_released_from_wc:,.0f}€ (New WC Req: {sim_wc_requirement:,.0f}€)
    * **Monthly Burn Reduction:** +{(s.annual_loan_payment - new_annual_payment)/12:,.0f}€/month
    """)

    # 6. NAVIGATION & STATE PERSISTENCE
    if st.button("Apply & Lock Interventions 🏁", type="primary", use_container_width=True):
        # Εδώ οι αλλαγές γίνονται μόνιμες για το Stage 5
        s.opening_cash = sim_opening_cash
        s.annual_loan_payment = new_annual_payment
        # Σημείωση: Το Factoring στην πράξη μειώνει τις μέρες AR, αλλά εδώ το περνάμε ως cash boost
        s.opening_cash += cash_released_from_wc 
        s.flow_step = 5
        st.rerun()
