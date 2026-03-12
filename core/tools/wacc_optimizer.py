import streamlit as st
import pandas as pd
import plotly.graph_objects as go

def get_clv_data(purchases, margin_per_order, retention_years, discount, churn, realization, risk_p, cac):
    """
    Calculates NPV Customer Lifetime Value year-by-year
    """
    # Convert percentages to decimals
    adj_disc = (float(discount) / 100) + (float(risk_p) / 100)
    churn_rate = float(churn) / 100
    cum_npv = -float(cac)
    data = []
    payback = None
    
    for t in range(1, int(retention_years) + 1):
        # Survival probability at year t: (1 - churn)^t
        survival = (1 - churn_rate) ** t
        # Realized cash flow adjusted for survival
        annual_flow = (float(purchases) * float(margin_per_order) * float(realization)) * survival
        # Discount to present value using risk-adjusted rate
        discounted_flow = annual_flow / ((1 + adj_disc) ** t)
        cum_npv += discounted_flow
        
        data.append({"Year": t, "Cumulative_NPV": float(cum_npv)})
        if cum_npv >= 0 and payback is None:
            payback = t
            
    return pd.DataFrame(data), cum_npv, payback

def show_clv_calculator():
    st.header("👥 Executive CLV Simulator")
    st.info("Advanced Unit Economics: Linking Customer Retention and Margins to Risk-Adjusted NPV.")

    s = st.session_state
    m = s.get("metrics", {})
    
    if not s.get('baseline_locked', False):
        st.warning("🔒 Access Denied: Please lock your Baseline in Home to enable CLV Unit Economics.")
        return 

    # Fetch dynamic unit economics from Global State (Engine)
    unit_margin = m.get('unit_contribution', float(s.get('price', 0) - s.get('variable_cost', 0)))
    
    st.write(f"**🔗 Core Engine Linked:** Current Unit Contribution: **{unit_margin:,.2f} €**")
    st.divider()

    # --- SCENARIOS INPUT ---
    col_a, col_b = st.columns(2)
    with col_a:
        st.subheader("📊 Scenario A (Baseline)")
        purch_a = st.number_input("Purchases / Year (A)", value=4.0, key="pa")
        units_a = st.number_input("Units / Order (A)", value=1.0, key="ua")
        cac_a = st.number_input("CAC (€) (A)", value=150.0, key="caca")
        churn_a = st.slider("Annual Churn % (A)", 0, 100, 15, key="cha")

    with col_b:
        st.subheader("🚀 Scenario B (Optimization)")
        purch_b = st.number_input("Purchases / Year (B)", value=5.0, key="pb")
        units_b = st.number_input("Units / Order (B)", value=1.2, key="ub")
        cac_b = st.number_input("CAC (€) (B)", value=180.0, key="cacb")
        churn_b = st.slider("Annual Churn % (B)", 0, 100, 8, key="chb")

    # --- NPV & RISK SETTINGS (The Linked Logic) ---
    with st.expander("⚙️ NPV Discount & Realization Settings", expanded=True):
        c1, c2 = st.columns(2)
        
        # Check for locked WACC from WACC Optimizer
        suggested_wacc = s.get('wacc_locked', 15.0)
        
        disc = c1.number_input(
            "Base Hurdle Rate / WACC (%)", 
            value=float(suggested_wacc),
            help="Defaults to locked WACC from Optimizer, but you can override it."
        )
        
        if 'wacc_locked' in s:
            st.caption(f"🔗 **Linked:** Using locked WACC ({s.wacc_locked:.2f}%)")
        else:
            st.caption("ℹ️ **Standard Rate:** Using default 15%. Calculate WACC to link.")

        risk_p = c1.number_input("Risk Premium (%)", value=3.0, help="Additional risk for churn volatility.")
        real = c2.number_input("Realization Rate (0.0 - 1.0)", value=0.90, help="Adjustment for non-collected revenue.")
        horizon = c2.slider("Analysis Horizon (Years)", 1, 15, 5)
        st.caption(f"**Effective Risk-Adjusted Discount Rate:** {disc + risk_p:.2f}%")

    # --- CALCULATION EXECUTION ---
    margin_a = unit_margin * units_a
    margin_b = unit_margin * units_b

    df_a, final_a, pb_a = get_clv_data(purch_a, margin_a, horizon, disc, churn_a, real, risk_p, cac_a)
    df_b, final_b, pb_b = get_clv_data(purch_b, margin_b, horizon, disc, churn_b, real, risk_p, cac_b)

    # --- RESULTS DASHBOARD ---
    st.divider()
    res_a, res_b = st.columns(2)
    
    with res_a:
        st.metric("NPV CLV (Scenario A)", f"{final_a:,.2f} €")
        ltv_a = final_a + cac_a
        ratio_a = ltv_a / cac_a if cac_a > 0 else 0
        st.write(f"LTV/CAC Ratio: **{ratio_a:.2f}x**")
        st.caption(f"Payback Period: {f'{pb_a} Years' if pb_a else 'Not Reached'}")

    with res_b:
        st.metric("NPV CLV (Scenario B)", f"{final_b:,.2f} €", delta=f"{final_b - final_a:,.2f} €")
        ltv_b = final_b + cac_b
        ratio_b = ltv_b / cac_b if cac_b > 0 else 0
        st.write(f"LTV/CAC Ratio: **{ratio_b:.2f}x**")
        st.caption(f"Payback Period: {f'{pb_b} Years' if pb_b else 'Not Reached'}")

    # --- VISUALIZATION ---
    st.subheader("📉 Cumulative NPV Projection")
    
    
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df_a['Year'], y=df_a['Cumulative_NPV'], name='Scenario A',
                             line=dict(color='#EF553B', dash='dash')))
    fig.add_trace(go.Scatter(x=df_b['Year'], y=df_b['Cumulative_NPV'], name='Scenario B',
                             line=dict(color='#00CC96', width=4)))
    fig.add_hline(y=0, line_dash="dot", line_color="white", annotation_text="Break-even Line")
    fig.update_layout(height=400, template="plotly_dark", margin=dict(l=20, r=20, t=20, b=20),
                      xaxis_title="Year", yaxis_title="Cumulative NPV (€)")
    st.plotly_chart(fig, use_container_width=True)

    # --- STRATEGIC VERDICT ---
    if ratio_b >= 3.0:
        st.success("🎯 **Strategic Verdict:** Scalable Unit Economics. LTV/CAC ≥ 3x meets the high-growth benchmark.")
    elif ratio_b >= 1.0:
        st.warning("⚠️ **Strategic Verdict:** Marginal Efficiency. The system is profitable but lacks significant scaling buffer.")
    else:
        st.error("🚨 **Strategic Verdict:** Value Destruction. CAC exceeds LTV. Every new customer reduces firm value.")

    # --- NAVIGATION ---
    st.divider()
    if st.button("⬅️ Back to Control Tower", use_container_width=True):
        st.session_state.flow_step = "home"
        st.session_state.selected_tool = None
        st.rerun()
