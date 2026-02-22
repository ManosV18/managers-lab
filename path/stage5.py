# path/step5_strategy.py
"""
Stage 5: Strategic Stress Test, QSPM & Pricing Power Radar
"""

import streamlit as st
import pandas as pd
import numpy as np


# ═══════════════════════════════════════════════════════════
# HELPER FUNCTIONS FOR PRICING POWER
# ═══════════════════════════════════════════════════════════
def normalize(value, min_val, max_val):
    """Normalize value to 0-1 range"""
    if max_val - min_val == 0:
        return 0
    return (value - min_val) / (max_val - min_val)


def calculate_pricing_power_score(margin, substitution, elasticity, concentration):
    """Calculate composite pricing power score (0-100)"""
    # Margin strength (higher = better)
    margin_score = normalize(margin, 0, 0.8)
    
    # Substitution exposure (lower = better)
    substitution_score = 1 - normalize(substitution, 0, 1)
    
    # Elasticity fragility (lower elasticity = stronger power)
    elasticity_score = 1 - normalize(elasticity, 0, 3)
    
    # Revenue concentration risk (lower = better)
    concentration_score = 1 - normalize(concentration, 0, 1)
    
    final_score = (
        margin_score * 0.35 +
        substitution_score * 0.25 +
        elasticity_score * 0.25 +
        concentration_score * 0.15
    )
    
    return round(final_score * 100, 1)


def classify_power(score):
    """Classify pricing power level"""
    if score < 30:
        return "Weak Pricing Power", "🔴"
    elif score < 55:
        return "Defensive Structure", "🟠"
    elif score < 75:
        return "Strong Position", "🟢"
    else:
        return "Dominant Pricing Power", "🏆"


