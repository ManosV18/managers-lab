import streamlit as st
import pandas as pd

def show_pricing_radar():
    st.header("📡 Strategic Pricing Radar")
    st.info("Resilience Analysis: Identifying the Indifference Point between Price and Volume.")
    
    # 1. FETCH DATA (Cold Analysis from Session State)
    s = st.session_state
    m = s.get("metrics", {})
    
    current_price = float(s.get('price', 100.0))
    current_vc = float(s.get('variable_cost', 60.0))
    current_cm = current_price - current_vc
    
    with st.expander("🔍 Current Margin Baseline", expanded=False):
        c_a, c_b, c_c = st.columns(3)
        c_a.metric("Base Price", f"€{current_price:,.2f}")
        c_b.metric("Variable Cost", f"€{current_vc:,.2f}")
        c_c.metric("Unit Contribution", f"€{current_cm:,.2f}")

    if current_cm <= 0:
        st.error("🚨 Negative Contribution Margin detected. Pricing analysis is mathematically void until Unit Cost < Price.")
        if st.button("⬅️ Back to Library"):
            st.session_state.selected_tool = None
            st.rerun()
        return

    # 2. SIMULATION SLIDERS
    st.subheader("🕹️ Pricing Simulation")
    price_change_pct = st.slider("Simulated Price Change (%)", -30, 50, 10, help="Adjust to see the required volume offset.")
    
    new_price = current_price * (1 + price_change_pct/100)
    new_cm = new_price - current_vc
    
    # 3. THE MATH OF INDIFFERENCE
    # Formula: Required Volume Change = (Current CM / New CM) - 1
    if new_cm > 0:
        permissible_vol_change = (current_cm / new_cm) - 1
    else:
        permissible_vol_change = -1.0 # Total collapse of margin

    # 4. EXECUTIVE METRICS
    col1, col2 = st.columns(2)
    col1.metric("New Simulated Price", f"€{new_price:,.2f}", f"{price_change_pct:+.1f}%")
    
    # Logic: Upward price movement allows for downward volume movement.
    color_logic = "normal" if price_change_pct > 0 else "inverse"
    col2.metric("Volume Indifference Δ", f"{permissible_vol_change*100:+.1f}%", 
                delta_color=color_logic, help="The percentage change in volume that results in ZERO change to total Gross Profit.")

    # 5. ANALYTICAL VERDICT
    st.divider()
    
    
    if price_change_pct > 0:
        st.success(f"**Verdict:** A {price_change_pct}% price increase allows for a **{abs(permissible_vol_change)*100:.1f}%** drop in volume before profitability is impacted. This is your 'Pricing Safety Buffer'.")
    elif price_change_pct < 0:
        st.warning(f"**Verdict:** A {abs(price_change_pct)}% price cut requires a **{abs(permissible_vol_change)*100:.1f}%** INCREASE in volume just to maintain current Gross Profit levels.")
    else:
        st.info("Neutral position. No change in unit economics.")

    # 6. SENSITIVITY MATRIX
    st.subheader("📊 Price/Volume Sensitivity Matrix")
    st.write("Quantitative breakdown of the 'Breakeven Volume' for various price scenarios.")
    
    sensitivity_data = []
    for pct in [-20, -10, -5, 0, 5, 10, 15, 25, 40]:
        temp_price = current_price * (1 + pct/100)
        temp_cm = temp_price - current_vc
        if temp_cm > 0:
            vol_change = ((current_cm / temp_cm) - 1) * 100
            status = "Allowable Loss" if vol_change < 0 else "Needed Gain"
        else:
            vol_change = -100.0
            status = "Margin Collapse"
        
        sensitivity_data.append({
            "Price Change (%)": f"{pct:+d}%",
            "Target Price (€)": f"{temp_price:,.2f}",
            "Volume Offset (%)": f"{vol_change:+.1f}%",
            "Strategic Profile": status
        })
    
    st.table(pd.DataFrame(sensitivity_data))

    # Navigation (Ευθυγραμμισμένο με το νέο app.py)
    st.divider()
    if st.button("⬅️ Back to Control Tower", use_container_width=True):
        st.session_state.flow_step = "home"
        st.session_state.selected_tool = None
        st.rerun()
    
