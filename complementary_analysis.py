import streamlit as st

# --- Helper functions ---
def parse_number(number_str):
    """Convert string with English decimal separator to float."""
    try:
        return float(number_str.replace(',', ''))
    except:
        return None

def format_number(number, decimals=2):
    return f"{number:,.{decimals}f}"

def format_percentage(number, decimals=1):
    return f"{number:.{decimals}f}%"

# --- Calculation ---
def calculate_required_sales_increase(
    old_price,
    price_decrease_pct,
    profit_suit,
    profit_shirt,
    profit_tie,
    profit_belt,
    profit_shoes,
    percent_shirt,
    percent_tie,
    percent_belt,
    percent_shoes
):
    """
    Calculates minimum % increase in Suit sales to maintain total profit
    after a price decrease, considering complementary products.
    """
    combined_profit = (
        profit_suit +
        percent_shirt * profit_shirt +
        percent_tie * profit_tie +
        percent_belt * profit_belt +
        percent_shoes * profit_shoes
    )

    new_price = old_price * (1 - price_decrease_pct)
    loss_per_unit = old_price - new_price
    new_total_profit = combined_profit - loss_per_unit

    try:
        required_increase = loss_per_unit / new_total_profit
        return required_increase * 100
    except ZeroDivisionError:
        return None

# --- Streamlit UI ---
def show_complementary_analysis():
    st.header("🧥 Complementary Product Analysis Tool")
    st.markdown("""
Estimate the **required sales increase of Suits** after a discount,  
considering the effect of complementary product purchases (Shirts, Ties, Belts, Shoes).

Use this tool to check **how much you need to sell to maintain total profit**.
""")

    with st.form("discount_impact_form"):
        st.subheader("Suit Pricing & Profit Data")

        old_price_input = st.text_input("Suit Price (€)", value=format_number(200))
        st.caption("The current selling price per Suit before discount.")

        price_decrease_input = st.text_input("Planned Price Decrease (%)", value=format_number(10.0))
        st.caption("Percentage reduction you plan to apply to the Suit price.")

        profit_suit_input = st.text_input("Profit per Suit (€)", value=format_number(60))
        st.caption("Net profit expected from selling one Suit.")

        st.subheader("Complementary Products Profit")

        profit_shirt_input = st.text_input("Profit per Shirt (€)", value=format_number(13))
        st.caption("Net profit from selling one Shirt, often purchased with a Suit.")

        profit_tie_input = st.text_input("Profit per Tie (€)", value=format_number(11))
        st.caption("Net profit from selling one Tie, often purchased with a Suit.")

        profit_belt_input = st.text_input("Profit per Belt (€)", value=format_number(11))
        st.caption("Net profit from selling one Belt, often purchased with a Suit.")

        profit_shoes_input = st.text_input("Profit per Shoes (€)", value=format_number(45))
        st.caption("Net profit from selling one pair of Shoes, often purchased with a Suit.")

        st.subheader("Complementary Product Purchase Rates")

        percent_shirt = st.slider("Percentage of customers buying Shirt", 0.0, 100.0, 90.0)
        st.caption("Estimated fraction of Suit buyers who also purchase a Shirt.")

        percent_tie = st.slider("Percentage of customers buying Tie", 0.0, 100.0, 70.0)
        st.caption("Estimated fraction of Suit buyers who also purchase a Tie.")

        percent_belt = st.slider("Percentage of customers buying Belt", 0.0, 100.0, 10.0)
        st.caption("Estimated fraction of Suit buyers who also purchase a Belt.")

        percent_shoes = st.slider("Percentage of customers buying Shoes", 0.0, 100.0, 5.0)
        st.caption("Estimated fraction of Suit buyers who also purchase Shoes.")

        submitted = st.form_submit_button("Calculate")

    if submitted:
        old_price = parse_number(old_price_input)
        price_decrease_pct = parse_number(price_decrease_input) / 100

        profit_suit = parse_number(profit_suit_input)
        profit_shirt = parse_number(profit_shirt_input)
        profit_tie = parse_number(profit_tie_input)
        profit_belt = parse_number(profit_belt_input)
        profit_shoes = parse_number(profit_shoes_input)

        if None in (old_price, price_decrease_pct, profit_suit,
                    profit_shirt, profit_tie, profit_belt, profit_shoes):
            st.error("❌ Please check that all numeric fields are correctly filled.")
            return

        result = calculate_required_sales_increase(
            old_price,
            price_decrease_pct,
            profit_suit,
            profit_shirt,
            profit_tie,
            profit_belt,
            profit_shoes,
            percent_shirt / 100,
            percent_tie / 100,
            percent_belt / 100,
            percent_shoes / 100
        )

        if result is None:
            st.error("❌ Cannot calculate. Try different values.")
        else:
            st.success(f"✅ Required suit sales increase: {format_percentage(result)}")
            st.markdown("""
ℹ️ **What this means**

This is the **minimum sales growth required** to fully offset the discount,  
taking into account the **additional profit generated by complementary products**
(Shirts, Ties, Belts, Shoes).
""")

            # Traffic-light interpretation
            if result < 10:
                st.success("🟢 **Low risk** — Required increase is small and usually achievable.")
            elif result <= 30:
                st.warning("🟠 **Moderate risk** — Sales must grow significantly to justify the discount.")
            else:
                st.error("🔴 **High risk** — The discount requires aggressive sales growth to avoid profit loss.")

