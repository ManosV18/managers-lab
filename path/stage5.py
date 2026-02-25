import streamlit as st
from core.sync import sync_global_state

def run_stage5():
    st.header("🏁 Stage 5: Strategic Recovery & Decision")
    st.caption("Final Synthesis: Choosing the structural path to viability.")
    st.divider()

    # 1. FINAL SYNC
    m = sync_global_state()
    s = st.session_state

    st.subheader("Current Vital Signs (Post-Intervention)")
    c1, c2, c3 = st.columns(3)
    c1.metric("Annual FCF", f"{m['fcf']:,.0f} €")
    c2.metric("Survival BEP", f"{m['survival_bep']:,.0f} Units")
    
    runway = m['runway_months']
    runway_label = f"{runway:,.1f} Mo" if runway < 100 else "Stable (∞)"
    c3.metric("Final Runway", runway_label, 
              delta="Target Reached" if runway >= 12 else "Critical", 
              delta_color="normal" if runway >= 12 else "inverse")

    # 2. STRATEGIC PIVOT SIMULATION
    st.divider()
    st.subheader("Simulate Final Recovery Strategy")
    choice = st.radio("Primary Focus for Recovery:", 
                      ["Path A: Margin Optimization (Efficiency)", 
                       "Path B: Volume Aggression (Scale)"])

    if choice == "Path A: Margin Optimization (Efficiency)":
        st.info("🎯 **Objective:** Reduce the 'Cash Wall' by improving unit contribution.")
        target_inc = st.slider("Target Margin Improvement (€/unit)", 0.0, 100.0, 15.0)
        
        sim_unit_cont = m['unit_contribution'] + target_inc
        sim_bep = m['cash_wall'] / sim_unit_cont if sim_unit_cont > 0 else float('inf')
        
        st.write(f"New Survival BEP: **{sim_bep:,.0f} units**")
        st.write(f"Volume reduction needed for break-even: **{max(0.0, m['survival_bep'] - sim_bep):,.0f} units**")
        
    else:
        st.info("🚀 **Objective:** Outrun fixed costs through aggressive sales growth.")
        target_vol_inc = st.slider("Target Volume Increase (Units)", 0, 10000, 2000)
        
        sim_vol = s.volume + target_vol_inc
        sim_fcf = (m['unit_contribution'] * sim_vol) - (s.fixed_cost + s.annual_loan_payment)
        
        st.write(f"New Projected FCF: **{sim_fcf:,.0f} €**")
        st.write(f"FCF Delta from Growth: **{sim_fcf - m['fcf']:+.0f} €**")

    # 3. THE COLD CONCLUSION
    st.divider()
    st.subheader("Final Mandate")
    if m['fcf'] < 0 and runway < 6:
        st.error("❌ **TERMINAL FAILURE:** The system collapses in less than 6 months. Analytical conclusion: Liquidation.")
    elif m['fcf'] < 0:
        st.warning("⚠️ **FRAGILE SURVIVAL:** You have bought time, but the business remains structurally deficient.")
    else:
        st.success("✅ **STRUCTURAL VIABILITY:** The business model is now stable. Focus on surplus optimization.")

    # 4. SYSTEM RESET
    st.divider()
    col_back, col_reset = st.columns(2)
    with col_back:
        if st.button("⬅️ Back to Stage 4", use_container_width=True):
            st.session_state.flow_step = "stage4"
            st.rerun()
    with col_reset:
        if st.button("🔄 Restart Analysis", type="secondary", use_container_width=True):
            # Καθαρισμός μόνο των απαραίτητων για επανεκκίνηση
            st.session_state.flow_step = "stage0"
            st.session_state.baseline_locked = False
            st.rerun()