# ═══════════════════════════════════════════════════════════
# MAIN FUNCTION
# ═══════════════════════════════════════════════════════════
def run_step():
    st.header("🏁 Stage 5: Strategic Analysis & Decision Framework")
    
    # ═══════════════════════════════════════════════════════════
    # 1. CORE DATA SYNC
    # ═══════════════════════════════════════════════════════════
    p = st.session_state.get('price', 20.0)
    vc = st.session_state.get('variable_cost', 12.0)
    q = st.session_state.get('volume', 1000)
    fixed_cost = st.session_state.get('fixed_cost', 96000.0)  # ✅ Sync με Stage 0
    liquidity_drain_annual = st.session_state.get('liquidity_drain', 0.0)
    
    # Baseline profit (για delta comparison)
    baseline_profit = ((p - vc) * q) - fixed_cost - liquidity_drain_annual
    
    # ═══════════════════════════════════════════════════════════
    # 2. STRESS TEST (Analytical Resilience)
    # ═══════════════════════════════════════════════════════════
    st.subheader("🛠️ Model Stress Testing")
    
    col1, col2 = st.columns(2)
    with col1:
        drop_sales = st.slider("Drop in Sales Volume (%)", 0, 50, 20)
    with col2:
        inc_costs = st.slider("Increase in Variable Costs (%)", 0, 30, 10)
    
    # Stressed calculations
    stressed_q = q * (1 - drop_sales/100)
    stressed_vc = vc * (1 + inc_costs/100)
    stressed_profit = ((p - stressed_vc) * stressed_q) - fixed_cost - liquidity_drain_annual
    
    # ✅ Visual Delta: Διαφορά από baseline
    profit_delta = stressed_profit - baseline_profit
    
    st.metric(
        "Stress-Tested Annual Profit", 
        f"{stressed_profit:,.2f} €",
        delta=f"{profit_delta:,.2f} €",
        delta_color="normal"
    )
    
    st.caption(f"Baseline Profit: {baseline_profit:,.2f} € | Fixed Costs: {fixed_cost:,.2f} € | Liquidity Drain: {liquidity_drain_annual:,.2f} €")
    
    st.divider()
    
    # ═══════════════════════════════════════════════════════════
    # 3. PRICING POWER RADAR
    # ═══════════════════════════════════════════════════════════
    with st.expander("📊 **Pricing Power Radar** - Evaluate Structural Pricing Strength", expanded=False):
        st.write("Assess your pricing power beyond simple elasticity calculations.")
        
        # ✅ Auto-calculate margin from core data
        auto_margin = (p - vc) / p if p > 0 else 0
        
        st.info(f"📌 **Auto-detected Margin:** {auto_margin*100:.1f}% (from Price: {p}€, VC: {vc}€)")
        
        col_a, col_b = st.columns(2)
        
        with col_a:
            st.subheader("Market Exposure")
            substitution = st.slider("Substitution Exposure (%)", 0.0, 100.0, 40.0, key="ppr_sub") / 100
            elasticity = st.slider("Price Elasticity", 0.1, 3.0, 1.2, key="ppr_elast")
        
        with col_b:
            st.subheader("Business Structure")
            concentration = st.slider("Revenue Concentration (%)", 0.0, 100.0, 30.0, key="ppr_conc") / 100
        
        # Calculate using auto margin
        score = calculate_pricing_power_score(auto_margin, substitution, elasticity, concentration)
        label, icon = classify_power(score)
        
        st.divider()
        
        # Results
        res1, res2 = st.columns(2)
        res1.metric("Pricing Power Score", f"{score}/100")
        res2.metric("Classification", f"{icon} {label}")
        
        # Interpretation
        if score < 30:
            st.error("⚠️ Weak pricing power. Price increases likely destroy volume.")
        elif score < 55:
            st.warning("⚡ Defensive position. Pricing decisions must be cautious.")
        elif score < 75:
            st.success("✅ Strong position. Measurable pricing flexibility exists.")
        else:
            st.success("🏆 Dominant pricing power. Brand/positioning creates insulation.")
        
        # Drivers breakdown
        st.subheader("🧠 Structural Drivers")
        drivers_df = pd.DataFrame({
            "Driver": [
                "Margin Strength",
                "Substitution Protection",
                "Elasticity Resistance",
                "Revenue Diversification"
            ],
            "Impact Level": [
                f"{auto_margin*100:.1f}%",
                f"{(1-substitution)*100:.1f}%",
                f"{(1 - (elasticity/3))*100:.1f}%",
                f"{(1-concentration)*100:.1f}%"
            ]
        })
        st.dataframe(drivers_df, use_container_width=True)
    
    st.divider()
    
    # ═══════════════════════════════════════════════════════════
    # 4. INTERACTIVE QSPM
    # ═══════════════════════════════════════════════════════════
    st.subheader("🎯 Custom QSPM: Strategic Selection")
    st.write("Define your weights and rate the attractiveness of each strategy.")
    
    # User-Defined Weights
    with st.expander("⚖️ Edit Strategic Weights (Must sum to 1.0)", expanded=True):
        c1, c2, c3 = st.columns(3)
        w_margin = c1.slider("Profit Margin Weight", 0.0, 0.5, 0.3, key="qspm_w1")
        w_growth = c2.slider("Market Growth Weight", 0.0, 0.5, 0.2, key="qspm_w2")
        w_liquidity = c3.slider("Cash Liquidity Weight", 0.0, 0.5, 0.3, key="qspm_w3")
        
        c4, c5 = st.columns(2)
        w_rivalry = c4.slider("Competitive Rivalry Weight", 0.0, 0.5, 0.1, key="qspm_w4")
        w_brand = c5.slider("Brand Equity Weight", 0.0, 0.5, 0.1, key="qspm_w5")
        
        total_w = w_margin + w_growth + w_liquidity + w_rivalry + w_brand
        st.write(f"**Total Weight Sum: {total_w:.2f}**")
        
        if round(total_w, 2) != 1.0:
            st.warning("⚠️ Adjust weights to sum to 1.0 for valid QSPM analysis.")
    
    # User-Defined Attractiveness Scores
    st.write("### Rate Strategy Attractiveness (1 = Low, 4 = High)")
    col_a, col_b = st.columns(2)
    
    with col_a:
        st.markdown("**Strategy A: Aggressive Scaling**")
        as_a_margin = st.selectbox("Margin Match (A)", [1,2,3,4], index=1, key="q_a1")
        as_a_liquidity = st.selectbox("Liquidity Match (A)", [1,2,3,4], index=0, key="q_a2")
    
    with col_b:
        st.markdown("**Strategy B: Efficiency First**")
        as_b_margin = st.selectbox("Margin Match (B)", [1,2,3,4], index=3, key="q_b1")
        as_b_liquidity = st.selectbox("Liquidity Match (B)", [1,2,3,4], index=3, key="q_b2")
    
    # QSPM Table Generation
    factors = [
        ("Operating Margin", w_margin, as_a_margin, as_b_margin),
        ("Market Growth", w_growth, 4, 2),
        ("Cash Liquidity", w_liquidity, as_a_liquidity, as_b_liquidity),
        ("Competitive Rivalry", w_rivalry, 2, 3),
        ("Brand Equity", w_brand, 3, 2)
    ]
    
    qspm_list = []
    for f, w, as_a, as_b in factors:
        qspm_list.append({
            "Key Factor": f,
            "Weight": w,
            "Scale (AS)": as_a,
            "Scale (TAS)": w * as_a,
            "Efficiency (AS)": as_b,
            "Efficiency (TAS)": w * as_b
        })
    
    df_qspm = pd.DataFrame(qspm_list)
    st.table(df_qspm)
    
    # Final Verdict
    total_tas_a = df_qspm["Scale (TAS)"].sum()
    total_tas_b = df_qspm["Efficiency (TAS)"].sum()
    
    st.divider()
    res_a, res_b = st.columns(2)
    res_a.metric("Scaling Score (TAS)", f"{total_tas_a:.2f}")
    res_b.metric("Efficiency Score (TAS)", f"{total_tas_b:.2f}")
    
    if total_tas_a > total_tas_b:
        st.success("🚀 **QSPM favors SCALING.** Growth is the recommended path forward.")
    else:
        st.warning("⚖️ **QSPM favors EFFICIENCY.** Focus on risk mitigation and optimization.")
    
    # ═══════════════════════════════════════════════════════════
    # 5. NAVIGATION
    # ═══════════════════════════════════════════════════════════
    st.divider()
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("⬅️ Back to Sustainability"):
            st.session_state.flow_step = 4
            st.rerun()
    
    with col2:
        if st.button("🔄 Restart Lab Analysis", type="primary", use_container_width=True):
            st.session_state.flow_step = 0
            st.rerun()
