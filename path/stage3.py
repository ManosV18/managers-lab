import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from core.engine import compute_core_metrics

def get_clv_data(purchases, margin_per_order, retention_years, discount, churn, realization, risk_p, cac):
    adj_disc = (discount / 100) + (risk_p / 100)
    churn_rate = churn / 100
    cum_npv = -cac
    data = []
    payback = None
    
    for t in range(1, int(retention_years) + 1):
        survival = (1 - churn_rate) ** t
        annual_flow = (purchases * margin_per_order * realization) * survival
        discounted_flow = annual_flow / ((1 + adj_disc) ** t)
        cum_npv += discounted_flow
        data.append({"Year": t, "Cumulative_NPV": cum_npv})
        if cum_npv >= 0 and payback is None:
            payback = t
    return pd.DataFrame(data), cum_npv, payback

def run_stage3():
    st.header("👥 Stage 3: Unit Economics (CLV & CAC)")
    st.caption("Advanced Customer Lifetime Value modeling: Syncing Unit Economics with Risk-Adjusted NPV.")

    # 1. SYNC WITH SHARED CORE
    metrics = compute_core_metrics()
    unit_margin = metrics['unit_contribution']
    st.info(f"🔗 **Core Engine Linked:** Current Unit Margin: **{unit_margin:,.2f} €**")

    # 2. INPUTS (Simplifying for the Path, using Scenario B as primary)
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Customer Behavior")
        purchases = st.number_input("Annual Purchase Frequency", value=4.0)
        units_per_order = st.number_input("Units per Order", value=1.0)
        churn = st.slider("Annual Churn Rate (%)", 0, 100, 15)
        
    with col2:
        st.subheader("Acquisition & Horizon")
        cac = st.number_input("Acquisition Cost (CAC) per Customer (€)", value=150.0)
        horizon = st.slider("Analysis Horizon (Years)", 1, 15, 5)

    # 3. ADVANCED ASSUMPTIONS (Expander to keep UI clean)
    with st.expander("⚙️ NPV & Risk Assumptions"):
        c1, c2 = st.columns(2)
        disc = c1.number_input("Base Discount Rate (%)", value=8.0)
        risk_p = c1.number_input("Customer Risk Premium (%)", value=3.0)
        real = c2.number_input("Realization Rate (0.0-1.0)", value=0.90)

    # 4. CALCULATION
    total_margin_per_order = unit_margin * units_per_order
    df, clv_npv, payback = get_clv_data(purchases, total_margin_per_order, horizon, disc, churn, real, risk_p, cac)

    # 5. DISPLAY METRICS
    st.divider()
    
    m1, m2, m3 = st.columns(3)
    m1.metric("Risk-Adjusted CLV (NPV)", f"{clv_npv:,.2f} €")
    m2.metric("CAC", f"{cac:,.2f} €")
    
    ltv_cac_ratio = (clv_npv + cac) / cac if cac > 0 else 0
    m3.metric("LTV/CAC Ratio", f"{ltv_cac_ratio:.2f}x")

    # 6. COLD VERDICT
    if ltv_cac_ratio < 3.0:
        st.warning("⚠️ **Fragile Economics:** The ratio is below the 3.0x industry benchmark. Scaling might destroy capital.")
    else:
        st.success("🏆 **Scalable Asset:** High CLV relative to CAC confirms structural strength.")

    # 7. NAVIGATION
    st.divider()
    nav1, nav2 = st.columns(2)
    with nav1:
        if st.button("⬅️ Back to Capital Structure"):
            st.session_state.flow_step = 2
            st.rerun()
    with nav2:
        if st.button("Proceed to Survival Stress Test ➡️", type="primary"):
            st.session_state.flow_step = 4
            st.rerun()
