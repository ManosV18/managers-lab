import streamlit as st
from core.sync import sync_global_state

def show_payables_manager():
    st.header("🤝 Payables Strategic Control")
    st.info("Using Corporate WACC as the hurdle rate to optimize strategies based on NPV analysis.")
    
    # 1. FETCH GLOBAL DATA
    metrics = sync_global_state()
    s = st.session_state
    
    # Βασικές παράμετροι από το σύστημα
    q = s.get('volume', 0)
    vc = s.get('variable_cost', 0.0)
    annual_purchases = q * vc
    current_ap_days = s.get('ap_days', 30)
    wacc_val = metrics.get('wacc', 0.20) 

    tab1, tab2 = st.tabs(["💰 Cash Flow Impact", "⚖️ Discount vs. Cost of Capital"])

    with tab1:
        st.subheader("Liquidity Optimization")
        new_ap_days = st.slider("Target Payment Terms (Days)", 0, 150, int(current_ap_days), key="ap_slider")
        cash_impact = ((new_ap_days - current_ap_days) / 365) * annual_purchases
        value_benefit = cash_impact * wacc_val
        
        c1, c2 = st.columns(2)
        c1.metric("Net Cash Impact", f"€ {cash_impact:,.2f}", delta=f"{new_ap_days - current_ap_days} Days")
        c2.metric("Annual Value Benefit", f"€ {max(0.0, value_benefit):,.2f}")

    with tab2:
        st.subheader("Receivables NPV Optimizer (Excel Logic)")
        
        # --- INPUTS ΑΚΡΙΒΩΣ ΟΠΩΣ Η ΕΙΚΟΝΑ ---
        col1, col2 = st.columns(2)
        with col1:
            c_sales = st.number_input("current_sales", value=1000.0)
            e_sales = st.number_input("extra_sales", value=250.0)
            disc_trial = st.number_input("discount_trial (%)", value=2.0) / 100
            prc_take = st.number_input("prc_clients_take_disc (%)", value=40.0) / 100
            cogs = st.number_input("COGS", value=800.0)
            wacc = st.number_input("WACC (%)", value=20.0) / 100
        
        with col2:
            d_take = st.number_input("days_curently_paying_clients_take_discount", value=60)
            d_not = st.number_input("days_curently_paying_clients_not_take_discount", value=120)
            n_days = st.number_input("new_days_payment_clients_take_disc", value=10)
            st.write(f"**avg_days_pay_suppliers:** {s.get('ap_days', 30.0)}")

        # --- ΥΠΟΛΟΓΙΣΜΟΙ ΑΚΡΙΒΩΣ ΑΠΟ ΤΙΣ ΦΟΡΜΟΥΛΕΣ ΤΗΣ ΕΙΚΟΝΑΣ ---
        prc_not = 1 - prc_take
        avg_curr_coll = (d_take * prc_take) + (d_not * prc_not)
        curr_receiv = (c_sales * avg_curr_coll) / 365
        
        total_n_sales = c_sales + e_sales
        prc_n_policy = ((c_sales * prc_take) + e_sales) / total_n_sales
        prc_o_policy = 1 - prc_n_policy
        
        n_avg_coll = (prc_n_policy * n_days) + (prc_o_policy * d_not)
        n_receiv = (total_n_sales * n_avg_coll) / 365
        
        free_cap = curr_receiv - n_receiv
        
        # Yellow Fields
        prof_extra = e_sales * (1 - (cogs / c_sales))
        prof_free_cap = free_cap * wacc
        disc_cost = total_n_sales * prc_n_policy * disc_trial
        
        npv = prof_extra + prof_free_cap - disc_cost
        
        # Maximum & Optimum Discount (Με τις δυνάμεις από την εικόνα)
        max_disc = 1 - (1 + (wacc/365))**(n_days - avg_curr_coll)
        opt_disc = 1 - (1 + (wacc/365))**(n_days - d_not)

        # --- ΕΜΦΑΝΙΣΗ ΑΠΟΤΕΛΕΣΜΑΤΩΝ ---
        st.divider()
        res1, res2 = st.columns(2)
        with res1:
            st.write(f"**avg_current_collection_days:** {avg_curr_coll:.2f}")
            st.write(f"**current_receivables:** €{curr_receiv:,.2f}")
            st.write(f"**new_avg_collection_period:** {n_avg_coll:.2f}")
            st.write(f"**new_receivables:** €{n_receiv:,.2f}")
            st.markdown(f"**free_capital: €{free_cap:,.2f}**")

        with res2:
            st.write(f"**profit_from_extra_sales:** €{prof_extra:,.2f}")
            st.
