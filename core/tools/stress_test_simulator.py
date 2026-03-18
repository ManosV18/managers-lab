import streamlit as st
import plotly.graph_objects as go
import pandas as pd

def show_stress_test_tool():
    st.header("🛡️ Strategic Stress Test & Sensitivity")
    st.info("Analysis of systemic resilience. Identifying which lever impacts liquidity the most.")
    
    s = st.session_state
    
    # 1. BASELINE DATA
    price = float(s.get('price', 100.0))
    vc = float(s.get('variable_cost', 60.0))
    volume = float(s.get('volume', 1000))
    fixed_costs = float(s.get('fixed_cost', 20000.0))
    current_cash = float(s.get('opening_cash', 0.0))
    
    # 2. SCENARIO INPUTS
    st.subheader("⚠️ Scenario Parameters")
    c1, c2, c3 = st.columns(3)
    rev_shock = c1.slider("Revenue Change (%)", -60, 20, -25) / 100
    dso_shock = c2.slider("Collection Delay (Days)", 0, 120, 30)
    cost_shock = c3.slider("Fixed Cost Spike (%)", 0, 50, 10) / 100

    # 3. CORE CALCULATIONS
    new_rev = (price * volume) * (1 + rev_shock)
    new_volume = volume * (1 + rev_shock)
    
    # Liquidity Drain (Compliance [2026-02-18]: 365 days)
    liquidity_impact = (new_rev / 365) * dso_shock
    
    new_profit = ((price - vc) * new_volume) - (fixed_costs * (1 + cost_shock))
    remaining_liquidity = current_cash - liquidity_impact + (new_profit / 12)
    
    # 4. RESULTS DASHBOARD
    st.divider()
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("New Revenue", f"$ {new_rev:,.0f}")
    m2.metric("New Profit (Annual)", f"$ {new_profit:,.0f}")
    m3.metric("Liquidity Drain", f"$ {liquidity_impact:,.0f}", delta_color="inverse")
    m4.metric("Post-Shock Cash", f"$ {remaining_liquidity:,.0f}", 
              delta=f"{remaining_liquidity - current_cash:,.0f}",
              delta_color="normal" if remaining_liquidity > 0 else "inverse")

    if remaining_liquidity < 0:
        st.error(f"🚨 **LIQUIDITY CRUNCH:** Funding gap of $ {abs(remaining_liquidity):,.0f} detected.")

    # 5. TORNADO CHART LOGIC (Sensitivity Analysis)
    st.subheader("🌪️ Sensitivity Analysis (Tornado Chart)")
    st.write("Impact of +/- 10% change in key variables on Net Liquidity.")

    # Sensitivity Calculations
    base_liq = remaining_liquidity
    
    # Sensitivity Levers
    levers = {
        "Collection Delay": ( (new_rev / 365) * (dso_shock * 1.1) , (new_rev / 365) * (dso_shock * 0.9) ),
        "Unit Price": ( ((price * 0.9 - vc) * new_volume - fixed_costs)/12 , ((price * 1.1 - vc) * new_volume - fixed_costs)/12 ),
        "Sales Volume": ( ((price - vc) * (new_volume * 0.9) - fixed_costs)/12 , ((price - vc) * (new_volume * 1.1) - fixed_costs)/12 )
    }
    
    tornado_data = []
    for label, (low_val, high_val) in levers.items():
        # We calculate the delta from the current 'remaining_liquidity'
        impact = abs(high_val - low_val)
        tornado_data.append({"Variable": label, "Low": low_val, "High": high_val, "Impact": impact})
    
    # Sort by impact for the 'tornado' effect
    tornado_data = sorted(tornado_data, key=lambda x: x["Impact"])

    fig = go.Figure()
    for item in tornado_data:
        fig.add_trace(go.Bar(
            y=[item["Variable"]],
            x=[item["Impact"]],
            orientation='h',
            marker_color='#1E3A8A',
            text=f"Var: {item['Variable']}",
            textposition='inside'
        ))

    fig.update_layout(
        showlegend=False,
        height=300,
        margin=dict(l=10, r=10, t=30, b=10),
        xaxis_title="Magnitude of Impact on Cash Flow",
        yaxis=dict(autorange="reversed")
    )
    st.plotly_chart(fig, use_container_width=True)

    # 6. NAVIGATION
    st.divider()
    if st.button("⬅️ Return to Control Tower", use_container_width=True):
        st.session_state.flow_step = "home"
        st.rerun()
