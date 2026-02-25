import streamlit as st
from core.sync import sync_global_state  # FIXED: Use sync instead of raw engine

def show_pricing_power_radar():
    st.header("🎯 Pricing Power Radar")
    st.write("Resilience Analysis: How much volume can you lose if you increase the price?")
    
    # 1. FETCH DATA SAFELY
    # Η sync_global_state καλεί εσωτερικά την calculate_metrics με τα 11 ορίσματα
    m = sync_global_state()
    s = st.session_state
    
    # Χρήση .get() για να αποφύγουμε το AttributeError
    current_price = s.get('price', 0.0)
    current_vc = s.get('variable_cost', 0.0)
    current_cm = m.get('unit_contribution', 0.0)
    
    # Αν το CM είναι 0, ορίζουμε μια ελάχιστη τιμή για να αποφύγουμε διαίρεση με το μηδέν
    if current_cm <= 0:
        st.warning("Current unit contribution is zero or negative. Pricing power analysis is limited.")

    # 2. SIMULATION SLIDERS
    st.divider()
    price_change_pct = st.slider("Price Change Simulation (%)", -30, 50, 10)
    new_price = current_price * (1 + price_change_pct/100)
    new_cm = new_price - current_vc
    
    # 3. THE MATH OF "INDIFFERENCE" (Break-even Volume Change)
    # Formula: ΔV = 1 - (Current CM / New CM)
    if new_cm > 0:
        permissible_vol_loss = 1 - (current_cm / new_cm)
    else:
        permissible_vol_loss = -1.0 # 100% loss if price falls below variable cost

    # 4. EXECUTIVE DISPLAY
    col1, col2 = st.columns(2)
    
    col1.metric("New Price", f"{new_price:,.2f} €", f"{price_change_pct:+.1f}%")
    
    if price_change_pct > 0:
        color = "normal"
        msg = f"**Analytical Verdict:** You can lose up to **{permissible_vol_loss*100:.1f}%** of your volume and maintain the SAME EBIT."
    else:
        color = "inverse"
        # Στην περίπτωση μείωσης τιμής, το permissible_vol_loss είναι αρνητικό, 
        # άρα δείχνει πόσο πρέπει να ΑΥΞΗΘΕΙ ο όγκος.
        needed_gain = abs(permissible_vol_loss) * 100
        msg = f"**Analytical Verdict:** You must increase volume by **{needed_gain:.1f}%** just to offset the price decrease."
        
    col2.metric(
        "Allowed Volume Change", 
        f"{permissible_vol_loss*100:+.1f}%", 
        delta_color=color
    )

    st.info(msg)

    

    # 5. NAVIGATION
    st.divider()
    if st.button("Back to Library Hub", use_container_width=True):
        st.session_state.selected_tool = None
        st.session_state.mode = "library"
        st.rerun()
