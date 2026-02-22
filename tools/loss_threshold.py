import streamlit as st
from core.engine import compute_core_metrics

def normalize(value, min_val, max_val):
    if max_val - min_val == 0: return 0
    return (value - min_val) / (max_val - min_val)

def show_pricing_power_radar():
    st.header("🎯 Pricing Power Radar")
    st.info("Evaluate your structural ability to maintain prices regardless of market pressure.")

    # 1. FETCH BASELINE
    metrics = compute_core_metrics()
    p = st.session_state.get('price', 0.0)
    vc = st.session_state.get('variable_cost', 0.0)
    
    auto_margin = (p - vc) / p if p > 0 else 0

    # 2. INPUT PARAMETERS (The 4 Pillars of Pricing Power)
    st.subheader("Market Positioning Factors")
    
    col1, col2 = st.columns(2)
    with col1:
        substitution = st.slider("Substitution Exposure (%)", 0, 100, 40, 
                                 help="How easy is it for customers to switch to a competitor or alternative?") / 100
        elasticity = st.slider("Price Elasticity", 0.1, 3.0, 1.2,
                               help="Sensitivity of demand to price changes. (1.0 = Proportional)")
    with col2:
        concentration = st.slider("Revenue Concentration (%)", 0, 100, 30,
                                  help="Percentage of revenue coming from your top 3 clients.") / 100
        brand_premium = st.slider("Brand/IP Strength (%)", 0, 100, 50,
                                  help="The value customers perceive beyond the functional utility.") / 100

    # 3. SCORING LOGIC (Cold Weights)
    # Η λογική παραμένει σταθερή: Υψηλά margins και brand + χαμηλό substitution και concentration = Υψηλή δύναμη.
    margin_score = normalize(auto_margin, 0, 0.8)
    sub_score = 1 - substitution
    elast_score = 1 - normalize(elasticity, 0, 3)
    conc_score = 1 - concentration
    brand_score = brand_premium

    final_score = (margin_score * 0.30 + sub_score * 0.25 + elast_score * 0.20 + conc_score * 0.15 + brand_score * 0.10) * 100

    # 4. RESULTS
    st.divider()
    
    
    
    res1, res2 = st.columns(2)
    res1.metric("Pricing Power Score", f"{final_score:.1f}/100")
    
    if final_score < 35:
        res2.error("🔴 Price Taker")
    elif final_score < 60:
        res2.warning("🟠 Defensive")
    else:
        res2.success("🟢 Price Maker")

    # 5. COLD VERDICT
    st.subheader("🧠 Strategic Verdict")
    if final_score < 35:
        st.write("You are an 'Order Taker'. Your price is dictated by the market. Any increase in Variable Costs will directly hit your survival buffer because you cannot pass the cost to the customer.")
    elif final_score < 60:
        st.write("You have a defensive moat, likely due to niche positioning or high switching costs. You can survive moderate shocks, but aggressive pricing is risky.")
    else:
        st.write("You are a 'Price Maker'. You have significant structural autonomy. You can optimize for profit rather than just volume.")

    st.caption(f"Calculated with an auto-detected contribution margin of {auto_margin:.1%}")
