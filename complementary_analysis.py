import streamlit as st

# =========================
# Helper functions
# =========================

def parse_number(number_str):
    try:
        return float(number_str.replace(",", ""))
    except:
        return None


def format_number(number, decimals=2):
    return f"{number:,.{decimals}f}"


def format_percentage(number, decimals=2):
    return f"{number:.{decimals}f}%"


# =========================
# Core calculation (Excel-equivalent)
# =========================

def calculate_required_sales_increase(
    suit_price,
    price_decrease_pct,   # negative number e.g. -0.10
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
    Excel-equivalent formula:
    = -discount / ( (total_profit_per_suit / price) + discount )
    """

    expected_complement_profit = (
        percent_shirt * profit_shirt +
        percent_tie * profit_tie +
        percent_belt * profit_belt +
        percent_shoes * profit_shoes
    )

    total_profit_per_suit = profit_suit + expected_complement_profit

    try:
        required_increase = -price_decrease_pct / (
            (total_profit_per_suit / suit_price) + price_decrease_pct
        )
        return required_increase * 100
    except ZeroDivisionError:
        return None


# =========================
# Streamlit UI
# =========================

def show_complementary_analysis():

    st.header("🧥 Complementary Products Analysis")
    st.markdown("""
This tool estimates **how much suit sales must increase**
after a **price reduction**, considering that customers
also buy **complementary products**.

Typical use cases:
- Pricing decisions
- Promotion planning
- Profit protection analysis
""")

    with st.form("complementary_form"):
        st.subheader("🔢 Core Product (Suit)")

        col1, col2 = st.columns(2)

        with col1:
            suit_price_input = st.text_input(
                "Suit Price (€)",
                value=format_number(200)
            )
            profit_suit_input = st.text_input(
                "Profit per Suit (€)",
                value=format_number(60)
            )
            price_decrease_input = st.text_input(
                "Price Decrease (%)",
                value=format_number(10)
            )

        st.subheader("👔 Complementary Products – Profit per Unit")

        col3, col4 = st.columns(2)

        with col3:
            profit_shirt_input = st.text_input("Shirt (€)", value=format_number(13))
            profit_tie_input = st.text_input("Tie (€)", value=format_number(11))

        with col4:
            profit_belt_input = st.text_input("Belt (€)", value=format_number(11))
            profit_shoes_input = st.text_input("Shoes (€)", value=format_number(45))

        st.subheader("📊 Customer Purchasing Probabilities")

        percent_shirt = st.slider("Customers buying Shirt (%)", 0.0, 100.0, 90.0) / 100
        percent_tie = st.slider("Customers buying Tie (%)", 0.0, 100.0, 70.0) / 100
        percent_belt = st.slider("Customers buying Belt (%)", 0.0, 100.0, 10.0) / 100
        percent_shoes = st.slider("Customers buying Shoes (%)", 0.0, 100.0, 5.0) / 100

        submitted = st.form_submit_button("📈 Calculate")


    if submitted:
        suit_price = parse_number(suit_price_input)
        profit_suit = parse_number(profit_suit_input)
        price_decrease_pct = -abs(parse_number(price_decrease_input) / 100)

        profit_shirt = parse_number(profit_shirt_input)
        profit_tie = parse_number(profit_tie_input)
        profit_belt = parse_number(profit_belt_input)
        profit_shoes = parse_number(profit_shoes_input)

        if None in (
            suit_price, profit_suit, price_decrease_pct,
            profit_shirt, profit_tie, profit_belt, profit_shoes
        ):
            st.error("❌ Please check all numeric inputs.")
            return

        result = calculate_required_sales_increase(
            suit_price,
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
            st.error("❌ Calculation not possible with these inputs.")
        else:
            st.subheader("📉 Result")
            st.metric(
                "Required Suit Sales Increase",
                format_percentage(result)
            )

            st.markdown("""
### 📘 Interpretation

Each suit sale generates:
- Profit from the suit itself
- **Expected profit** from complementary products

A price reduction reduces **profit per suit**.
To maintain **total profit**, sales volume must increase.

This result shows the **minimum increase in suit sales**
required to offset the discount.
""")

            st.caption("Calculation follows marginal profit logic (Excel-equivalent).")
