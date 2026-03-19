import streamlit as st
import pandas as pd

def calculate_sales_loss_threshold(our_p, u_cost, price_cut_pct):
    """
    McKinsey Pricing Logic: 
    Max Volume Loss = (Price Cut %) / (Current Margin % - Price Cut %)
    """
    current_margin_dollars = our_p - u_cost
    current_margin_pct = current_margin_dollars / our_p
    
    # Μετατροπή του cut σε δεκαδικό (π.χ. 10% -> 0.10)
    cut = abs(price_cut_pct) / 100
    
    try:
        # Ο τύπος υπολογίζει το σημείο αδιαφορίας (Indifference Point)
        denom = current_margin_pct - cut
        if denom <= 0: return None
        threshold = (cut / current_margin_pct) * 100
        return threshold
    except ZeroDivisionError:
        return None

def show_loss_threshold_before_price_cut():
    st.header("📉 Sales Loss Threshold Analysis")
    st.info("Strategic Pricing: Calculate the maximum volume loss you can absorb before a price match becomes necessary.")

    s = st.session_state
    
    # --- 1. DATA AUDIT & LINKING ---
    # Τραβάμε τα δεδομένα live από το Home Baseline
    base_price = float(s.get('price', 150.0))
    base_vc = float(s.get('variable_cost', 90.0))
    
    with st.expander("🔍 Linked Baseline Data", expanded=False):
        st.write(f"Current Price (from Home): **${base_price:,.2f}**")
        st.write(f"Current Unit VC (from Home): **${base_vc:,.2f}**")
        st.caption("To change these, go back to the Home Strategy Room.")

    st.divider()

    # --- 2. INPUT SECTION ---
    st.subheader("1. Competitor & Tactical Parameters")
    col1, col2 = st.columns(2)
    
    with col1:
        comp_old = st.number_input("Competitor Original Price ($)", value=base_price, step=1.0)
        comp_new = st.number_input("Competitor New Price ($)", value=base_price * 0.9, step=1.0)
    
    with col2:
        # Επιτρέπουμε τοπικό override για το πείραμα, αλλά με default τις τιμές του Home
        our_price = st.number_input("Our Current Price ($)", value=base_price, step=1.0)
        unit_cost = st.number_input("Our Unit Cost (VC) ($)", value=base_vc, step=1.0)

    # --- 3. CALCULATION ---
    # Υπολογίζουμε το % της μείωσης που έκανε ο ανταγωνιστής
    price_cut_pct = ((comp_new - comp_old) / comp_old) * 100 if comp_old != 0 else 0
    
    # Υπολογίζουμε το Threshold
    threshold = calculate_sales_loss_threshold(our_price, unit_cost, price_cut_pct)

    # --- 4. EXECUTIVE VERDICT ---
    st.divider()
    if threshold is not None:
        if threshold <= 0:
            st.error("🚨 **Systemic Vulnerability:** Your margins are too thin. Any price match will result in immediate loss.")
        else:
            # Executive Display Box
            st.subheader("2. Strategic Indifference Point")
            
            
            
            st.markdown(f"""
            <div style="background-color:#1E3A8A; padding:25px; border-radius:10px; color: white; text-align: center;">
                <h4 style="margin:0; color:#cbd5e1;">Max Allowable Volume Loss</h4>
                <p style="font-size:48px; font-weight:bold; margin:10px 0;">{threshold:.2f}%</p>
                <p style="font-size:16px; color:#94a3b8; line-height:1.4;">
                    If the competitor's <b>{abs(price_cut_pct):.1f}%</b> price cut results in a sales drop of 
                    <b>less than {threshold:.2f}%</b>, holding your price is more profitable than matching them.
                </p>
            </div>
            """, unsafe_allow_html=True)

            st.write("---")
            st.subheader("💡 Decision Matrix")
            
            c1, c2 = st.columns(2)
            margin_impact = (our_price - unit_cost) / our_price
            
            with c1:
                st.metric("Current Margin %", f"{margin_impact:.1%}")
                st.caption("Your buffer to absorb shocks.")
            
            with c2:
                if abs(price_cut_pct) > (margin_impact * 100):
                    st.warning("⚠️ **Warning:** The competitor's cut is deeper than your entire margin. Matching is impossible without rethinking your cost structure.")
                elif threshold < 10:
                    st.warning("⚠️ **High Sensitivity:** You can only afford a small volume loss. Matching might be necessary if the market is price-sensitive.")
                else:
                    st.success("✅ **Robust Buffer:** You can afford a significant volume drop. Avoid a price war.")

    # --- 5. NAVIGATION ---
    st.divider()
    if st.button("⬅️ Back to Control Tower", use_container_width=True):
        st.session_state.flow_step = "home"
        st.session_state.selected_tool = None
        st.rerun()
