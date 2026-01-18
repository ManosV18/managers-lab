import streamlit as st

# --- Helper functions ---
def parse_number(number_str):
    try:
        return float(number_str.replace(',', ''))
    except:
        return None

def format_number(number, decimals=2):
    return f"{number:,.{decimals}f}"

def format_percentage(number, decimals=1):
    return f"{number:.{decimals}f}%"

# --- Calculation (DO NOT CHANGE) ---
def calculate_sales_loss_threshold(
    competitor_old_price,
    competitor_new_price,
    our_price,
    unit_cost
):
    try:
        top = (competitor_new_price - competitor_old_price) / competitor_old_price
        bottom = (unit_cost - our_price) / our_price
        if bottom == 0:
            return None
        return (top / bottom) * 100
    except ZeroDivisionError:
        return None

# --- Streamlit UI ---
def show_loss_threshold_before_price_cut():

    st.header("📉 Sales Loss Threshold Before Price Cut")

    st.markdown(
        "Competitors lowered their prices. **Should you react or hold your price?**\n\n"
        "This tool shows **how much sales volume you can afford to lose (%)** "
        "before cutting your price becomes unavoidable."
    )

    with st.form("loss_threshold_form"):

        competitor_old_price_input = st.text_input(
            "Competitor price BEFORE the cut",
            value=format_number(8.0)
        )
        st.caption(
            "The price at which your competitor was selling before the price reduction."
        )

        competitor_new_price_input = st.text_input(
            "Competitor price AFTER the cut",
            value=format_number(7.2)
        )
        st.caption(
            "The new lower price your competitor is offering after the discount."
        )

        our_price_input = st.text_input(
            "Your current selling price",
            value=format_number(8.0)
        )
        st.caption(
            "The price at which you currently sell your product or service."
        )

        unit_cost_input = st.text_input(
            "Your variable cost per unit",
            value=format_number(4.5)
        )
        st.caption(
            "Your direct cost per unit sold (materials, production, delivery, commissions). "
            "This is the minimum level that limits how much you can cut prices."
        )

        submitted = st.form_submit_button("Calculate loss threshold")

    if submitted:
        competitor_old_price = parse_number(competitor_old_price_input)
        competitor_new_price = parse_number(competitor_new_price_input)
        our_price = parse_number(our_price_input)
        unit_cost = parse_number(unit_cost_input)

        if None in (competitor_old_price, competitor_new_price, our_price, unit_cost):
            st.error("⚠️ Please check that all numeric fields are filled correctly.")
            return

        result = calculate_sales_loss_threshold(
            competitor_old_price,
            competitor_new_price,
            our_price,
            unit_cost
        )

        if result is None:
            st.error("⚠️ Cannot calculate. Check the input values.")
        elif result <= 0:
            st.warning(
                "❗ You have no sales loss margin.\n\n"
                "Your current price leaves no room to absorb competitive pressure."
            )
        else:
            st.success(
                f"✅ You can afford to lose up to **{format_percentage(result)}** of sales "
                "before a price cut becomes necessary."
            )

    st.markdown("---")
