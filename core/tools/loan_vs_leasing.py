import streamlit as st

def format_eur(amount):
    return f"€{amount:,.0f}"

def calculate_final_burden(l_rate, wc_rate, years, val, l_fin, ls_fin, e_loan, e_ls, resid, dep_y, tax, pay_when):
    # Loan Logic
    loan_amount = val * l_fin
    pmt_l = (loan_amount * l_rate) / (1 - (1 + l_rate)**-years)
    total_int_l = (pmt_l * years) - loan_amount
    total_dep_l = (val / dep_y) * years
    tax_shield_l = (total_int_l + total_dep_l + e_loan) * tax
    final_loan = (val + e_loan + total_int_l) - tax_shield_l
    
    # Leasing Logic
    ls_amount = val * ls_fin
    pmt_ls = (ls_amount * l_rate) / (1 - (1 + l_rate)**-years)
    total_int_ls = (pmt_ls * years) - ls_amount
    # Στο leasing συνήθως εκπίπτει όλο το μίσθωμα ή μεγάλο μέρος του
    tax_shield_ls = (total_int_ls + (val - resid) + e_ls) * tax
    final_ls = (val + e_ls + total_int_ls + resid) - tax_shield_ls

    return {
        'int_l': total_int_l,
        'dep_l': total_dep_l,
        'tax_l': tax_shield_l,
        'final_loan': final_loan,
        'int_ls': total_int_ls,
        'dep_ls': (val - resid),
        'tax_ls': tax_shield_ls,
        'final_ls': final_ls
    }

def loan_vs_leasing_ui():
    st.header("📊 Loan vs Leasing – Analytical Tool")
    
    # Σύνδεση με το Stage 0 - tax_rate (Default 35% αν δεν βρει τίποτα)
    default_tax = float(st.session_state.get('tax_rate', 35.0))
    
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("📌 Όροι Χρηματοδότησης")
        l_rate = st.number_input("Loan Interest Rate (%)", value=6.0, key="lvl_loan_rate_in") / 100
        wc_rate = st.number_input("WC Interest Rate (%)", value=8.0, key="lvl_wc_rate_in") / 100
        years = st.number_input("Duration (Years)", value=15, key="lvl_years_in")
        tax = st.number_input("Tax Rate (%)", value=default_tax, key="lvl_tax_in") / 100
        pay_when = 1 if st.radio("Payment Timing", ["Beginning", "End"], key="lvl_timing_in") == "Beginning" else 0

    with col2:
        st.subheader("🏗️ Στοιχεία Επένδυσης")
        val = st.number_input("Property Value (€)", value=250000.0, key="lvl_val_in")
        l_fin = st.number_input("Loan Financing (%)", value=70.0, key="lvl_lfin_in") / 100
        ls_fin = st.number_input("Leasing Financing (%)", value=100.0, key="lvl_lsfin_in") / 100
        e_loan = st.number_input("Loan Expenses (€)", value=35000.0, key="lvl_eloan_in")
        e_ls = st.number_input("Leasing Expenses (€)", value=30000.0, key="lvl_els_in")
        resid = st.number_input("Residual Value (€)", value=3530.0, key="lvl_resid_in")
        dep_y = st.number_input("Depreciation Period (Years)", value=30, key="lvl_depy_in")

    # Υπολογισμοί
    res = calculate_final_burden(l_rate, wc_rate, years, val, l_fin, ls_fin, e_loan, e_ls, resid, dep_y, tax, pay_when)

    st.divider()

    # --- ΑΝΑΛΥΣΗ ---
    st.subheader("📑 Πώς προκύπτουν τα νούμερα (Ανάλυση)")
    
    t_l, t_ls = st.tabs(["🏦 Ανάλυση Δανείου", "🧾 Ανάλυση Leasing"])
    
    with t_l:
        st.write("### Βήμα-Βήμα Υπολογισμός Δανείου")
        st.write(f"1️⃣ **Κόστος Αγοράς:** {format_eur(val)} (Ακίνητο) + {format_eur(e_loan)} (Έξοδα) = **{format_eur(val + e_loan)}**")
        st.write(f"2️⃣ **Συνολικοί Τόκοι:** Πληρώνεις συνολικά τόκους ύψους **{format_eur(res['int_l'])}** στη διάρκεια των {years} ετών.")
        st.write(f"3️⃣ **Αποσβέσεις:** Δικαιούσαι να αφαιρέσεις από τα έσοδα **{format_eur(res['dep_l'])}** λόγω παλαιότητας.")
        st.info(f"💡 **Φορολογική Ασπίδα:** (Τόκοι + Αποσβέσεις) * {tax*100}% = **{format_eur(res['tax_l'])}** (Αυτό το ποσό γλιτώνεις από την εφορία)")
        st.success(f"🎯 **ΤΕΛΙΚΟ ΠΡΑΓΜΑΤΙΚΟ ΚΟΣΤΟΣ:** {format_eur(res['final_loan'])}")

    with t_ls:
        st.write("### Βήμα-Βήμα Υπολογισμός Leasing")
        st.write(f"1️⃣ **Κόστος Αγοράς:** {format_eur(val)} + {format_eur(e_ls)} = **{format_eur(val + e_ls)}**")
        st.write(f"2️⃣ **Κόστος Χρήματος:** Οι τόκοι του leasing ανέρχονται σε **{format_eur(res['int_ls'])}**.")
        st.write(f"3️⃣ **Εκπιπτόμενα Έξοδα:** Συνολικά έξοδα που δηλώνεις = **{format_eur(res['int_ls'] + res['dep_ls'])}**")
        st.info(f"💡 **Φορολογική Ασπίδα:** Εκπιπτόμενα * {tax*100}% = **{format_eur(res['tax_ls'])}** (Το κέρδος σου από το φόρο)")
        st.success(f"🎯 **ΤΕΛΙΚΟ ΠΡΑΓΜΑΤΙΚΟ ΚΟΣΤΟΣ:** {format_eur(res['final_ls'])}")

    st.divider()
    
    # Τελικά Metrics
    c1, c2 = st.columns(2)
    c1.metric("🏦 ΤΕΛΙΚΟ ΒΑΡΟΣ ΔΑΝΕΙΟΥ", format_eur(res['final_loan']))
    c2.metric("🧾 ΤΕΛΙΚΟ ΒΑΡΟΣ LEASING", format_eur(res['final_ls']))

    if st.button("⬅️ Back to Library Hub", key="lvl_back"):
        st.session_state.selected_tool = None
        st.rerun()
