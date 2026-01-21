import streamlit as st
import pandas as pd


# -------------------------------
# HELPERS
# -------------------------------

def normalize_weights(weights):
    total = sum(weights)
    if total == 0:
        return weights
    return [w / total for w in weights]

# -------------------------------
# UI
# -------------------------------

def show_qspm_tool():

    st.title("🧭 QSPM – Quantitative Strategic Planning Matrix")
    st.subheader("Compare **two strategies** based on your own judgment")

    st.markdown("""
    ⚠️ **Important clarification**

    - This tool **does NOT predict the market**
    - It **does NOT estimate probabilities**
    - All inputs reflect **your managerial judgment**

    👉 The QSPM simply **organizes your thinking** and
    shows which strategy is **more consistent with your assumptions**.
    """)

    st.divider()

    # -------------------------------
    # STRATEGY NAMES
    # -------------------------------

    col1, col2 = st.columns(2)
    with col1:
        strategy_A = st.text_input("Strategy A name", value="Strategy A")
    with col2:
        strategy_B = st.text_input("Strategy B name", value="Strategy B")

    st.divider()

    # -------------------------------
    # CRITERIA SETUP
    # -------------------------------

    st.subheader("1️⃣ Strategic Criteria")

    st.markdown("""
    Define the criteria **you consider important** for this decision.
    These typically come from previous analyses (pricing, substitution,
