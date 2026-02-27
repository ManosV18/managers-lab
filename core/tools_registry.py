import streamlit as st
import importlib
import os
import sys
import importlib.util
import plotly.graph_objects as go

# =========================================================
# 1. ΟΙ ΜΗΧΑΝΕΣ ΥΠΟΛΟΓΙΣΜΟΥ (ΜΗΝ ΤΙΣ ΑΛΛΑΞΕΙΣ)
# =========================================================

def pmt(rate, nper, pv, fv=0, when=0):
    if rate == 0: return -(pv + fv) / nper
    temp = (1 + rate) ** nper
    payment = (pv * temp * rate + fv * rate) / (temp - 1)
    if when == 1: payment /= (1 + rate)
    return payment

def format_eur(x):
    return f"€ {x:,.0f}".replace(",", ".")

def calculate_final_burden(loan_rate, wc_rate, years, prop_val, l_fin_pct, ls_fin_pct, e_loan, e_ls, resid, dep_y, tax, pay_when):
    months = 12
    n_months = years * months
    acq_loan = prop_val + e_loan
    acq_ls = prop_val + e_ls
    wc_loan_amt = prop_val - (prop_val * l_fin_pct) + e_loan 
    wc_ls_amt = prop_val - (prop_val * ls_fin_pct) + e_ls     
    m_loan = pmt(loan_rate / months, n_months, prop_val * l_fin_pct, 0, pay_when)
    m_ls = pmt(loan_rate / months, n_months, prop_val * ls_fin_pct, 0, pay_when)
    m_wc_loan = pmt(wc_rate / months, n_months, wc_loan_amt, 0, pay_when)
    m_wc_ls = pmt(wc_rate / months, n_months, wc_ls_amt, 0, pay_when)
    total_m_loan = m_loan + m_wc_loan 
    total_m_ls = m_ls + m_wc_ls       
    int_loan = (total_m_loan * n_months) - prop_val 
    int_ls = (total_m_ls * n_months) - prop_val     
    cost_loan = int_loan + prop_val
    cost_ls = int_ls + prop_val
    dep_loan = acq_loan / dep_y * years 
    dep_ls = acq_ls + resid 
    deduct_loan = int_loan + dep_loan 
    deduct_ls = (m_wc_ls * n_months - wc_ls_amt) + dep_ls 
    tax_b_loan = deduct_loan * tax 
    tax_b_ls = deduct_ls * tax     
    return {
        "final_loan": cost_loan - tax_b_loan, "final_ls": cost_ls - tax_b_ls,
        "int_l": int_loan, "int_ls": int_ls, "dep_l": dep_loan, "dep_ls": dep_ls,
        "tax_l": tax_b_loan, "tax_ls": tax_b_ls
    }

# =========================================================
# 2. ΤΟ ΕΡΓΑΛΕΙΟ ΠΟΥ ΒΛΕΠΕΙ Ο ΧΡΗΣΤΗΣ (UI)
# =========================================================

def loan_vs_leasing_ui():
    st.header("📊 Loan vs Leasing – Αναλυτική Σύγκριση")
    
    # Σύνδεση με Stage 0
    default_tax = float(st.session_state.get('tax_rate', 22.0))
    
    col1, col2 = st.columns(2)
    with col1:
        l_rate = st.number_input("Επιτόκιο Δανείου (%)", value=6.0) / 100
        wc_rate = st.number_input("Επιτόκιο Κεφαλαίου Κίνησης (%)", value=8.0) / 100
        years = st.number_input("Διάρκεια (Έτη)", value=15)
        tax = st.number_input("Φορολογικός Συντελεστής (%)", value=default_tax) / 100
        pay_when = 1 if st.radio("Πληρωμή", ["Αρχή μήνα", "Τέλος μήνα"]) == "Αρχή μήνα" else 0

    with col2:
        val = st.number_input("Αξία Ακινήτου (€)", value=250000.0)
        l_fin = st.number_input("Χρηματοδότηση Δανείου (%)", value=70.0) / 100
        ls_fin = st.number_input("Χρηματοδότηση Leasing (%)", value=100.0) / 100
        e_loan = st.number_input("Έξοδα Δανείου (€)", value=35000.0)
        e_ls = st.number_input("Έξοδα Leasing (€)", value=30000.0)
        resid = st.number_input("Υπολειμματική Αξία (€)", value=3530.0)
        dep_y = st.number_input("Έτη Απόσβεσης", value=30)

    res = calculate_final_burden(l_rate, wc_rate, years, val, l_fin, ls_fin, e_loan, e_ls, resid, dep_y, tax, pay_when)

    st.divider()
    st.subheader("📑 Βήμα-Βήμα η Λογική (Πώς βγαίνει το αποτέλεσμα)")
    
    t1, t2 = st.tabs(["🏦 Ανάλυση Δανείου", "🧾 Ανάλυση Leasing"])
    
    with t1:
        st.write(f"1. **Συνολικό Κόστος:** Τόκοι {format_eur(res['int_l'])} + Αρχική Αξία = {format_eur(res['int_l'] + val)}")
        st.write(f"2. **Εκπιπτόμενα Έξοδα:** Τόκοι + Αποσβέσεις ({format_eur(res['dep_l'])})")
        st.info(f"3. **Φορολογικό Όφελος:** Γλιτώνετε από το φόρο {format_eur(res['tax_l'])}")
        st.success(f"**ΤΕΛΙΚΗ ΠΡΑΓΜΑΤΙΚΗ ΕΠΙΒΑΡΥΝΣΗ:** {format_eur(res['final_loan'])}")

    with t2:
        st.write(f"1. **Συνολικό Κόστος:** Τόκοι {format_eur(res['int_ls'])} + Αρχική Αξία = {format_eur(res['int_ls'] + val)}")
        st.write(f"2. **Εκπιπτόμενα Έξοδα:** Ποσό που δηλώνεται στην εφορία: {format_eur(res['int_ls'] + res['dep_ls'])}")
        st.info(f"3. **Φορολογικό Όφελος:** Γλιτώνετε από το φόρο {format_eur(res['tax_ls'])}")
        st.success(f"**ΤΕΛΙΚΗ ΠΡΑΓΜΑΤΙΚΗ ΕΠΙΒΑΡΥΝΣΗ:** {format_eur(res['final_ls'])}")

    if st.button("⬅️ Επιστροφή στη Βιβλιοθήκη"):
        st.session_state.selected_tool = None
        st.rerun()

# =========================================================
# 3. ΤΟ ΚΕΝΤΡΙΚΟ ΜΕΝΟΥ ΤΗΣ ΒΙΒΛΙΟΘΗΚΗΣ
# =========================================================

def show_library():
    if st.sidebar.button("🏠 Exit Library"):
        st.session_state.flow_step = "home"
        st.session_state.selected_tool = None
        st.rerun()

    st.title("🏛️ Strategic Tool Library")

    if st.session_state.get('selected_tool') is None:
        t1, t2 = st.tabs(["💰 Finance", "🛡️ Risk"])
        with t1:
            if st.button("⚖️ Loan vs Leasing Analyzer", use_container_width=True):
                st.session_state.selected_tool = ("INTERNAL", "loan_vs_leasing_ui")
                st.rerun()
    else:
        mod_name, func_name = st.session_state.selected_tool
        if mod_name == "INTERNAL":
            # Αυτή η γραμμή εκτελεί τη συνάρτηση που είναι γραμμένη ΠΑΝΩ
            if func_name in globals():
                globals()[func_name]()
            else:
                st.error(f"Δεν βρέθηκε η συνάρτηση: {func_name}")
