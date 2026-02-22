import streamlit as st
import pandas as pd

def run_step():
    st.header("🏢 Stage 4: Sustainability & Structural Break-Even")
    st.info("Annual analysis of fixed costs, debt, and inventory carrying costs.")

    # 1. DYNAMIC SYNC WITH STAGE 0 & STAGE 2
    # Fetching annual data to maintain consistency with Stage 1
    p = st.session_state.get('price', 100.0)
    vc = st.session_state.get('variable_cost', 60.0)
    q_annual = st.session_state.get('volume', 1000.0)
    
    # Inventory carrying cost (Annual) from Stage 2
    liquidity_drain_annual = st.session_state.get('liquidity_drain', 0.0)
    
    unit_margin = p - vc
    annual_revenue = p * q_annual

    st.write(f"**🔗 Linked to Global Data:** Annual Volume: {q_annual:,.0f} units | Unit Margin: {unit_margin:,.2f} €")

    # 2. ANNUAL FIXED COSTS INPUTS
    st.subheader("Annual Operating Obligations")
    col1, col2 = st.columns(2)
    with col1:
        # We multiply by 12 if the user thinks in monthly terms, or input annual directly
        annual_rent = st.number_input("Annual Rent & Utilities (€)", value=18000.0)
        annual_salaries = st.number_input("Annual Salaries & Insurance (€)", value=54000.0)
    with col2:
        annual_loan = st.number_input("Annual Debt Service (€)", value=12000.0)
        annual_admin = st.number_input("Annual Admin & Software (€)", value=6000.0)

    # 3. CALCULATIONS (All Annual)
    total_fixed_costs = annual_rent + annual_salaries + annual_admin
    ebit = (unit_margin * q_annual) - total_fixed_costs
    
    # Total obligations include fixed costs + debt repayment
    total_annual_obligations = total_fixed_costs + annual_loan
    
    # Break-Even Point in Units (Annual)
    if unit_margin > 0:
        be_units_annual = total_annual_obligations / unit_margin
    else:
        be_units_annual = 0

    # Final Net Profit after inventory "Slow-Stock Penalty"
    final_net_profit = ebit - annual_loan - liquidity_drain_annual

    # 4. RESULTS DISPLAY
    st.divider()
    res1, res2, res3 = st.columns(3)
    
    with res1:
        st.metric("Annual BEP Units", f"{be_units_annual:,.0f}")
        st.caption("Units needed to cover all costs")

    with res2:
        st.metric("Annual EBIT", f"{ebit:,.2f} €")
        st.caption("Operating profit before debt")

    with res3:
        st.metric("Final Net Profit", f"{final_net_profit:,.2f} €", 
                  delta=f"-{liquidity_drain_annual:,.2f} Stock Cost", delta_color="inverse")
        st.caption("Bottom line after all costs")

    # Στο τέλος του βήματος 4 (Results & Sync), πρόσθεσε:
        st.session_state.liquidity_drain = working_capital_req * 0.10  # Υποθετικό κόστος κεφαλαίου 10%

    # 5. STRATEGIC SIGNAL (Annual Logic)
    st.divider()
    if q_annual < be_units_annual:
        st.error(f"🔴 **Survival Alert:** You are {be_units_annual - q_annual:,.0f} units below the annual break-even point.")
    else:
        st.success(f"🟢 **Operational Surplus:** You are {q_annual - be_units_annual:,.0f} units above the annual survival threshold.")

    if liquidity_drain_annual > (ebit * 0.15) and ebit > 0:
        st.warning(f"⚠️ **Efficiency Risk:** Slow-moving stock costs consume {(liquidity_drain_annual/ebit)*100:.1f}% of annual EBIT.")

    # 6. NAVIGATION
    st.divider()
    nav1, nav2 = st.columns(2)
    with nav1:
        if st.button("⬅️ Back to Stage 3"):
            st.session_state.flow_step = 3
            st.rerun()
    with nav2:
        if st.button("Proceed to Final Strategy (Stage 5) ➡️", type="primary"):
            st.session_state.flow_step = 5
            st.rerun()
