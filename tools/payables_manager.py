import streamlit as st
from core.sync import sync_global_state

def show_payables_manager():
    st.header("🤝 Payables Strategic Control")
    st.info("Using Corporate WACC as the hurdle rate to optimize payment strategies and cash retention.")
    
    # 1. FETCH GLOBAL DATA
    metrics = sync_global_state()
    s = st.session_state
    
    q = s.get('volume', 0)
    vc = s.get('variable_cost', 0.0)
    sales_val = s.get('sales', 1000.0) # current_sales από εικόνα
    
    # Δεδομένα από engine/state
    annual_purchases = q * vc
    current_ap_days = s.get('ap_days', 30)
    hurdle_rate = metrics.get('wacc', 0.20) # WACC 20% από εικόνα
    
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
        st.subheader("NPV Strategic Evaluator")
        
        # Inputs ΑΚΡΙΒΩΣ από την εικόνα σου
        col1, col2, col3 = st.columns(3)
        extra_sales = col1.number_input("extra_sales", value=250.0)
        cogs = col2.number_input("COGS", value=800.0)
        discount_trial = col3.number_input("discount_trial (%)", value=2.0) / 100

        # Days inputs
        d1, d2, d3 = st.columns(3)
        days_take_disc = d1.number_input("days_take_disc", value=60)
        days_not_take_disc = d2.number_input("days_not_take_disc", value=120)
        new_days_limit = d3.number_input("new_days_limit", value=10)
        
        prc_take = st.slider("% Clients Taking Discount", 0.0, 1.0, 0.40)

        # --- ΥΠΟΛΟΓΙΣΜΟΙ NPV ΑΚΡΙΒΩΣ ΟΠΩΣ ΣΤΗΝ ΕΙΚΟΝΑ ---
        # 1. Current State
        avg_collection_days = (days_take_disc * prc_take) + (days_not_take_disc * (1 - prc_take))
        current_receivables = (sales_val * avg_collection_days) / 365
        
        # 2. New Policy State
        total_sales = sales_val + extra_sales
        prcnt_new_policy = ((sales_val * prc_take) + extra_sales) / total_sales
        new_avg_period = (prcnt_new_policy * new_days_limit) + ((1 - prcnt_new_policy) * days_not_take_disc)
        new_receivables = (total_sales * new_avg_period) / 365
        
        # 3. NPV Components
        free_capital = current_receivables - new_receivables
        profit_extra_sales = extra_sales * (1 - (cogs / sales_val))
        profit_free_cap = free_capital * hurdle_rate
        cost_of_discount = total_sales * prcnt_new_policy * discount_trial
        
        # Τελικό NPV
        final_npv = profit_extra_sales + profit_free_cap - cost_of_discount

        st.divider()
        st.write(f"Profit from Free Capital: **€{profit_free_cap:,.2f}**")
        st.write(f"Profit from Extra Sales: **€{profit_extra_sales:,.2f}**")
        st.write(f"Cost of Discount: **€{cost_of_discount:,.2f}**")
        
        if final_npv > 0:
            st.success(f"✅ **Verdict: ACCEPT STRATEGY (NPV: €{final_npv:,.2f})**")
        else:
            st.error(f"🚨 **Verdict: REJECT STRATEGY (NPV: €{final_npv:,.2f})**")
            
        # Thresholds
        max_disc = (profit_extra_sales + profit_free_cap) / (total_sales * prcnt_new_policy)
        st.info(f"Maximum Discount for Break-even: **{max_disc:.2%}**")

    st.divider()
    if st.button("Sync Target Days to Global Strategy"):
        st.session_state.ap_days = new_ap_days
        st.success(f"Global Days updated to {new_ap_days}.")

    if st.button("Back to Library Hub"):
        st.session_state.selected_tool = None
        st.rerun()
