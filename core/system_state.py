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



import streamlit as st

def run_step():
    st.header("⚙️ Stage 0: System Calibration")
    st.caption("Establish the core economic parameters of the enterprise.")

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Revenue Structure")
        st.session_state.price = st.number_input("Price per Unit (€)", min_value=0.0, value=float(st.session_state.price))
        st.session_state.volume = st.number_input("Annual Volume (Units)", min_value=0, value=int(st.session_state.volume))
        
        revenue = st.session_state.price * st.session_state.volume
        st.metric("Annual Revenue", f"{revenue:,.0f} €")

    with col2:
        st.subheader("Cost Structure")
        st.session_state.variable_cost = st.number_input("Variable Cost per Unit (€)", min_value=0.0, value=float(st.session_state.variable_cost))
        st.session_state.fixed_cost = st.number_input("Annual Fixed Costs (€)", min_value=0.0, value=float(st.session_state.fixed_cost))

        p = st.session_state.price
        vc = st.session_state.variable_cost
        margin = (p - vc) / p if p > 0 else 0

        if p <= 0:
            st.error("❌ Price must be greater than zero.")
        elif p <= vc:
            st.error(f"❌ Critical: Negative/Zero Margin ({margin:.1%}). Value destruction in progress.")
        elif margin < 0.20:
            st.warning(f"⚠️ Low structural buffer ({margin:.1%}). High sensitivity detected.")
        else:
            st.success(f"✅ Healthy Margin: {margin:.1%}")

    st.divider()

    st.subheader("⏳ Cash Timing & Durability")
    with st.expander("Configure Working Capital Cycle", expanded=False):
        st.caption("Standard industry defaults applied (45/60/30 days). Adjust for precision.")
        c1, c2, c3 = st.columns(3)
        st.session_state.ar_days = c1.number_input("Receivables Days", value=int(st.session_state.ar_days))
        st.session_state.inventory_days = c2.number_input("Inventory Days", value=int(st.session_state.inventory_days))
        st.session_state.payables_days = c3.number_input("Payables Days", value=int(st.session_state.payables_days))

    st.divider()

    if st.button("Lock Baseline & Continue ➡️", use_container_width=True, type="primary"):
        if st.session_state.price > st.session_state.variable_cost:
            st.session_state.baseline_locked = True
            st.session_state.flow_step = 1
            st.session_state.mode = "path"
            st.rerun()
        else:
            st.error("Cannot lock: Non-viable economic structure.")



import streamlit as st
import plotly.graph_objects as go

