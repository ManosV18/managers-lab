import streamlit as st
from core.sync import sync_global_state

def show_payables_manager():
    st.header("🎯 Receivables Strategic Optimizer (NPV Analysis)")
    st.info("Ανάλυση της επίδρασης της πιστωτικής πολιτικής στην αξία της επιχείρησης (Βάσει Excel).")

    # 1. FETCH GLOBAL DATA
    metrics = sync_global_state()
    s = st.session_state

    # 2. INPUTS - ΑΚΡΙΒΩΣ ΟΠΩΣ ΣΤΗΝ ΕΙΚΟΝΑ
    st.subheader("📥 Input Parameters")
    c1, c2 = st.columns(2)
    
    with c1:
        current_sales = st.number_input("current_sales", value=1000.0)
        extra_sales = st.number_input("extra_sales", value=250.0)
        discount_trial = st.number_input("discount_trial (%)", value=2.0) / 100
        prc_clients_take_disc = st.number_input("prc_clients_take_disc (%)", value=40.0) / 100
        cogs = st.number_input("COGS", value=800.0)
        wacc = st.number_input("WACC (%)", value=20.0) / 100

    with c2:
        days_curr_take_disc = st.number_input("days_curently_paying_clients_take_discount", value=60)
        days_curr_not_take_disc = st.number_input("days_curently_paying_clients_not_take_discount", value=120)
        new_days_take_disc = st.number_input("new_days_payment_clients_take_disc", value=10)
        st.write("---")
        st.write(f"**avg_days_pay_suppliers:** {s.get('ap_days', 30.0)}")

    # 3. CALCULATIONS - ΑΚΡΙΒΩΣ ΟΙ ΦΟΡΜΟΥΛΕΣ ΤΗΣ ΕΙΚΟΝΑΣ
    # ---------------------------------------------------------
    prc_clients_not_take_disc = 1 - prc_clients_take_disc
    avg_current_collection_days = (days_curr_take_disc * prc_clients_take_disc) + (days_curr_not_take_disc * prc_clients_not_take_disc)
    
    # Χρήση 365 ημερών βάσει οδηγίας
    current_receivables = (current_sales * avg_current_collection_days) / 365
    
    total_new_sales = current_sales + extra_sales
    prcnt_of_total_new_clients_in_new_policy = ((current_sales * prc_clients_take_disc) + extra_sales) / total_new_sales
    prcnt_of_total_new_clients_in_old_policy = 1 - prcnt_of_total_new_clients_in_new_policy
    
    new_avg_collection_period = (prcnt_of_total_new_clients_in_new_policy * new_days_take_disc) + (prcnt_of_total_new_clients_in_old_policy * days_curr_not_take_disc)
    new_receivables = (total_new_sales * new_avg_collection_period) / 365
    
    free_capital = current_receivables - new_receivables
    
    # Profit & Cost Analysis
    profit_from_extra_sales = extra_sales * (1 - (cogs / current_sales))
    profit_from_free_capital = free_capital * wacc
    discount_cost = total_new_sales * prcnt_of_total_new_clients_in_new_policy * discount_trial
    
    # NPV Calculation
    npv = profit_from_extra_sales + profit_from_free_capital - discount_cost

    # 4. DISPLAY RESULTS - ΤΑ ΚΙΤΡΙΝΑ ΠΕΔΙΑ ΤΗΣ ΕΙΚΟΝΑΣ
    st.divider()
    st.subheader("📊 Financial Impact (NPV Results)")
    
    res1, res2, res3 = st.columns(3)
    
    with res1:
        st.metric("Free Capital", f"€{free_capital:,.2f}")
        st.write(f"**Current Receivables:** €{current_receivables:,.2f}")
        st.write(f"**New Receivables:** €{new_receivables:,.2f}")

    with res2:
        st.write(f"**Profit from Extra Sales:** €{profit_from_extra_sales:,.2f}")
        st.write(f"**Profit from Free Capital:** €{profit_from_free_capital:,.2f}")
        st.write(f"**Discount Cost:** €{discount_cost:,.2f}")

    with res3:
        st.metric("NPV", f"€{npv:,.2f}")
        
    st.divider()

    # 5. BREAK-EVEN & OPTIMUM (Από το κάτω μέρος της εικόνας)
    st.subheader("💡 Strategy Thresholds")
    
    # maximum_discount (NPV Break Even)
    # Η έκπτωση στην οποία το NPV γίνεται μηδέν
    max_discount_val = (profit_from_extra_sales + profit_from_free_capital) / (total_new_sales * prcnt_of_total_new_clients_in_new_policy)
    
    # optimum_discount (Βάσει της φόρμουλας NPV της εικόνας)
    # Προσέγγιση optimum discount βάσει χρονικής αξίας χρήματος
    opt_discount_val = 1 - ((1 + (wacc/365))**(new_days_take_disc - avg_current_collection_days))

    c_break1, c_break2 = st.columns(2)
    c_break1.write(f"**maximum_discount (NPV Break Even):**")
    c_break1.info(f"{max_discount_val:.2%}")
