import streamlit as st
from core.engine import compute_core_metrics

def run_stage5():
    st.header("🏁 Stage 5: Strategic Recovery & Decision")
    st.caption("Final Synthesis: Choosing the structural path to viability.")

    # 1. FINAL SYNC
    m = compute_core_metrics()
    s = st.session_state

    # Υπολογισμός τρέχοντος Runway (μετά τις παρεμβάσεις του Stage 4)
    monthly_net = (m["ocf"] - s.annual_loan_payment) / 12
    current_cash_reserve = s.get('opening_cash', 0.0) - m['total_wc_requirement']
    
    runway = current_cash_reserve / abs(monthly_net) if monthly_net < 0 else 100.0

    st.subheader("Current Vital Signs (Post-Intervention)")
    c1, c2, c3 = st.columns(3)
    c1.metric("Annual FCF", f"{m['fcf']:,.0f} €")
    c2.metric("Survival BEP", f"{m['survival_bep']:,.0f} Units")
    c3.metric("Final Runway", f"{runway:,.1f} Mo" if runway < 100 else "Stable")

    # 2. STRATEGIC PIVOT SIMULATION
    st.divider()
    st.subheader("Simulate Recovery Strategy")
    
    choice = st.radio("Primary Focus:", 
                     ["Path A: Margin Optimization (Efficiency)", 
                      "Path B: Volume Aggression (Scaling)"])

    

    if choice == "Path A: Margin Optimization (Efficiency)":
        st.info("🎯 **Target:** Βελτίωση Unit Contribution (Τιμή ή Μεταβλητό Κόστος).")
        target_inc = st.slider("Target Margin Improvement (€/unit)", 0.0, 100.0, 15.0)
        
        sim_unit_cont = m['unit_contribution'] + target_inc
        # Νέο BEP βασισμένο στο ήδη μειωμένο Annual Loan Payment από το Stage 4
        sim_bep = (s.fixed_cost + s.annual_loan_payment + m['total_wc_requirement']) / sim_unit_cont
        
        st.write(f"New Survival BEP: **{sim_bep:,.0f} units**")
        st.write(f"Reduction in required volume: **{max(0.0, m['survival_bep'] - sim_bep):,.0f} units**")
        
    else:
        st.info("🚀 **Target:** Επιθετική αύξηση πωλήσεων.")
        target_vol_inc = st.slider("Target Volume Increase (Units)", 0, 10000, 2000)
        
        sim_vol = s.volume + target_vol_inc
        # Νέο FCF = (Volume * Unit Cont) - Fixed - Debt
        sim_fcf = (m['unit_contribution'] * sim_vol) - (s.fixed_cost + s.annual_loan_payment)
        
        st.write(f"New Projected FCF: **{sim_fcf:,.0f} €**")
        st.write(f"FCF Delta: **{sim_fcf - m['fcf']:+.0f} €**")

    # 3. FINAL MANDATE (The Cold Conclusion)
    st.divider()
    st.subheader("Final Mandate")
    
    if m['fcf'] < 0 and runway < 6:
        st.error("❌ **TERMINAL FAILURE:** Παρά τις παρεμβάσεις, η επιχείρηση καταρρέει σε λιγότερο από 6 μήνες. Η ρευστοποίηση ή η πλήρης αναστολή λειτουργίας είναι η μόνη ορθολογική επιλογή.")
    elif m['fcf'] < 0:
        st.warning("⚠️ **FRAGILE SURVIVAL:** Η επιχείρηση 'αγόρασε χρόνο', αλλά παραμένει δομικά ελλειμματική. Η επιτυχία του Pivot είναι θέμα ζωής και θανάτου.")
    else:
        st.success("✅ **VIABLE MODEL:** Το σύστημα είναι πλέον σταθερό. Το focus μετατοπίζεται από την επιβίωση στην ανάπτυξη (Growth).")

    # 4. RESET SYSTEM
    if st.button("🔄 Restart War Room Analysis", use_container_width=True):
        st.session_state.flow_step = 0
        st.session_state.baseline_locked = False
        st.rerun()
