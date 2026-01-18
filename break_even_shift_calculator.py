import streamlit as st
import matplotlib.pyplot as plt

# -------------------------------------------------
# Helper functions
# -------------------------------------------------

def parse_number_en(number_str):
    return float(number_str)

def format_number_en(number, decimals=2):
    return f"{number:,.{decimals}f}"

def format_percentage_en(number, decimals=1):
    return f"{number*100:.{decimals}f}%"


# -------------------------------------------------
# Core calculations (DO NOT CHANGE LOGIC)
# -------------------------------------------------

def calculate_break_even_shift(
    fixed_costs,
    new_investment,
    old_price,
    new_price,
    old_unit_cost,
    new_unit_cost,
    units_sold
):
    old_cm = old_price - old_unit_cost
    new_cm = new_price - new_unit_cost

    if old_cm <= 0 or new_cm <= 0:
        return None, None, None, None

    total_fixed_old = fixed_costs
    total_fixed_new = fixed_costs + new_investment

    old_break_even = total_fixed_old / old_cm
    new_break_even = total_fixed_new / new_cm

    percent_change = (new_break_even - old_break_even) / old_break_even
    units_change = new_break_even - old_break_even

    return old_break_even, new_break_even, percent_change, units_change


# -------------------------------------------------
# Plot
# -------------------------------------------------

def plot_break_even_shift(
    fixed_costs,
    new_investment,
    old_price,
    new_price,
    old_unit_cost,
    new_unit_cost,
    units_sold
):
    old_cm = old_price - old_unit_cost
    total_fixed_old = fixed_costs
    total_fixed_new = fixed_costs + new_investment

    x = list(range(0, int(units_sold * 2)))

    old_total_cost = [total_fixed_old + old_unit_cost * q for q in x]
    new_total_cost = [total_fixed_new + new_unit_cost * q for q in x]
    old_revenue = [old_price * q for q in x]
    new_revenue = [new_price * q for q in x]

    plt.figure(figsize=(8, 5))
    plt.plot(x, old_total_cost, 'r--', label="Old Total Cost")
    plt.plot(x, new_total_cost, 'r-', label="New Total Cost")
    plt.plot(x, old_revenue, 'g--', label="Old Revenue")
    plt.plot(x, new_revenue, 'g-', label="New Revenue")

    plt.xlabel("Units Sold")
    plt.ylabel("USD")
    plt.title("Break-Even Shift Analysis")
    plt.legend()
    plt.grid(True)

    st.pyplot(plt)


# -------------------------------------------------
# Streamlit UI
# -------------------------------------------------

def show_break_even_shift_calculator():
    st.header("🟠 Break-Even Decision Tool")
    st.markdown(
        "Answer client questions **immediately**, without spreadsheets. "
        "Leave any field as **0** if it does not apply."
    )

    with st.form("break_even_form"):
        fixed_costs_input = st.text_input(
            "Existing fixed costs per month (recurring expenses)",
            "10000.00"
        )
        new_investment_input = st.text_input(
            "Additional fixed investment (enter 0 if none)",
            "0.00"
        )
        old_price_input = st.text_input(
            "Current selling price per unit",
            "10.50"
        )
        new_price_input = st.text_input(
            "New selling price per unit",
            "11.00"
        )
        old_unit_cost_input = st.text_input(
            "Current variable cost per unit",
            "6.00"
        )
        new_unit_cost_input = st.text_input(
            "New variable cost per unit",
            "6.50"
        )
        units_sold_input = st.text_input(
            "Units sold last period",
            "500"
        )

        submitted = st.form_submit_button("Run decision check")

    if submitted:
        try:
            fixed_costs = parse_number_en(fixed_costs_input)
            new_investment = parse_number_en(new_investment_input)
            old_price = parse_number_en(old_price_input)
            new_price = parse_number_en(new_price_input)
            old_unit_cost = parse_number_en(old_unit_cost_input)
            new_unit_cost = parse_number_en(new_unit_cost_input)
            units_sold = parse_number_en(units_sold_input)

            old_bep, new_bep, percent_change, units_change = calculate_break_even_shift(
                fixed_costs,
                new_investment,
                old_price,
                new_price,
                old_unit_cost,
                new_unit_cost,
                units_sold
            )

            if percent_change is None:
                st.error(
                    "Contribution margin is zero or negative. "
                    "This decision destroys the business model."
                )
                return

            st.success(f"Old break-even: {format_number_en(old_bep, 0)} units")
            st.success(f"New break-even: {format_number_en(new_bep, 0)} units")

            st.markdown(f"- **Additional units required:** {format_number_en(units_change,0)}")
            st.markdown(f"- **Break-even change:** {format_percentage_en(percent_change)}")

            if percent_change < 0.10:
                st.success("🟢 Absorbed by current model")
            elif percent_change <= 0.30:
                st.warning("🟠 Looks small, but stresses sales capacity")
            else:
                st.error("🔴 High-risk decision — survival threshold jumps")

            plot_break_even_shift(
                fixed_costs,
                new_investment,
                old_price,
                new_price,
                old_unit_cost,
                new_unit_cost,
                units_sold
            )

        except Exception as e:
            st.error(f"Input error: {e}")
