import streamlit as st

def turnover_quantity_based(avg_qty, sold_qty):
    """
    Calculate inventory turnover in days based on quantity.
    """
    if sold_qty == 0:
        return 0
    return round((avg_qty * 365) / sold_qty, 2)

def turnover_value_based(avg_value, cost_of_goods_sold):
    """
    Calculate inventory turnover in days based on value.
    """
    if cost_of_goods_sold == 0:
        return 0
    return round((avg_value * 365) / cost_of_goods_sold, 2)


def show_inventory_turnover_calculator():
    st.title("📦 Inventory Turnover Calculator")
    st.caption(
        "Estimate the **average time inventory is held** before being sold, "
        "either by quantity or by value. Useful for inventory management and cash flow planning."
    )

    st.header("🔢 Calculation Method")
    method = st.radio(
        "Choose a calculation method",
        ["📊 Quantity-Based", "💶 Value-Based"]
    )
    st.caption(
        "📊 Quantity-Based: calculates turnover in days based on units.\n"
        "💶 Value-Based: calculates turnover in days based on inventory value and COGS."
    )

    num_items = st.number_input(
        "Number of Products",
        min_value=1,
        max_value=10,
        value=4
    )

    product_names = []
    quantity_inputs = []
    value_inputs = []

    st.markdown("### 📝 Input Data")
    for i in range(num_items):
        st.markdown(f"#### Product {i+1}")
        name = st.text_input(f"Product Name {i+1}", key=f"name_{i}")

        if method == "📊 Quantity-Based":
            avg_inventory = st.number_input(
                "Average Inventory (units)",
                min_value=0.0,
                key=f"inv_qty_{i}"
            )
            sold_quantity = st.number_input(
                "Units Sold",
                min_value=0.0,
                key=f"sold_qty_{i}"
            )
            st.caption(
                "Enter the **average inventory in units** and the **number of units sold** "
                "during the period. These values are used to calculate turnover in days."
            )
            quantity_inputs.append((avg_inventory, sold_quantity))

        else:
            avg_inventory_value = st.number_input(
                "Average Inventory Value (€)",
                min_value=0.0,
                key=f"inv_val_{i}"
            )
            cogs = st.number_input(
                "Cost of Goods Sold (€)",
                min_value=0.0,
                key=f"cogs_{i}"
            )
            st.caption(
                "Enter the **average inventory value** and the **cost of goods sold** during the period. "
                "These values are used to calculate turnover in days based on monetary value."
            )
            value_inputs.append((avg_inventory_value, cogs))

        product_names.append(name)

    if st.button("📈 Calculate"):
        st.markdown("---")
        st.subheader("📊 Results")
        for i, name in enumerate(product_names):
            if method == "📊 Quantity-Based":
                avg_inv, sold = quantity_inputs[i]
                result = turnover_quantity_based(avg_inv, sold)
                st.metric(
                    f"🛒 {name} (Quantity-Based)",
                    f"{result} days"
                )
            else:
                avg_val, cogs = value_inputs[i]
                result = turnover_value_based(avg_val, cogs)
                st.metric(
                    f"💰 {name} (Value-Based)",
                    f"{result} days"
                )

        st.caption(
            "The results represent the **average number of days inventory is held**. "
            "Lower days indicate faster turnover, which improves cash flow and reduces storage costs."
        )
