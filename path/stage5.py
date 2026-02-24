import streamlit as st
from core.engine import compute_core_metrics

def run_stage5():
    st.header("🏁 Stage 5: Strategic Recovery & Decision")
    st.caption("Final Synthesis: Choosing the path to structural viability.")

    metrics = compute_core_metrics()
    s = st.session_state

    # 1. FINAL PERFORMANCE SNAPSHOT
    st.subheader("Current Vital Signs")
    c1, c2, c3 = st.columns(3)
    
    fcf = metrics['fcf']
    c1.metric("Annual FCF", f"{fcf:,.0f} €")
    c2.metric("Survival BEP", f"{metrics['survival_bep']:,.0f} Units")
    
    # Runway calculation
    monthly_net = fcf / 12
    runway = (s.opening_cash_balance - metrics['total_wc_requirement']) / abs(monthly_net) if monthly_net < 0 else 100
    c3.metric("Final Runway", f"{runway:,.1f} Months" if runway < 100 else "Stable")

    # 2. STRATEGIC PIVOT SIMULATION
    st.divider()
    st.subheader("Choose Your Recovery Path")
    
    choice = st.radio("Primary Strategic Focus:", 
                     ["Path A: Margin Optimization (Efficiency)", 
                      "Path B: Volume Aggression (Scaling)"])

    if choice == "Path A: Margin Optimization (Efficiency)":
        st.info("🎯 Focus: Increasing Unit Contribution by cutting Variable Costs or raising Price.")
        target_increase = st.slider("Target Margin Improvement (€ per unit)", 0.0, 50.0, 10.0)
        
        # Simulation
        sim_unit_cont = metrics['unit_contribution'] + target_increase
        sim_bep = metrics['cash_wall'] / sim_unit_cont
        
        st.write(f"New Survival BEP: **{sim_bep:,.0f} units** (Reduction of {metrics['survival_bep'] - sim_bep:,.0f} units)")
        
    else:
        st.info("🚀 Focus: Increasing Sales Volume through market expansion.")
        target_vol = st.slider("Target Volume Increase (Units)", 0, 5000, 1000)
        
        # Simulation
        sim_vol = s.volume + target_vol
        sim_fcf = (metrics['unit_contribution'] * sim_vol) - metrics['cash_wall'] + metrics['total_wc_requirement']
        
        st.write(f"New Projected FCF: **{sim_fcf:,.0f} €**")

    # 3. THE COLD DECISION (GO / NO-GO)
    st.divider()
    st.subheader("Final Mandate")
    
    if fcf < 0 and runway < 6:
        st.error("❌ **NO-GO:** The system is in a state of terminal collapse. Immediate restructuring or liquidation is the only analytical conclusion.")
    elif fcf < 0:
        st.warning("⚠️ **TRANSITION:** The system is viable but requires immediate execution of the chosen recovery path.")
    else:
        st.success("✅ **GO:** The business model is structurally sound. Focus on optimizing the surplus.")

    

    # 4. RESET
    if st.button("🔄 Restart War Room Analysis", use_container_width=True):
        st.session_state.flow_step = 0
        st.session_state.baseline_locked = False
        st.rerun()