def run_step():
    st.header("📉 Stage 1: Break-Even Analysis")
    st.info("Calculates the minimum volume needed to cover all variable and fixed costs.")

    # 1. DYNAMIC SYNC FROM STAGE 0
    # Note: Using 'fixed_cost' (singular) to match your Stage 0 code
    price = st.session_state.get('price', 0.0)
    variable_cost = st.session_state.get('variable_cost', 0.0)
    current_volume = st.session_state.get('volume', 0.0)
    
    # Check for Price/Volume to avoid calculation errors
    if price <= 0 or current_volume <= 0:
        st.warning("⚠️ Baseline data missing. Please return to Stage 0.")
        if st.button("⬅️ Back to Stage 0"):
            st.session_state.flow_step = 0
            st.rerun()
        return

    # 2. FIXED COSTS INPUT (Linked to Stage 0)
    st.subheader("Annual Fixed Costs")
    
    # We use a unique key 'fixed_cost_input' but default its value 
    # to the one stored in session_state.fixed_cost
    fixed_cost = st.number_input(
        "Total Annual Fixed Costs (€)", 
        min_value=0.0, 
        value=float(st.session_state.get('fixed_cost', 50000.0)),
        step=1000.0,
        key="fixed_cost_sync"
    )
    
    # Update the global session state so other stages see the change
    st.session_state.fixed_cost = fixed_cost

    # 3. BREAK-EVEN CALCULATIONS
    unit_contribution = price - variable_cost
    
    if unit_contribution > 0:
        be_units = fixed_cost / unit_contribution
        be_revenue = be_units * price
    else:
        be_units = 0
        be_revenue = 0

    # 4. RESULTS DISPLAY
    st.divider()
    res1, res2, res3 = st.columns(3)
    
    with res1:
        st.metric("Break-Even Units", f"{be_units:,.0f}")
    with res2:
        st.metric("Break-Even Revenue", f"{be_revenue:,.2f} €")
    with res3:
        safety_margin = ((current_volume - be_units) / current_volume * 100) if current_volume > 0 else 0
        st.metric("Margin of Safety", f"{safety_margin:.1f}%", 
                  delta=f"{current_volume - be_units:,.0f} units surplus")

    # 5. VISUALIZATION
    
    
    max_x = int(max(be_units, current_volume) * 1.5)
    if max_x == 0: max_x = 100
    x_vals = list(range(0, max_x, max(1, max_x // 20)))
    rev_y = [x * price for x in x_vals]
    costs_y = [fixed_cost + (x * variable_cost) for x in x_vals]

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=x_vals, y=rev_y, name='Total Revenue', line=dict(color='#00CC96')))
    fig.add_trace(go.Scatter(x=x_vals, y=costs_y, name='Total Costs', line=dict(color='#EF553B')))
    fig.add_vline(x=be_units, line_dash="dash", line_color="white", annotation_text="Break-Even Point")
    
    fig.update_layout(title="Annual Break-Even Chart", xaxis_title="Units", yaxis_title="Euros", template="plotly_dark")
    st.plotly_chart(fig, use_container_width=True)

    # 6. NAVIGATION
    nav1, nav2 = st.columns(2)
    with nav1:
        if st.button("⬅️ Back to Calibration"):
            st.session_state.flow_step = 0
            st.rerun()
    with nav2:
        if st.button("Proceed to Stage 2 ➡️", type="primary"):
            st.session_state.flow_step = 2
            st.rerun()


# path/step2_cash.py
"""
Stage 2: Cash Conversion Cycle (CCC)
Measures working capital efficiency and liquidity gap
"""

import streamlit as st


def run_step():
    """Stage 2: Cash Conversion Cycle Analysis"""
    
    st.header("💰 Stage 2: Cash Conversion Cycle (CCC)")
    st.info("Measures the time (in days) it takes to convert investments in inventory into cash flows from sales.")
    
    # ═══════════════════════════════════════════════════════════
    # 1. SYNC WITH SHARED CORE
    # ═══════════════════════════════════════════════════════════
    q = st.session_state.get('volume', 1000)
    vc = st.session_state.get('variable_cost', 12.0)
    p = st.session_state.get('price', 20.0)
    
    annual_cogs = q * vc 
    annual_revenue = q * p
    days_in_year = 365
    
    st.write(f"**Global Baseline:** Annual COGS: {annual_cogs:,.2f} € | Annual Revenue: {annual_revenue:,.2f} €")
    st.divider()
    
    # ═══════════════════════════════════════════════════════════
    # 2. INPUTS
    # ═══════════════════════════════════════════════════════════
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.subheader("📦 Inventory")
        inv_days = st.number_input(
            "Inventory Days", 
            min_value=0, 
            max_value=365,
            value=st.session_state.get('inventory_days', 60),
            help="Average days products sit in stock before being sold"
        )
        inventory_value = (inv_days / days_in_year) * annual_cogs
        st.caption(f"💰 Stock Value: **{inventory_value:,.2f} €**")
    
    with col2:
        st.subheader("💳 Receivables")
        ar_days = st.number_input(
            "Accounts Receivable Days", 
            min_value=0,
            max_value=365,
            value=st.session_state.get('ar_days', 45),
            help="Average days to collect payment from customers"
        )
        ar_value = (ar_days / days_in_year) * annual_revenue
        st.caption(f"💰 Owed by Clients: **{ar_value:,.2f} €**")
    
    with col3:
        st.subheader("💸 Payables")
        ap_days = st.number_input(
            "Accounts Payable Days", 
            min_value=0,
            max_value=365,
            value=st.session_state.get('payables_days', 30),
            help="Average days you take to pay suppliers"
        )
        ap_value = (ap_days / days_in_year) * annual_cogs
        st.caption(f"💰 Owed to Suppliers: **{ap_value:,.2f} €**")
    
    # ═══════════════════════════════════════════════════════════
    # 3. CALCULATIONS
    # ═══════════════════════════════════════════════════════════
    ccc = inv_days + ar_days - ap_days
    working_capital_req = inventory_value + ar_value - ap_value
    
    # ═══════════════════════════════════════════════════════════
    # 4. RESULTS & SYNC
    # ═══════════════════════════════════════════════════════════
    st.divider()
    
    res1, res2 = st.columns(2)
    
    with res1:
        # Color coding
        if ccc < 0:
            color = "green"
            status = "Negative CCC (Excellent!)"
        elif ccc < 30:
            color = "green"
            status = "Healthy"
        elif ccc < 60:
            color = "orange"
            status = "Monitor"
        elif ccc < 90:
            color = "orange"
            status = "Caution"
        else:
            color = "red"
            status = "High Risk"
        
        st.metric(
            "Cash Conversion Cycle", 
            f"{ccc} Days", 
            delta=f"{ccc} days delay" if ccc > 0 else "Cash before payment!",
            delta_color="inverse" if ccc > 0 else "normal"
        )
        st.markdown(f"Status: :{color}[**{status}**]")
    
    with res2:
        st.metric(
            "Working Capital Requirement", 
            f"{working_capital_req:,.2f} €",
            help="Cash tied up in operations"
        )
        
        # Save to session state
        st.session_state.inventory_days = inv_days
        st.session_state.ar_days = ar_days
        st.session_state.payables_days = ap_days
        st.session_state.ccc = ccc
        st.session_state.working_capital_req = working_capital_req
    
    # ═══════════════════════════════════════════════════════════
    # 5. BREAKDOWN TABLE
    # ═══════════════════════════════════════════════════════════
    st.divider()
    
    st.subheader("📊 Working Capital Breakdown")
    
    import pandas as pd
    breakdown_df = pd.DataFrame({
        "Component": [
            "Inventory (Stock)",
            "Receivables (Owed to us)",
            "Payables (Owed by us)",
            "Net Working Capital"
        ],
        "Days": [
            f"{inv_days} days",
            f"{ar_days} days",
            f"-{ap_days} days",
            f"{ccc} days"
        ],
        "Value (€)": [
            f"{inventory_value:,.2f}",
            f"{ar_value:,.2f}",
            f"-{ap_value:,.2f}",
            f"{working_capital_req:,.2f}"
        ]
    })
    
    st.dataframe(breakdown_df, use_container_width=True, hide_index=True)
    
    # ═══════════════════════════════════════════════════════════
    # 6. COLD INSIGHT
    # ═══════════════════════════════════════════════════════════
    st.divider()
    
    daily_cash_release = annual_cogs / 365
    
    if ccc > 0:
        st.info(f"💡 **Cold Insight:** Every day you reduce the CCC, you release **~{daily_cash_release:,.2f} €** in cash.")
    else:
        st.success(f"🎯 **Negative CCC Achieved!** You get paid **before** you pay suppliers. This is a cash-generating machine!")
    
    # ═══════════════════════════════════════════════════════════
    # 7. NAVIGATION
    # ═══════════════════════════════════════════════════════════
    st.divider()
    
    nav1, nav2 = st.columns(2)
    
    with nav1:
        if st.button("⬅️ Back to Survival Anchor"):
            st.session_state.flow_step = 1
            st.rerun()
    
    with nav2:
        if st.button("Proceed to Unit Economics ➡️", type="primary"):
            st.session_state.flow_step = 3
            st.rerun()



import streamlit as st
import pandas as pd
import plotly.graph_objects as go

def run_step():
    st.header("📊 Stage 3: Unit Economics & CLV Analysis")
    
    # 1. FETCH BASELINE
    p = float(st.session_state.get('price', 100.0))
    vc = float(st.session_state.get('variable_cost', 60.0))
    initial_margin = p - vc
    
    # 2. INPUTS
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Customer Behavior")
        total_customers = st.number_input("Active Customer Base", min_value=1, value=500)
        purch_per_year = st.number_input("Purchases per Year", min_value=1.0, value=4.0)
        cac = st.number_input("Acquisition Cost (CAC) €", min_value=1.0, value=150.0)
        
    with col2:
        st.subheader("Retention Strategy")
        churn_rate = st.slider("Annual Churn Rate (%)", 0, 100, 15)
        # We use a key to force state update
        ret_discount = st.slider("Retention Discount (%)", 0, 50, 5, key="ret_disc_slider")
        horizon = st.slider("Analysis Horizon (Years)", 1, 10, 5)

    # 3. ANALYSTICAL CALCULATIONS (Direct Impact)
    # Year 1 Margin: 1st purchase at full price, remaining at discount
    y1_margin = initial_margin + ((purch_per_year - 1) * ( (p * (1 - ret_discount/100)) - vc ))
    
    # Subsequent Years Margin: All purchases at discount
    subsequent_annual_margin = purch_per_year * ( (p * (1 - ret_discount/100)) - vc )
    
    discount_rate = 0.10
    total_clv_npv = 0
    data = []
    
    for t in range(1, horizon + 1):
        survival = (1 - (churn_rate/100)) ** (t-1)
        # Apply y1_margin for the first year, subsequent_annual_margin for the rest
        current_margin = y1_margin if t == 1 else subsequent_annual_margin
        
        annual_flow = (current_margin * survival) / ((1 + discount_rate) ** t)
        total_clv_npv += annual_flow
        data.append({"Year": t, "Cumulative_NPV": total_clv_npv - cac})

    ltv_cac_ratio = total_clv_npv / cac if cac > 0 else 0

    # 4. DYNAMIC RESULTS
    st.divider()
    c1, c2, c3 = st.columns(3)
    c1.metric("Adjusted CLV (NPV)", f"{total_clv_npv:,.2f} €")
    
    # Delta shows the impact of the discount compared to a 0% discount scenario
    full_clv = (initial_margin * purch_per_year * 3) # rough estimate for comparison
    c2.metric("LTV / CAC Ratio", f"{ltv_cac_ratio:.2f}x")
    
    payback_months = (cac / y1_margin) * 12 if y1_margin > 0 else 0
    c3.metric("CAC Payback", f"{payback_months:.1f} Months")

    # 5. VISUALIZATION
    df = pd.DataFrame(data)
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df['Year'], y=df['Cumulative_NPV'], 
                             line=dict(color='#00CC96', width=4), fill='tozeroy'))
    fig.add_hline(y=0, line_dash="dot", line_color="white")
    fig.update_layout(title="Customer Profitability Over Time", template="plotly_dark")
    st.plotly_chart(fig, use_container_width=True)

    

    # 6. STRATEGIC VERDICT
    if subsequent_annual_margin <= 0:
        st.error(f"❌ **Analytical Failure:** A {ret_discount}% discount drops your margin per purchase below zero. You are paying customers to stay.")
    elif ltv_cac_ratio < 3:
        st.warning("⚠️ **Efficiency Risk:** LTV/CAC is below 3x. Marketing spend is not yielding enough long-term value.")
    else:
        st.success("✅ **Sustainable Unit Economics:** Your model absorbs the retention discount while maintaining a healthy LTV/CAC.")

    # 7. NAVIGATION
    st.divider()
    if st.button("Proceed to Stage 4 ➡️", type="primary"):
        st.session_state.flow_step = 4
        st.rerun()


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



