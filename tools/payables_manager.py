import streamlit as st
from core.sync import sync_global_state

def show_payables_manager():
    st.header("🤝 Payables Strategic Control")
    st.info("Using Corporate WACC as the hurdle rate to optimize supplier payment strategies and cash retention.")
    
    # 1. FETCH GLOBAL DATA (Χρήση sync για αποφυγή του σφάλματος των 11 ορισμάτων)
    metrics = sync_global_state()
    s = st.session_state
    
    q = s.get('volume', 0)
    vc = s.get('variable_cost', 0.0)
    current_sales = s.get('sales', 1000.0) 
    
    annual_purchases = q * vc
    current_ap_days = s.get('ap_days', 30)
    wacc = metrics.get('wacc', 0.20) # 20% από την εικόνα σας
    
    st.write(f"**🔗 Opportunity Cost (WACC):** {wacc:.1%}")

    tab1, tab2 = st.tabs(["💰 Cash Flow Impact", "⚖️ Discount vs. Cost of Capital"])

    with tab1:
        st.subheader("Liquidity Optimization")
        new_ap_days = st.slider("Target Payment Terms (Days)", 0, 150, int(current_ap_days), key="ap_slider")
        
        # Υπολογισμός Cash Impact (365 ημέρες)
        cash_impact = ((new_ap_days - current_ap_days) / 365) * annual_purchases
        value_benefit = cash_impact * wacc
        
        c1, c2 = st.columns(2)
        c1.metric("Net Cash Impact", f"€ {cash_impact:,.2f}", 
                  delta=f"{new_ap_days - current_ap_days} Days Shift")
        
        c2.metric("Annual Value Benefit", f"€ {max(0.0, value_benefit):,.2f}")

    with tab2:
        # ΕΜΦΑΝΙΣΗ ΑΚΡΙΒΩΣ ΟΠΩΣ Η ΕΙΚΟΝΑ ΤΟΥ EXCEL
        st.subheader("Receivables Strategic Optimizer (Excel View)")
        
        # Πρώτο block δεδομένων
        col_ex1, col_ex2 = st.columns(2)
        extra_sales = col_ex1.number_input("extra_sales", value=250.0)
        discount_trial = col_ex1.number_input("discount_trial (%)", value=2.0) / 100
        prc_clients_take_disc = col_ex1.number_input("prc_clients_take_disc (%)", value=40.0) / 100
        
        days_take_disc = col_ex2.number_input("days_curently_paying_clients_take_discount", value=60)
        days_not_take_disc = col_ex2.number_input("days_curently_paying_clients_not_take_discount", value=120)
        new_days_limit = col_ex2.number_input("new_days_payment_clients_take_disc", value=10)
        cogs = col_ex2.number_input("COGS", value=800.0)

        # --- ΥΠΟΛΟΓΙΣΜΟΙ ΑΚΡΙΒΩΣ ΑΠΟ ΤΗΝ ΕΙΚΟΝΑ ---
        prc_not_take_disc = 1 - prc_clients_take_disc
        avg_current_days = (days_take_disc * prc_clients_take_disc) + (days_not_take_disc * prc_not_take_disc)
        current_receivables = (current_sales * avg_current_days) / 365
        
        total_new_sales = current_sales + extra_sales
        prc_new_policy = ((current_sales * prc_clients_take_disc) + extra_sales) / total_new_sales
        new_avg_period = (prc_new_policy * new_days_limit) + ((1 - prc_new_policy) * days_not_take_disc)
        new_receivables = (total_new_sales * new_avg_period) / 365
        
        free_capital = current_receivables - new_receivables
        profit_extra = extra_sales * (1 - (cogs / current_sales))
        profit_free_cap = free_capital * wacc
        discount_cost = total_new_sales * prc_new_policy * discount_trial
        
        final_npv = profit_extra + profit_free_cap - discount_cost

        # Εμφάνιση αποτελεσμάτων (Κίτρινα πεδία Excel)
        st.divider()
        st.write(f"**avg_current_collection_days:** {avg_current_days:.2f}")
        st.write(f"**current_receivables:** €{current_receivables:,.2f}")
        st.write(f"**new_avg_collection_period:** {new_avg_period:.2f}")
        st.write(f"**new_receivables:** €{new_receivables:,.2f}")
        
        st.write(f"---")
        st.markdown(f"**free_capital:** <span style='color:blue'>€{free_capital:,.2f}</span>", unsafe_allow_html=True)
        st.write(f"**profit_from_extra_sales:** €{profit_extra:,.2f}")
        st.write(f"**profit_from_free_capital:** €{profit_free_cap:,.2f}")
        st.write(f"**discount_cost:** €{discount_cost:,.2f}")
        
        st.divider()
        if final_npv > 0:
            st.success(f"**NPV:** € {final_npv:,.2f} ✅ (Strategy Profitable)")
        else:
            st.error(f"**NPV:** € {final_npv:,.2f} 🚨 (Strategy Value-Destructive)")

    st.divider()
    if st.button("Sync Target Days to Global Strategy", use_container_width=True):
        st.session_state.ap_days = new_ap_days
        st.success(f"Global Payables Days updated to {new_ap_days} days.")
    
    if st.button("Back to Library Hub", use_container_width=True):
        st.session_state.selected_tool = None
        st.rerun()
