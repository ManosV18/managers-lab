import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import numpy as np

# =================================================================
# 1. CORE ENGINE SETTINGS & INITIALIZATION
# =================================================================
st.set_page_config(page_title="Managers' Lab Engine", layout="wide")

def initialize_state():
    """Αρχικοποίηση του Shared Core State"""
    if 'flow_step' not in st.session_state:
        st.session_state.flow_step = 0
    
    defaults = {
        'price': 100.0,
        'volume': 1000,
        'variable_cost': 60.0,
        'fixed_operating_cost': 50000.0,
        'annual_loan_payment': 12000.0,
        'cost_of_capital': 0.10,
        'dso': 45,
        'dio': 60,
        'dpo': 30,
        'retention_rate': 0.85,
        'cac': 150.0,
        'purch_per_year': 4.0,
        'liquidity_drain_annual': 0.0,
        'total_fixed_cost': 0.0
    }
    for key, val in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = val

initialize_state()

# =================================================================
# 2. GLOBAL DERIVED CALCULATIONS
# =================================================================
# Αυτά τρέχουν σε κάθε rerun για να είναι πάντα συγχρονισμένα
price = st.session_state.price
volume = st.session_state.volume
vc = st.session_state.variable_cost
foc = st.session_state.fixed_operating_cost

unit_contribution = price - vc
revenue = price * volume
operating_bep = foc / unit_contribution if unit_contribution > 0 else 0

# =================================================================
# 3. STAGE FUNCTIONS
# =================================================================

def stage_0_calibration():
    st.header("⚙️ Stage 0: System Calibration")
    st.caption("Establish core economic parameters. All subsequent stages depend on these inputs.")
    
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Revenue Structure")
        st.session_state.price = st.number_input("Price per Unit (€)", min_value=0.1, value=float(st.session_state.price))
        st.session_state.volume = st.number_input("Annual Volume (Units)", min_value=1, value=int(st.session_state.volume))
        st.metric("Annual Revenue", f"{revenue:,.2f} €")

    with col2:
        st.subheader("Cost Structure")
        st.session_state.variable_cost = st.number_input("Variable Cost per Unit (€)", min_value=0.0, value=float(st.session_state.variable_cost))
        st.session_state.fixed_operating_cost = st.number_input("Annual Fixed Operating Costs (€)", min_value=0.0, value=float(st.session_state.fixed_operating_cost))
        st.metric("Unit Contribution", f"{unit_contribution:,.2f} €", f"{(unit_contribution/price if price > 0 else 0):.1%}")

    st.divider()
    if st.button("Lock Baseline & Continue ➡️", type="primary", use_container_width=True):
        st.session_state.flow_step = 1
        st.rerun()

def stage_1_operating_bep():
    st.header("📉 Stage 1: Operating Break-Even")
    st.info("Operating BEP = fixed_operating_cost / unit_contribution. This covers only the base overhead.")
    
    res1, res2 = st.columns(2)
    res1.metric("Operating BEP Units", f"{operating_bep:,.0f}")
    res2.metric("Operating BEP Revenue", f"{(operating_bep * price):,.2f} €")

    # Chart logic
    max_x = int(max(operating_bep, volume) * 1.5)
    x_vals = np.linspace(0, max_x, 20)
    rev_y = x_vals * price
    costs_y = foc + (x_vals * vc)

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=x_vals, y=rev_y, name='Revenue', line=dict(color='#00CC96')))
    fig.add_trace(go.Scatter(x=x_vals, y=costs_y, name='Op. Costs', line=dict(color='#EF553B')))
    fig.update_layout(title="Operating Break-Even Visualization", template="plotly_dark")
    st.plotly_chart(fig, use_container_width=True)

    nav1, nav2 = st.columns(2)
    if nav1.button("⬅️ Back to Calibration"): st.session_state.flow_step = 0; st.rerun()
    if nav2.button("Stage 2: Liquidity Physics ➡️"): st.session_state.flow_step = 2; st.rerun()

