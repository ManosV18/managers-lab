import streamlit as st
import plotly.graph_objects as go
import pandas as pd

def show_stress_test_tool():
    """
    Strategic Stress Test & Liquidity Audit Tool.
    Focuses on Variable Cost impact and DSO (Collection Delay).
    """
    st.header("🛡️ Strategic Stress Test & Liquidity Audit")
    
    s = st.session_state
    
    # 1. BASELINE DATA RETRIEVAL
    price = float(s.get('price', 100.0))
    vc = float(s.get('variable_cost', 60.0))
    volume = float(s.get('volume', 1000))
    fixed_costs = float(s.get('fixed_cost', 20000.0))
    current_cash = float(s.get('opening_cash', 0.0))
    
    # 2. SCENARIO PARAMETERS (USER INPUTS)
    st.subheader("⚠️ Scenario Parameters")
    c1, c2, c3 = st.columns(3)
    rev_shock = c1.slider("Revenue Change (%)", -60, 20, -25) / 100
    dso_shock = c2.slider("Collection Delay (Days)", 0, 120, 30)
    cost_shock = c3.slider("Variable Cost Spike (%)", 0, 50, 10) / 100

    # 3. IMPACT CALCULATIONS
    new_volume = volume * (1 + rev_shock)
    new_vc = vc * (1 + cost_shock)
    new_rev = new_volume * price
    
    # Liquidity Drain (Instruction [2026-02-18]: 365 days)
    liquidity_impact = (new_rev / 365) * dso_shock
    
    # Profitability calculation
    new_profit = ((price - new_vc) * new_volume) - fixed_costs
    
    # Post-Shock Cash (Current Cash - Liquidity Drain + 1 Month of Adjusted Profit)
    remaining_liquidity = current_cash - liquidity_impact + (new_profit / 12)
    
    # 4. EXECUTIVE DASHBOARD
    st.divider()
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("New Revenue", f"$ {new_rev:,.0f}")
    m2.metric("New Unit VC", f"$ {new_vc:,.2f}", delta=f"{cost_shock:.0%}", delta_color="inverse")
    m3.metric("Liquidity Drain", f"$ {liquidity_impact:,.0f}", delta_color="inverse")
    
    cash_delta = remaining_liquidity - current_cash
    m4.metric("Post-Shock Cash", f"$ {remaining_liquidity:,.0f}", 
              delta=f"{cash_delta:,.0f}",
              delta_color="normal" if remaining_liquidity > 0 else "inverse")

    # 5. REMEDIES TABLE (Triggered on negative liquidity)
    if remaining_liquidity < 0:
        st.error(f"🚨 **LIQUIDITY CRUNCH:** Funding gap of $ {abs(remaining_liquidity):,.0f} detected.")
        
        st.subheader("📋 Strategic Action Plan (Remedies)")
        gap = abs(remaining_liquidity)
        
        # Calculate exactly what is needed to bridge the gap
        daily_rev = (new_rev / 365) if new_rev > 0 else 1
        dso_reduction_needed = gap / daily_rev
        vc_reduction_needed = (gap * 12 / new_volume) if new_volume > 0 else 0
        
        remedy_data = {
            "Strategy": ["DSO Optimization", "Variable Cost Reduction", "Capital Injection"],
            "Target Action": [
                f"Reduce Collection Days by {int(dso_reduction_needed) + 1} days",
                f"Cut Unit Variable Cost by $ {vc_reduction_needed:.2f}",
                f"Secure fresh funding of $ {gap:,.0f}"
            ],
            "Impact": ["Immediate Liquidity", "Profit & Liquidity", "Instant Safety"]
        }
        st.table(pd.DataFrame(remedy_data))

    # 6. TORNADO CHART (SENSITIVITY ANALYSIS)
    st.subheader("🌪️ Sensitivity Analysis (Tornado Chart)")
    st.write("Impact of a 10% adverse change in each variable on Monthly Cash Flow.")

    # Calculate Sensitivity deltas
    # Impact of 10% more DSO
    dso_sens = abs(((new_rev / 365) * (dso_shock * 1.1)) - liquidity_impact)
    # Impact of 10% more Variable Cost (Monthly)
    vc_sens = abs((((price - (new_vc * 1.1)) * new_volume - fixed_costs)/12) - (new_profit / 12))
    # Impact of 10% less Volume (Monthly)
    vol_sens = abs((((price - new_vc) * (new_volume * 0.9) - fixed_costs)/12) - (new_profit / 12))

    tornado_items = [
        {"Variable": "DSO (Liquidity)", "Impact": dso_sens},
        {"Variable": "Variable Cost (Profit)", "Impact": vc_sens},
        {"Variable": "Sales Volume", "Impact": vol_sens}
    ]
    tornado_items = sorted(tornado_items, key=lambda x: x["Impact"])

    fig = go.Figure()
    fig.add_trace(go.Bar(
        y=[item["Variable"] for item in tornado_items],
        x=[item["Impact"] for item in tornado_items],
        orientation='h',
        marker_color='#1E3A8A'
    ))
    
    fig.update_layout(
        height=300, 
        margin=dict(l=10, r=10, t=30, b=10),
        xaxis_title="Magnitude of Negative Impact on Cash ($)",
        template="plotly_white"
    )
    st.plotly_chart(fig, use_container_width=True)

    # 7. NAVIGATION
    st.divider()
    if st.button("⬅️ Return to Control Tower", use_container_width=True):
        st.session_state.flow_step = "home"
        st.rerun()
