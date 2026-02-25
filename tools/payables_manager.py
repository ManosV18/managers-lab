import streamlit as st
from core.sync import sync_global_state

def show_payables_manager():
    st.header("🤝 Receivables Strategic Optimizer")
    
    # 1. FETCH DATA
    metrics = sync_global_state()
    s = st.session_state
    
    # INPUTS
    c1, c2 = st.columns(2)
    with c1:
        current_sales = st.number_input("current_sales", value=1000.0)
        extra_sales = st.number_input("extra_sales", value=250.0)
        discount_trial = st.number_input("discount_trial (%)", value=2.0) / 100
        prc_clients_take_disc = st.number_input("prc_clients_take_disc (%)", value=40.0) / 100
        cogs = st.number_input("COGS", value=800.0)
        wacc = st.number_input("WACC (%)", value=20.0) / 100

    with c2:
        days_take_disc = st.number_input("days_curently_paying_clients_take_discount", value=60)
        days_curr_not_take = st.number_input("days_curently_paying_clients_not_take_discount", value=120)
        new_days_limit = st.number_input("new_days_payment_clients_take_disc", value=10)

    # --- ΥΠΟΛΟΓΙΣΜΟΙ NPV ΒΑΣΕΙ ΕΙΚΟΝΑΣ ---
    prc_not_take = 1.0 - prc_clients_take_disc
    avg_curr_days = (days_take_disc * prc_clients_take_disc) + (days_curr_not_take * prc_not_take)
    curr_receiv = (current_sales * avg_curr_days) / 365
    
    total_sales = current_sales + extra_sales
    prc_new_policy = ((current_sales * prc_clients_take_disc) + extra_sales) / total_sales
    
    new_avg_period = (prc_new_policy * new_days_limit) + ((1 - prc_new_policy) * days_curr_not_take)
    new_receiv = (total_sales * new_avg_period) / 365
    
    free_cap = curr_receiv - new_receiv
    
    prof_extra = extra_sales * (1 - (cogs / current_sales))
    prof_free_cap = free_cap * wacc
    disc_cost = total_sales * prc_new_policy * discount_trial
    npv_result = prof_extra + prof_free_cap - disc_cost

    # --- ΥΠΟΛΟΓΙΣΜΟΣ THRESHOLDS (Χειρουργική Ακρίβεια) ---
    base = 1.0 + (wacc / 365.0)
    
    # 1. Maximum Discount: 1 - (Base ^ (10 - 96))
    exp_max = float(new_days_limit - avg_curr_days)
    max_d = 1.0 - (base ** exp_max)
    
    # 2. Optimum Discount: 1 - (Base ^ (10 - 120))
    exp_opt = float(new_days_limit - days_curr_not_take)
    opt_d = 1.0 - (base ** exp_opt)

    # --- DISPLAY ---
    st.divider()
    st.subheader(f"NPV Result: € {npv_result:.2f}")
    
    res_col1, res_col2 = st.columns(2)
    with res_col1:
        st.metric("Maximum Discount (Break Even)", f"{max_d:.2%}")
    with res_col2:
        st.metric("Optimum Discount", f"{opt_d:.2%}")

    st.info(f"Free Capital Released: € {free_cap:,.2f}")
    
    if st.button("Back to Hub"):
        st.session_state.selected_tool = None
        st.rerun()