# path/step5_strategy.py
"""
Stage 5: Strategic Stress Test, QSPM & Pricing Power Radar
"""

import streamlit as st
import pandas as pd
import numpy as np


# ═══════════════════════════════════════════════════════════
# HELPER FUNCTIONS FOR PRICING POWER
# ═══════════════════════════════════════════════════════════
def normalize(value, min_val, max_val):
    """Normalize value to 0-1 range"""
    if max_val - min_val == 0:
        return 0
    return (value - min_val) / (max_val - min_val)


def calculate_pricing_power_score(margin, substitution, elasticity, concentration):
    """Calculate composite pricing power score (0-100)"""
    # Margin strength (higher = better)
    margin_score = normalize(margin, 0, 0.8)
    
    # Substitution exposure (lower = better)
    substitution_score = 1 - normalize(substitution, 0, 1)
    
    # Elasticity fragility (lower elasticity = stronger power)
    elasticity_score = 1 - normalize(elasticity, 0, 3)
    
    # Revenue concentration risk (lower = better)
    concentration_score = 1 - normalize(concentration, 0, 1)
    
    final_score = (
        margin_score * 0.35 +
        substitution_score * 0.25 +
        elasticity_score * 0.25 +
        concentration_score * 0.15
    )
    
    return round(final_score * 100, 1)


