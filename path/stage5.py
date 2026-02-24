import streamlit as st
from core.engine import compute_core_metrics

def run_stage5():
    st.header("🏁 Stage 5: Strategic Recovery & Decision")
    st.caption("Final Synthesis: Choosing the path to structural viability.")

    # 1. FINAL PERFORMANCE SNAPSHOT (Single Source of Truth)
    m = compute_core_metrics()
    s = st.session_state

    st.subheader("Current Vital Signs")
    c1, c2, c3 = st.columns(3)
    
    fcf = m['fcf']
    # Χρήση του διορθωμένου naming opening_cash
    current_cash_reserve = s.get('opening_cash', 0.0) - m['total_wc_requirement']
    
    # Runway calculation
    monthly_net = fcf / 12
    runway = current_cash_reserve / abs(monthly_net) if monthly_net < 0 else 100
    
    c1.metric("Annual FCF", f"{fcf:,.0f} €")
    c2.metric("Survival BEP", f"{m['survival_bep']:,.0f} Units")
    c3.metric("Final Runway", f"{runway:,.1f} Months" if runway < 100 else "Stable")

    # 2. STRATEGIC PIVOT SIMULATION
    st.divider()
    st.subheader("Choose Your Recovery Path")
    
    choice = st.radio("Primary Strategic Focus:", 
                     ["Path A: Margin Optimization (Efficiency)", 
                      "Path B: Volume Aggression (Scaling)"])

    

    if choice == "Path A: Margin Optimization (Efficiency)":
        st.info("🎯 **Focus:** Βελτίωση του Unit Contribution μέσω αύξησης τιμής ή μείωσης Variable Costs.")
        target_increase = st.slider("Target Margin Improvement (€ per unit)", 0.0, 100.0, 10.0)
        
        # Simulation Logic
        sim_unit_cont = m['unit_contribution'] + target_increase
        # Το νέο BEP υπολογίζεται πάνω στο ήδη "χειρουργημένο" Cash Wall (από το Stage 4)
        sim_bep = m['cash_wall'] / sim_unit_cont if sim_unit_cont > 0 else float('inf')
        
        st.write(f"New Survival BEP: **{sim_bep:,.0f} units**")
        st.write(f"Reduction in required volume: **{max(0.0, m['survival_bep'] - sim_bep):,.0f} units**")
        
    else:
        st.info("🚀 **Focus:** Επιθετική αύξηση όγκου πωλήσεων για την κάλυψη των σταθερών εξόδων.")
        target_vol_inc = st.slider("Target Volume Increase (Units)", 0, 10000, 1000)
        
        # Simulation Logic
        sim_vol = s.volume + target_vol_inc
        # Νέο FCF = (Νέο Volume * Unit Cont) - (Fixed Costs + Debt Service)
        # Σημείωση: Αγνοούμε την αλλαγή στο WC για την απλότητα του simulation στο stage 5
        sim_fcf = (m['unit_contribution'] * sim_vol) - (s.fixed_cost + s.annual_loan_payment)
        
        st.write(f"New Projected FCF: **{sim_fcf:,.0f} €**")
        st.write(f"Improvement in FCF: **{sim_fcf - fcf:,.0f} €**")

    # 3. THE COLD DECISION (GO / NO-GO)
    st.divider()
    st.subheader("Final Mandate")
    
    if fcf < 0 and runway < 6:
        st.error("❌ **NO-GO:** Το σύστημα βρίσκεται σε κατάσταση τερματικής κατάρρευσης. Η ρευστότητα επαρκεί για λιγότερο από 6 μήνες. Απαιτείται άμεση εκκαθάριση ή ριζική κεφαλαιακή αναδιάρθρωση.")
    elif fcf < 0:
        st.warning("⚠️ **TRANSITION:** Το μοντέλο είναι οριακό. Η επιβίωση εξαρτάται απόλυτα από την επιτυχή εκτέλεση της στρατηγικής που επιλέχθηκε παραπάνω.")
    else:
        st.success("✅ **GO:** Το επιχειρηματικό μοντέλο είναι δομικά υγιές. Η στρατηγική πρέπει να επικεντρωθεί στη μεγιστοποίηση της απόδοσης του πλεονάσματος.")

    # 4. RESET
    st.divider()
    if st.button("🔄 Restart War Room Analysis", use_container_width=True):
        # Καθαρισμός κρίσιμων flags για νέο simulation
        st.session_state.flow_step = 0
        st.session_state.baseline_locked = False
        # Προαιρετικά: s.clear() αν θέλεις πλήρες reset
