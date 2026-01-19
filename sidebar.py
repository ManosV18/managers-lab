# sidebar.py
import streamlit as st

def scenario_selector():
    st.sidebar.header("🛠 What-If Scenario")

    return st.sidebar.radio(
        "Select intervention type",
        [
            "Price Change",
            "Discount with Complementary Products",
            "Product Substitution",
            "Break-Even Shift",
            "Customer Lifetime Value"
        ]
    )