def classify_power(score):
    """Classify pricing power level"""
    if score < 30:
        return "Weak Pricing Power", "🔴"
    elif score < 55:
        return "Defensive Structure", "🟠"
    elif score < 75:
        return "Strong Position", ""
    else:
        return "Dominant Pricing Power", ""


# ═══════════════════════════════════════════════════════════
# MAIN FUNCTION
# ═══════════════════════════════════════════════════════════
def run_step():
    st.header("🏁 Stage 5: Strategic Analysis & Decision Framework")
    
    # ═══════════════════════════════════════════════════════════
    # 1. CORE DATA SYNC
    # ═══════════════════════════════════════════════════════════
    p = st.session_state.get('price', 20.0)
    vc = st.session_state.get('variable_cost', 12.0)
    q = st.session_state.get('volume', 1000)
    fixed_cost = st.session_state.get('fixed_cost', 96000.0)  # ✅ Sync με Stage 0
    liquidity_drain_annual = st.session_state.get('liquidity_drain', 0.0)
    
    # Baseline profit (για delta comparison)
    baseline_profit = ((p - vc) * q) - fixed_cost - liquidity_drain_annual
    
    # ═══════════════════════════════════════════════════════════
    # 2. STRESS TEST (Analytical Resilience)
    # ═══════════════════════════════════════════════════════════
    st.subheader("🛠️ Model Stress Testing")
    
    col1, col2 = st.columns(2)
    with col1:
        drop_sales = st.slider("Drop in Sales Volume (%)", 0, 50, 20)
    with col2:
        inc_costs = st.slider("Increase in Variable Costs (%)", 0, 30, 10)
    
    # Stressed calculations
    stressed_q = q * (1 - drop_sales/100)
    stressed_vc = vc * (1 + inc_costs/100)
    stressed_profit = ((p - stressed_vc) * stressed_q) - fixed_cost - liquidity_drain_annual
    
    # ✅ Visual Delta: Διαφορά από baseline
    profit_delta = stressed_profit - baseline_profit
    
    st.metric(
        "Stress-Tested Annual Profit", 
        f"{stressed_profit:,.2f} €",
        delta=f"{profit_delta:,.2f} €",
        delta_color="normal"
    )
    
    st.caption(f"Baseline Profit: {baseline_profit:,.2f} € | Fixed Costs: {fixed_cost:,.2f} € | Liquidity Drain: {liquidity_drain_annual:,.2f} €")
    
    st.divider()
    
    # ═══════════════════════════════════════════════════════════
    # 3. PRICING POWER RADAR
    # ═══════════════════════════════════════════════════════════
    with st.expander("📊 **Pricing Power Radar** - Evaluate Structural Pricing Strength", expanded=False):
        st.write("Assess your pricing power beyond simple elasticity calculations.")
        
        # ✅ Auto-calculate margin from core data
        auto_margin = (p - vc) / p if p > 0 else 0
        
        st.info(f"📌 **Auto-detected Margin:** {auto_margin*100:.1f}% (from Price: {p}€, VC: {vc}€)")
        
        col_a, col_b = st.columns(2)
        
        with col_a:
            st.subheader("Market Exposure")
            substitution = st.slider("Substitution Exposure (%)", 0.0, 100.0, 40.0, key="ppr_sub") / 100
            elasticity = st.slider("Price Elasticity", 0.1, 3.0, 1.2, key="ppr_elast")
        
        with col_b:
            st.subheader("Business Structure")
            concentration = st.slider("Revenue Concentration (%)", 0.0, 100.0, 30.0, key="ppr_conc") / 100
        
        # Calculate using auto margin
        score = calculate_pricing_power_score(auto_margin, substitution, elasticity, concentration)
        label, icon = classify_power(score)
        
        st.divider()
        
        # Results
        res1, res2 = st.columns(2)
        res1.metric("Pricing Power Score", f"{score}/100")
        res2.metric("Classification", f"{icon} {label}")
        
        # Interpretation
        if score < 30:
            st.error("⚠️ Weak pricing power. Price increases likely destroy volume.")
        elif score < 55:
            st.warning("⚡ Defensive position. Pricing decisions must be cautious.")
        elif score < 75:
            st.success("✅ Strong position. Measurable pricing flexibility exists.")
        else:
            st.success("🏆 Dominant pricing power. Brand/positioning creates insulation.")
        
        # Drivers breakdown
        st.subheader("🧠 Structural Drivers")
        drivers_df = pd.DataFrame({
            "Driver": [
                "Margin Strength",
                "Substitution Protection",
                "Elasticity Resistance",
                "Revenue Diversification"
            ],
            "Impact Level": [
                f"{auto_margin*100:.1f}%",
                f"{(1-substitution)*100:.1f}%",
                f"{(1 - (elasticity/3))*100:.1f}%",
                f"{(1-concentration)*100:.1f}%"
            ]
        })
        st.dataframe(drivers_df, use_container_width=True)
    
    st.divider()
    
    # ═══════════════════════════════════════════════════════════
    # 4. INTERACTIVE QSPM
    # ═══════════════════════════════════════════════════════════
    st.subheader("🎯 Custom QSPM: Strategic Selection")
    st.write("Define your weights and rate the attractiveness of each strategy.")
    
    # User-Defined Weights
    with st.expander("⚖️ Edit Strategic Weights (Must sum to 1.0)", expanded=True):
        c1, c2, c3 = st.columns(3)
        w_margin = c1.slider("Profit Margin Weight", 0.0, 0.5, 0.3, key="qspm_w1")
        w_growth = c2.slider("Market Growth Weight", 0.0, 0.5, 0.2, key="qspm_w2")
        w_liquidity = c3.slider("Cash Liquidity Weight", 0.0, 0.5, 0.3, key="qspm_w3")
        
        c4, c5 = st.columns(2)
        w_rivalry = c4.slider("Competitive Rivalry Weight", 0.0, 0.5, 0.1, key="qspm_w4")
        w_brand = c5.slider("Brand Equity Weight", 0.0, 0.5, 0.1, key="qspm_w5")
        
        total_w = w_margin + w_growth + w_liquidity + w_rivalry + w_brand
        st.write(f"**Total Weight Sum: {total_w:.2f}**")
        
        if round(total_w, 2) != 1.0:
            st.warning("⚠️ Adjust weights to sum to 1.0 for valid QSPM analysis.")
    
    # User-Defined Attractiveness Scores
    st.write("### Rate Strategy Attractiveness (1 = Low, 4 = High)")
    col_a, col_b = st.columns(2)
    
    with col_a:
        st.markdown("**Strategy A: Aggressive Scaling**")
        as_a_margin = st.selectbox("Margin Match (A)", [1,2,3,4], index=1, key="q_a1")
        as_a_liquidity = st.selectbox("Liquidity Match (A)", [1,2,3,4], index=0, key="q_a2")
    
    with col_b:
        st.markdown("**Strategy B: Efficiency First**")
        as_b_margin = st.selectbox("Margin Match (B)", [1,2,3,4], index=3, key="q_b1")
        as_b_liquidity = st.selectbox("Liquidity Match (B)", [1,2,3,4], index=3, key="q_b2")
    
    # QSPM Table Generation
    factors = [
        ("Operating Margin", w_margin, as_a_margin, as_b_margin),
        ("Market Growth", w_growth, 4, 2),
        ("Cash Liquidity", w_liquidity, as_a_liquidity, as_b_liquidity),
        ("Competitive Rivalry", w_rivalry, 2, 3),
        ("Brand Equity", w_brand, 3, 2)
    ]
    
    qspm_list = []
    for f, w, as_a, as_b in factors:
        qspm_list.append({
            "Key Factor": f,
            "Weight": w,
            "Scale (AS)": as_a,
            "Scale (TAS)": w * as_a,
            "Efficiency (AS)": as_b,
            "Efficiency (TAS)": w * as_b
        })
    
    df_qspm = pd.DataFrame(qspm_list)
    st.table(df_qspm)
    
    # Final Verdict
    total_tas_a = df_qspm["Scale (TAS)"].sum()
    total_tas_b = df_qspm["Efficiency (TAS)"].sum()
    
    st.divider()
    res_a, res_b = st.columns(2)
    res_a.metric("Scaling Score (TAS)", f"{total_tas_a:.2f}")
    res_b.metric("Efficiency Score (TAS)", f"{total_tas_b:.2f}")
    
    if total_tas_a > total_tas_b:
        st.success("🚀 **QSPM favors SCALING.** Growth is the recommended path forward.")
    else:
        st.warning("⚖️ **QSPM favors EFFICIENCY.** Focus on risk mitigation and optimization.")
    
    # ═══════════════════════════════════════════════════════════
    # 5. NAVIGATION
    # ═══════════════════════════════════════════════════════════
    st.divider()
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("⬅️ Back to Sustainability"):
            st.session_state.flow_step = 4
            st.rerun()
    
    with col2:
        if st.button("🔄 Restart Lab Analysis", type="primary", use_container_width=True):
            st.session_state.flow_step = 0
            st.rerun()


