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

    # Υπολογισμοί (Η "Μηχανή" σου)
    res = calculate_final_burden(l_rate, wc_rate, years, val, l_fin, ls_fin, e_loan, e_ls, resid, dep_y, tax, pay_when)

    st.divider()

    # --- ΑΝΑΛΥΤΙΚΗ ΠΑΡΟΥΣΙΑΣΗ (Excel Logic) ---
    st.subheader("📑 Αναλυτική Επεξήγηση Πράξεων")
    
    tab_l, tab_ls = st.tabs(["🏦 Ανάλυση Δανείου (Step-by-Step)", "🧾 Ανάλυση Leasing (Step-by-Step)"])
    
    with tab_l:
        st.write(f"**1. Κόστος Απόκτησης:** {format_eur(val)} + Έξοδα {format_eur(e_loan)} = **{format_eur(val + e_loan)}**")
        st.write(f"**2. Τόκοι Περιόδου:** Συνολικές δόσεις - Αρχικό Κεφάλαιο = **{format_eur(res['int_l'])}**")
        st.write(f"**3. Αποσβέσεις:** ({format_eur(val + e_loan)} / {dep_y} έτη) * {years} έτη = **{format_eur(res['dep_l'])}**")
        st.info(f"**4. Φορολογικό Όφελος:** (Τόκοι + Αποσβέσεις) * {tax*100}% = **{format_eur(res['tax_l'])}**")
        st.success(f"**ΤΕΛΙΚΗ ΕΠΙΒΑΡΥΝΣΗ ΔΑΝΕΙΟΥ:** Συνολικό Κόστος - Φορ. Όφελος = **{format_eur(res['final_loan'])}**")

    with tab_ls:
        st.write(f"**1. Κόστος Απόκτησης:** {format_eur(val)} + Έξοδα {format_eur(e_ls)} = **{format_eur(val + e_ls)}**")
        st.write(f"**2. Τόκοι Leasing:** {format_eur(res['int_ls'])}")
        st.write(f"**3. Εκπιπτόμενα Έξοδα:** Τόκοι + Αποσβέσεις/Μισθώματα = **{format_eur(res['int_ls'] + res['dep_ls'])}**")
        st.info(f"**4. Φορολογικό Όφελος:** Εκπιπτόμενα * {tax*100}% = **{format_eur(res['tax_ls'])}**")
        st.success(f"**ΤΕΛΙΚΗ ΕΠΙΒΑΡΥΝΣΗ LEASING:** Συνολικό Κόστος - Φορ. Όφελος = **{format_eur(res['final_ls'])}**")

    st.divider()
    
    # Metrics για γρήγορη ματιά
    c_l, c_ls = st.columns(2)
    c_l.metric("🏦 ΔΑΝΕΙΟ (Τελικό)", format_eur(res['final_loan']))
    c_ls.metric("🧾 LEASING (Τελικό)", format_eur(res['final_ls']))

    # Sensitivity Chart
    st.subheader("📈 Ευαισθησία Επιτοκίου (Πώς επηρεάζεται το Leasing)")
    test_rates = [l_rate + (i/1000) for i in range(-50, 55, 5)]
    ls_vals = [calculate_final_burden(r, wc_rate, years, val, l_fin, ls_fin, e_loan, e_ls, resid, dep_y, tax, pay_when)['final_ls'] for r in test_rates]
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=[r*100 for r in test_rates], y=ls_vals, name="Κόστος Leasing"))
    fig.add_hline(y=res['final_loan'], line_dash="dash", line_color="red", annotation_text="Σταθερό Κόστος Δανείου")
    fig.update_layout(template="plotly_dark", xaxis_title="Επιτόκιο (%)", yaxis_title="Τελική Επιβάρυνση (€)")
    st.plotly_chart(fig, use_container_width=True)

    if st.button("⬅️ Επιστροφή στη Βιβλιοθήκη", key="lvl_back_btn"):
        st.session_state.selected_tool = None
        st.rerun()
