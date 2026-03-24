import streamlit as st

def run_deal_auditor(s):
    st.header("🕵️ Individual Deal & Cash Gap Auditor")
    st.info("Μετατρέψτε τον χρόνο σε χρήμα: Πόσο σας κοστίζει η αναμονή για ένα deal;")

    # --- 1. Εισαγωγή Χρονικών Δεδομένων (Days) ---
    st.subheader("⏳ Time Metrics (Days)")
    col_d1, col_d2, col_d3 = st.columns(3)
    with col_d1:
        days_inv = st.number_input("Days in Stock (Physical)", value=45, help="Πόσες μέρες μένει το προϊόν στην αποθήκη.")
    with col_d2:
        days_ar = st.number_input("Days to Collect (Customer)", value=90, help="Πότε θα σας πληρώσει ο πελάτης.")
    with col_d3:
        days_ap = st.number_input("Days to Pay (Supplier)", value=30, help="Πότε πρέπει να πληρώσετε εσείς.")

    # Υπολογισμός Cash Gap (Τρύπα Ρευστότητας)
    cash_gap = (days_inv + days_ar) - days_ap

    # --- 2. Οικονομικά Στοιχεία (Money) ---
    st.subheader("💰 Deal Financials")
    col_v1, col_v2 = st.columns(2)
    with col_v1:
        cost_value = st.number_input("Cost of Goods Sold (COGS)", value=70000, help="Το κεφάλαιο που βγαίνει από το ταμείο σας.")
    with col_v2:
        revenue = st.number_input("Total Deal Revenue", value=100000)

    # --- 3. Κόστος Κεφαλαίου (WACC) ---
    # Το παίρνουμε από το session state (s) που ήδη έχεις
    wacc = s.get("metrics", {}).get("wacc", 0.10)
    
    # Το Πραγματικό Κόστος της Αναμονής (Financial Carrying Cost)
    cost_of_waiting = (cost_value * wacc * (cash_gap / 365))
    
    # --- 4. Αποτελέσματα & Visuals ---
    st.divider()
    
    accounting_profit = revenue - cost_value
    real_profit = accounting_profit - cost_of_waiting
    real_margin = (real_profit / revenue) * 100 if revenue > 0 else 0

    c1, c2, c3 = st.columns(3)
    c1.metric("Cash Gap", f"{cash_gap} Days", delta=f"{cash_gap} Days Delay", delta_color="inverse")
    c2.metric("Accounting Profit", f"${accounting_profit:,.0f}")
    c3.metric("REAL Profit (Adjusted)", f"${real_profit:,.0f}", delta=f"-${cost_of_waiting:,.2f} Interest", delta_color="inverse")

    if cash_gap > 120:
        st.error(f"🚨 ΠΡΟΣΟΧΗ: Αυτό το deal χρηματοδοτεί τον πελάτη για {cash_gap} ημέρες με δικά σας έξοδα!")
    
    st.progress(min(max(cash_gap / 365, 0.0), 1.0))
    st.caption("Οπτικοποίηση του ετήσιου κύκλου εγκλωβισμού κεφαλαίου.")
