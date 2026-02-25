import streamlit as st
import plotly.graph_objects as go
from core.sync import sync_global_state

def show_wacc_optimizer():
    metrics = sync_global_state()
    s = st.session_state
    
    st.header("📉 WACC Optimizer (Hamada Logic)")
    st.info("The Cost of Equity ($Re$) now adjusts automatically as you increase Debt, reflecting the higher financial risk.")

    # 1. BASELINE DATA
    current_wacc = s.get('wacc', 0.15)
    tax_rate = s.get('tax_rate', 0.22)
    
    # 2. HAMADA INPUTS
    st.subheader("⚙️ Risk Parameters")
    c1, c2 = st.columns(2)
    with c1:
        unlevered_beta = st.slider("Unlevered Beta (Business Risk)", 0.5, 2.0, 1.0, help="Risk of the business without any debt.")
    with c2:
        risk_free_rate = st.slider("Risk-Free Rate (%)", 1.0, 10.0, 4.0) / 100
        market_premium = st.slider("Market Risk Premium (%)", 3.0, 10.0, 6.0) / 100

    st.subheader("🛠️ Capital Mix & Impact")
    col1, col2 = st.columns(2)
    
    with col1:
        equity_weight = st.slider("Equity Weight (%)", 10, 100, 70, key="wacc_e_weight") / 100
        debt_weight = 1.0 - equity_weight
        d_e_ratio = debt_weight / equity_weight if equity_weight > 0 else 0

    # 3. HAMADA EQUATION & CAPM
    # Step 1: Levered Beta = Unlevered Beta * [1 + (1 - T) * (D/E)]
    levered_beta = unlevered_beta * (1 + (1 - tax_rate) * d_e_ratio)
    
    # Step 2: Cost of Equity (CAPM) = Rf + Beta * (Rm - Rf)
    adjusted_re = risk_free_rate + (levered_beta * market_premium)
    
    with col2:
        cost_of_debt = st.number_input("Cost of Debt (Pre-tax %)", 1.0, 25.0, 6.0) / 100
        after_tax_rd = cost_of_debt * (1 - tax_rate)
        st.metric("Adjusted Cost of Equity (Re)", f"{adjusted_re:.2%}", help="Calculated via Hamada + CAPM")

    # 4. WACC CALCULATION
    optimized_wacc = (equity_weight * adjusted_re) + (debt_weight * after_tax_rd)

    # 5. RESULTS
    st.divider()
    m1, m2, m3 = st.columns(3)
    m1.metric("Levered Beta", f"{levered_beta:.2f}")
    m2.metric("Optimized WACC", f"{optimized_wacc:.2%}", 
              delta=f"{optimized_wacc - current_wacc:+.2%}", delta_color="inverse")
    m3.metric("D/E Ratio", f"{d_e_ratio:.2f}")

    # 6. VISUALIZATION: THE WACC CURVE
    # Generate data for the U-shaped curve
    e_range = [i/100 for i in range(10, 101, 5)]
    wacc_curve = []
    for e in e_range:
        d = 1.0 - e
        de = d / e
        l_beta = unlevered_beta * (1 + (1 - tax_rate) * de)
        re = risk_free_rate + (l_beta * market_premium)
        w = (e * re) + (d * after_tax_rd)
        wacc_curve.append(w)

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=[(1-e)*100 for e in e_range], y=wacc_curve, name="WACC Curve", line
