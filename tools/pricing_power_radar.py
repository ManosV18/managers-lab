import streamlit as st
from core.engine import compute_core_metrics

def show_pricing_power_radar():
    st.subheader("🎯 Pricing Power Radar")
    st.write("Resilience Analysis: How much volume can you lose if you increase the price?")
    
    # 1. Fetch data from the Engine
    m = compute_core_metrics()
    current_price = st.session_state.price
    current_vc = st.session_state.variable_cost
    current_cm = m['unit_contribution']
    
    # 2. Simulation Sliders
    st.divider()
    price_change_pct = st.slider("Price Change Simulation (%)", -30, 50, 10)
    new_price = current_price * (1 + price_change_pct/100)
    new_cm = new_price - current_vc
    
    # 3. The Math of "Indifference" (Break-even Point)
    # Correction: Check if the new contribution margin is positive
    if new_cm > 0:
        permissible_vol_loss = 1 - (current_cm / new_cm)
    else:
        permissible_vol_loss = -1.0 # 100% loss if the price falls below variable cost

    # 4. Executive Display
    col1, col2 = st.columns(2)
    
    col1.metric("New Price", f"{new_price:,.2f} €", f"{price_change_pct:+.1f}%")
    
    # FORMAT CORRECTION: Use :+.1f instead of :+.1;f
    if price_change_pct > 0:
        color = "normal"
        msg = f"You can lose up to **{permissible_vol_loss*100:.1f}%** of your customers and maintain the SAME profit."
    else:
        color = "inverse"
        # In the case of a price decrease, permissible_vol_loss is negative,
        # so it shows how much volume you MUST gain.
        msg = f"You need to increase volume by **{abs(permissible_vol_loss)*100:.1f}%** to offset the price decrease."
        
    col2.metric(
        "Allowed Volume Change", 
        f"{permissible_vol_loss*100:+.1f}%", 
        delta_color=color
    )

    st.info(msg)

    # 5. Navigation
    if st.button("Back to Library Hub"):
        st.session_state.selected_tool = None
        st.session_state.mode = "library"
        st.rerun()
