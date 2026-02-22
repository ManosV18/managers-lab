import streamlit as st
import pandas as pd
import plotly.express as px
from core.engine import compute_core_metrics

def show_pricing_power_radar():
    st.header("🎯 Pricing Power Radar")
    st.caption("Strategic Audit: Evaluate your structural ability to defend or increase prices.")

    # 1. FETCH CONTEXT
    metrics = compute_core_metrics()
    p = st.session_state.price
    vc = st.session_state.variable_cost
    current_margin = (metrics['unit_contribution'] / p) * 100 if p > 0 else 0

    # 2. EVALUATION PILLARS
    st.subheader("Structural Assessment")
    st.write("Rate your position on a scale of 1 (Weak) to 10 (Dominant).")

    col1, col2 = st.columns(2)
    
    with col1:
        brand_score = st.slider("Brand Equity & Loyalty", 1, 10, 5, 
                                help="Do customers choose you for 'who' you are or just for the price?")
        switching_costs = st.slider("Switching Costs", 1, 10, 5, 
                                help="How difficult/expensive is it for a customer to move to a competitor?")
        
    with col2:
        scarcity_score = st.slider("Product Scarcity / IP", 1, 10, 5, 
                                help="Do you have unique features, patents, or limited availability?")
        market_share = st.slider("Market Concentration", 1, 10, 5, 
                                help="Are you a leader in a niche or one of many small players?")

    # 3. CALCULATIONS
    # Προσθέτουμε και το Margin ως 5ο πυλώνα (αυτόματα από το Engine)
    margin_score = min(int(current_margin / 5), 10) if current_margin > 0 else 1
    
    radar_data = pd.DataFrame({
        'Pillar': ['Brand', 'Switching Costs', 'Scarcity', 'Market Power', 'Margin Strength'],
        'Score': [brand_score, switching_costs, scarcity_score, market_share, margin_score]
    })

    # 4. VISUALIZATION
    
    
    fig = px.line_polar(radar_data, r='Score', theta='Pillar', line_close=True,
                        template="plotly_dark", range_r=[0, 10])
    fig.update_traces(fill='toself', line_color='#00CC96')
    fig.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0, 10])))
    
    st.plotly_chart(fig, use_container_width=True)

    # 5. ANALYST'S SCORE & VERDICT
    total_score = radar_data['Score'].mean()
    
    st.divider()
    res1, res2 = st.columns(2)
    res1.metric("Pricing Power Index", f"{total_score:.1f} / 10")

    # 6. COLD ANALYSIS VERDICT
    if total_score < 4:
        st.error("🔴 **Price Taker:** Δεν έχετε καμία δύναμη επιβολής τιμής. Οποιαδήποτε αύξηση θα προκαλέσει άμεση φυγή πελατών. Εστιάστε στη μείωση κόστους.")
    elif total_score < 7:
        st.warning("🟠 **Defensive Position:** Έχετε κάποια προστασία, αλλά η τιμολόγηση πρέπει να είναι προσεκτική. Χρειάζεστε 'συνοδευτική' αξία για κάθε αύξηση.")
    else:
        st.success("🏆 **Price Maker:** Διαθέτετε ισχυρή δομική προστασία. Μπορείτε να δοκιμάσετε αυξήσεις τιμών για τη βελτίωση του Margin με χαμηλό ρίσκο.")

    # 7. STRATEGIC LINK
    if st.button("Simulate Price Increase in Simulator"):
        st.session_state.selected_tool = "Break-Even Shift Analysis"
        st.rerun()
