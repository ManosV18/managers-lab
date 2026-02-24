import streamlit as st
from core.engine import compute_core_metrics

def show_pricing_power_radar():
    st.subheader("🎯 Pricing Power Radar")
    st.write("Ανάλυση ανθεκτικότητας: Πόσο Volume μπορείς να χάσεις αν αυξήσεις την τιμή;")
    
    # 1. Λήψη δεδομένων από τον Engine
    m = compute_core_metrics()
    current_price = st.session_state.price
    current_vc = st.session_state.variable_cost
    current_cm = m['unit_contribution']
    
    # 2. Simulation Sliders
    st.divider()
    price_change_pct = st.slider("Προσομοίωση Μεταβολής Τιμής (%)", -30, 50, 10)
    new_price = current_price * (1 + price_change_pct/100)
    new_cm = new_price - current_vc
    
    # 3. Τα Μαθηματικά της "Ισορροπίας" (Indifference Point)
    # Για να μείνει το συνολικό Contribution Margin ίδιο:
    # New_Vol * New_CM = Old_Vol * Old_CM  =>  New_Vol/Old_Vol = Old_CM / New_CM
    if new_cm > 0:
        permissible_vol_loss = 1 - (current_cm / new_cm)
    else:
        permissible_vol_loss = -1.0 # Fatal state

    # 4. Executive Display
    col1, col2 = st.columns(2)
    
    col1.metric("Νέα Τιμή", f"{new_price:,.2f} €", f"{price_change_pct:+.1f}%")
    
    if price_change_pct > 0:
        color = "normal"
        msg = f"Μπορείς να χάσεις έως και **{permissible_vol_loss*100:.1f}%** των πελατών σου και να έχεις το ΙΔΙΟ κέρδος."
    else:
        color = "inverse"
        msg = f"Πρέπει να αυξήσεις το Volume κατά **{abs(permissible_vol_loss)*100:.1f}%** για να καλύψεις τη μείωση τιμής."
        
    col2.metric("Επιτρεπτή Μεταβολή Volume", f"{permissible_vol_loss*100:+.1;f}%", delta_color=color)

    st.info(msg)

    

    # 5. Reset Button για το Tool
    if st.button("Back to Library Hub"):
        st.session_state.selected_tool = None
        st.session_state.mode = "library"
        st.rerun()
