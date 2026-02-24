import streamlit as st
import pandas as pd
import numpy as np
from core.engine import compute_core_metrics

def get_clv_data(purchases, margin_per_order, retention_years, discount, churn, realization, risk_p, cac):
    # Το discount rate περιλαμβάνει το WACC και το ειδικό Risk Premium
    adj_disc = (discount/100) + (risk_p/100)
    churn_rate = churn/100
    cum_npv = -cac
    data = []
    
    # Year 0: Acquisition Phase
    data.append({"Year": 0, "Annual_Cash_Flow": -cac, "Cumulative_NPV": -cac})
    
    payback = None
    for t in range(1, int(retention_years) + 1):
        # Πιθανότητα ο πελάτης να είναι ακόμα ενεργός
        survival_prob = (1 - churn_rate)**t
        
        # Ετήσια ροή: (Συχνότητα * Περιθώριο * Πιθανότητα Είσπραξης) * Πιθανότητα Επιβίωσης
        annual_flow = (purchases * margin_per_order * realization) * survival_prob
        
        # Προεξόφληση (Discounting)
        discounted_flow = annual_flow / ((1 + adj_disc)**t)
        
        cum_npv += discounted_flow
        data.append({
            "Year": t, 
            "Annual_Cash_Flow": annual_flow, 
            "Cumulative_NPV": cum_npv
        })
        
        if cum_npv >= 0 and payback is None:
            payback = t
            
    return pd.DataFrame(data), cum_npv, payback

def run_stage3():
    st.header("👥 Stage 3: Unit Economics (CLV & CAC)")
    st.caption("Strategic Value Audit: Evaluating the Net Present Value of Customer Assets.")

    # 1. Engine Sync
    metrics = compute_core_metrics()
    unit_margin = metrics.get('unit_contribution', 0)
    
    st.info(f"🔗 **Engine Sync:** Current Unit Contribution: **{unit_margin:,.2f} €**")

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Customer Behavior")
        purchases = st.number_input("Annual Purchase Frequency", min_value=0.1, value=4.0, step=0.5, key="freq_s3")
        units_per_order = st.number_input("Units per Order", min_value=1.0, value=1.0, step=0.5, key="units_s3")
        churn = st.slider("Annual Churn Rate (%)", 0, 100, 15, key="churn_s3")

    with col2:
        st.subheader("Acquisition Economics")
        cac = st.number_input("Acquisition Cost (CAC) per Customer (€)", min_value=0.0, value=150.0, key="cac_s3")
        horizon = st.slider("Analysis Horizon (Years)", 1, 15, 5, key="horizon_s3")

    with st.expander("⚙️ Risk & NPV Assumptions", expanded=False):
        c1, c2 = st.columns(2)
        base_wacc = st.session_state.get('wacc', 0.12) * 100
        disc = c1.number_input("Base Discount Rate (WACC %)", value=float(base_wacc), key="wacc_s3")
        risk_p = c1.number_input("Customer Risk Premium (%)", value=3.0, help="Extra risk for specific customer segments.", key="risk_s3")
        real = c2.number_input("Cash Realization Rate (0.0-1.0)", value=0.9, min_value=0.1, max_value=1.0, key="real_s3")

    # 2. Calculations
    total_margin_per_order = unit_margin * units_per_order
    df, clv_npv, payback = get_clv_data(purchases, total_margin_per_order, horizon, disc, churn, real, risk_p, cac)

    # 3. KPIs
    st.divider()
    m1, m2, m3 = st.columns(3)
    m1.metric("Risk-Adjusted CLV (NPV)", f"{clv_npv:,.2f} €")
    m2.metric("Acquisition Cost (CAC)", f"{cac:,.2f} €")
    
    ltv_cac_ratio = (clv_npv + cac) / cac if cac > 0 else 0
    m3.metric("LTV / CAC Ratio", f"{ltv_cac_ratio:.2f}x", 
              delta="Target > 3.0x", delta_color="normal" if ltv_cac_ratio >= 3 else "inverse")

    # 4. Visual Analysis
    st.subheader("Customer Equity Curve (Cumulative NPV)")
    # Χρωματισμός της γραμμής για να ξεχωρίζει το break-even
    st.line_chart(df.set_index("Year")["Cumulative_NPV"])
    
    # 5. Cold Assessment Logic
    st.divider()
    st.subheader("🔬 Analytical Conclusion")
    
    if ltv_cac_ratio < 1.0:
        st.error(f"🚨 **Value Destruction:** You are spending {cac}€ to acquire an asset worth {clv_npv+cac:.2f}€. This is a direct drain on capital.")
    elif ltv_cac_ratio < 3.0:
        st.warning(f"⚠️ **Inefficient Scaling:** Ratio ({ltv_cac_ratio:.2f}x) is below the 3.0x benchmark. Payback period: {payback if payback else '>'+str(horizon)} years. Growth will be capital-intensive.")
    else:
        st.success(f"🏆 **High-Velocity Asset:** Strong unit economics. Payback achieved in Year {payback if payback else 'N/A'}. This model supports aggressive scaling.")

    # 6. Navigation
    st.divider()
    nav1, nav2 = st.columns(2)
    with nav1:
        if st.button("⬅️ Back to Liquidity", use_container_width=True):
            st.session_state.flow_step = 2
            st.rerun()
    with nav2:
        if st.button("Proceed to Stage 4: Survival Stress Test ➡️", type="primary", use_container_width=True):
            st.session_state.flow_step = 4
            st.rerun()
