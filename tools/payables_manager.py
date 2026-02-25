import streamlit as st
import pandas as pd
from core.sync import sync_global_state

def show_payables_manager():
    st.header("🤝 Payables Strategic Control")
    st.info("Analytical view of supplier terms and their impact on corporate WACC.")
    
    # 1. FETCH GLOBAL DATA
    metrics = sync_global_state()
    s = st.session_state
    
    q = s.get('volume', 0)
    vc = s.get('variable_cost', 0.0)
    annual_purchases = q * vc
    current_ap_days = s.get('ap_days', 30.0)
    hurdle_rate = metrics.get('wacc', 0.15)
    
    st.write(f"**🔗 Annual Purchases Value:** € {annual_purchases:,.2f} | **WACC:** {hurdle_rate:.1%}")
    st.divider()

    # 2. FULL ANALYTICAL VIEW (Ο παλαιός τρόπος: Όλα στην οθόνη)
    st.subheader("1. Payment Terms & Cash Impact")
    
    # Στήλες για άμεση εισαγωγή και σύγκριση
    col_main = st.columns([2, 2, 2])
    
    with col_main[0]:
        st.markdown("**Current State**")
        st.write(f"Days: {current_ap_days}")
        current_capital_locked = (current_ap_days / 365) * annual_purchases
        st.write(f"Accounts Payable: € {current_capital_locked:,.2f}")

    with col_main[1]:
        st.markdown("**Target Strategy**")
        new_ap_days = st.number_input("Set Target Days", min_value=0, max_value=200, value=int(current_ap_days))
        new_capital_locked = (new_ap_days / 365) * annual_purchases
        st.write(f"Target AP: € {new_capital_locked:,.2f}")

    with col_main[2]:
        st.markdown("**Net Financial Impact**")
        cash_impact = new_capital_locked - current_capital_locked
        benefit = cash_impact * hurdle_rate
        st.metric("Cash Released", f"€ {cash_impact:,.2f}", delta=f"{new_ap_days - current_ap_days} Days")
        st.metric("Annual Value Benefit", f"€ {max(0.0, benefit):,.2f}")

    st.divider()

    # 3. DISCOUNT ANALYSIS (Ορατό ταυτόχρονα)
    st.subheader("2. Early Payment Discount (EPD) Evaluator")
    
    c_disc = st.columns(3)
    epd_pct = c_disc[0].number_input("Discount % (e.g. 2%)", value=2.0) / 100
    epd_days = c_disc[1].number_input("Discount Period (Days)", value=10)
    net_days = c_disc[2].number_input("Full Term (Days)", value=30)

    if net_days > epd_days:
        # Formula: (Discount / (1-Discount)) * (365 / (Net - Discount Days))
        implied_rate = (epd_pct / (1 - epd_pct)) * (365 / (net_days - epd_days))
        
        # Cold Comparison
        st.write(f"💡 **Implied Annual Return:** {implied_rate:.1%} vs **Corporate WACC:** {hurdle_rate:.1%}")
        
        if implied_rate > hurdle_rate:
            st.success(f"✅ **Strategic Verdict:** TAKE THE DISCOUNT. Profitability increases by {implied_rate - hurdle_rate:.1%}")
        else:
            st.error(f"🚨 **Strategic Verdict:** DELAY PAYMENT. Cost of early payment exceeds WACC.")
    
    st.divider()

    # 4. ACTIONS & SYNC
    c_act = st.columns(2)
    if c_act[0].button("💾 Sync Target to Global Model", use_container_width=True):
        st.session_state.ap_days = float(new_ap_days)
        st.success("Global Model Updated.")

    if c_act[1].button("⬅️ Exit to Library", use_container_width=True):
        st.session_state.selected_tool = None
        st.rerun()
