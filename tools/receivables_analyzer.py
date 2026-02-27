def show_receivables_analyzer_ui():
    # 1. FETCH & SYNC DATA
    metrics = sync_global_state()
    s = st.session_state
    
    # Baseline Values (Immutable in this context)
    sys_revenue = float(metrics.get('revenue', 0.0))
    sys_cogs = float(s.get('volume', 0)) * float(s.get('variable_cost', 0.0))
    sys_wacc = float(s.get('wacc', 0.15))
    sys_ar_days = float(s.get('ar_days', 45))
    sys_ap_days = float(s.get('ap_days', 30))

    st.title("📊 Strategic Receivables Analyzer (NPV Mode)")
    st.warning("🔒 Baseline Constants (Sales, COGS, Suppliers, WACC) are locked to ensure data integrity.")

    with st.form("npv_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### 📋 Market Assumptions")
            # ΚΛΕΙΔΩΜΕΝΟ
            c_sales = st.number_input("Current Sales (€)", value=sys_revenue, disabled=True)
            # ΑΝΟΙΧΤΟ: Η υπόθεση για την ανάπτυξη
            e_sales = st.number_input("Extra Sales Expected (€)", value=sys_revenue * 0.10, help="Πόσες νέες πωλήσεις θα φέρει η χαλάρωση της πίστωσης;")
            # ΑΝΟΙΧΤΟ: Η νέα πολιτική έκπτωσης
            d_trial = st.number_input("Proposed Discount %", value=2.0, step=0.1) / 100
            p_take = st.number_input("% Clients who will take the Discount", value=40.0, step=1.0) / 100
            
        with col2:
            st.markdown("### ⏱️ Timeline & Logic")
            # ΑΝΟΙΧΤΟ: Οι ημέρες της νέας πολιτικής
            d_new = st.number_input("New Payment Target (Days)", value=10, step=1)
            # ΚΛΕΙΔΩΜΕΝΟ: COGS, WACC & Suppliers
            cogs_val = st.number_input("Cost of Goods Sold (COGS €)", value=sys_cogs, disabled=True)
            wacc_val = st.number_input("WACC % (Cost of Capital)", value=sys_wacc * 100, disabled=True) / 100
            d_supps = st.number_input("Supplier Payment Days (DPO)", value=int(sys_ap_days), disabled=True)
            
            # Δευτερεύουσες παραμέτροι συγχρονισμένες
            d_take = st.number_input("Days (Current - Take group)", value=int(sys_ar_days), help="Οι ημέρες που πληρώνουν τώρα αυτοί που θα πάρουν την έκπτωση")
            d_no_take = st.number_input("Days (Current - No-Take group)", value=int(sys_ar_days * 2), help="Οι ημέρες που πληρώνουν τώρα αυτοί που ΘΑ ΑΡΝΗΘΟΥΝ την έκπτωση")

        submitted = st.form_submit_button("Execute NPV Strategy Simulation", use_container_width=True)

    if submitted:
        # Εκτέλεση του αλγορίθμου NPV (Decimal Precision)
        r = calculate_discount_npv(c_sales, e_sales, d_trial, p_take, d_take, d_no_take, d_new, cogs_val, wacc_val, d_supps)
        
        st.divider()
        # Κύρια Αποτελέσματα
        c1, c2, c3 = st.columns(3)
        c1.metric("Strategy NPV", f"€{r['npv']:,.2f}", delta="Profitable" if r['npv'] > 0 else "Loss-making", delta_color="normal" if r['npv'] > 0 else "inverse")
        c2.metric("Breakeven Discount", f"{r['max_discount']:.2f}%", help="Η μέγιστη έκπτωση που μπορείς να δώσεις χωρίς να χάσεις λεφτά.")
        c3.metric("Optimum Discount", f"{r['optimum_discount']:.2f}%")

        

        # Δυναμικό κουμπί ενημέρωσης κεντρικού συστήματος
        if r['npv'] > 0:
            st.success("🎯 Η προσομοίωση δείχνει θετικό NPV. Μπορείτε να εφαρμόσετε αυτή την πολιτική στο Baseline.")
            if st.button("🚀 Apply & Sync with War Room", type="primary", use_container_width=True):
                # Συγχρονισμός Ημερών Είσπραξης
                st.session_state.ar_days = d_new
                # Συγχρονισμός Νέου Όγκου (Volume Expansion)
                growth_factor = 1 + (e_sales / c_sales) if c_sales > 0 else 1
                st.session_state.volume = float(s.get('volume', 0)) * float(growth_factor)
                
                st.info("Baseline updated. All subsequent stages will reflect the new Volume and AR Days.")
                st.rerun()
        else:
            st.error("⚠️ Η συγκεκριμένη πολιτική καταστρέφει αξία (Αρνητικό NPV). Μην την εφαρμόσετε.")

    if st.button("⬅️ Return to Library Hub"):
        st.session_state.selected_tool = None
        st.rerun()
