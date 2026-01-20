import streamlit as st
import matplotlib.pyplot as plt
import numpy as np

# -------------------------------
# LOGIC
# -------------------------------

def required_sales_increase(price_reduction_pct, contribution_margin, substitution_factor):
    """
    Calculate required sales increase (%) to compensate for price reduction,
    adjusted for substitution effects.
    """
    if contribution_margin <= 0 or contribution_margin >= 1:
        return 0
    base_increase = price_reduction_pct / contribution_margin * 100
    adjusted_increase = base_increase * substitution_factor
    return round(adjusted_increase, 2)


def feasible_sales_increase(required_increase, max_market_capacity_pct):
    """
    Adjust required sales increase for finite market capacity.
    """
    return min(required_increase, max_market_capacity_pct)


def plot_substitutes_sensitivity(base_value, scenarios):
    """
    Tornado sensitivity chart for substitutes.
    """
    labels = []
    impacts = []

    for name, factor in scenarios.items():
        adjusted = base_value * factor
        impact = adjusted - base_value
        labels.append(name)
        impacts.append(impact)

    impacts = np.array(impacts)

    fig, ax = plt.subplots()
    ax.barh(labels, impacts, color='skyblue')
    ax.axvline(0, color='black', linewidth=0.8)
    ax.set_xlabel("Impact on Required Sales Increase (%)")
    ax.set_title("Sensitivity Analysis – Substitutes")
    plt.tight_layout()
    return fig

# -------------------------------
# UI
# -------------------------------

def show_substitutes_sensitivity_tool():
    st.title("🔁 Substitutes – Sales Sensitivity Analysis Tool")

    st.markdown("""
This tool estimates how **substitute products affect the required sales increase**  
after a **price reduction** for your main product.

It also accounts for **finite market size**, showing what is **actually feasible**.
""")

    st.subheader("📥 Base Scenario")
    col1, col2 = st.columns(2)

    with col1:
        price_reduction = st.number_input(
            "Price Reduction (%)",
            min_value=0.0,
            value=5.0,
            step=0.5
        ) / 100

        contribution_margin = st.number_input(
            "Contribution Margin (%)",
            min_value=1.0,
            max_value=99.0,
            value=40.0,
            step=1.0
        ) / 100

    with col2:
        max_market_capacity = st.number_input(
            "Max Market Capacity (%)",
            min_value=0.0,
            max_value=500.0,
            value=150.0,
            step=5.0
        )

    base_required = required_sales_increase(price_reduction, contribution_margin, substitution_factor=1.0)
    feasible_increase = feasible_sales_increase(base_required, max_market_capacity)

    st.info(f"📌 **Base Required Sales Increase:** {base_required}%")
    st.success(f"📌 **Feasible Sales Increase (considering market limit):** {feasible_increase}%")

    st.divider()
    st.subheader("🔁 Substitution Scenarios")
    st.markdown("Define how aggressively substitute products impact sales:")

    low = st.slider("Low substitution", 0.5, 1.0, 0.8, 0.05)
    base = st.slider("Base case", 0.8, 1.2, 1.0, 0.05)
    high = st.slider("High substitution", 1.0, 1.5, 1.25, 0.05)
    aggressive = st.slider("Very aggressive substitute", 1.2, 2.0, 1.5, 0.05)

    scenarios = {
        "Low substitution": low,
        "Base case": base,
        "High substitution": high,
        "Very aggressive substitute": aggressive
    }

    st.divider()

    if st.button("📊 Run Sensitivity Analysis"):
        st.subheader("📈 Scenario Results")
        for name, factor in scenarios.items():
            adjusted = required_sales_increase(price_reduction, contribution_margin, factor)
            feasible = feasible_sales_increase(adjusted, max_market_capacity)
            st.write(f"**{name}** → Required: {adjusted}%, Feasible: {feasible}%")

        st.subheader("📊 Sensitivity Diagram")
        fig = plot_substitutes_sensitivity(base_required, scenarios)
        st.pyplot(fig)

        st.divider()

        st.markdown("""
### 🧠 How to read this chart
- ➖ Left: low substitute effect  
- ➕ Right: high substitute effect  
- Bars show how substitution changes the **required sales increase**  
- Feasible sales may be **lower** than required if the market is limited  

✔ If the worst-case scenario exceeds market capacity → price reduction may **not be feasible**
""")
