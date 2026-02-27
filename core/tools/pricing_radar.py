import streamlit as st
from core.sync import sync_global_state
import pandas as pd

def show_pricing_power_radar():
    st.header("🎯 Pricing Power Radar")
    st.write("Resilience Analysis: How much volume can you lose if you increase the price?")
    
    # 1. FETCH DATA SAFELY
    m = sync_global_state()
    s = st.session_state
    
    current_price = s.get('price', 0.0)
    current_vc = s.get('variable_cost', 0.0)
    current_cm = m.get('unit_contribution', 0.0)
    
    if current_cm <= 0:
        st.warning("Current unit contribution is zero or negative. Pricing power analysis is limited.")
        return

    # 2. SIMULATION SLIDERS
    st.divider()
    price_change_pct = st.slider("Price Change Simulation (%)", -30, 50, 10)
    new_price = current_price * (1 + price_change_pct/100)
    new_cm = new_price - current_vc
    
    # 3. THE MATH OF "INDIFFERENCE"
    # Formula: ΔV = 1 - (Current CM / New CM)
    if new_cm > 0:
        permissible_vol_loss = 1 - (current_cm / new_cm)
    else:
        permissible_vol_loss = -1.0 

    # 4. EXECUTIVE DISPLAY
    col1, col2 = st.columns(2)
    col1.metric("New Price", f"{new_price:,.2f} €", f"{price_change_pct:+.1f}%")
    
    color = "normal" if price_change_pct > 0 else "inverse"
    col2.metric("Allowed Volume Change", f"{permissible_vol_loss*100:+.1f}%", delta_color=color)

    if price_change_pct > 0:
        st.info(f"**Analytical Verdict:** You can lose up to **{permissible_vol_loss*100:.1f}%** of your volume and maintain the SAME EBIT.")
    else:
        needed_gain = abs(permissible_vol_loss) * 100
        st.error(f"**Analytical Verdict:** You must increase volume by **{needed_gain:.1f}%** just to offset the price decrease.")

    # 5. SENSITIVITY TABLE (Προσθήκη για ολική εικόνα)
    st.subheader("📊 Price/Volume Sensitivity Matrix")
    sensitivity_data = []
    for pct in [-20, -10, -5, 5, 10, 15, 20, 25, 30]:
        temp_price = current_price * (1 + pct/100)
        temp_cm = temp_price - current_vc
        if temp_cm > 0:
            vol_change = (1 - (current_cm / temp_cm)) * 100
        else:
            vol_change = -100.0
        sensitivity_data.append({"Price Change": f"{pct}%", "Indifference Volume Δ": f"{vol_change:.1f}%"})
    
    st.table(pd.DataFrame(sensitivity_data))

    # 6. NAVIGATION
    st.divider()
    if st.button("Back to Library Hub", use_container_width=True):
        st.session_state.selected_tool = None
        st.session_state.mode = "library"
        st.rerun()
