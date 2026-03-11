import streamlit as st
import plotly.graph_objects as go

def show_wacc_optimizer():
    # 1. FETCH DATA (Analytical Consistency)
    s = st.session_state
    st.header("📉 WACC Optimizer")
    st.info("The Cost of Equity (Re) adjusts dynamically based on the Debt/Equity ratio, reflecting the leveraged systematic risk.")

    # 2. BASELINE DATA
    current_wacc = s.get('wacc', 0.15)
    tax_rate = s.get('tax_rate', 0.22)
    
    # 3. HAMADA & CAPM INPUTS
    st.subheader("1. Risk & Market Parameters")
    
    c1, c2 = st.columns(2)
    with c1:
        unlevered_beta = st.slider("Unlevered Beta (Business Risk)", 0.5, 2.0, 1.0, 
                                    help="The intrinsic risk of the industry without financial leverage.", key="ham_ub")
    with c2:
        risk_free_rate = st.slider("Risk-Free Rate (%)", 1.0, 10.0, 4.0, key="ham_rf") / 100
        market_premium = st.slider("Market Risk Premium (%)", 3.0, 10.0, 6.0, key="ham_mrp") / 100

    st.subheader("2. Capital Structure Simulation")
    col1, col2 = st.columns(2)
    
    with col1:
        equity_weight = st.slider("Equity Weight (%)", 10, 100, 70, key="wacc_e_weight_slider") / 100
        debt_weight = 1.0 - equity_weight
        d_e_ratio = debt_weight / equity_weight if equity_weight > 0 else 0

    # 4. CALCULATIONS (Hamada Logic)
    # Step 1: Levered Beta = Unlevered Beta * [1 + (1 - T) * (D/E)]
    levered_beta = unlevered_beta * (1 + (1 - tax_rate) * d_e_ratio)
    
    # Step 2: Cost of Equity (CAPM) = Rf + Beta * (Rm - Rf)
    adjusted_re = risk_free_rate + (levered_beta * market_premium)
    
    with col2:
        cost_of_debt = st.number_input("Cost of Debt (Pre-tax %)", 1.0, 25.0, 6.0, key="ham_rd") / 100
        after_tax_rd = cost_of_debt * (1 - tax_rate)
        st.metric("Adjusted Cost of Equity (Re)", f"{adjusted_re:.2%}", help="Increases as Debt/Equity increases due to financial risk.")

    # Step 3: WACC = (E/V * Re) + (D/V * Rd * (1-T))
    optimized_wacc = (equity_weight * adjusted_re) + (debt_weight * after_tax_rd)

    # 5. RESULTS DASHBOARD
    st.divider()
    m1, m2, m3 = st.columns(3)
    m1.metric("Levered Beta", f"{levered_beta:.2f}")
    m2.metric("Optimized WACC", f"{optimized_wacc:.2%}", 
              delta=f"{optimized_wacc - current_wacc:+.2%}", delta_color="inverse")
    m3.metric("D/E Ratio", f"{d_e_ratio:.2f}")

    # 6. VISUALIZATION: THE OPTIMAL WACC CURVE
    
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
    fig.add_trace(go.Scatter(x=[(1-e)*100 for e in e_range], y=wacc_curve, 
                             name="WACC Curve", line=dict(color='#00ffcc', width=3)))
    fig.add_vline(x=debt_weight*100, line_dash="dash", line_color="red", annotation_text="Current Debt")
    fig.update_layout(title="WACC vs. Leverage (Identifying the Optimal Point)", 
                      xaxis_title="Debt Weight (%)", yaxis_title="WACC (%)", 
                      template="plotly_dark", height=400)
    st.plotly_chart(fig, use_container_width=True)

    # 7. ANALYST'S VERDICT
    st.subheader("🧠 Strategic Verdict")
    if d_e_ratio > 2.0:
        st.error("🚨 **High Leverage Warning:** The current D/E ratio significantly inflates your Cost of Equity. The system is highly sensitive to market shocks.")
    elif optimized_wacc < current_wacc:
        st.success("✅ **Optimization Potential:** The simulated mix results in a lower cost of capital than the current system baseline.")
    else:
        st.warning("⚖️ **Conservative Position:** Increasing equity weight may stabilize the system but increases the overall cost of capital due to the lack of tax shields.")

    # 8. ACTION BUTTONS
    cb1, cb2 = st.columns(2)
    with cb1:
        if st.button("🎯 Apply to System", use_container_width=True):
            st.session_state.wacc = optimized_wacc
            st.success("System WACC updated!")
            st.rerun()
    with cb2:
        if st.button("⬅️ Back to Library Hub", use_container_width=True):
            st.session_state.selected_tool = None
            st.rerun()
