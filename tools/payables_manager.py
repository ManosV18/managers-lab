import streamlit as st
import pandas as pd
from core.engine import compute_core_metrics

def show_payables_manager():
    st.header("🤝 Payables Strategic Control")
    st.info("Optimize supplier payment terms and evaluate Early Payment Discounts (EPD).")

    # 1. SYNC WITH SHARED CORE
    metrics = compute_core_metrics()
    q = st.session_state.get('volume', 0)
    vc = st.session_state.get('variable_cost', 0.0)
    annual_purchases = q * vc
    
    current_ap_days = st.session_state.get('payables_days', 30)
    cost_of_capital = st.session_state.get('interest_rate', 0.08)
    
    st.write(f"**🔗 Core Baseline Linked:** Annual Purchases: **€ {annual_purchases:,.2f}** | WACC: **{cost_of_capital:.1%}**")

    tab1, tab2 = st.tabs(["💰 Cash Flow Impact", "⚖️ Discount vs. WACC"])

    with tab1:
        st.subheader("Working Capital Simulation")
        col_a, col_b = st.columns(2)
        
        with col_a:
            st.write(f"**Current Terms:** {current_ap_days} Days")
            current_ap_value = (current_ap_days / 365) * annual_purchases
            st.metric("Supplier Financing", f"€ {current_ap_value:,.2f}")

        with col_b:
            new_ap_days = st.slider("Target Payment Terms (Days)", 0, 150, int(current_ap_days))
            new_ap_value = (new_ap_days / 365) * annual_purchases
            st.metric("New Financing Level", f"€ {new_ap_value:,.2f}")

        cash_impact = new_ap_value - current_ap_value
        interest_benefit = cash_impact * cost_of_capital

        st.divider()
        res1, res2 = st.columns(2)
        res1.metric("Net Cash Impact", f"€ {cash_impact:,.2f}", 
                   delta="Inflow" if cash_impact >= 0 else "Outflow")
        res2.metric("Annual Interest Savings", f"€ {max(0.0, interest_benefit):,.2f}")

    with tab2:
        st.subheader("Early Payment Discount (EPD) Evaluator")
        st.write("Compare a supplier's discount offer against your cost of capital.")
        
        
        
        c1, c2, c3 = st.columns(3)
        epd_pct = c1.number_input("Discount Offered (%)", value=2.0, step=0.5) / 100
        epd_days = c2.number_input("Paid within (Days)", value=10)
        net_days = c3.number_input("Otherwise Net (Days)", value=30)

        # Formula: (Discount % / (1 - Discount %)) * (365 / (Net Days - Discount Days))
        if net_days > epd_days:
            implied_ann_rate = (epd_pct / (1 - epd_pct)) * (365 / (net_days - epd_days))
            
            st.divider()
            st.write(f"**EPD Implied Annual Interest Rate:** {implied_ann_rate:.1%}")
            st.write(f"**Your Corporate WACC:** {cost_of_capital:.1%}")

            if implied_ann_rate > cost_of_capital:
                st.success("✅ **Verdict: TAKE THE DISCOUNT.** Paying early is cheaper than using your own capital.")
            else:
                st.error("🚨 **Verdict: DECLINE & DELAY.** Keeping the cash is more valuable than the discount.")
        else:
            st.warning("Net days must be greater than discount days.")

    if st.button("🔄 Sync Target Days to Global Baseline", use_container_width=True):
        st.session_state.payables_days = new_ap_days
        st.success(f"Global AP Days updated to {new_ap_days}.")
