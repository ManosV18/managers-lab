import streamlit as st
from utils import format_number_gr, parse_gr_number, format_percentage_gr

def calculate_sales_loss_threshold(
    competitor_old_price,
    competitor_new_price,
    our_price,
    unit_cost
):
    try:
        # Numerator: Percentage change in competitor's price
        top = (competitor_new_price - competitor_old_price) / competitor_old_price
        # Denominator: (Unit Cost - Our Price) / Our Price -> Negative CM ratio
        bottom = (unit_cost - our_price) / our_price
        
        if bottom == 0:
            return None
            
        # Result as a percentage
        result = top / bottom
        return result * 100 
    except ZeroDivisionError:
        return None

def show_loss_threshold_before_price_cut():
    st.header("📉 Sales Loss Threshold Analysis")
    st.write("Determine the maximum volume loss sustainable before matching a competitor's price cut.")

    st.markdown("""
    ### 🧠 Strategic Context
    When a competitor lowers their price, matching them immediately might destroy your margin. 
    This tool calculates the **indifference point**: the exact percentage of sales volume you can afford to lose 
    while maintaining the same total contribution profit as you would if you had matched their price.
    """)

    with st.form("loss_threshold_form"):
        col1, col2 = st.columns(2)

        with col1:
            st.subheader("🏁 Competitor Status")
            competitor_old_price_input = st.text_input("Competitor Initial Price (€)", value="8,00")
            competitor_new_price_input = st.text_input("Competitor New Price (€)", value="7,20")

        with col2:
            st.subheader("🏢 Our Economics")
            our_price_input = st.text_input("Our Current Selling Price (€)", value="8,00")
            unit_cost_input = st.text_input("Our Unit Cost (COGS) (€)", value="4,50")

        submitted = st.form_submit_button("Calculate Threshold", use_container_width=True)

    if submitted:
        # Parsing using your existing GR format utils
        comp_old = parse_gr_number(competitor_old_price_input)
        comp_new = parse_gr_number(competitor_new_price_input)
        our_p = parse_gr_number(our_price_input)
        u_cost = parse_gr_number(unit_cost_input)

        if None in (comp_old, comp_new, our_p, u_cost):
            st.error("⚠️ Validation Error: Please ensure all fields are numeric.")
            return

        # Core Calculation
        result = calculate_sales_loss_threshold(comp_old, comp_new, our_p, u_cost)

        st.divider()
        
        if result is None:
            st.error("⚠️ Calculation Error: Check your input values (Price must be higher than Unit Cost).")
        elif result <= 0:
            st.warning("❗ No Margin for Loss: Your price/cost structure is already at parity or below the competitor's move.")
        else:
            # Executive Result Display
            st.subheader("Analytical Verdict")
            st.success(f"### Maximum Allowable Volume Loss: {result:.2f}%")
            
            st.info(f"""
            **Insight:** You can lose up to **{result:.2f}%** of your customers to the competitor 
            and still be more profitable than you would be if you lowered your price to **€{comp_new:.2f}**.
            """)
            
            # Comparative Metrics
            m1, m2 = st.columns(2)
            current_cm = our_p - u_cost
            m1.metric("Current Unit Margin", f"€{current_cm:.2f}")
            m2.metric("Competitor Price Cut", f"{((comp_new-comp_old)/comp_old)*100:.1f}%")

    st.divider()
    if st.button("Back to Library Hub", use_container_width=True):
        st.session_state.selected_tool = None
        st.rerun()