import streamlit as st

def initialize_system_state():
    """Initializes the 5 pillars of the system + UI State."""

    # UI State
    if 'mode' not in st.session_state: st.session_state.mode = "home"
    if 'flow_step' not in st.session_state: st.session_state.flow_step = 0
    if 'baseline_locked' not in st.session_state: st.session_state.baseline_locked = False
    if 'selected_tool' not in st.session_state: st.session_state.selected_tool = None

    # 1. Revenue Engine
    if 'price' not in st.session_state: st.session_state.price = 30.0
    if 'volume' not in st.session_state: st.session_state.volume = 10000

    # 2. Cost Structure
    if 'variable_cost' not in st.session_state: st.session_state.variable_cost = 15.0
    if 'fixed_cost' not in st.session_state: st.session_state.fixed_cost = 5000.0

    # 3. Time & Cash Pressure
    if 'ar_days' not in st.session_state: st.session_state.ar_days = 45
    if 'inventory_days' not in st.session_state: st.session_state.inventory_days = 60
    if 'payables_days' not in st.session_state: st.session_state.payables_days = 30

    # 4. Capital & Financing
    if 'debt' not in st.session_state: st.session_state.debt = 20000.0
    if 'interest_rate' not in st.session_state: st.session_state.interest_rate = 0.05

    # 5. Durability
    if 'retention_rate' not in st.session_state: st.session_state.retention_rate = 0.85


