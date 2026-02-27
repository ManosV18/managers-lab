import streamlit as st
import pandas as pd

def show_pricing_radar():
    st.header("📡 Strategic Pricing Radar")
    st.info("Resilience Analysis: How much volume can you afford to lose if you increase prices?")
    
    # 1. FETCH DATA DIRECTLY FROM SESSION STATE (Cold Analysis)
    # Using defaults if the user hasn't completed Stage 0
    s = st.session_state
    current_price = float(s.get('price', 100.0))
    current_vc = float(s.get('variable_cost', 60.0))
    current_cm = current_price - current_vc
    
    # Display current base parameters
    with st.expander("🔍 View Current Base Parameters"):
        c_a, c_b, c_c = st.columns(3)
        c_a.metric("Base Price", f"€{current_price:,.2f}")
        c_b.metric("Variable Cost", f"€{current_vc:,.2f}")
        c_c.metric("Unit Contribution", f"€{current_cm:,.2f}")

    if current_cm <= 0:
        st.warning("⚠️ Current unit contribution is zero or negative. Pricing power analysis is mathematically restricted.")
        if st.button("⬅️ Back to Library"):
            st.session_state.selected_tool = None
            st.rerun()
        return

    # 2. SIMULATION SLIDERS
    st.divider()
    st.subheader("🕹️ Simulation Scenarios")
    price_change_pct = st.slider("Simulated Price Change (%)", -30, 50, 10)
    
    new_price = current_price * (1 + price_change_pct/100)
    new_cm = new_price - current_vc
    
    # 3. THE MATH OF "INDIFFERENCE" (Break-even Volume)
    # Formula: Required Volume Change = (Current CM / New CM) - 1
    if new_cm > 0:
        # We use the indifference formula to find the volume change that keeps Gross Profit stable
        permissible_vol_change = (current_cm / new_cm) - 1
    else:
        permissible_vol_change = -1.0 

    # 4. EXECUTIVE METRICS
    col1, col2 = st.columns(2)
    col1.metric("New Simulated Price", f"€{new_price:,.2f}", f"{price_change_pct:+.1f}%")
    
    # Logic: If price goes up, volume can go down. If price goes down, volume must go up.
    color = "normal" if price_change_pct > 0 else "inverse"
    col2.metric("Indifference Volume Δ", f"{permissible_vol_change*100:+.1f}%", delta_color=color)

    # 5. ANALYTICAL VERDICT
    st.markdown("---")
    if price_change_pct > 0:
        st.success(f"**Verdict:** You can lose up to **{abs(permissible_vol_change)*100:.1f}%** of your volume and maintain the SAME total profit.")
    elif price_change_pct < 0:
        st.error(f"**Verdict:** You must increase volume by **{abs(permissible_vol_change)*100:.1f}%** just to offset the price decrease.")
    else:
        st.info("No price change selected.")

    # 6. SENSITIVITY MATRIX
    st.subheader("📊 Price/Volume Sensitivity Matrix")
    st.write("This table shows the 'Breakeven Volume' for various price points.")
    
    sensitivity_data = []
    for pct in [-20, -10, -5, 0, 5, 10, 15, 20, 25, 30]:
        temp_price = current_price * (1 + pct/100)
        temp_cm = temp_price - current_vc
        if temp_cm > 0:
            vol_change = ((current_cm / temp_cm) - 1) * 100
        else:
            vol_change = -100.0
        
        sensitivity_data.append({
            "Price Δ (%)": f"{pct:+d}%",
            "New Price (€)": f"{temp_price:,.2f}",
            "Max Vol. Loss / Needed Gain (%)": f"{vol_change:+.1f}%"
        })
    
    st.table(pd.DataFrame(sensitivity_data))

    # 7. NAVIGATION
    st.divider()
    if st.button("⬅️ Back to Library Hub", use_container_width=True):
        st.session_state.selected_tool = None
        st.rerun()
