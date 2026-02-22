import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from core.engine import compute_core_metrics

def run_stage3():
    st.header("📊 Stage 3: Unit Economics & CLV Analysis")
    st.caption("Evaluate the long-term durability of your customer relationships.")
    
    # 1. FETCH SYNCED METRICS
    metrics = compute_core_metrics()
    p = st.session_state.price
    vc = st.session_state.variable_cost
    initial_unit_contribution = metrics["unit_contribution"]
    
    # 2. INPUTS (SYNCED WITH CORE STATE)
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Customer Behavior")
        # Ενημερώνουμε το state απευθείας
        st.session_state.purch_per_year = st.number_input(
            "Purchases per Year", 
            min_value=0.1, 
            value=float(st.session_state.purch_per_year)
        )
        st.session_state.cac = st.number_input(
            "Acquisition Cost (CAC) €", 
            min_value=0.0, 
            value=float(st.session_state.cac)
        )
        
    with col2:
        st.subheader("Retention Strategy")
        # Slider για Retention αντί για Churn (πιο analytical focus)
        ret_rate = st.slider(
            "Annual Retention Rate (%)", 
            0, 100, 
            int(st.session_state.retention_rate * 100)
        )
        st.session_state.retention_rate = ret_rate / 100
        
        ret_discount = st.slider("Retention Discount (%)", 0, 50, 5)
        horizon = st.slider("Analysis Horizon (Years)", 1, 15, 5)

    # 3. ANALYTICAL CALCULATIONS
    # Year 1 Margin: 1st purchase full price, others at discount
    y1_margin = initial_unit_contribution + ((st.session_state.purch_per_year - 1) * ((p * (1 - ret_discount/100)) - vc))
    
    # Subsequent Years Margin: All purchases at discount
    subsequent_annual_contribution = st.session_state.purch_per_year * ((p * (1 - ret_discount/100)) - vc)
    
    discount_rate = 0.10 # WACC assumption
    total_clv_npv = 0
    data = []
    
    for t in range(1, horizon + 1):
        # Probability of customer still being active
        survival_prob = st.session_state.retention_rate ** (t - 1)
        current_year_margin = y1_margin if t == 1 else subsequent_annual_contribution
        
        annual_flow = (current_year_margin * survival_prob) / ((1 + discount_rate) ** t)
        total_clv_npv += annual_flow
        data.append({"Year": t, "Cumulative_NPV": total_clv_npv - st.session_state.cac})

    ltv_cac_ratio = total_clv_npv / st.session_state.cac if st.session_state.cac > 0 else 0

    # 4. RESULTS DISPLAY
    st.divider()
    c1, c2, c3 = st.columns(3)
    c1.metric("LTV (NPV)", f"{total_clv_npv:,.2f} €")
    c2.metric("LTV / CAC Ratio", f"{ltv_cac_ratio:.2f}x")
    
    payback_months = (st.session_state.cac / y1_margin) * 12 if y1_margin > 0 else 0
    c3.metric("CAC Payback", f"{payback_months:.1f} Months")

    # 5. VISUALIZATION
    
    df = pd.DataFrame(data)
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df['Year'], 
        y=df['Cumulative_NPV'], 
        line=dict(color='#00CC96', width=4), 
        fill='tozeroy',
        name="Net CLV"
    ))
    fig.add_hline(y=0, line_dash="dot", line_color="white")
    fig.update_layout(
        title="Customer Profitability Path (NPV)", 
        template="plotly_dark",
        xaxis_title="Years",
        yaxis_title="Cumulative Euro"
    )
    st.plotly_chart(fig, use_container_width=True)

    # 6. STRATEGIC VERDICT
    if subsequent_annual_contribution <= 0:
        st.error(f"❌ **Analytical Failure:** Retention discount of {ret_discount}% destroys unit economics. Margin is negative.")
    elif ltv_cac_ratio < 3:
        st.warning("⚠️ **Efficiency Risk:** LTV/CAC < 3x. Customer acquisition is too expensive relative to lifetime value.")
    else:
        st.success("✅ **Sustainable Unit Economics:** Model absorbs retention costs while maintaining healthy growth margins.")

    # 7. NAVIGATION
    st.divider()
    nav1, nav2 = st.columns(2)
    with nav1:
        if st.button("⬅️ Back to Capital Structure"):
            st.session_state.flow_step = 2
            st.rerun()
    with nav2:
        if st.button("Proceed to Stage 4 (Sustainability) ➡️", type="primary"):
            st.session_state.flow_step = 4
            st.rerun()
