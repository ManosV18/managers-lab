import streamlit as st
import pandas as pd

def show_deal_auditor():
    s = st.session_state
    st.header("🕵️ Individual Deal & Cash Gap Auditor")
    st.info("Μετατρέψτε τον χρόνο σε χρήμα. Υπολογίστε πόσο σας κοστίζει η 'πίστωση' και η 'αποθήκη' ανά πελάτη.")

    # --- 1. TIME METRICS (DAYS) ---
    st.subheader("⏳ Time Metrics (Days)")
    col1, col2, col3 = st.columns(3)
    with col1:
        days_inv = st.number_input("Days in Stock (Πόσο μένει στην αποθήκη)", value=int(s.get("inv_days", 45)))
    with col2:
        days_ar = st.number_input("Days to Collect (Πότε πληρώνει ο πελάτης)", value=int(s.get("ar_days", 90)))
    with col3:
        days_ap = st.number_input("Days to Pay (Πότε πληρώνετε τον προμηθευτή)", value=int(s.get("ap_days", 30)))

    # Υπολογισμός Cash Gap
    cash_gap = (days_inv + days_ar) - days_ap

    # --- 2. DEAL FINANCIALS ---
    st.subheader("💰 Deal Financials")
    c1, c2 = st.columns(2)
    with c1:
        cost_value = st.number_input("Cost of Goods / COGS ($)", value=70000.0, help="Το κεφάλαιο που βγήκε από το ταμείο για αυτό το deal.")
    with c2:
        revenue = st.number_input("Expected Revenue ($)", value=100000.0)

    # --- 3. CALCULATIONS ---
    # Παίρνουμε το WACC από τις μετρικές του engine
    wacc = s.metrics.get("wacc", 0.10)
    
    # Πραγματικό κόστος χρηματοδότησης της αναμονής
    cost_of_waiting = (cost_value * wacc * (cash_gap / 365))
    
    accounting_profit = revenue - cost_value
    real_profit = accounting_profit - cost_of_waiting
    real_margin = (real_profit / revenue) if revenue > 0 else 0

    # --- 4. RESULTS ---
    st.divider()
    res1, res2, res3 = st.columns(3)
    
    res1.metric("Cash Gap", f"{cash_gap} Days", delta=f"{cash_gap} Days Delay", delta_color="inverse")
    res2.metric("Accounting Profit", f"${accounting_profit:,.0f}")
    res3.metric("REAL Adjusted Profit", f"${real_profit:,.0f}", delta=f"-${cost_of_waiting:,.2f} Finance Cost", delta_color="inverse")

    # --- 5. VISUALIZATION ---
    st.subheader("📊 Profit Erosion Analysis")
    chart_data = pd.DataFrame({
        "Type": ["Accounting Profit", "Real Profit (Time Adjusted)"],
        "Value": [accounting_profit, real_profit]
    })
    st.bar_chart(data=chart_data, x="Type", y="Value")

    if cash_gap > 100:
        st.error(f"⚠️ ΠΡΟΣΟΧΗ: Αυτό το deal 'στραγγίζει' τη ρευστότητα. Χρηματοδοτείτε τον πελάτη για {cash_gap} ημέρες.")
    
    st.write(f"💡 **Analysis:** Το πραγματικό σας περιθώριο (Margin) έπεσε στο **{real_margin:.1%}** λόγω του κόστους κεφαλαίου.")