import streamlit as st

def show_about():
    st.title("🧪 About Managers' Lab")
    st.markdown("---")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("Framework Overview")
        st.write("""
        **Managers' Lab** is a structural decision system designed to model 
        the economic mechanics of a business before strategy is applied.
        
        It focuses on measurable fundamentals:
        revenue structure, cost behavior, cash timing, capital pressure, 
        and durability over a 365-day operating cycle.
        
        All analytical modules project stress onto the same shared baseline,
        ensuring consistency across simulations.
        """)
        
        st.subheader("What This System Is Not")
        st.write("""
        - Not accounting software  
        - Not KPI decoration  
        - Not optimism-based forecasting  

        The objective is structural clarity — not presentation.
        """)

    with col2:
        st.subheader("Contact")
        st.write("For methodology questions or technical feedback:")
        
        st.markdown("📧 **Email:** manosv@gmail.com")
        st.markdown("🌐 **Medium:** [https://medium.com/@ManosV_18]")
        
        st.divider()
        st.caption("Version: 2.0.1 (Stable Build)")
        st.caption("Architecture: Shared Core System")

    if st.button("⬅️ Back to Control Center"):
        st.session_state.mode = "home"
        st.rerun()

import streamlit as st

def show_home():
    # PHASE A: Entry Mode (No Baseline Defined)
    if not st.session_state.get('baseline_locked', False):
        st.title("🧪 Managers’ Lab")
        st.subheader("System Status: Baseline Not Defined")
        st.divider()
        st.write(
            "The system requires a structural baseline before analysis can begin. "
            "Define revenue structure, cost behavior, and operating assumptions "
            "to activate the decision environment."
        )

        if st.button("Define Baseline (Stage 0)", use_container_width=True, type="primary"):
            st.session_state.mode = "path"
            st.session_state.flow_step = 0
            st.rerun()

    # PHASE B: Control Center Mode (System Operational)
    else:
        st.title("🧪 Managers’ Lab — Control Center")
        st.caption("Structural Overview — 365-Day Operating Model")
        st.markdown("---")

        # Calculations from Shared Core
        # Ensure these keys exist in core/system_state.py
        p = st.session_state.get('price', 0.0)
        v = st.session_state.get('volume', 0)
        vc = st.session_state.get('variable_cost', 0.0)
        fc = st.session_state.get('fixed_cost', 0.0)
        debt = st.session_state.get('debt', 0.0)
        rate = st.session_state.get('interest_rate', 0.0)
        
        rev = p * v
        ebit = ((p - vc) * v) - fc
        net_profit = ebit - (debt * rate)
        margin = (p - vc) / p if p > 0 else 0

        # Executive Metrics
        c1, c2, c3 = st.columns(3)
        c1.metric("Annual Revenue", f"{rev:,.0f} €")
        c2.metric("Net Profit (Post-Interest)", f"{net_profit:,.0f} €", delta=f"EBIT: {ebit:,.0f} €")
        c3.metric("Contribution Margin", f"{margin:.1%}")

        st.divider()
        
        # Navigation Hub
        st.subheader("Analysis Environment")
        col_a, col_b = st.columns(2)
        with col_a:
            if st.button("Enter Structured Path", use_container_width=True, type="primary"):
                st.session_state.mode = "path"
                st.session_state.flow_step = 1
                st.rerun()
        with col_b:
            if st.button("Open Tool Library", use_container_width=True):
                st.session_state.mode = "library"
                st.rerun()

        st.divider()
        with st.expander("System Configuration"):
            st.write(
                "The baseline defines the structural mechanics of the system. "
                "Modifying it will recalibrate all analytical modules."
            )
            if st.button("Unlock Baseline & Recalibrate", use_container_width=True):
                st.session_state.baseline_locked = False
                st.session_state.mode = "path"
                st.session_state.flow_step = 0
                st.rerun()


