import streamlit as st
from core.sync import sync_global_state

def show_payables_manager():
    st.header("🤝 Receivables Strategy (Excel Mirror)")
    
    # 1. FETCH DATA
    metrics = sync_global_state()
    s = st.session_state
    
    # INPUTS - ΑΚΡΙΒΩΣ ΟΠΩΣ Η ΕΙΚΟΝΑ
    st.subheader("📥 Excel Inputs")
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
        new_days_limit = st.number_input("new_days_payment_clients_take_disc", value=10)

    # 2. ΥΠΟΛΟΓΙΣΜΟΙ ΒΗΜΑ-ΒΗΜΑ (ΑΚΡΙΒΩΣ ΟΙ ΦΟΡΜΟΥΛΕΣ ΤΗΣ ΕΙΚΟΝΑΣ)
    prc_clients_not_take_disc = 1 - prc_clients_take_disc
    
    # avg_current_collection_days
    avg_curr_days = (days_curr_take_disc * prc_clients_take_disc) + (days_curr_not_take_disc * prc_clients_not_take_disc)
    
    # current_receivables (365 ημέρες)
    curr_receiv = (current_sales * avg_curr_days) / 365
    
    # prcnt_of_total_new_clients_in_new_policy
    total_new_sales = current_sales + extra_sales
    prc_new_policy = ((current_sales * prc_clients_take_disc) + extra_sales) / total_new_sales
    
    # prcnt_of_total_new_clients_in_old_policy
    prc_old_policy = 1 - prc_new_policy
    
    # new_avg_collection_period
    new_avg_period = (prc_new_policy * new_days_limit) + (prc_old_policy * days_curr_not_take_disc)
    
    # new_receivables
    new_receiv = (total_new_sales * new_avg_period) / 365
    
    # free_capital
    free_cap = curr_receiv - new_receiv
    
    # --- YELLOW FIELDS ---
    profit_extra = extra_sales * (1 - (cogs / current_sales))
    profit_free_cap = free_cap * wacc
    discount_cost = total_new_sales * prc_new_policy * discount_trial
    
    # NPV
    final_npv = profit_extra + profit_free_cap - discount_cost

    # --- THRESHOLDS (Με βάση την εικόνα) ---
    max_disc = 1 - ((1 + (wacc/365))**(new_days_limit - avg_curr_days))
    opt_disc = 1 - ((1 + (wacc/365))**(new_days_limit - days_curr_not_take_disc))

    # 3. DISPLAY - ΑΥΣΤΗΡΑ ΑΝΑΛΥΤΙΚΑ
    st.divider()
    res1, res2 = st.columns(2)
    
    with res1:
        st.write(f"**avg_current_collection_days:** {avg_curr_days}")
        st.write(f"**current_receivables:** {curr_receiv:.2f}")
        st.write(f"**new_avg_collection_period:** {new_avg_period:.2f}")
        st.write(f"**new_receivables:** {new_receiv:.2f}")
        st.info(f"**free_capital:** {free_cap:.2f}")

    with res2:
        st.write(f"**profit_from_extra_sales:** {profit_extra:.1f}")
        st.write(f"**profit_from_free_capital:** {profit_free_cap:.2f}")
        st.write(f"**discount_cost:** {discount_cost:.1f}")
        st.success(f"### **NPV: {final_npv:.2f}**")

    st.divider()
    st.warning(f"**maximum_discount (NPV Break Even):** {max_disc:.2%}")
    st.warning(f"**optimum_discount:** {opt_disc:.2%}")

    if st.button("Back to Library"):
        st.session_state.selected_tool = None
        st.rerun()
