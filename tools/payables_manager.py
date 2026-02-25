import streamlit as st
from core.sync import sync_global_state

def show_payables_manager():
    st.header("🤝 Strategic NPV Analysis")
    
    # 1. FETCH DATA
    metrics = sync_global_state()
    s = st.session_state
    
    # Σταθερές από το σύστημα
    current_sales = s.get('sales', 1000.0)
    wacc = 0.20 # Όπως στην εικόνα
    
    tab1, tab2 = st.tabs(["💰 Cash Flow Impact", "⚖️ NPV Optimizer (Excel View)"])

    with tab1:
        st.subheader("Liquidity Optimization")
        annual_purchases = s.get('volume', 0) * s.get('variable_cost', 0.0)
        current_ap_days = s.get('ap_days', 30.0)
        new_ap_days = st.slider("Target Payment Terms", 0, 150, int(current_ap_days))
        
        cash_impact = ((new_ap_days - current_ap_days) / 365) * annual_purchases
        st.metric("Net Cash Impact", f"€ {cash_impact:,.2f}")

    with tab2:
        # INPUTS ΑΚΡΙΒΩΣ ΟΠΩΣ Η ΕΙΚΟΝΑ
        c1, c2 = st.columns(2)
        with c1:
            e_sales = st.number_input("extra_sales", value=250.0)
            disc_trial = st.number_input("discount_trial (%)", value=2.0) / 100
            prc_take = st.number_input("prc_clients_take_disc (%)", value=40.0) / 100
            cogs = st.number_input("COGS", value=800.0)
        with c2:
            d_take = st.number_input("days_paying_clients_take_discount", value=60)
            d_not = st.number_input("days_paying_clients_not_take_discount", value=120)
            n_days = st.number_input("new_days_limit", value=10)

        # --- ΟΙ ΦΟΡΜΟΥΛΕΣ ΤΟΥ EXCEL ΜΙΑ ΠΡΟΣ ΜΙΑ ---
        prc_not_take = 1.0 - prc_take
        avg_curr_days = (d_take * prc_take) + (d_not * prc_not_take)
        curr_receiv = (current_sales * avg_curr_days) / 365
        
        total_sales = current_sales + e_sales
        prc_new_pol = ((current_sales * prc_take) + e_sales) / total_sales
        prc_old_pol = 1.0 - prc_new_pol
        
        new_avg_period = (prc_new_pol * n_days) + (prc_old_pol * d_not)
        new_receiv = (total_sales * new_avg_period) / 365
        
        free_cap = curr_receiv - new_receiv
        
        # Yellow Fields
        prof_extra = e_sales * (1.0 - (cogs / current_sales))
        prof_free_cap = free_cap * wacc
        cost_disc = total_sales * prc_new_pol * disc_trial
        
        final_npv = prof_extra + prof_free_cap - cost_disc

        # Thresholds (Calculated step-by-step to avoid syntax errors)
        daily_wacc = 1.0 + (wacc / 365)
        max_d = 1.0 - (daily_wacc ** (n_days - avg_curr_days))
        opt_d = 1.0 - (daily_wacc ** (n_days - d_not))

        # DISPLAY
        st.divider()
        col_res1, col_res2 = st.columns(2)
        col_res1.write(f"Free Capital: **€ {free_cap:.2f}**")
        col_res1.write(f"Profit from Extra Sales: **€ {prof_extra:.2f}**")
        col_res2.write(f"Profit from Free Capital: **€ {prof_free_cap:.2f}**")
        col_res2.write(f"Discount Cost: **€ {cost_disc:.2f}**")
        
        st.subheader(f"NPV: € {final_npv:.2f}")
        st.write(f"**Maximum Discount:** {max_d:.2%}")
        st.write(f"**Optimum Discount:** {opt_d:.2%}")

    if st.button("Back to Hub"):
        st.session_state.selected_tool = None
        st.rerun()
