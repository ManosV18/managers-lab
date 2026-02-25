import streamlit as st
from core.sync import sync_global_state

def run_stage2():
    st.title("💳 Stage 2: Capital Structure & WACC")
    
    # 1. FETCH DATA
    m = sync_global_state()
    s = st.session_state

    st.markdown("""
    Ανάλυση του κόστους κεφαλαίου και της εξυπηρέτησης του χρέους. 
    Εδώ εξετάζουμε αν η απόδοση της επιχείρησης καλύπτει τις απαιτήσεις των επενδυτών και των τραπεζών.
    """)

    # 2. FINANCIAL METRICS
    c1, c2, c3 = st.columns(3)
    
    wacc = s.get('wacc', 0.15)
    annual_debt = s.get('annual_loan_payment', 0.0)
    ebit = m.get('ebit', 0.0)
    
    c1.metric("WACC (Cost of Capital)", f"{wacc:.1%}")
    c2.metric("Annual Debt Service", f"{annual_debt:,.0f} €")
    
    # Debt Service Coverage Ratio (DSCR)
    dscr = (ebit / annual_debt) if annual_debt > 0 else 5.0 # default high if no debt
    c3.metric("Debt Coverage (DSCR)", f"{dscr:.2f}x", 
              delta="Safe" if dscr > 1.2 else "Critical",
              delta_color="normal" if dscr > 1.2 else "inverse")

    # 3. ANALYTICAL INSIGHT
    st.divider()
    st.subheader("Capital Leverage Insights")
    
    if dscr < 1:
        st.error(f"🚨 **CASH FLOW ALERT:** Το EBIT ({ebit:,.0f}€) δεν καλύπτει τις δόσεις των δανείων ({annual_debt:,.0f}€). Η επιχείρηση 'καίει' μετρητά για να εξυπηρετήσει το χρέος.")
    elif dscr < 1.2:
        st.warning("⚠️ **FRAGILE LIQUIDITY:** Η κάλυψη χρέους είναι οριακή. Οποιαδήποτε πτώση πωλήσεων θα προκαλέσει αδυναμία πληρωμής.")
    else:
        st.success("✅ **DEBT SUSTAINABILITY:** Η επιχείρηση παράγει επαρκή κέρδη για την εξυπηρέτηση των δανειακών της υποχρεώσεων.")

    # 4. NAVIGATION (Διασφάλιση ροής προς Stage 3)
    st.divider()
    col_prev, col_next = st.columns(2)
    with col_prev:
        if st.button("⬅️ Back to Stage 1"):
            st.session_state.flow_step = "stage1"
            st.rerun()
    with col_next:
        if st.button("Proceed to Stage 3 ➡️"):
            st.session_state.flow_step = "stage3"
            st.rerun()