def stage_2_liquidity():
    st.header("💰 Stage 2: Liquidity Physics")
    st.info("Measures the cost of capital tied up in the business cycle.")
    
    col1, col2, col3 = st.columns(3)
    st.session_state.dso = col1.number_input("DSO (Receivables)", value=int(st.session_state.dso))
    st.session_state.dio = col2.number_input("DIO (Inventory)", value=int(st.session_state.dio))
    st.session_state.dpo = col3.number_input("DPO (Payables)", value=int(st.session_state.dpo))
    
    ccc = st.session_state.dso + st.session_state.dio - st.session_state.dpo
    wcr = revenue * (ccc / 365) # Working Capital Required
    
    coc = st.number_input("Cost of Capital (WACC) %", value=float(st.session_state.cost_of_capital * 100)) / 100
    st.session_state.cost_of_capital = coc
    
    # OUTPUT FOR STAGE 4
    st.session_state.liquidity_drain_annual = wcr * coc

    st.divider()
    res1, res2, res3 = st.columns(3)
    res1.metric("CCC (Days)", f"{ccc}")
    res2.metric("Capital Required", f"{wcr:,.2f} €")
    res3.metric("Annual Liquidity Cost", f"{st.session_state.liquidity_drain_annual:,.2f} €")

    nav1, nav2 = st.columns(2)
    if nav1.button("⬅️ Back"): st.session_state.flow_step = 1; st.rerun()
    if nav2.button("Stage 3: Customer Engine ➡️"): st.session_state.flow_step = 3; st.rerun()

def stage_3_customer_economics():
    st.header("📊 Stage 3: Customer Engine (Analytical)")
    st.caption("Customer Lifetime Value Analysis (Parallel Layer)")
    
    col1, col2 = st.columns(2)
    with col1:
        st.session_state.cac = st.number_input("CAC (€)", value=float(st.session_state.cac))
        st.session_state.purch_per_year = st.number_input("Purchases/Year", value=float(st.session_state.purch_per_year))
    with col2:
        st.session_state.retention_rate = st.slider("Retention %", 0, 100, int(st.session_state.retention_rate * 100)) / 100

    churn = 1 - st.session_state.retention_rate
    clv = (unit_contribution * st.session_state.purch_per_year) / (churn + 0.1)
    ltv_cac = clv / st.session_state.cac if st.session_state.cac > 0 else 0

    st.metric("LTV / CAC Ratio", f"{ltv_cac:.2f}x")
    
    if st.button("Proceed to Structural Survival ➡️"):
        st.session_state.flow_step = 4
        st.rerun()

def stage_4_structural_survival():
    st.header("🏢 Stage 4: Structural Survival Layer")
    st.info("Full Survival BEP = (FOC + Loans + Liquidity Drain) / Unit Contribution")
    
    loan = st.number_input("Annual Debt Service (€)", value=float(st.session_state.annual_loan_payment))
    st.session_state.annual_loan_payment = loan
    
    # THE CORE CALCULATION
    st.session_state.total_fixed_cost = foc + loan + st.session_state.liquidity_drain_annual
    full_survival_bep = st.session_state.total_fixed_cost / unit_contribution if unit_contribution > 0 else 0

    st.divider()
    m1, m2 = st.columns(2)
    m1.metric("Total Fixed Obligations", f"{st.session_state.total_fixed_cost:,.2f} €")
    m2.metric("Full Survival BEP", f"{full_survival_bep:,.0f} Units")

    if volume >= full_survival_bep:
        st.success(f"Viable: {volume - full_survival_bep:,.0f} units surplus over survival threshold.")
    else:
        st.error(f"Structural Deficit: {full_survival_bep - volume:,.0f} additional units needed to cover all costs.")

    nav1, nav2 = st.columns(2)
    if nav1.button("⬅️ Back"): st.session_state.flow_step = 3; st.rerun()
    if nav2.button("Stage 5: Strategy Engine ➡️"): st.session_state.flow_step = 5; st.rerun()

def stage_5_strategy_engine():
    st.header("🏁 Stage 5: Strategic Simulation")
    
    st.subheader("Scenario Modifier (What-If)")
    v_mod = st.slider("Volume Growth %", -30, 100, 0)
    p_mod = st.slider("Price Strategy %", -10, 30, 0)
    
    # Simulation Logic
    sim_p = price * (1 + p_mod/100)
    sim_v = volume * (1 + v_mod/100)
    sim_uc = sim_p - vc
    sim_profit = (sim_uc * sim_v) - st.session_state.total_fixed_cost

    st.divider()
    st.metric("Simulated Net Profit", f"{sim_profit:,.2f} €", 
              delta=f"{sim_profit - ((unit_contribution * volume) - st.session_state.total_fixed_cost):,.2f} € vs Baseline")

    if st.button("🔄 Restart Lab Analysis", use_container_width=True):
        st.session_state.flow_step = 0
        st.rerun()

# =================================================================
# 4. ROUTER
# =================================================================
stages = {
    0: stage_0_calibration,
    1: stage_1_operating_bep,
    2: stage_2_liquidity,
    3: stage_3_customer_economics,
    4: stage_4_structural_survival,
    5: stage_5_strategy_engine
}

stages[st.session_state.flow_step]()
