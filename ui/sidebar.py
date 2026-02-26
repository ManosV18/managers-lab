import streamlit as st
from core.sync import lock_baseline


def show_sidebar():

    st.sidebar.title("Baseline Inputs")

    st.sidebar.number_input("Price", key="price", value=10.0)
    st.sidebar.number_input("Volume", key="volume", value=1000.0)
    st.sidebar.number_input("Variable Cost", key="variable_cost", value=5.0)
    st.sidebar.number_input("Fixed Cost", key="fixed_cost", value=2000.0)
    st.sidebar.number_input("WACC", key="wacc", value=0.1)
    st.sidebar.number_input("Tax Rate", key="tax_rate", value=0.22)
    st.sidebar.number_input("AR Days", key="ar_days", value=30.0)
    st.sidebar.number_input("Inventory Days", key="inventory_days", value=30.0)
    st.sidebar.number_input("AP Days", key="ap_days", value=30.0)
    st.sidebar.number_input("Annual Debt Service", key="annual_debt_service", value=0.0)
    st.sidebar.number_input("Opening Cash", key="opening_cash", value=0.0)

    if st.sidebar.button("🔒 Lock Baseline"):
        lock_baseline()
