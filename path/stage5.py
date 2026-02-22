import streamlit as st
import pandas as pd
import numpy as np
from core.engine import compute_core_metrics

# ═══════════════════════════════════════════════════════════
# HELPER FUNCTIONS
# ═══════════════════════════════════════════════════════════
def normalize(value, min_val, max_val):
    if max_val - min_val == 0: return 0
    return (value - min_val) / (max_val - min_val)

def calculate_pricing_power_score(margin, substitution, elasticity, concentration):
    margin_score = normalize(margin, 0, 0.8)
    substitution_score = 1 - normalize(substitution, 0, 1)
    elasticity_score = 1 - normalize(elasticity, 0, 3)
    concentration_score = 1 - normalize(concentration, 0, 1)
    
    final_score = (margin_score * 0.35 + substitution_score * 0.25 + 
                   elasticity_score * 0.25 + concentration_score * 0.15)
    return round(final_score * 100, 1)

def classify_power(score):
    if score < 30: return "Weak Pricing Power", "🔴"
    elif score < 55: return "Defensive Structure", "🟠"
    elif score < 75: return "Strong Position", "🟢"
    else: return "Dominant Pricing Power", "🏆"

# ═══════════════════════════════════════════════════════════
# MAIN FUNCTION
# ═══════════════════════════════════════════════════════════
def run_stage5():
    st.header("🏁 Stage 5: Strategic Analysis & Decision Framework")
    st.caption("Final synthesis: Stress testing and strategic selection.")
    
    # 1. CORE DATA SYNC
    metrics = compute_core_metrics()
    p = st.session_state.price
    vc = st.session_state.variable_cost
    q = st.session_state.volume
    fixed_cost = st.session_state.fixed_cost
    liquidity_drain = st.session_state.liquidity_drain_annual
    
    baseline_profit = metrics['net_profit']
    
    # 2. STRESS TEST
    st.subheader("🛠️ Model Stress Testing")
    col1, col2 = st.columns(2)
    with col1:
        drop_sales = st.slider("Drop in Sales Volume (%)", 0, 50, 20)
    with col2:
        inc_costs = st.slider("Increase in Variable Costs (%)", 0, 30, 10)
    
    stressed_q = q * (1 - drop_sales/100)
    stressed_vc = vc * (1 + inc_costs/100)
    # Stressed calculation using core logic
    stressed_ebit = ((p - stressed_vc) * stressed_q) - fixed_cost
    interest_cost = metrics.get('interest', 0.0)
    stressed_profit = stressed_ebit - interest_cost - liquidity_drain
    
    profit_delta = stressed_profit - baseline_profit
    
    st.metric(
        "Stress-Tested Annual Profit", 
        f"{stressed_profit:,.2f} €",
        delta=f"{profit_delta:,.2f} €",
        delta_color="normal"
    )
    
    # 3. PRICING POWER RADAR
    
    with st.expander("📊 Pricing Power Radar", expanded=False):
        auto_margin = metrics['unit_contribution'] / p if p > 0 else 0
        st.info(f"📌 Auto-detected Margin: {auto_margin:.1%}")
        
        c_a, c_b = st.columns(2)
        substitution = c_a.slider("Substitution Exposure (%)", 0, 100, 40) / 100
        elasticity = c_a.slider("Price Elasticity", 0.1, 3.0, 1.2)
        concentration = c_b.slider("Revenue Concentration (%)", 0, 100, 30) / 100
        
        score = calculate_pricing_power_score(auto_margin, substitution, elasticity, concentration)
        label, icon = classify_power(score)
        
        res1, res2 = st.columns(2)
        res1.metric("Pricing Power Score", f"{score}/100")
        res2.metric("Classification", f"{icon} {label}")

    st.divider()

    # 4. INTERACTIVE QSPM
    st.subheader("🎯 Custom QSPM: Strategic Selection")
    
    with st.expander("⚖️ Edit Strategic Weights (Sum = 1.0)", expanded=True):
        w_margin = st.slider("Profit Margin Weight", 0.0, 0.5, 0.4)
        w_liquidity = st.slider("Cash Liquidity Weight", 0.0, 0.5, 0.4)
        w_growth = 1.0 - (w_margin + w_liquidity)
        st.write(f"Remaining Growth Weight: **{w_growth:.2f}**")

    # QSPM Simple Logic
    st.write("### Rate Strategy Attractiveness (1-4)")
    ca, cb = st.columns(2)
    as_a = ca.slider("Strategy A (Scaling) - Overall Match", 1, 4, 2)
    as_b = cb.slider("Strategy B (Efficiency) - Overall Match", 1, 4, 3)
    
    total_a = (w_margin * as_a) + (w_liquidity * (as_a-1)) + (w_growth * 4)
    total_b = (w_margin * as_b) + (w_liquidity * as_b) + (w_growth * 2)

    st.divider()
    r_a, r_b = st.columns(2)
    r_a.metric("Scaling Score", f"{total_a:.2f}")
    r_b.metric("Efficiency Score", f"{total_b:.2f}")
    
    if total_a > total_b:
        st.success("🚀 **Decision: SCALING.** The model supports aggressive growth.")
    else:
        st.warning("⚖️ **Decision: EFFICIENCY.** Focus on margin and cash optimization.")

    # 5. NAVIGATION
    st.divider()
    nav1, nav2 = st.columns(2)
    with nav1:
        if st.button("⬅️ Back to Sustainability"):
            st.session_state.flow_step = 4
            st.rerun()
    with nav2:
        if st.button("🔄 Restart Lab Analysis", type="primary", use_container_width=True):
            st.session_state.flow_step = 0
            st.session_state.mode = "home"
            st.rerun()
