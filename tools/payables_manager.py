import streamlit as st
from core.engine import compute_core_metrics

def show_payables_manager():
    st.header("🤝 Payables Strategic Control")
    st.info("Using Corporate WACC as the hurdle rate for supplier payments.")
    
    metrics = compute_core_metrics()
    q = st.session_state.get('volume', 0)
    vc = st.session_state.get('variable_cost', 0.0)
    annual_purchases = q * vc
    
    current_ap_days = st.session_state.get('payables_days', 30)
    # ΑΛΛΑΓΗ: Χρήση WACC αντί για Interest Rate
    hurdle_rate = metrics['wacc'] 
    
    st.write(f"**🔗 Hurdle Rate Linked (WACC):** {hurdle_rate:.1%}")

    tab1, tab2 = st.tabs(["💰 Cash Flow Impact", "⚖️ Discount vs. Cost of Capital"])

    with tab1:
        new_ap_days = st.slider("Target Payment Terms (Days)", 0, 150, int(current_ap_days), key="ap_slider")
        cash_impact = ((new_ap_days - current_ap_days) / 365) * annual_purchases
        # Benefit calculated on WACC
        value_benefit = cash_impact * hurdle_rate
        
        st.metric("Net Cash Impact", f"€ {cash_impact:,.2f}")
        st.metric("Annual Value Benefit", f"€ {max(0.0, value_benefit):,.2f}")

    with tab2:
        st.subheader("Early Payment Discount (EPD) Evaluator")
        c1, c2, c3 = st.columns(3)
        epd_pct = c1.number_input("Discount Offered (%)", value=2.0, key="epd_p") / 100
        epd_days = c2.number_input("Paid within (Days)", value=10, key="epd_d")
        net_days = c3.number_input("Otherwise Net (Days)", value=30, key="epd_n")

        if net_days > epd_days:
            implied_rate = (epd_pct / (1 - epd_pct)) * (365 / (net_days - epd_days))
            st.write(f"EPD Implied Annual Rate: **{implied_rate:.1%}**")
            st.write(f"Corporate WACC: **{hurdle_rate:.1%}**")

            if implied_rate > hurdle_rate:
                st.success("✅ **Verdict: TAKE THE DISCOUNT.** The discount is more profitable than the cost of capital.")
            else:
                st.error("🚨 **Verdict: DELAY PAYMENT.** Better to keep the cash as its internal value (WACC) is higher.")