import streamlit as st

def show_library():
    st.title("📚 Tool Library")
    st.caption("Direct access to all analytical modules.")

    categories = {
        "📈 Pricing & Break-Even": [
            ("Break-Even Shift Analysis",  "break_even_shift_calculator", "show_break_even_shift_calculator"),
            ("Loss Threshold Analysis",    "loss_threshold",              "show_loss_threshold_before_price_cut"),
            ("Pricing Power Radar",        "pricing_power_radar",         "show_pricing_power_radar"),
        ],
        "💰 Finance & Cash Flow": [
            ("Cash Cycle Calculator",      "cash_cycle",                  "run_cash_cycle_app"),
            ("Cash Fragility Index",       "cash_fragility_index",        "show_cash_fragility_index"),
            ("Credit Policy Analysis",     "credit_policy_app",           "show_credit_policy_analysis"),
            ("Supplier Credit Analysis",   "supplier_credit_app",         "show_supplier_credit_analysis"),
            ("Loan vs Leasing",            "loan_vs_leasing_calculator",  "loan_vs_leasing_ui"),
        ],
        "👥 Customer & Strategy": [
            ("CLV Analysis",               "clv_calculator",              "show_clv_calculator"),
            ("QSPM Strategy Tool",         "qspm_two_strategies",         "show_qspm_tool"),
            ("Substitutes Sensitivity",    "substitution_analysis_tool",  "show_substitutes_sensitivity_tool"),
            ("Complementary Analysis",     "complementary_analysis",      "show_complementary_analysis"),
        ],
        "📦 Operations": [
            ("Unit Cost Calculator",       "unit_cost_app",               "show_unit_cost_app"),
            ("Inventory Turnover",         "inventory_turnover_calculator","show_inventory_turnover_calculator"),
            ("Credit Days Calculator",     "credit_days_calculator",      "show_credit_days_calculator"),
            ("Discount NPV Analysis",      "discount_npv_ui",             "show_discount_npv_ui"),
        ],
    }

    cat_names  = list(categories.keys())
    all_tools  = {t[0]: (cat_idx, t_idx)
                  for cat_idx, (_, tools) in enumerate(categories.items())
                  for t_idx, t in enumerate(tools)}

    # ── FIX 3: Resolve default indexes BEFORE widgets are drawn,
    #    and clear selected_tool immediately so subsequent rerenders don't re-apply it ──
    selected_tool = st.session_state.get("selected_tool")

    if selected_tool and selected_tool in all_tools:
        default_cat_index, default_tool_index = all_tools[selected_tool]
    else:
        default_cat_index, default_tool_index = 0, 0

    # Clear NOW (before widgets) so future rerenders start fresh
    st.session_state.selected_tool = None

    # ── Widget: Category ──
    selected_cat = st.selectbox(
        "Choose Category",
        cat_names,
        index=default_cat_index,
    )

    tool_list  = categories[selected_cat]
    tool_names = [t[0] for t in tool_list]

    # ── FIX 4: If the user manually picked a different category via the selectbox,
    #    the default_tool_index from the previous category is no longer valid ──
    current_cat_index = cat_names.index(selected_cat)
    if current_cat_index != default_cat_index:
        default_tool_index = 0                     # reset to first tool in new category
    elif default_tool_index >= len(tool_names):    # safety clamp (shouldn't happen, but just in case)
        default_tool_index = 0

    # ── Widget: Tool ──
    selected_tool_name = st.radio("Select Tool", tool_names, index=default_tool_index)

    tool_data     = next(t for t in tool_list if t[0] == selected_tool_name)
    file_name     = tool_data[1]
    function_name = tool_data[2]

    st.divider()

    # ── FIX 5: Show the real exception so developers can debug ──
    try:
        module = __import__(f"tools.{file_name}", fromlist=[function_name])
        func   = getattr(module, function_name)
        func()
    except ModuleNotFoundError:
        st.error(f"❌ Module not found: `tools/{file_name}.py`")
    except AttributeError:
        st.error(f"❌ Function `{function_name}` not found in `tools/{file_name}.py`")
    except Exception as e:
        st.error(f"❌ Error while running `{function_name}`: {e}")
        st.exception(e)   # shows full traceback in dev mode

