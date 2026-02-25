import streamlit as st
import plotly.graph_objects as go
from core.sync import sync_global_state

def show_wacc_optimizer():
    # 1. FETCH CURRENT DATA
    metrics = sync_global_state()
    s = st.session_state
    
    st.header("📉 WACC Optimizer & Capital Structure")
    st.info("Analyze how shifting between Equity and Debt affects your Weighted Average Cost of Capital.")

    # 2. BASELINE VALUES
    current_wacc = s.get('wacc', 0.15)
    tax_rate = s.get('tax_rate', 0.22)

    # 3. OPTIMIZATION SLIDERS (With Unique Keys)
    st.subheader("🛠️ Adjust Capital Mix")
    col1, col2 = st.columns(2)
    
    with col1:
        cost_of_equity = st.slider("Cost of Equity (%)", 5.0, 30.0, float(current_wacc * 100), key="wacc_re") / 100
        cost_of_debt = st.slider("Cost of Debt (Pre-tax %)", 1.0, 20.0, 6.0, key="wacc_rd") / 100
    
    with col2:
        equity_weight = st.slider("Equity Weight (%)", 0, 100, 70, key="wacc_e_weight") / 100
        debt_weight = 1.0 - equity_weight
        st.caption(f"Resulting Debt Weight: {debt_weight:.0%}")

    # 4. WACC CALCULATION
    # Formula: $$WACC = (E/V * Re) + (D/V * Rd * (1 - T))$$
    after_tax_debt = cost_of_debt * (1 - tax_rate)
    optimized_wacc = (equity_weight * cost_of_equity) + (debt_weight * after_tax_debt)

    # 5. RESULTS & COMPARISON
    st.divider()
    m1, m2, m3 = st.columns(3)
    
    m1.metric("Current WACC", f"{current_wacc:.2%}")
    m2.metric("Optimized WACC", f"{optimized_wacc:.2%}", 
              delta=f"{optimized_wacc - current_wacc:+.2%}", 
              delta_color="inverse")
    m3.metric("Tax Shield Effect", f"{after_tax_debt:.2%}", help="Cost of Debt after tax deduction")
    
    # 6. VISUALIZATION
    
    
    labels = ['Equity', 'Debt']
    values = [equity_weight, debt_weight]
    
    fig = go.Figure(data=[go.Pie(labels=labels, values=values, hole=.3, marker=dict(colors=['#1f77b4', '#ff7f0e']))])
    fig.update_layout(title_text="Target Capital Structure", template="plotly_dark", height=400)
    st.plotly_chart(fig, use_container_width=True)

    # 7. ACTION BUTTONS
    col_btn1, col_btn2 = st.columns(2)
    
    with col_btn1:
        if st.button("🎯 Apply Optimized WACC", use_container_width=True, key="apply_wacc_btn"):
            st.session_state.wacc = optimized_wacc
            st.session_state.wacc_locked = True
            st.success(f"System WACC updated to {optimized_wacc:.2%}")
            st.rerun()

    with col_btn2:
        if st.button("⬅️ Back to Library Hub", use_container_width=True, key="back_from_wacc"):
            st.session_state.selected_tool = None
            st.rerun()
