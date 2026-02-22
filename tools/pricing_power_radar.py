import streamlit as st
import pandas as pd
import plotly.express as px
from core.engine import compute_core_metrics

def show_pricing_power_radar():
    st.header("🎯 Pricing Power Radar")
    st.caption("Strategic Audit: Evaluate your structural ability to defend or increase prices.")

    # 1. FETCH CONTEXT FROM GLOBAL ENGINE
    metrics = compute_core_metrics()
    p = st.session_state.price
    current_margin = (metrics['unit_contribution'] / p) * 100 if p > 0 else 0

    # 2. EVALUATION PILLARS
    st.subheader("Structural Assessment")
    st.write("Rate your position on a scale of 1 (Commoditized/Weak) to 10 (Unique/Dominant).")

    col1, col2 = st.columns(2)
    
    with col1:
        brand_score = st.slider("Brand Equity & Loyalty", 1, 10, 5, 
                                help="Do customers choose you for 'who' you are or strictly for the lowest price?")
        switching_costs = st.slider("Switching Costs", 1, 10, 5, 
                                help="How difficult/expensive is it for a customer to move to a competitor?")
        
    with col2:
        scarcity_score = st.slider("Product Scarcity / IP", 1, 10, 5, 
                                help="Do you have unique features, patents, or limited market availability?")
        market_share = st.slider("Market Concentration", 1, 10, 5, 
                                help="Are you a leader in a niche or one of many small, interchangeable players?")

    # 3. CALCULATIONS
    # Automatically derive the 5th pillar (Margin Strength) from the Engine
    # Scaling: 5% margin = 1 point, up to 50% margin = 10 points
    margin_score = min(max(int(current_margin / 5), 1), 10)
    
    radar_data = pd.DataFrame({
        'Pillar': ['Brand Equity', 'Switching Costs', 'Scarcity/IP', 'Market Power', 'Margin Strength'],
        'Score': [brand_score, switching_costs, scarcity_score, market_share, margin_score]
    })

    # 4. VISUALIZATION
    
    
    fig = px.line_polar(radar_data, r='Score', theta='Pillar', line_close=True,
                        template="plotly_dark", range_r=[0, 10])
    fig.update_traces(fill='toself', line_color='#00CC96')
    fig.update_layout(
        polar=dict(radialaxis=dict(visible=True, range=[0, 10])),
        showlegend=False,
        margin=dict(l=40, r=40, t=40, b=40)
    )
    
    st.plotly_chart(fig, use_container_width=True)

    # 5. ANALYTICAL SCORING
    total_score = radar_data['Score'].mean()
    
    st.divider()
    res1, res2 = st.columns(2)
    res1.metric("Pricing Power Index", f"{total_score:.1f} / 10")

    # 6. COLD ANALYSIS VERDICT
    if total_score < 4:
        st.error(
            "🔴 **Price Taker:** You possess zero pricing authority. Any price increase will likely trigger "
            "immediate customer churn. Focus strictly on cost optimization and survival efficiency."
        )
    elif total_score < 7:
        st.warning(
            "🟠 **Defensive Position:** You have moderate structural protection. Price adjustments must be "
            "cautious and accompanied by clear value communication to prevent volume erosion."
        )
    else:
        st.success(
            "🏆 **Price Maker:** Significant structural insulation detected. You have the leverage to test "
            "price increases to expand margins with minimal risk of critical volume loss."
        )

    # 7. STRATEGIC LINKAGE
    st.write("---")
    st.subheader("Next Strategic Step")
    if st.button("Simulate Impact in Break-Even Simulator"):
        st.session_state.selected_tool = "Break-Even Shift Analysis"
        st.rerun()
