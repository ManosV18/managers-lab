import streamlit as st
from core.engine import compute_core_metrics

def run_stage2():
    st.header("💰 Stage 2: Capital & Cash Cycle")
    st.caption("Analyze how debt and operational efficiency impact your survival threshold.")

    # 1. PRELIMINARY SYNC
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
        input_rate = st.number_input(
            "Annual Interest Rate (%)",
            min_value=0.0,
            max_value=100.0,
            value=float(st.session_state.get('interest_rate', 0.0) * 100),
            step=0.5
        )
        st.session_state.interest_rate = input_rate / 100

    # =====================================================
    # CASH CONVERSION CYCLE (CCC)
    # =====================================================
    with col2:
        st.subheader("Operational Efficiency")
        c1, c2, c3 = st.columns(3)
        dio = c1.number_input("DIO (Stock)", value=st.session_state.get('inventory_days', 60))
        dso = c2.number_input("DSO (Sales)", value=st.session_state.get('ar_days', 45))
        dpo = c3.number_input("DPO (Payables)", value=st.session_state.get('payables_days', 30))

        ccc = dio + dso - dpo
        st.session_state.inventory_days = dio
        st.session_state.ar_days = dso
        st.session_state.payables_days = dpo
        st.session_state.ccc = ccc

    # =====================================================
    # ENGINE UPDATE (CALCULATE DRAIN)
    # =====================================================
    # We update the drain based on the new CCC
    annual_cogs = st.session_state.volume * st.session_state.variable_cost
    # Working Capital required to fund the cycle
    st.session_state.liquidity_drain_annual = (ccc / 365) * annual_cogs
    
    # RE-COMPUTE with new debt and drain data
    metrics = compute_core_metrics()

    st.divider()

    # =====================================================
    # RESULTS & IMPACT ANALYSIS
    # =====================================================
    st.subheader("Survival Impact Analysis")
    
    

    c1, c2, c3 = st.columns(3)
    
    bep_increase = metrics['survival_bep'] - metrics['operating_bep']
    
    c1.metric("Survival BEP", f"{metrics['survival_bep']:,.0f} units", 
              help="Includes Fixed Costs + Interest + Liquidity Drain")
    c2.metric("Cash Friction (Drain)", f"{st.session_state.liquidity_drain_annual:,.0f} €", 
              delta=f"{ccc} days cycle", delta_color="inverse")
    c3.metric("Net Economic Profit", f"{metrics['net_profit']:,.0f} €")

    # COLD VERDICT
    if metrics['net_profit'] < 0:
        st.error("🚨 **Structural Failure:** After debt service and cash cycle friction, the business is depleting capital.")
    else:
        st.success("✅ **Stable Structure:** The business generates enough margin to cover both interest and the cash cycle gap.")

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
        # Changed the label to reflect that CLV is next
        if st.button("Proceed to Stage 3 (CLV) ➡️", type="primary"):
            st.session_state.flow_step = 3
            st.rerun()
