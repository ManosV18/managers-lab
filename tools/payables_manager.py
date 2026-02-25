import streamlit as st
from core.sync import sync_global_state  # Χρήση του sync για να αποφύγουμε το σφάλμα

def show_payables_manager():
    st.header("🤝 Payables Strategic Control")
    st.info("Using Corporate WACC as the hurdle rate to optimize supplier payment strategies and cash retention.")
    
    # 1. FETCH GLOBAL DATA
    # Αντικατάσταση του compute_core_metrics() με sync_global_state() για σταθερότητα
    metrics = sync_global_state()
    q = st.session_state.get('volume', 0)
    vc = st.session_state.get('variable_cost', 0.0)
    
    # Annual purchases estimated based on Variable Cost
    annual_purchases = q * vc
    current_ap_days = st.session_state.get('ap_days', 30) # Χρήση του ap_days όπως στην engine
    
    # Using WACC as the opportunity cost of cash
    hurdle_rate = metrics.get('wacc', 0.15) 
    
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
        
        col1, col2, col3 = st.columns(3)
        epd_pct = col1.number_input("Discount Offered (%)", value=2.0, min_value=0.0, max_value=10.0, step=0.1, key="epd_p") / 100
        epd_days = col2.number_input("Discount Period (Days)", value=10, key="epd_d")
        net_days = col3.number_input("Full Term (Days)", value=30, key="epd_n")

        if net_days > epd_days:
            # Formula: (Discount / (1-Discount)) * (365 / (Net - Discount Days))
            implied_rate = (epd_pct / (1 - epd_pct)) * (365 / (net_days - epd_days))
            
            st.divider()
            st.write(f"Implied Annual Return from Discount: **{implied_rate:.1%}**")
            st.write(f"Your Internal Cost of Capital (WACC): **{hurdle_rate:.1%}**")

            if implied_rate > hurdle_rate:
                st.success("✅ **Verdict: TAKE THE DISCOUNT.** The discount rate is higher than your cost of capital.")
            else:
                st.error("🚨 **Verdict: DELAY PAYMENT.** It is more profitable to keep the cash until the final due date.")

    st.divider()
    
    # NAVIGATION & SYNC
    col_nav1, col_nav2 = st.columns(2)
    with col_nav1:
        if st.button("Sync Target Days to Global Strategy"):
            st.session_state.ap_days = new_ap_days
            st.success(f"Global Payables Days updated to {new_ap_days} days.")
    
    with col_nav2:
        if st.button("Back to Library Hub"):
            st.session_state.selected_tool = None
            st.rerun()
