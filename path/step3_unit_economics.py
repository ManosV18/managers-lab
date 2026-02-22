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
