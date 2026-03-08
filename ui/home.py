import streamlit as st

st.title("Business Decision Toolkit")

st.write("""
Understand your business and make better decisions.
Simple tools to evaluate cash, pricing, costs, and growth.
""")

# -----------------------------
# CASH & LIQUIDITY
# -----------------------------

st.header("💰 Cash & Liquidity")

col1, col2 = st.columns(2)

with col1:
    if st.button("How long could my business survive without new revenue?"):
        st.switch_page("tools/cash_fragility_index.py")

    st.caption("Estimate how many days your business can continue operating if no new money comes in.")

with col2:
    if st.button("How quickly do my sales turn into cash?"):
        st.switch_page("tools/cash_cycle.py")

    st.caption("Measure how long it takes to collect cash after making a sale.")


col3, col4 = st.columns(2)

with col3:
    if st.button("Am I collecting money from customers efficiently?"):
        st.switch_page("tools/receivables_analyzer.py")

    st.caption("Analyze delayed payments and understand how customers affect your cash flow.")

with col4:
    if st.button("How should I schedule supplier payments to protect cash?"):
        st.switch_page("tools/payables_manager.py")

    st.caption("Plan supplier payments in a way that protects liquidity.")


# -----------------------------
# PRICING & PROFIT
# -----------------------------

st.header("💵 Pricing & Profit")

col1, col2 = st.columns(2)

with col1:
    if st.button("How many sales do I need to cover my costs?"):
        st.switch_page("tools/break_even_shift_calculator.py")

    st.caption("Calculate the sales level required for your business to break even.")

with col2:
    if st.button("How much can I reduce my price before the business becomes risky?"):
        st.switch_page("tools/loss_threshold.py")

    st.caption("Find the maximum price reduction your business can tolerate.")

col3, col4 = st.columns(2)

with col3:
    if st.button("Which pricing strategy produces the most profit?"):
        st.switch_page("tools/pricing_strategy.py")

    st.caption("Compare different pricing strategies and their impact on profit.")

with col4:
    if st.button("How do price changes affect my competitiveness and sales?"):
        st.switch_page("tools/pricing_radar.py")

    st.caption("Understand how pricing affects market position and demand.")


# -----------------------------
# COSTS & OPERATIONS
# -----------------------------

st.header("📦 Costs & Operations")

col1, col2 = st.columns(2)

with col1:
    if st.button("What does it actually cost me to produce one unit?"):
        st.switch_page("tools/unit_cost_analyzer.py")

    st.caption("Calculate the real cost behind each unit you produce.")

with col2:
    if st.button("How much inventory should I keep to meet demand?"):
        st.switch_page("tools/inventory_manager.py")

    st.caption("Avoid shortages or excess stock by optimizing inventory levels.")


# -----------------------------
# GROWTH & INVESTMENT
# -----------------------------

st.header("📈 Growth & Investment")

col1, col2 = st.columns(2)

with col1:
    if st.button("How much funding do I need to support growth?"):
        st.switch_page("tools/growth_funding.py")

    st.caption("Estimate the capital required to expand your business.")

with col2:
    if st.button("Loan or leasing: which is better for my equipment?"):
        st.switch_page("tools/loan_vs_leasing.py")

    st.caption("Compare financing options for equipment purchases.")

col3, col4 = st.columns(2)

with col3:
    if st.button("What is the best cost of capital for my investments?"):
        st.switch_page("tools/wacc_optimizer.py")

    st.caption("Evaluate the optimal mix of financing sources.")


# -----------------------------
# STRATEGY & RISK
# -----------------------------

st.header("🧠 Strategy & Risk")

col1, col2 = st.columns(2)

with col1:
    if st.button("Which strategy is the best choice for my business?"):
        st.switch_page("tools/qspm_analyzer.py")

    st.caption("Compare strategic alternatives using weighted decision factors.")

with col2:
    if st.button("How would my business perform under economic stress?"):
        st.switch_page("tools/stress_test_simulator.py")

    st.caption("Simulate scenarios like revenue drops or cost increases.")

col3, col4 = st.columns(2)

with col3:
    if st.button("How resilient is my business to unexpected pressures?"):
        st.switch_page("tools/financial_resilience_app.py")

    st.caption("Evaluate overall financial strength and resilience.")

with col4:
    if st.button("See all key financial indicators in one place"):
        st.switch_page("tools/executive_dashboard.py")

    st.caption("A dashboard with the most important financial indicators.")
