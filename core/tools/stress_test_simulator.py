import streamlit as st
import plotly.graph_objects as go
import pandas as pd

def show_stress_test_tool():
    """
    Strategic Stress Test & Liquidity Audit Tool.
    Focuses on Variable Cost impact, DSO (Collection Delay) and Debt Service obligations.
    """
    st.header("🛡️ Strategic Stress Test & Liquidity Audit")
    
    s = st.session_state
    metrics = s.get("metrics", {})
    if not metrics:
        st.warning("⚠️ Baseline not locked. Please lock parameters in Home first.")
        return
    
    # 1. BASELINE DATA RETRIEVAL (Linked to Home Inputs)
    price = float(s.get('price', 150.0))
    vc = float(s.get('variable_cost', 90.0))
    volume = float(s.get('volume', 15000))
    fixed_costs = float(s.get('fixed_cost', 450000.0))
    current_cash = float(s.get('opening_cash', 150000.0))
    
    # Financial Obligations (Critical for Stress Test)
    annual_debt_service = float(s.get('annual_debt_service', 70000.0))
    depreciation = float(s.get('depreciation', 50000.0))
    tax_rate = float(s.get('tax_rate', 22.0)) / 100

    # 2. SCENARIO PARAMETERS (USER INPUTS)
    st.subheader("⚠️ Scenario Parameters")
    c1, c2, c3 = st.columns(3)
    rev_shock = c1.slider("Revenue Change (%)", -60, 20, -25) / 100
    dso_shock = c2.slider("Additional Collection Delay (Days)", 0, 120, 30)
    cost_shock = c3.slider("Variable Cost Spike (%)", 0, 50, 10) / 100

    # 3. IMPACT CALCULATIONS
    new_volume = volume * (1 + rev_shock)
    new_vc = vc * (1 + cost_shock)
    new_rev = new_volume * price
    
    # Liquidity Drain (Instruction [2026-02-18]: 365 days)
    # The cash "trapped" because customers pay later
    liquidity_impact = (new_rev / 365) * dso_shock
    
    # Profitability calculation (EBIT)
    new_ebit = ((price - new_vc) * new_volume) - fixed_costs - depreciation
    new_tax = max(0, new_ebit * tax_rate)
    new_net_profit = new_ebit - new_tax
    
    # Monthly Cash Flow Post-Shock (Net Profit + Depr - Debt Service Share)
    monthly_cash_flow = (new_net_profit + depreciation - (annual_debt_service / 12)) 
    
    # Post-Shock Cash (Current Cash - DSO Drain + 1 Month of Adjusted Cash Flow)
    remaining_liquidity = current_cash - liquidity_impact + monthly_cash_flow
    
    # 4. EXECUTIVE DASHBOARD
    st.divider()
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("New Revenue", f"${new_rev:,.0f}")
    m2.metric("New Unit VC", f"${new_vc:,.2f}", delta=f"{cost_shock:.0%}", delta_color="inverse")
    m3.metric("DSO Drain", f"${liquidity_impact:,.0f}", delta_color="inverse", help="Cash trapped due to collection delays.")
    
    cash_delta = remaining_liquidity - current_cash
    m4.metric("Survival Liquidity", f"${remaining_liquidity:,.0f}", 
              delta=f"${cash_delta:,.0f}",
              delta_color="normal" if remaining_liquidity > 0 else "inverse")

    # 5. REMEDIES TABLE (Triggered on negative liquidity)
    if remaining_liquidity < 0:
        st.error(f"🚨 **LIQUIDITY CRUNCH:** Funding gap of ${abs(remaining_liquidity):,.0f} detected.")
        
        st.subheader("📋 Strategic Action Plan (Remedies)")
        gap = abs(remaining_liquidity)
        
        daily_rev = (new_rev / 365) if new_rev > 0 else 1
        dso_reduction_needed = gap / daily_rev
        
        remedy_data = {
            "Strategy": ["DSO Optimization", "Debt Service Restructuring", "Capital Injection"],
            "Target Action": [
                f"Recover {int(dso_reduction_needed) + 1} days of credit",
                f"Defer ${gap:,.0f} of principal payments",
                f"Secure fresh funding of ${gap:,.0f}"
            ],
            "Impact": ["Immediate Liquidity", "Cash Preservation", "Instant Safety"]
        }
        st.table(pd.DataFrame(remedy_data))

    # 6. TORNADO CHART (SENSITIVITY ANALYSIS)
    st.subheader("🌪️ Sensitivity Analysis (Tornado Chart)")
    
    # Impact calculations for Tornado
    dso_sens = (new_rev / 365) * (dso_shock * 0.1) # 10% change in shock
    vc_sens = (new_volume * (new_vc * 0.1)) / 12   # Monthly impact of 10% VC spike
    vol_sens = ((price - new_vc) * (new_volume * 0.1)) / 12 # Monthly impact of 10% vol drop

    tornado_items = [
        {"Variable": "Collection Delay (DSO)", "Impact": dso_sens},
        {"Variable": "Variable Cost Spike", "Impact": vc_sens},
        {"Variable": "Sales Volume Drop", "Impact": vol_sens}
    ]
    tornado_items = sorted(tornado_items, key=lambda x: x["Impact"])

    

    fig = go.Figure()
    fig.add_trace(go.Bar(
        y=[item["Variable"] for item in tornado_items],
        x=[item["Impact"] for item in tornado_items],
        orientation='h',
        marker_color='#ef4444' # Red for risk impact
    ))
    
    fig.update_layout(
        height=300, 
        margin=dict(l=10, r=10, t=30, b=10),
        xaxis_title="Potential Negative Impact on Monthly Cash ($)",
        template="plotly_white"
    )
    st.plotly_chart(fig, use_container_width=True)

    # 7. NAVIGATION
    st.divider()
    if st.button("⬅️ Return to Hub", use_container_width=True):
        s.flow_step = "home"
        st.rerun()
