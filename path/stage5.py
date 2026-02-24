import streamlit as st
from core.engine import compute_core_metrics

def run_stage5():
    st.header("🏁 Stage 5: Strategic Recovery & Decision")
    st.caption("Final Synthesis: Choosing the structural path to viability.")

    # 1. FINAL SYNC (Single Source of Truth)
    # This pulls the metrics after all Stage 4 interventions are locked
    m = compute_core_metrics()
    s = st.session_state

    # Calculation of Final Liquidity Position
    # monthly_net = (OCF - Debt Service) / 12
    monthly_net = (m["ocf"] - s.annual_loan_payment) / 12
    current_cash_reserve = s.get('opening_cash', 0.0) - m['total_wc_requirement']
    
    runway = current_cash_reserve / abs(monthly_net) if monthly_net < 0 else 100.0

    st.subheader("Current Vital Signs (Post-Intervention)")
    c1, c2, c3 = st.columns(3)
    c1.metric("Annual FCF", f"{m['fcf']:,.0f} €")
    c2.metric("Survival BEP", f"{m['survival_bep']:,.0f} Units")
    
    # Runway Status
    runway_label = f"{runway:,.1f} Mo" if runway < 100 else "Stable (∞)"
    c3.metric("Final Runway", runway_label, delta="Stable" if runway >= 100 else "Limited", delta_color="normal" if runway >= 100 else "inverse")

    # 2. STRATEGIC PIVOT SIMULATION
    st.divider()
    st.subheader("Simulate Recovery Strategy")
    st.write("Determine which lever—Margin or Volume—closes the structural gap most effectively.")
    
    choice = st.radio("Primary Strategic Focus:", 
                     ["Path A: Margin Optimization (Efficiency)", 
                      "Path B: Volume Aggression (Scaling)"])

    

    if choice == "Path A: Margin Optimization (Efficiency)":
        st.info("🎯 **Target:** Improving Unit Contribution by increasing Price or reducing Variable Costs.")
        target_inc = st.slider("Target Margin Improvement (€/unit)", 0.0, 100.0, 15.0)
        
        sim_unit_cont = m['unit_contribution'] + target_inc
        # New BEP based on the 'locked' fixed costs and debt service from Stage 4
        sim_bep = (s.fixed_cost + s.annual_loan_payment + m['total_wc_requirement']) / sim_unit_cont if sim_unit_cont > 0 else float('inf')
        
        st.write(f"New Survival BEP: **{sim_bep:,.0f} units**")
        st.write(f"Required Volume Reduction: **{max(0.0, m['survival_bep'] - sim_bep):,.0f} units**")
        
    else:
        st.info("🚀 **Target:** Aggressive market expansion to cover fixed obligations through scale.")
        target_vol_inc = st.slider("Target Volume Increase (Units)", 0, 10000, 2000)
        
        sim_vol = s.volume + target_vol_inc
        # New FCF = (Volume * Unit Cont) - (Fixed Costs + Debt Service)
        sim_fcf = (m['unit_contribution'] * sim_vol) - (s.fixed_cost + s.annual_loan_payment)
        
        st.write(f"New Projected FCF: **{sim_fcf:,.0f} €**")
        st.write(f"FCF Improvement: **{sim_fcf - m['fcf']:+.0f} €**")

    # 3. THE COLD CONCLUSION (Final Mandate)
    st.divider()
    st.subheader("Final Mandate")
    
    if m['fcf'] < 0 and runway < 6:
        st.error("❌ **TERMINAL FAILURE:** Despite interventions, the system collapses in less than 6 months. Liquidation or immediate suspension of operations is the only analytical conclusion.")
    elif m['fcf'] < 0:
        st.warning("⚠️ **FRAGILE SURVIVAL:** You have 'bought time,' but the business remains structurally deficient. Pivot execution is now a matter of life or death.")
    else:
        st.success("✅ **STRUCTURAL VIABILITY:** The business model is now stable. Shift focus from survival to growth and surplus optimization.")

    

    # 4. SYSTEM RESET
    st.divider()
    if st.button("🔄 Restart War Room Analysis", type="secondary", use_container_width=True):
        st.session_state.flow_step = 0
        st.session_state.baseline_locked = False
        st.rerun()
