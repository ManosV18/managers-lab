import streamlit as st

# --- Import your modules ---
from state import current_state
from sidebar import scenario_selector
from engine import run_engine

# --- Page configuration ---
st.set_page_config(page_title="Managers’ Lab What-If Engine", page_icon="🧪", layout="centered")

st.title("🧪 Managers’ Lab - What-If Engine")
st.markdown("""
Welcome! This dashboard lets you test **different business scenarios** and see the impact on your key metrics.  
Adjust inputs in the **Current State** section and select a scenario from the sidebar.
""")

# --- 1️⃣ Current Business State ---
st.sidebar.header("📍 Current State Inputs")
state = current_state()  # returns dict with price, profit, sales

# --- 2️⃣ Scenario selection ---
scenario = scenario_selector()  # radio in sidebar

# --- 3️⃣ Run selected scenario ---
run_engine(scenario, state)
