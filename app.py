import streamlit as st

from state import current_state
from sidebar import scenario_selector
from engine import run_engine


st.set_page_config(page_title="What-If Engine", layout="centered")

st.title("🧠 Business What-If Engine")
st.caption("Decision support — not calculators")

# 1️⃣ Current business state
state = current_state()

st.markdown("---")

# 2️⃣ Scenario selection
scenario = scenario_selector()

st.markdown("---")

# 3️⃣ Run decision engine
run_engine(scenario, state)
