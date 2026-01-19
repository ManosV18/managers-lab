# state.py
import streamlit as st

def current_state():
    st.header("📍 Current Business State")
    st.caption("Baseline reference for all scenarios")

    return {
        "price": st.number_input("Current Price (€)", 200.0),
        "profit": st.number_input("Profit per Unit (€)", 60.0),
        "sales": st.number_input("Current Sales Volume", 100.0)
    }