import streamlit as st

def render_sidebar():
    with st.sidebar:
        st.title("🧪 Managers’ Lab")
        st.caption("Strategic Decision Support")
        
        st.divider()

        # Home Button
        if st.button("🏠 Home", use_container_width=True):
            st.session_state.mode = "home"
            st.session_state.selected_tool = None
            st.rerun()
            
        st.divider()
        st.subheader("Navigation")

        # Tool Library Button
        if st.button("📚 Tool Library", use_container_width=True):
            st.session_state.mode = "library"
            st.session_state.selected_tool = None
            st.rerun()

        # Structured Path Button
        # Logic: If not locked, start at Stage 0. If locked, resume/start at Stage 1.
        if st.button("🧭 Structured Path", use_container_width=True):
            st.session_state.mode = "path"
            if not st.session_state.get('baseline_locked', False):
                st.session_state.flow_step = 0
            else:
                st.session_state.flow_step = 1
            st.session_state.selected_tool = None
            st.rerun()

        # Progress Bar (Visible only in Path mode)
        if st.session_state.get('mode') == "path":
            step = st.session_state.get('flow_step', 0)
            if step > 0:  # Only show progress for Analysis Stages 1-5
                st.divider()
                st.caption(f"Analysis Progress: Stage {step} of 5")
                st.progress(step / 5)

        # Support & Information Section
        st.divider()
        if st.button("ℹ️ About & Support", use_container_width=True):
            st.session_state.mode = "about"
            st.session_state.selected_tool = None
            st.rerun()

        # Cold Analysis Footer Note
        st.divider()
        st.caption("Analytical focus: Efficiency, Stability, & Survival Margin.")
        st.caption("System Version: 2.0.1")
