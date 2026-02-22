import streamlit as st
from core.engine import compute_core_metrics

def show_loss_threshold_before_price_cut():
    st.header("📉 Loss Threshold Analysis")
    st.info("Calculate the maximum allowable price reduction or volume drop before the business enters a deficit.")

    # 1. FETCH BASELINE DATA
    metrics = compute_core_metrics()
    p = st.session_state.get('price', 0.0)
    vc = st.session_state.get('variable_cost', 0.0)
    q = st.session_state.get('volume', 0)
    
    current_margin_per_unit = p - vc
    current_total_contribution = current_margin_per_unit * q
    fixed_obligations = st.session_state.get('fixed_cost', 0.0) + metrics.get('interest', 0.0)

    # 2. ANALYSIS
    st.subheader("Current Structural Resistance")
    
    

    # Υπολογισμός του Margin of Safety σε επίπεδο τιμής
    # Break-even Price = (Fixed Obligations / Q) + VC
    be_price = (fixed_obligations / q) + vc if q > 0 else 0
    max_price_cut = p - be_price
    max_price_cut_pct = (max_price_cut / p) * 100 if p > 0 else 0

    c1, c2 = st.columns(2)
    c1.metric("Current Unit Margin", f"{current_margin_per_unit:,.2f} €")
    c1.metric("Break-even Price", f"{be_price:,.2f} €", help="The price below which you lose money on every sale considering fixed costs.")
    
    c2.metric("Max Price Cut Allowed", f"{max_price_cut:,.2f} €", delta=f"-{max_price_cut_pct:.1f}%", delta_color="inverse")
    
    st.divider()

    # 3. INTERACTIVE SIMULATOR
    st.subheader("What-If Scenario")
    new_price = st.slider("Simulated Price Change (€)", 
                          min_value=float(vc), 
                          max_value=float(p * 1.5), 
                          value=float(p))
    
    new_margin = new_price - vc
    new_ebit = (new_margin * q) - fixed_obligations
    
    if new_ebit < 0:
        st.error(f"🚨 **Warning:** At a price of {new_price:,.2f} €, you will have an annual loss of {abs(new_ebit):,.2f} €.")
    else:
        st.success(f"✅ **Safe:** At this price, you still generate {new_ebit:,.2f} € in net profit.")

    # 4. COLD VERDICT
    st.markdown(f"""
    ### 🧠 Strategic Insight
    Your business model has a **{max_price_cut_pct:.1f}% pricing buffer**. 
    If your competitors drop prices more than this, or if your costs (VC) rise by more than **{max_price_cut:,.2f} €** per unit, 
    your current volume will no longer be enough to sustain your fixed obligations.
    """)
