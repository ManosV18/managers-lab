import streamlit as st
from core.sync import sync_global_state

def show_payables_manager():
    st.header("🤝 Payables & Receivables Strategic Control")
    st.info("Πλήρης αναπαραγωγή του μοντέλου NPV βάσει των υπολογισμών του Excel.")
    
    # 1. FETCH GLOBAL DATA
    metrics = sync_global_state()
    s = st.session_state
    
    # Αρχικές τιμές από το σύστημα (Default τιμές από την εικόνα σου)
    q = s.get('volume', 0)
    vc = s.get('variable_cost', 0.0)
    annual_purchases = q * vc
    current_ap_days = s.get('ap_days', 30.0)

    tab1, tab2 = st.tabs(["💰 Cash Flow Impact", "⚖️ Discount NPV Evaluator"])

    with tab1:
        st.subheader("Liquidity Optimization")
        wacc_val = metrics.get('wacc', 0.20)
        new_ap_days = st.slider("Target Payment Terms (Days)", 0, 150, int(current_ap_days), key="ap_slider")
        
        # Υπολογισμός Cash Impact (365 ημέρες βάσει οδηγίας)
        cash_impact = ((new_ap_days - current_ap_days) / 365) * annual_purchases
        value_benefit = cash_impact * wacc_val
        
        c1, c2 = st.columns(2)
        c1.metric("Net Cash Impact", f"€ {cash_impact:,.2f}", delta=f"{int(new_ap_days - current_ap_days)} Days")
        c2.metric("Annual Value Benefit", f"€ {max(0.0, value_benefit):,.2f}")

    with tab2:
        st.subheader("Receivables NPV Optimizer (Excel Mirror)")
        
        # --- INPUTS (ΑΠΟ ΤΗΝ ΕΙΚΟΝΑ EXCEL) ---
        col1, col2 = st.columns(2)
        with col1:
            current_sales = st.number_input("current_sales", value=1000.0)
            extra_sales = st.number_input("extra_sales", value=250.0)
            discount_trial = st.number_input("discount_trial (%)", value=2.0) / 100
            prc_clients_take_disc = st.number_input("prc_clients_take_disc (%)", value=40.0) / 100
            cogs = st.number_input("COGS", value=800.0)
            wacc = st.number_input("WACC (%)", value=20.0) / 100
        
        with col2:
            days_take_disc = st.number_input("days_curently_paying_clients_take_discount", value=60)
            days_not_take_disc = st.number_input("days_curently_paying_clients_not_take_discount", value=120)
            new_days_limit = st.number_input("new_days_payment_clients_take_disc", value=10)
            st.write(f"**avg_days_pay_suppliers:** {s.get('ap_days', 30.0)}")

        # --- ΥΠΟΛΟΓΙΣΜΟΙ ΑΚΡΙΒΩΣ ΟΠΩΣ ΤΟ EXCEL (ΣΥΜΦΩΝΑ ΜΕ ΤΙΣ ΕΙΚΟΝΕΣ) ---
        
        # 1. prc_clients_not_take_disc = 1 - prc_clients_take_disc
        prc_not_take = 1 - prc_clients_take_disc
        
        # 2. avg_current_collection_days = (days_take_disc * prc_take) + (days_not_take * prc_not_take)
        avg_curr_days = (days_take_disc * prc_clients_take_disc) + (days_not_take_disc * prc_not_take)
        
        # 3. current_receivables = current_sales * avg_current_collection_days / 365
        curr_receiv = (current_sales * avg_curr_days) / 365
        
        # 4. prcnt_of_total_new_clients_in_new_policy = ((current_sales * prc_take) + extra_sales) / (current_sales + extra_sales)
        total_new_sales = current_sales + extra_sales
        prc_new_policy = ((current_sales * prc_clients_take_disc) + extra_sales) / total_new_sales
        
        # 5. prcnt_of_total_new_clients_in_old_policy = 1 - prc_new_policy
        prc_old_policy = 1 - prc_new_policy
        
        # 6. new_avg_collection_period = (prc_new_policy * new_days_limit) + (prc_old_policy * days_not_take)
        new_avg_period = (prc_new_policy * new_days_limit) + (prc_old_policy * days_not_take_disc)
        
        # 7. new_receivables = total_new_sales * new_avg_period / 365
        new_receiv = (total_new_sales * new_avg_period) / 365
        
        # 8. free_capital = current_receivables - new_receivables
        free_cap = curr_receiv - new_receiv
        
        # --- ΥΠΟΛΟΓΙΣΜΟΙ NPV (ΚΙΤΡΙΝΑ ΠΕΔΙΑ) ---
        
        # 9. profit_from_extra_sales = extra_sales * (1 - (COGS / current_sales))
        prof_extra = extra_sales * (1 - (cogs / current_sales))
        
        # 10. profit_from_free_capital = free_capital * WACC
        prof_free_cap = free_cap * wacc
        
        # 11. discount_cost = (current_sales + extra_sales) * prc_new_policy * discount_trial
        disc_cost = total_new_sales * prc_new_policy * discount_trial
        
        # 12. NPV = prof_extra + prof_free_cap - disc_cost
        final_npv = prof_extra + prof_free_cap - disc_cost

        # --- THRESHOLDS (POWER FORMULAS) ---
        # maximum_discount = 1 - (1 + (WACC/365))^(new_days - avg_curr_days)
        daily_wacc = 1 + (wacc / 365)
        max_d = 1 - (daily_wacc**(new_days_limit - avg_curr_days))
        
        # optimum_discount = 1 - (1 + (WACC/365))^(new_days - days_not_take)
        opt_d = 1 - (daily_wacc**(new_days_limit - days_not_take_disc))

        # --- DISPLAY RESULTS (ΕΝΔΙΑΜΕΣΑ & ΤΕΛΙΚΑ) ---
        st.divider()
        r1, r2 = st.columns(2)
        with r1:
            st.write(f"**Current Receivables:** €{curr_receiv:,.2f}")
            st.write(f"**New Receivables:** €{new_receiv:,.2f}")
            st.info(f"**Free Capital:** €{free_cap:,.2f}")
        
        with r2:
            st.write(f"**Profit from Sales:** €{prof_extra:,.2f}")
            st.write(f"**Profit from Capital:** €{prof_free_cap:,.2f}")
            st.write(f"**Discount Cost:** €{disc_cost:,.2f}")
            st.success(f"**NPV:** €{final_npv:,.2f}")

        st.divider()
        st.subheader("💡 Strategic Thresholds")
        st.write(f"**Maximum Discount (NPV Break Even):** {max_d:.2%}")
        st.write(f"**Optimum Discount:** {opt_d:.2%}")

    st.divider()
    if st.button("Back to Library Hub", use_container_width=True):
        st.session_state.selected_tool = None
        st.rerun()
