import streamlit as st
import pandas as pd

def show_deal_auditor():
    s = st.session_state
    st.header("🕵️ Individual Deal & Cash Gap Auditor")
    st.info("Convert time into money. Calculate the real financing cost of inventory and credit terms for any specific deal.")

    # --- 1. TIME METRICS (DAYS) ---
    st.subheader("⏳ Time Metrics (Days)")
    col1, col2, col3 = st.columns(3)
    with col1:
        days_inv = st.number_input("Days in Stock (Inventory Duration)", value=int(s.get("inv_days", 45)))
    with col2:
        days_ar = st.number_input("Days to Collect (Receivables Terms)", value=int(s.get("ar_days", 90)))
    with col3:
        days_ap = st.number_input("Days to Pay (Supplier Terms)", value=int(s.get("ap_days", 30)))

    # Calculation: The Cash Conversion Gap for this specific deal
    cash_gap = (days_inv + days_ar) - days_ap

    # --- 2. DEAL FINANCIALS ---
    st.subheader("💰 Deal Financials")
    c1, c2 = st.columns(2)
    with c1:
        cost_value = st.number_input("Cost of Goods Sold (COGS Value)", value=70000.0, help="The actual capital tied up in this transaction.")
    with c2:
        revenue = st.number_input("Gross Deal Revenue", value=100000.0)

    # --- 3. THE "INVISIBLE" COST CALCULATIONS ---
    # Fetching WACC from the simulation engine
    wacc = s.metrics.get("wacc", 0.10)
    
    # Financial Carrying Cost (The interest cost for the days capital is stuck)
    # Based on your rule: Year = 365 days
    financing_cost = (cost_value * wacc * (cash_gap / 365))
    
    accounting_profit = revenue - cost_value
    real_profit = accounting_profit - financing_cost
    real_margin = (real_profit / revenue) if revenue > 0 else 0

    # --- 4. RESULTS DASHBOARD ---
    st.divider()
    res1, res2, res3 = st.columns(3)
    
    res1.metric("Cash Gap", f"{cash_gap} Days", delta=f"{cash_gap} Days Lag", delta_color="inverse")
    res2.metric("Accounting Profit", f"${accounting_profit:,.0f}")
    res3.metric("REAL Adjusted Profit", f"${real_profit:,.0f}", delta=f"-${financing_cost:,.2f} Carrying Cost", delta_color="inverse")

    # --- 5. VISUALIZATION: PROFIT EROSION ---
    st.subheader("📊 Profit Erosion Analysis")
    
    # Simple dataframe for the bar chart
    data = {
        "Profit Type": ["Accounting (Gross)", "Real (Time-Adjusted)"],
        "Value": [accounting_profit, real_profit]
    }
    df = pd.DataFrame(data)
    
    st.bar_chart(data=df, x="Profit Type", y="Value")
    
    

    # --- 6. CRITICAL ALERTS ---
    if cash_gap > 100:
        st.error(f"🚨 CRITICAL LIQUIDITY DRAIN: This deal traps capital for {cash_gap} days. You are essentially providing interest-free financing to your client.")
    
    st.warning(f"💡 **Strategic Insight:** Your margin dropped from **{(accounting_profit/revenue):.1%}** to **{real_margin:.1%}** due to the cost of capital. Time is eating your profit.")
