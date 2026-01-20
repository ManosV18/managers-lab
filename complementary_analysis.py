import streamlit as st

# ---------- Helpers ----------
def parse_number(x):
    try:
        return float(x.replace(",", ""))
    except:
        return None

def format_percentage(x, decimals=2):
    return f"{x:.{decimals}f}%"

# ---------- Core calculation ----------
def calculate_max_product_A_sales_drop(
    old_price,
    price_increase_pct,
    profit_A,
    profit_B,
    profit_C,
    profit_D,
    percent_B,
    percent_C,
    percent_D
):
    weighted_substitute_profit = (
        percent_B * profit_B +
        percent_C * profit_C +
        percent_D * profit_D
    )

    numerator = -price_increase_pct
    denominator = ((profit_A - weighted_substitute_profit) / old_price) + price_increase_pct

    if denominator == 0:
        return None

    return (numerator / denominator) * 100

# ---------- UI ----------
def show_complementary_analysis():
    st.header("🔁 Substitution Analysis – Product A Price Increase")

    st.markdown("""
**Goal:**  
Estimate the **maximum acceptable sales drop of Product A**  
after a price increase, **without reducing total department profit**.

⚠️ Customers who do not switch to another product are assumed to **leave without buying anything**.
""")

    with st.form("substitution_form"):
        st.subheader("Product A (Price Increase)")
        old_price = parse_number(st.text_input("Current price of Product A (€)", "1.50"))
        price_increase_pct = parse_number(st.text_input("Price increase (%)", "10")) / 100
        profit_A = parse_number(st.text_input("Profit per unit – Product A (€)", "0.30"))

        st.subheader("Substitute Products – Profit per Unit (€)")
        profit_B = parse_number(st.text_input("Product B", "0.20"))
        profit_C = parse_number(st.text_input("Product C", "0.20"))
        profit_D = parse_number(st.text_input("Product D", "0.05"))

        st.subheader("Customer Switching (%)")
        percent_B = st.slider("Switch to Product B", 0.0, 100.0, 45.0) / 100
        percent_C = st.slider("Switch to Product C", 0.0, 100.0, 20.0) / 100
        percent_D = st.slider("Switch to Product D", 0.0, 100.0, 5.0) / 100

        submitted = st.form_submit_button("📊 Calculate")

    if submitted:
        total_switch = percent_B + percent_C + percent_D
        if total_switch > 1:
            st.error("Total switching percentage cannot exceed 100%.")
            return

        no_purchase = 1 - total_switch

        result = calculate_max_product_A_sales_drop(
            old_price,
            price_increase_pct,
            profit_A,
            profit_B,
            profit_C,
            profit_D,
            percent_B,
            percent_C,
            percent_D
        )

        st.markdown("---")
        st.subheader("📈 Results")

        st.metric(
            "Maximum acceptable sales drop of Product A",
            format_percentage(result)
        )

        st.caption(
            f"Customers not purchasing anything after the price increase: "
            f"{format_percentage(no_purchase * 100)}"
        )

