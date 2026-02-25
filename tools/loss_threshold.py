import streamlit as st
import pandas as pd
from utils import parse_gr_number

def calculate_sales_loss_threshold(comp_old, comp_new, our_p, u_cost):
    try:
        # Numerator: % change in competitor price
        top = (comp_new - comp_old) / comp_old
        # Denominator: (Unit Cost - Our Price) / Our Price
        bottom = (u_cost - our_p) / our_p
        if bottom == 0: return None
        return (top / bottom) * 100
    except ZeroDivisionError:
        return None

def show_loss_threshold_before_price_cut():
    st.header("📉 Sales Loss Threshold Analysis")
    st.write("Evaluate how much volume you can afford to lose before reacting to a competitor's price cut.")

    # --- INPUT FORM ---
    with st.form("loss_threshold_form"):
        col1, col2 = st.columns(2)
        with col1:
            comp_old_in = st.text_input("Competitor Original Price (€)", value="8,00")
            our_price_in = st.text_input("Our Selling Price (€)", value="8,00")
        with col2:
            comp_new_in = st.text_input("Competitor New Price (€)", value="7,20")
            unit_cost_in = st.text_input("Our Unit Cost (COGS) (€)", value="4,50")
        
        submitted = st.form_submit_button("Run Analysis", use_container_width=True)

    if submitted:
        c_old = parse_gr_number(comp_old_in)
        c_new = parse_gr_number(comp_new_in)
        o_price = parse_gr_number(our_price_in)
        u_cost = parse_gr_number(unit_cost_in)

        if None in (c_old, c_new, o_price, u_cost):
            st.error("⚠️ Please ensure all inputs are valid numbers.")
            return

        # 1. Scenario Table (Mirroring Excel)
        st.subheader("📊 Scenario Overview")
        summary_df = pd.DataFrame({
            "Description": [
                "Competitor Original Price",
                "Competitor New Price",
                "Our Selling Price",
                "Our Unit Cost (COGS)"
            ],
            "Value": [
                f"€ {c_old:,.2f}",
                f"€ {c_new:,.2f}",
                f"€ {o_price:,.2f}",
                f"€ {u_cost:,.2f}"
            ]
        })
        st.table(summary_df.set_index("Description"))

        # 2. Calculation
        result = calculate_sales_loss_threshold(c_old, c_new, o_price, u_cost)

        st.divider()
        if result is not None:
            if result <= 0:
                st.warning("❗ No threshold available. Your price/cost structure provides no buffer.")
            else:
                # Executive Result Display
                st.markdown(f"""
                <div style="background-color:#f8f9fb; padding:25px; border-radius:10px; border: 1px solid #dee2e6; border-left: 8px solid #ff4b4b;">
                    <h4 style="margin:0; color:#31333F;">Maximum Sales Volume Loss Threshold</h4>
                    <p style="font-size:36px; font-weight:bold; color:#ff4b4b; margin:10px 0;">{result:.2f}%</p>
                    <p style="font-size:14px; color:#555; line-height:1.4;">
                        This is the "Indifference Point". If you expect to lose <b>less</b> than {result:.2f}% of your volume, 
                        holding your price is more profitable than matching the competitor.
                    </p>
                </div>
                """, unsafe_allow_html=True)

                # Fixed Variable Name: price_cut_pct
                price_cut_pct = ((c_new - c_old) / c_old) * 100
                st.info(f"**Competitive Context:** The competitor has implemented a **{abs(price_cut_pct):.1f}%** price reduction.")

    st.divider()
    if st.button("Back to Library Hub", use_container_width=True):
        st.session_state.selected_tool = None
        st.rerun()
