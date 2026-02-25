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
        # Parsing data
        c_old = parse_gr_number(comp_old_in)
        c_new = parse_gr_number(comp_new_in)
        o_price = parse_gr_number(our_price_in)
        u_cost = parse_gr_number(unit_cost_in)

        if None in (c_old, c_new, o_price, u_cost):
            st.error("⚠️ Please ensure all inputs are valid numbers.")
            return

        # 1. Πίνακας Δεδομένων (Mirroring Excel Format)
        st.subheader("📊 Scenario Overview")
        data = {
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
        }
        df = pd.DataFrame(data)
        st.table(df.set_index("Description"))

        # 2. Υπολογισμός Αποτελέσματος
        result = calculate_sales_loss_threshold(c_old, c_new, o_price, u_cost)

        st.divider()
        if result is not None:
            if result <= 0:
                st.warning("❗ No threshold available. Your current price/cost structure provides no buffer.")
            else:
                # Εμφάνιση με μεγάλη έμφαση στο κάτω μέρος όπως το Excel
                st.markdown(f"""
                <div style="background-color:#f0f2f6; padding:20px; border-radius:10px; border-left: 5px solid #ff4b4b;">
                    <h3 style="margin:0;">Maximum Sales Volume Loss Threshold</h3>
                    <p style="font-size:30px; font-weight:bold; color:#ff4b4b; margin:0;">{result:.2f}%</p>
                    <p style="font-size:14px; color:#555;">You can lose up to this percentage of sales volume and still be more profitable than if you matched the competitor's price cut.</p>
                </div>
                """, unsafe_allow_html=True)

                # Πρόσθετο Insight
                price_cut_
