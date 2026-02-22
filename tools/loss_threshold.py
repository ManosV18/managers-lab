import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from core.engine import compute_core_metrics

def show_loss_threshold_before_price_cut():
    st.header("📉 Loss Threshold Analysis")
    st.caption("Strategic Filter: Calculate the required volume surge to offset price reductions.")

    # 1. FETCH GLOBAL BASELINE
    metrics = compute_core_metrics()
    current_p = st.session_state.price
    current_vc = st.session_state.variable_cost
    current_m = metrics['unit_contribution'] # Original Margin (P - VC)

    if current_m <= 0:
        st.error("❌ Current unit margin is zero or negative. Analysis cannot proceed.")
        return

    # 2. SIMULATION INPUT
    st.subheader("Price Reduction Scenario")
    discount_pct = st.slider("Proposed Price Discount (%)", 1, 50, 10)
    
    new_p = current_p * (1 - discount_pct/100)
    new_m = new_p - current_vc

    # 3. ANALYTICAL CALCULATIONS
    if new_m <= 0:
        st.error(f"🚨 **Critical Failure:** A {discount_pct}% discount obliterates the unit margin. You will lose money on every unit sold, regardless of volume.")
    else:
        # Formula for required Volume Increase: (M_old / M_new) - 1
        req_vol_increase_pct = (current_m / new_m) - 1
        new_required_volume = st.session_state.volume * (1 + req_vol_increase_pct)

        # 4. RESULTS DISPLAY
        st.divider()
        c1, c2, c3 = st.columns(3)
        
        c1.metric("New Unit Margin", f"{new_m:,.2f} €", delta=f"-{discount_pct}%")
        c2.metric("Req. Volume Increase", f"+{req_vol_increase_pct*100:.1f}%")
        c3.metric("New Sales Target (Units)", f"{new_required_volume:,.0f}")

        # 5. VISUALIZATION: The "Danger Zone" Chart
        
        
        discounts = [5, 10, 15, 20, 25, 30, 35, 40]
        required_vol = []
        for d in discounts:
            m_sim = (current_p * (1 - d/100)) - current_vc
            v_inc = (current_m / m_sim - 1) * 100 if m_sim > 0 else None
            required_vol.append(v_inc)

        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=discounts, 
            y=required_vol, 
            mode='lines+markers', 
            line=dict(color='#EF553B', width=3), 
            name="Required Volume Jump"
        ))
        
        fig.update_layout(
            title="Price Discount vs. Required Volume Surge",
            xaxis_title="Price Discount (%)",
            yaxis_title="Required Volume Increase (%)",
            template="plotly_dark",
            hovermode="x unified"
        )
        st.plotly_chart(fig, use_container_width=True)

        # 6. ANALYTICAL VERDICT
        st.info(
            f"**Analytical Verdict:** To maintain current profit levels after the discount, "
            f"for every 100 units currently sold, you must sell **{100*(1+req_vol_increase_pct):,.0f}** units tomorrow."
        )

        if req_vol_increase_pct > 0.5:
            st.warning(
                "⚠️ **High Structural Risk:** The required volume surge exceeds 50%. It is mathematically improbable "
                "that demand elasticity will offset this margin compression in most market conditions."
            )
