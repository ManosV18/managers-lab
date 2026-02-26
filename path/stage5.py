import streamlit as st
from core.sync import sync_global_state

def run_stage5():
    st.header("🏁 Stage 5: Strategic Recovery & Decision")
    st.caption("Final Synthesis: Choosing the structural path to viability.")
    st.divider()

    m = sync_global_state()
    s = st.session_state

    # Data Extraction (Aligned with Engine)
    fcf = float(m.get('fcf', 0.0))
    bep = float(m.get('bep_units', 0.0)) # Διόρθωση ονόματος
    runway = float(m.get('runway_months', 0.0))
    unit_cont = float(m.get('unit_contribution', 0.0))
    fixed_cost = float(s.get('fixed_cost', 0.0))
    loan = float(s.get('annual_debt_service', 0.0)) # Διόρθωση ονόματος
    volume = float(s.get('volume', 0))

    st.subheader("Current Vital Signs (Post-Intervention)")
    c1, c2, c3 = st.columns(3)
    c1.metric("Annual FCF", f"€ {fcf:,.0f}")
    c2.metric("Survival BEP", f"{bep:,.0f} Units")
    
    runway_label = f"{runway:,.1f} Mo" if (runway < 100 and runway > 0) else "Stable (∞)"
    c3.metric("Final Runway", runway_label, 
              delta="Target Reached" if (runway >= 12 or runway < 0) else "Critical", 
              delta_color="normal" if (runway >= 12 or runway < 0) else "inverse")

    # 2. STRATEGIC PIVOT SIMULATION
    st.divider()
    st.subheader("Simulate Final Recovery Strategy")
    choice = st.radio("Primary Focus for Recovery:", 
                      ["Path A: Margin Optimization (Efficiency)", 
                       "Path B: Volume Aggression (Scale)"])

    if choice == "Path A: Margin Optimization (Efficiency)":
        st.info("🎯 **Objective:** Reduce the BEP by improving unit contribution.")
        target_inc = st.slider("Target Margin Improvement (€/unit)", 0.0, 100.0, 15.0)
        
        sim_unit_cont = unit_cont + target_inc
        # BEP = (Fixed Costs + Debt) / Unit Contribution
        sim_bep = (fixed_cost + loan) / sim_unit_cont if sim_unit_cont > 0 else 0
        
        st.write(f"New Survival BEP: **{sim_bep:,.0f} units**")
        st.write(f"Efficiency Gain (BEP Reduction): **{max(0.0, bep - sim_bep):,.0f} units**")
        
    else:
        st.info("🚀 **Objective:** Outrun fixed costs through aggressive sales growth.")
        target_vol_inc = st.slider("Target Volume Increase (Units)", 0, 10000, 2000)
        
        sim_vol = volume + target_vol_inc
        sim_fcf = (unit_cont * sim_vol) - (fixed_cost + loan)
        
        st.write(f"New Projected FCF: **€ {sim_fcf:,.0f}**")
        st.write(f"FCF Delta from Growth: **€ {sim_fcf - fcf:+.0f}**")

    # 

    # 3. THE COLD CONCLUSION
    st.divider()
    st.subheader("Final Mandate")
    if fcf < 0 and (runway < 6 and runway > 0):
        st.error("❌ **TERMINAL FAILURE:** The system collapses in less than 6 months. Analytical conclusion: Liquidation.")
    elif fcf < 0:
        st.warning("⚠️ **FRAGILE SURVIVAL:** You have bought time, but the business remains structurally deficient.")
    else:
        st.success("✅ **STRUCTURAL VIABILITY:** The business model is now stable. Focus on surplus optimization.")

    # 4. SYSTEM RESET & NAVIGATION
    st.divider()
    col_back, col_reset = st.columns(2)
    with col_back:
        if st.button("⬅️ Back to Stage 4", use_container_width=True):
            st.session_state.flow_step = "stage4"
            st.rerun()
    with col_reset:
        if st.button("🔄 Restart Analysis", type="secondary", use_container_width=True):
            st.session_state.flow_step = "stage0"
            st.session_state.baseline_locked = False
            st.rerun()
