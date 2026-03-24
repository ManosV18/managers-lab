import streamlit as st

def show_deal_auditor():
    s = st.session_state
    st.header("🕵️ Deal & Cash Gap Auditor")
    st.caption("Υπολογισμός πραγματικού κόστους αναμονής και 'Financial Gap' ανά deal.")

    # 1. TIME METRICS
    st.subheader("⏳ Time Metrics (Days)")
    col1, col2, col3 = st.columns(3)
    with col1:
        days_inv = st.number_input("Days in Stock (Physical)", value=s.inv_days)
    with col2:
        days_ar = st.number_input("Days to Collect (Customer)", value=s.ar_days)
    with col3:
        days_ap = st.number_input("Days to Pay (Supplier)", value=s.ap_days)

    cash_gap = (days_inv + days_ar) - days_ap

    # 2. FINANCIALS
    st.subheader("💰 Deal Financials")
    c1, c2 = st.columns(2)
    with c1:
        cost_value = st.number_input("Cost of Goods (COGS Value)", value=70000.0)
    with c2:
        revenue = st.number_input("Expected Revenue", value=100000.0)

    # 3. CALCULATIONS
    wacc = s.metrics.get("wacc", 0.10)
    cost_of_waiting = (cost_value * wacc * (cash_gap / 365))
    
    accounting_profit = revenue - cost_value
    real_profit = accounting_profit - cost_of_waiting
    real_margin = (real_profit / revenue) if revenue > 0 else 0

    # 4. RESULTS DISPLAY
    st.divider()
    res1, res2, res3 = st.columns(3)
    res1.metric("Cash Gap", f"{cash_gap} Days", delta=f"{cash_gap} Days Delay", delta_color="inverse")
    res2.metric("Accounting Profit", f"€{accounting_profit:,.0f}")
    res3.metric("REAL Profit", f"€{real_profit:,.0f}", delta=f"-€{cost_of_waiting:,.2f} Cost", delta_color="inverse")

    if cash_gap > 100:
        st.error(f"🚨 SOS: Το κεφάλαιο εγκλωβίζεται για {cash_gap} μέρες. Αυτό το deal 'τρώει' τη ρευστότητα της εταιρείας.")
