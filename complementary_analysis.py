import streamlit as st

# --- Helper functions for English number formatting ---
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
    price_decrease_pct,  # decimal, e.g., 0.10 for 10%
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
    st.write("Complementary Product Analysis")
    st.header("🧥 Estimate Suit Sales Increase after Discount")
    st.title("What happens if customers buy accessories too? 👔👞")
    st.markdown("""
The manager is considering a price reduction on suits. However, customers also purchase
other products (e.g., shirts, ties, belts, shoes).

👉 How much must suit sales increase to maintain total profit?
""")

    with st.form("discount_impact_form"):
        col1, col2 = st.columns(2)

        with col1:
            old_price_input = st.text_input("Suit Price (€)", value=format_number(200))
            profit_suit_input = st.text_input("Profit per Suit (€)", value=format_number(60))
            price_decrease_input = st.text_input("Price Decrease (%)", value=format_number(10.0))

            shirt_profit_input = st.text_input("Profit per Shirt (€)", value=format_number(13))
            tie_profit_input = st.text_input("Profit per Tie (€)", value=format_number(11))

        with col2:
            belt_profit_input = st.text_input("Profit per Belt (€)", value=format_number(11))
            shoes_profit_input = st.text_input("Profit per Shoes (€)", value=format_number(45))

            percent_shirt = st.slider("Percentage of customers buying Shirt", 0.0, 100.0, 90.0) / 100
            percent_tie = st.slider("Percentage of customers buying Tie", 0.0, 100.0, 70.0) / 100
            percent_belt = st.slider("Percentage of customers buying Belt", 0.0, 100.0, 10.0) / 100
            percent_shoes = st.slider("Percentage of customers buying Shoes", 0.0, 100.0, 5.0) / 100

        submitted = st.form_submit_button("Calculate")

    if submitted:
        old_price = parse_number(old_price_input)
        profit_suit = parse_number(profit_suit_input)
        price_decrease_pct = parse_number(price_decrease_input) / 100  # from % to decimal

        profit_shirt = parse_number(shirt_profit_input)
        profit_tie = parse_number(tie_profit_input)
        profit_belt = parse_number(belt_profit_input)
        profit_shoes = parse_number(shoes_profit_input)

        if None in (
            old_price, profit_suit, price_decrease_pct,
            profit_shirt, profit_tie, profit_belt, profit_shoes
        ):
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
            percent_shirt,
            percent_tie,
            percent_belt,
            percent_shoes
        )

        if result is None:
            st.error("❌ Cannot calculate. Try different values.")
        else:
            st.success(f"✅ Required suit sales increase: {format_percentage(result)}")

