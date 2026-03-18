import streamlit as st
import plotly.graph_objects as go

def show_stress_test_tool():
    st.header("🛡️ Strategic Stress Test & Liquidity Audit")
    
    s = st.session_state
    
    # 1. BASELINE DATA
    price = float(s.get('price', 100.0))
    vc = float(s.get('variable_cost', 60.0))
    volume = float(s.get('volume', 1000))
    fixed_costs = float(s.get('fixed_cost', 20000.0))
    current_cash = float(s.get('opening_cash', 0.0))
    
    # 2. SCENARIO PARAMETERS
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
    
    new_profit = ((price - new_vc) * new_volume) - fixed_costs
    remaining_liquidity = current_cash - liquidity_impact + (new_profit / 12)
    
    # 4. RESULTS DASHBOARD
    st.divider()
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("New Revenue", f"$ {new_rev:,.0f}")
    m2.metric("New Variable Cost", f"$ {new_vc:,.0f}", delta=f"{cost_shock:.0%}", delta_color="inverse")
    m3.metric("Liquidity Drain", f"$ {liquidity_impact:,.0f}", delta_color="inverse")
    m4.metric("Post-Shock Cash", f"$ {remaining_liquidity:,.0f}", delta_color="normal" if remaining_liquidity > 0 else "inverse")

    # 5. REMEDIES TABLE (Only shows if cash is negative)
    if remaining_liquidity < 0:
        st.error(f"🚨 **LIQUIDITY CRUNCH:** Funding gap of $ {abs(remaining_liquidity):,.0f}")
        
        st.subheader("📋 Strategic Action Plan (Remedies)")
        gap = abs(remaining_liquidity)
        
        # Calculations for remedies
        dso_reduction_needed = (gap / (new_rev / 365)) if new_rev > 0 else 0
        vc_reduction_needed = (gap * 12 / new_volume) if new_volume > 0 else 0
        
        remedy_data = {
            "Strategy": ["DSO Optimization", "Variable Cost Cut", "Emergency Funding"],
            "Target Action": [
                f"Reduce Collection Days by {int(dso_reduction_needed) + 1} days",
                f"Lower Unit Variable Cost by $ {vc_reduction_needed:.2f}",
                f"Inject $ {gap:,.0f} of Fresh Working Capital"
            ],
            "Impact": ["Immediate Liquidity", "Profit & Liquidity", "Immediate Safety"]
        }
        st.table(remedy_data)

    # 6. TORNADO CHART (Sensitivity)
    st.subheader("🌪️ Sensitivity Analysis (Tornado Chart)")
    
    # Comparing impact of 10% change in VC vs DSO
    vc_impact = abs(((price - (new_vc * 1.1)) * new_volume - fixed_costs)/12 - base_profit_mo_placeholder := 0)
    dso_impact = abs(((new_rev / 365) * (dso_shock * 1.1)) - ((new_rev / 365) * (dso_shock)))
    
    fig = go.Figure()
    fig.add_trace(go.Bar(y=["Var. Cost", "DSO Delay"], x=[vc_impact, dso_impact], orientation='h', marker_color='#1E3A8A'))
    fig.update_layout(height=250, margin=dict(l=10, r=10, t=30, b=10), xaxis_title="Cash Flow Impact Magnitude")
    st.plotly_chart(fig, use_container_width=True)

    st.divider()
    if st.button("⬅️ Return to Control Tower", use_container_width=True):
        st.session_state.flow_step = "home"
        st.rerun()
