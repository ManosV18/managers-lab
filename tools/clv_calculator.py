import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from core.engine import compute_core_metrics

def get_clv_data(purchases, margin_per_order, retention_years, discount, churn, realization, risk_p, cac):
    # Adjusted discount rate for risk: (Base Discount + Risk Premium)
    adj_disc = (discount / 100) + (risk_p / 100)
    churn_rate = churn / 100
    cum_npv = -cac
    data = []
    payback = None
    
    for t in range(1, int(retention_years) + 1):
        # Survival probability: (1 - churn)^t
        survival = (1 - churn_rate) ** t
        # Realized cash flow after risk and survival
        annual_flow = (purchases * margin_per_order * realization) * survival
        # Discounted to present value
        discounted_flow = annual_flow / ((1 + adj_disc) ** t)
        
        cum_npv += discounted_flow
        data.append({"Year": t, "Cumulative_NPV": cum_npv})
        
        if cum_npv >= 0 and payback is None:
            payback = t
            
    return pd.DataFrame(data), cum_npv, payback

def show_clv_calculator():
    st.header("👥 Executive CLV Simulator")
    st.info("Advanced Customer Lifetime Value modeling: Syncing Unit Economics with Risk-Adjusted NPV.")

    # 1. SYNC WITH SHARED CORE
    metrics = compute_core_metrics()
    p = st.session_state.get('price', 0.0)
    vc = st.session_state.get('variable_cost', 0.0)
    
    # Τραβάμε το WACC απευθείας από τον Engine (που το παίρνει από το Sidebar)
    wacc_global = metrics.get('wacc', 0.10) * 100 
    
    unit_margin = metrics['unit_contribution']
    st.write(f"**🔗 Core Baseline Linked:** Current Unit Margin: **{unit_margin:,.2f} €**")

    st.divider()

    # 2. SCENARIO INPUTS
    col_a, col_b = st.columns(2)
    
    with col_a:
        st.subheader("📊 Scenario A (Base)")
        purch_a = st.number_input("Purchases / Year (A)", value=4.0, key="pa")
        units_a = st.number_input("Units / Order (A)", value=1.0, key="ua")
        cac_a = st.number_input("CAC (€) (A)", value=150.0, key="caca")
        churn_a = st.slider("Annual Churn % (A)", 0, 100, 15, key="cha")

    with col_b:
        st.subheader("🚀 Scenario B (Target)")
        purch_b = st.number_input("Purchases / Year (B)", value=5.0, key="pb")
        units_b = st.number_input("Units / Order (B)", value=1.2, key="ub") # Default 1.2 για να δούμε διαφορά
        cac_b = st.number_input("CAC (€) (B)", value=180.0, key="cacb")
        churn_b = st.slider("Annual Churn % (B)", 0, 100, 8, key="chb")

    # 3. STRUCTURAL ASSUMPTIONS (NPV Logic)
    with st.expander("⚙️ NPV & Risk-Adjusted WACC Settings"):
        st.markdown("""
        **NPV Logic:** Προεξοφλούμε τις μελλοντικές ροές κάθε πελάτη στο σήμερα, αφαιρώντας το κόστος απόκτησης (CAC).
        """)
        
        c1, c2 = st.columns(2)
        # Χρήση του παγκόσμιου WACC με δυνατότητα τοπικής υπέρβασης
        disc = c1.number_input("Base WACC (%)", value=float(wacc_global))
        risk_p = c1.number_input("Risk Premium (%)", value=3.0, help="Extra risk for this segment.")
        real = c2.number_input("Realization Rate (0-1)", value=0.90, help="Probability of collecting the full margin.")
        horizon = c2.slider("Analysis Horizon (Years)", 1, 10, 5)
        
        total_rate = disc + risk_p
        st.caption(f"**Effective Discount Rate:** {total_rate:.2f}%")

    # 4. EXECUTION
    margin_a = unit_margin * units_a
    margin_b = unit_margin * units_b

    df_a, final_a, pb_a = get_clv_data(purch_a, margin_a, horizon, disc, churn_a, real, risk_p, cac_a)
    df_b, final_b, pb_b = get_clv_data(purch_b, margin_b, horizon, disc, churn_b, real, risk_p, cac_b)

    # 5. RESULTS COMPARISON
    st.divider()
    res_a, res_b = st.columns(2)
    
    with res_a:
        st.metric("NPV CLV (A)", f"{final_a:,.2f} €")
        ltv_a = final_a + cac_a
        ratio_a = ltv_a / cac_a if cac_a > 0 else 0
        st.write(f"LTV/CAC Ratio: **{ratio_a:.2f}x**")
        st.caption(f"Payback: {f'{pb_a} Yrs' if pb_a else 'Never'}")

    with res_b:
        st.metric("NPV CLV (B)", f"{final_b:,.2f} €", delta=f"{final_b - final_a:,.2f} €")
        ltv_b = final_b + cac_b
        ratio_b = ltv_b / cac_b if cac_b > 0 else 0
        st.write(f"LTV/CAC Ratio: **{ratio_b:.2f}x**")
        st.caption(f"Payback: {f'{pb_b} Yrs' if pb_b else 'Never'}")

    # 6. VISUALIZATION
    st.subheader("📉 Cumulative NPV Projection")
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df_a['Year'], y=df_a['Cumulative_NPV'], name='Scenario A', line=dict(color='#EF553B', dash='dash')))
    fig.add_trace(go.Scatter(x=df_b['Year'], y=df_b['Cumulative_NPV'], name='Scenario B', line=dict(color='#00CC96', width=4)))
    fig.add_hline(y=0, line_dash="dot", line_color="white")
    fig.update_layout(xaxis_title="Years", yaxis_title="Cumulative Value (€)", height=400, template="plotly_dark")
    st.plotly_chart(fig, use_container_width=True)

    

    # 7. STRATEGIC VERDICT
    st.divider()
    if ratio_b >= 3.0:
        st.success("🎯 **Strategy B is Scalable:** The LTV is at least 3x the CAC, which is the industry standard for healthy growth.")
    else:
        st.warning("⚠️ **Efficiency Risk:** LTV/CAC ratio is below 3.0. You are buying customers too expensively for the value they return.")

    if st.button("Back to Library Hub"):
        st.session_state.selected_tool = None
        st.rerun()
