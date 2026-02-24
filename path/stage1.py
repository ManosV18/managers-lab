import streamlit as st
from core.engine import compute_core_metrics

def run_stage1():
    st.header("📈 Stage 1: Efficiency & Unit Economics")
    st.caption("The Atomic Level: Analyzing the profitability of a single transaction.")
    st.divider()

    # 1. FETCH METRICS
    m = compute_core_metrics()
    s = st.session_state

    # 2. KEY PERFORMANCE INDICATORS (Unit Level)
    c1, c2, c3 = st.columns(3)
    
    # Unit Contribution
    c1.metric("Unit Contribution", f"{m['unit_contribution']:,.2f} €", 
              help="Money left to cover fixed costs after variable costs are paid.")
    
    # Contribution Ratio
    c2.metric("Margin Ratio", f"{m['contribution_ratio']*100:.1f}%", 
              help="Percentage of each Euro that contributes to fixed cost coverage.")
    
    # Efficiency Score (Custom Insight)
    efficiency_status = "OPTIMAL" if m['contribution_ratio'] > 0.4 else "THIN"
    c3.metric("Efficiency Status", efficiency_status, 
              delta="Check Pricing" if efficiency_status == "THIN" else "Strong")

    # 3. VISUALIZATION: PRICE VS COSTS
    st.subheader("Unit Cost Structure")
    
    # Δημιουργία δεδομένων για το γράφημα
    cost_data = {
        "Category": ["Variable Cost", "Unit Contribution"],
        "Value": [s.variable_cost, m['unit_contribution']]
    }
    st.bar_chart(data=cost_data, x="Category", y="Value")

    

    # 4. COLD ASSESSMENT
    st.divider()
    st.subheader("🔬 Managerial Insight")
    
    if m['contribution_ratio'] < 0.2:
        st.warning("⚠️ **Low Margin Trap:** Your margins are dangerously thin. A small increase in variable costs or a slight price drop could turn this unit non-viable.")
    elif m['contribution_ratio'] > 0.5:
        st.success("💎 **High Value Unit:** You have significant pricing power or cost efficiency. This unit is a strong engine for scaling.")
    else:
        st.info("⚖️ **Standard Efficiency:** Your unit economics are within typical operational bounds.")

    # 5. NAVIGATION
    st.divider()
    col_prev, col_next = st.columns([1, 1])
    
    with col_prev:
        if st.button("⬅️ Back to Control Center", use_container_width=True):
            st.session_state.flow_step = 0
            st.rerun()
            
    with col_next:
        if st.button("Next: Volume Shock Simulation 📉", type="primary", use_container_width=True):
            st.session_state.flow_step = 2
            st.rerun()
