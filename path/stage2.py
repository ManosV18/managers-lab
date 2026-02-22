import streamlit as st
from core.engine import compute_core_metrics

def run_stage2():
    st.header("💰 Stage 2: Capital & Financing Structure")
    st.caption("Analyze how debt and interest impact your survival threshold.")

    # 1. RECALCULATE METRICS
    metrics = compute_core_metrics()
    
    col1, col2 = st.columns(2)

    # =====================================================
    # DEBT & INTEREST INPUTS
    # =====================================================
    with col1:
        st.subheader("Financing Parameters")
        
        st.session_state.debt = st.number_input(
            "Total Outstanding Debt (€)",
            min_value=0.0,
            value=float(st.session_state.get('debt', 0.0)),
            step=5000.0
        )
        
        # Display as percentage, store as decimal
        input_rate = st.number_input(
            "Annual Interest Rate (%)",
            min_value=0.0,
            max_value=100.0,
            value=float(st.session_state.get('interest_rate', 0.0) * 100),
            step=0.5
        )
        st.session_state.interest_rate = input_rate / 100

    # =====================================================
    # CASH DRAIN VISUALIZATION
    # =====================================================
    with col2:
        st.subheader("Financial Obligations")
        st.metric("Annual Interest Expense", f"{metrics['interest']:,.0f} €")
        st.metric("Liquidity Drain (Working Cap)", f"{st.session_state.get('liquidity_drain_annual', 0.0):,.0f} €")

    st.divider()

    # =====================================================
    # IMPACT ANALYSIS
    # =====================================================
    st.subheader("Survival Impact Analysis")
    
    # Visualizing how debt pushes the BEP higher
    

    c1, c2, c3 = st.columns(3)
    
    # Calculate the 'Financial Gap'
    bep_increase = metrics['survival_bep'] - metrics['operating_bep']
    
    c1.metric("Survival BEP", f"{metrics['survival_bep']:,.0f} units")
    c2.metric("Debt 'Tax' (in Units)", f"{bep_increase:,.0f} units", 
              help="Extra units you must sell just to pay for your financing and maintain liquidity.")
    c3.metric("Net Economic Profit", f"{metrics['net_profit']:,.0f} €")

    # COLD VERDICT
    if metrics['net_profit'] < 0:
        st.error("🚨 **Structural Failure:** Your net profit is negative after financing costs. The business is currently a 'wealth-destroyer'.")
    else:
        st.success("✅ **Sustainable Structure:** The business generates enough margin to service its debt and maintain liquidity.")

    # =====================================================
    # NAVIGATION
    # =====================================================
    st.divider()
    nav1, nav2 = st.columns(2)
    with nav1:
        if st.button("⬅️ Back to Break-Even"):
            st.session_state.flow_step = 1
            st.rerun()
    with nav2:
        if st.button("Proceed to Stage 3 (Cash Cycle) ➡️", type="primary"):
            st.session_state.flow_step = 3
            st.rerun()
