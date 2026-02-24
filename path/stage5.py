import streamlit as st
import pandas as pd
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
    st.caption("Final synthesis: Stress testing the model and making the cold-blooded strategic choice.")
    
    # 1. CORE DATA SYNC
    metrics = compute_core_metrics()
    p = st.session_state.get('price', 0)
    vc = st.session_state.get('variable_cost', 0)
    q = st.session_state.get('volume', 0)
    fixed_cost = st.session_state.get('fixed_cost', 0)
    liquidity_drain = st.session_state.get('liquidity_drain_annual', 0)
    
    baseline_profit = metrics['net_profit']
    
    # 2. STRESS TEST
    st.subheader("🛠️ Model Stress Testing")
    st.write("How does the business react to negative market shifts?")
    col1, col2 = st.columns(2)
    with col1:
        drop_sales = st.slider("Drop in Sales Volume (%)", 0, 50, 20)
    with col2:
        inc_costs = st.slider("Increase in Variable Costs (%)", 0, 30, 10)
    
    # Stressed Calculations
    stressed_q = q * (1 - drop_sales/100)
    stressed_vc = vc * (1 + inc_costs/100)
    
    # Διορθωμένο profit calculation (περιλαμβάνει φόρους αν το ebit είναι θετικό)
    stressed_ebit = ((p - stressed_vc) * stressed_q) - fixed_cost
    interest_cost = st.session_state.get('debt', 0) * st.session_state.get('interest_rate', 0.05)
    stressed_ebt = stressed_ebit - interest_cost
    stressed_tax = max(0, stressed_ebt * st.session_state.get('tax_rate', 0.22))
    stressed_profit = stressed_ebt - stressed_tax - liquidity_drain
    
    profit_delta = stressed_profit - baseline_profit
    
    st.metric(
        "Stress-Tested Annual Profit", 
        f"{stressed_profit:,.0f} €",
        delta=f"{profit_delta:,.0f} € vs Baseline",
        delta_color="normal"
    )
    
    if stressed_profit < 0:
        st.error("💀 **Critical Failure:** Under this stress scenario, the enterprise destroys cash.")
    else:
        st.success("🛡️ **Resilience:** The system remains profitable even under pressure.")

    # 3. PRICING POWER RADAR
    st.divider()
    with st.expander("📊 Pricing Power Radar", expanded=False):
        auto_margin = metrics['unit_contribution'] / p if p > 0 else 0
        st.info(f"📌 Auto-detected Gross Margin: {auto_margin:.1%}")
        
        c_a, c_b = st.columns(2)
        substitution = c_a.slider("Substitution Exposure (%)", 0, 100, 40) / 100
        elasticity = c_a.slider("Price Elasticity (1.0 = neutral)", 0.1, 3.0, 1.2)
        concentration = c_b.slider("Client Concentration (%)", 0, 100, 30) / 100
        
        score = calculate_pricing_power_score(auto_margin, substitution, elasticity, concentration)
        label, icon = classify_power(score)
        
        res1, res2 = st.columns(2)
        res1.metric("Pricing Power Score", f"{score}/100")
        res2.metric("Classification", f"{icon} {label}")

    

    # 4. INTERACTIVE QSPM
    st.divider()
    st.subheader("🎯 Strategic Selection (QSPM)")
    
    with st.expander("⚖️ Strategic Weights (Sum = 1.0)", expanded=True):
        w_margin = st.slider("Weight: Profit Margin", 0.0, 0.5, 0.4)
        w_liquidity = st.slider("Weight: Cash Liquidity", 0.0, 0.5, 0.4)
        w_growth = round(1.0 - (w_margin + w_liquidity), 2)
        st.write(f"Remaining Weight for Growth: **{w_growth}**")

    st.write("### Strategy Attractiveness Score (1-4)")
    ca, cb = st.columns(2)
    as_a = ca.slider("Scaling (Aggressive Expansion)", 1, 4, 2)
    as_b = cb.slider("Efficiency (Cost & WC Optimization)", 1, 4, 3)
    
    # Simple weighted score
    total_a = (w_margin * as_a) + (w_liquidity * (as_a-1)) + (w_growth * 4)
    total_b = (w_margin * as_b) + (w_liquidity * as_b) + (w_growth * 2)

    r_a, r_b = st.columns(2)
    r_a.metric("Scaling Strategy Score", f"{total_a:.2f}")
    r_b.metric("Efficiency Strategy Score", f"{total_b:.2f}")
    
    if total_a > total_b:
        st.success("🚀 **Strategic Mandate: SCALING.** The model supports expansion.")
    else:
        st.warning("⚖️ **Strategic Mandate: EFFICIENCY.** Focus on margin and cash cycles.")

    # 5. NAVIGATION
    st.divider()
    nav1, nav2 = st.columns(2)
    with nav1:
        if st.button("⬅️ Back to Stress Test"):
            st.session_state.flow_step = 4
            st.rerun()
    with nav2:
        if st.button("🔄 Restart Managers' Lab", type="primary", use_container_width=True):
            st.session_state.flow_step = 0
            st.session_state.mode = "home"
            st.rerun()
