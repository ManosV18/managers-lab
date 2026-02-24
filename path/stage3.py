import streamlit as st
import pandas as pd
from core.engine import compute_core_metrics

def get_clv_data(purchases, margin_per_order, retention_years, discount, churn, realization, risk_p, cac):
    adj_disc = (discount/100) + (risk_p/100)
    churn_rate = churn/100
    cum_npv = -cac
    data = []
    
    # Έτος 0: Η στιγμή της απόκτησης (μόνο έξοδο CAC)
    data.append({"Year": 0, "Cumulative_NPV": -cac})
    
    payback = None
    for t in range(1, int(retention_years) + 1):
        survival = (1 - churn_rate)**t
        annual_flow = (purchases * margin_per_order * realization) * survival
        discounted_flow = annual_flow / ((1 + adj_disc)**t)
        cum_npv += discounted_flow
        data.append({"Year": t, "Cumulative_NPV": cum_npv})
        
        if cum_npv >= 0 and payback is None:
            payback = t
            
    return pd.DataFrame(data), cum_npv, payback

def run_stage3():
    st.header("👥 Stage 3: Unit Economics (CLV & CAC)")
    st.caption("Advanced Customer Lifetime Value modeling: Syncing Unit Economics with Risk-Adjusted NPV.")

    # 1. Σύνδεση με τον Engine
    metrics = compute_core_metrics()
    unit_margin = metrics.get('unit_contribution', 0)
    st.info(f"🔗 **Core Engine Linked:** Current Unit Margin: **{unit_margin:,.2f} €**")

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Customer Behavior")
        purchases = st.number_input("Annual Purchase Frequency", value=4.0, step=1.0)
        units_per_order = st.number_input("Units per Order", value=1.0, step=1.0)
        churn = st.slider("Annual Churn Rate (%)", 0, 100, 15)

    with col2:
        st.subheader("Acquisition & Horizon")
        cac = st.number_input("Acquisition Cost (CAC) per Customer (€)", min_value=0.0, value=150.0)
        horizon = st.slider("Analysis Horizon (Years)", 1, 15, 5)

    with st.expander("⚙️ NPV & Risk Assumptions"):
        c1, c2 = st.columns(2)
        # Χρήση του WACC από το Stage 0 ως βάση
        base_wacc = st.session_state.get('wacc', 0.12) * 100
        disc = c1.number_input("Base Discount Rate (WACC %)", value=float(base_wacc))
        risk_p = c1.number_input("Specific Customer Risk Premium (%)", value=3.0)
        real = c2.number_input("Cash Realization Rate (0.0-1.0)", value=0.9, max_value=1.0)

    # 2. Υπολογισμοί CLV
    total_margin_per_order = unit_margin * units_per_order
    df, clv_npv, payback = get_clv_data(purchases, total_margin_per_order, horizon, disc, churn, real, risk_p, cac)

    # 3. Key Performance Indicators
    st.divider()
    m1, m2, m3 = st.columns(3)
    m1.metric("Risk-Adjusted CLV (NPV)", f"{clv_npv:,.2f} €")
    m2.metric("CAC", f"{cac:,.2f} €")
    
    # LTV/CAC Ratio (Gross LTV = NPV + CAC)
    ltv_cac_ratio = (clv_npv + cac) / cac if cac > 0 else 0
    m3.metric("LTV / CAC Ratio", f"{ltv_cac_ratio:.2f}x")

    # 4. Visual Analysis (The Break-even Chart)
    st.subheader("Customer Equity Growth (Cumulative NPV)")
    st.line_chart(df.set_index("Year"))
    
    

    # 5. Cold Assessment
    if ltv_cac_ratio < 3.0:
        st.warning(f"⚠️ **Fragile Economics:** Ratio ({ltv_cac_ratio:.2f}x) is below the 3.0x benchmark. Payback period: {payback if payback else '>'+str(horizon)} years.")
    else:
        st.success(f"🏆 **Scalable Asset:** High CLV relative to CAC. Payback achieved in Year {payback if payback else 'N/A'}.")

    # 6. Navigation
    st.divider()
    nav1, nav2 = st.columns(2)
    with nav1:
        if st.button("⬅️ Back to Liquidity", use_container_width=True):
            st.session_state.flow_step = 2
            st.rerun()
    with nav2:
        if st.button("Proceed to Survival Stress Test ➡️", type="primary", use_container_width=True):
            st.session_state.flow_step = 4
            st.rerun()
