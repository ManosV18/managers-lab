import streamlit as st
from core.sync import sync_global_state

def show_payables_manager():
    st.header("🤝 Payables Strategic Control")
    st.info("Using Corporate WACC as the hurdle rate to optimize supplier payment strategies and cash retention.")
    
    # 1. FETCH GLOBAL DATA (Μέσω sync για αποφυγή σφαλμάτων)
    metrics = sync_global_state()
    s = st.session_state
    
    q = s.get('volume', 0)
    vc = s.get('variable_cost', 0.0)
    current_sales = s.get('sales', 1000.0) # current_sales από εικόνα
    
    annual_purchases = q * vc
    current_ap_days = s.get('ap_days', 30)
    hurdle_rate = metrics.get('wacc', 0.20) # WACC από εικόνα
    
    st.write(f"**🔗 Opportunity Cost (WACC):** {hurdle_rate:.1%}")

    tab1, tab2 = st.tabs(["💰 Cash Flow Impact", "⚖️ Discount vs. Cost of Capital"])

    with tab1:
        st.subheader("Liquidity Optimization")
        new_ap_days = st.slider("Target Payment Terms (Days)", 0, 150, int(current_ap_days), key="ap_slider")
        
        # Calculation of cash released/trapped
        cash_impact = ((new_ap_days - current_ap_days) / 365) * annual_purchases
        value_benefit = cash_impact * hurdle_rate
        
        c1, c2 = st.columns(2)
        c1.metric("Net Cash Impact", f"€ {cash_impact:,.2f}", 
                  delta=f"{new_ap_days - current_ap_days} Days Shift")
        
        c2.metric("Annual Value Benefit", f"€ {max(0.0, value_benefit):,.2f}")

    with tab2:
        st.subheader("Early Payment Discount (EPD) Evaluator")
        
        # ΕΙΣΑΓΩΓΗ ΔΕΔΟΜΕΝΩΝ ΑΚΡΙΒΩΣ ΑΠΟ ΤΗΝ ΕΙΚΟΝΑ
        col1, col2, col3 = st.columns(3)
        extra_sales = col1.number_input("extra_sales", value=250.0)
        cogs = col2.number_input("COGS", value=800.0)
        discount_trial = col3.number_input("discount_trial (%)", value=2.0) / 100

        d1, d2, d3 = st.columns(3)
        days_take_disc = d1.number_input("days_curently_paying_clients_take_discount", value=60)
        days_not_take_disc = d2.number_input("days_curently_paying_clients_not_take_discount", value=120)
        new_days_limit = d3.number_input("new_days_payment_clients_take_disc", value=10)
        
        prc_take = st.slider("prc_clients_take_disc", 0.0, 1.0, 0.40)

        # --- ΟΙ ΦΟΡΜΟΥΛΕΣ ΤΟΥ EXCEL (ΑΚΡΙΒΩΣ) ---
        # avg_current_collection_days
        avg_curr_days = (days_take_disc * prc_take) + (days_not_take_disc * (1 - prc_take))
        
        # current_receivables
        curr_receiv = (current_sales * avg_curr_days) / 365
        
        # prcnt_of_total_new_clients_in_new_policy
        total_new_sales = current_sales + extra_sales
        prc_new_policy = ((current_sales * prc_take) + extra_sales) / total_new_sales
        
        # new_avg_collection_period
        new_avg_period = (prc_new_policy * new_days_limit) + ((1 - prc_new_policy) * days_not_take_disc)
        
        # new_receivables
        new_receiv = (total_new_sales * new_avg_period) / 365
        
        # free_capital
        free_cap = curr_receiv - new_receiv
        
        # profit_from_extra_sales
        prof_extra = extra_sales * (1 - (cogs / current_sales))
        
        # profit_from_free_capital
        prof_free_cap = free_cap * hurdle_rate
        
        # discount_cost
        disc_cost = total_new_sales * prc_new_policy * discount_trial
        
        # NPV
        final_npv = prof_extra + prof_free_cap - disc_cost

        st.divider()
        
        # ΕΜΦΑΝΙ
