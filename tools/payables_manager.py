import streamlit as st
from core.sync import sync_global_state

def show_payables_manager():
    st.header("🤝 Strategic NPV Analysis")
    st.info("Πλήρης αναπαραγωγή του μοντέλου Excel για την αξιολόγηση πιστωτικής πολιτικής.")
    
    # 1. FETCH GLOBAL DATA
    metrics = sync_global_state()
    s = st.session_state
    
    # Βασικές τιμές από το σύστημα
    q = s.get('volume', 0)
    vc = s.get('variable_cost', 0.0)
    annual_purchases = q * vc
    current_ap_days = s.get('ap_days', 30.0)
    
    tab1, tab2 = st.tabs(["💰 Cash Flow Impact", "⚖️ Discount vs. Cost of Capital"])

    with tab1:
        st.subheader("Liquidity Optimization")
        wacc_val = metrics.get('wacc', 0.20)
        new_ap_days = st.slider("Target Payment Terms (Days)", 0, 150, int(current_ap_days), key="ap_slider")
        
        cash_impact = ((new_ap_days - current_ap_days) / 365) * annual_purchases
        value_benefit = cash_impact * wacc_val
        
        c1, c2 = st.columns(2)
        c1.metric("Net Cash Impact", "€ {:,.2f}".format(cash_impact), delta="{:d} Days".format(int(new_ap_days - current_ap_days)))
        c2.metric("Annual Value Benefit", "€ {:,.2f}".format(max(0.0, value_benefit)))

    with tab2:
        st.subheader("Receivables NPV Optimizer")
        
        # --- INPUTS ΑΚΡΙΒΩΣ ΟΠΩΣ Η ΕΙΚΟΝΑ ---
        col1, col2 = st.columns(2)
        with col1:
            c_sales = st.number_input("current_sales", value=1000.0)
            e_sales = st.number_input("extra_sales", value=250.0)
            disc_trial = st.number_input("discount_trial (%)", value=2.0) / 100
            prc_take = st.number_input("prc_clients_take_disc (%)", value=40.0) / 100
            cogs_input = st.number_input("COGS", value=800.0)
            wacc_input = st.number_input("WACC (%)", value=20.0) / 100
        
        with col2:
            d_take = st.number_input("days_curently_paying_clients_take_discount", value=60)
            d_not = st.number_input("days_curently_paying_clients_not_take_discount", value=120)
            n_days = st.number_input("new_days_payment_clients_take_disc", value=10)
            st.write("**avg_days_pay_suppliers:**", s.get('ap_days', 30.0))

        # --- ΥΠΟΛΟΓΙΣΜΟΙ ΑΚΡΙΒΩΣ ΑΠΟ ΤΙΣ ΦΟΡΜΟΥΛΕΣ ΤΗΣ ΕΙΚΟΝΑΣ ---
        prc_not = 1.0 - prc_take
        avg_curr_days = (d_take * prc_take) + (d_not * prc_not)
        curr_receiv = (c_sales * avg_curr_days) / 365.0
        
        total_n_sales = c_sales + e_sales
        prc_n_policy = ((c_sales * prc_take) + e_sales) / total_n_sales
        prc_o_policy = 1.0 - prc_n_policy
        
        n_avg_period = (prc_n_policy * n_days) + (prc_o_policy * d_not)
        n_receiv = (total_n_sales * n_avg_period) / 365.0
        
        free_cap = curr_receiv - n_receiv
        
        # Yellow Fields
        prof_extra = e_sales * (1.0 - (cogs_input / c_sales))
        prof_free_cap = free_cap * wacc_input
        d_cost = total_n_sales * prc_n_policy * disc_trial
        
        npv_final = prof_extra + prof_free_cap - d_cost
        
        # Maximum & Optimum Discount (Power formulas)
        # Σύμφωνα με την εικόνα: 1-((1+(WACC/365))^(new_days-avg_days))
        max_d = 1.0 - ((1.0 + (wacc_input / 365.0))**(n_days - avg_curr_days))
        opt_d = 1.0 - ((1.0 + (wacc_input / 365.0))**(n_days - d_not))

        # --- ΕΜΦΑΝΙΣΗ ΑΠΟΤΕΛΕΣΜΑΤΩΝ ---
        st.divider()
        res1, res2 = st.columns(2)
        with res1:
            st.write("**avg_current_collection_days:**", round(avg_curr_days, 2))
            st.write("**current_receivables:** €", round(curr_receiv, 2))
            st.write("**new_avg_collection_period:**", round(n_avg_period, 2))
            st.write("**new_receivables:** €", round(n_receiv, 2))
            st.info("**free_capital: € {:,.2f}**".format(free_cap))

        with res2:
            st.write("**profit_from_extra_sales:** €", round(prof_extra, 2))
            st.write("**profit_from_free_capital:** €", round(prof_free_cap, 2))
            st.write("**discount_cost:** €", round(d_cost, 2))
            st.success("**NPV: € {:,.2f}**".format(npv_final))

        st.divider()
        st.warning("**maximum_discount (NPV Break Even):** {:.2%}".format(max_d))
        st.warning("**optimum_discount:** {:.2%}".format(opt_d))

    st.divider()
    if st.button("Sync Target Days", use_container_width=True):
        st.session_state.ap_days = float(new_ap_days)
        st.success("Updated.")
        
    if st.button("Back to Library Hub", use_container_width=True):
        st.session_state.selected_tool = None
        st.rerun()
