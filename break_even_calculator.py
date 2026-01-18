import streamlit as st
import matplotlib.pyplot as plt

# ---------- Helpers ----------
def parse_number_en(x):
    return float(x)

def format_number_en(x, d=2):
    return f"{x:,.{d}f}"

def format_percentage_en(x, d=1):
    return f"{x*100:.{d}f}%"

# ---------- Core calculation ----------
def calculate_break_even_engine(
    old_price, new_price,
    old_cost, new_cost,
    investment_cost,
    units_sold
):
    old_cm = old_price - old_cost
    new_cm = new_price - new_cost

    if old_cm <= 0 or new_cm <= 0:
        return None

    fixed_costs_old = old_cm * units_sold
    fixed_costs_new = fixed_costs_old + investment_cost

    old_bep = fixed_costs_old / old_cm
    new_bep = fixed_costs_new / new_cm

    percent_change = (new_bep - old_bep) / old_bep
    units_change = new_bep - old_bep

    return old_bep, new_bep, percent_change, units_change

# ---------- Plot ----------
def plot_break_even(old_price, new_price, old_cost, new_cost, investment_cost, units_sold):
    old_cm = old_price - old_cost
    fixed_old = old_cm * units_sold
    fixed_new = fixed_old + investment_cost

    max_q = int(max(units_sold, fixed_new / max(new_price - new_cost, 0.01)) * 1.6)
    x = list(range(0, max_q))

    old_cost_line = [fixed_old + old_cost * q for q in x]
    new_cost_line = [fixed_new + new_cost * q for q in x]
    old_rev = [old_price * q for q in x]
    new_rev = [new_price * q for q in x]

    plt.figure(figsize=(8, 5))
    plt.plot(x, old_cost_line, "r--", label="Current cost structure")
    plt.plot(x, new_cost_line, "r-", label="After decision")
    plt.plot(x, old_rev, "g--", label="Current price")
    plt.plot(x, new_rev, "g-", label="After decision")

    plt.xlabel("Units sold")
    plt.ylabel("$")
    plt.title("Break-Even Impact of Your Decision")
    plt.legend()
    plt.grid(True)
    st.pyplot(plt)

# ---------- UI ----------
def show_break_even():

    st.header("🟢 Can you afford this decision?")
    st.markdown(
        "Answer pricing, cost or investment questions instantly — **without spreadsheets**.\n\n"
        "If something does not apply, simply enter **0**."
    )

    with st.form("break_even_engine"):
        st.subheader("Current situation")

        old_price = st.text_input("Current selling price per unit ($)", "50")
        old_cost = st.text_input("Current direct cost per unit ($)", "30")
        units_sold = st.text_input("Units sold in a normal period", "1000")

        st.subheader("Proposed decision")

        new_price = st.text_input("New selling price ($)", "50")
        new_cost = st.text_input("New direct cost per unit ($)", "30")
        investment_cost = st.text_input("One-off investment required ($)", "0")

        submitted = st.form_submit_button("Test the decision")

    if submitted:
        try:
            result = calculate_break_even_engine(
                parse_number_en(old_price),
                parse_number_en(new_price),
                parse_number_en(old_cost),
                parse_number_en(new_cost),
                parse_number_en(investment_cost),
                parse_number_en(units_sold),
            )

            if result is None:
                st.error("Contribution margin must be positive.")
                return

            old_bep, new_bep, pct, delta_units = result

            st.success(f"Current break-even: {format_number_en(old_bep,0)} units")
            st.success(f"New break-even: {format_number_en(new_bep,0)} units")

            st.markdown(f"- Extra units required: **{format_number_en(delta_units,0)}**")
            st.markdown(f"- Break-even change: **{format_percentage_en(pct)}**")

            if pct < 0.10:
                st.success("🟢 Decision absorbed by the existing business model.")
            elif pct <= 0.30:
                st.warning("🟠 Decision looks small, but requires a risky sales increase.")
            else:
                st.error("🔴 Decision materially raises the survival threshold.")

            plot_break_even(
                parse_number_en(old_price),
                parse_number_en(new_price),
                parse_number_en(old_cost),
                parse_number_en(new_cost),
                parse_number_en(investment_cost),
                parse_number_en(units_sold),
            )

        except Exception as e:
            st.error(f"Input error: {e}")
