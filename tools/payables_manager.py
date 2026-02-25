import streamlit as st
from core.engine import compute_core_metrics

def show_payables_manager():
    st.header("🤝 Payables Strategic Control")
    st.info("Using Corporate WACC as the hurdle rate to optimize supplier payment strategies and cash retention.")

    # -------------------------------------------------
    # 1. FETCH GLOBAL DATA (Single Source of Truth)
    # -------------------------------------------------
    metrics = compute_core_metrics()
    
    q = st.session_state.get('volume', 0)
    vc = st.session_state.get('variable_cost', 0.0)
    current_ap_days = st.session_state.get('ap_days', 30)

    # Estimated annual purchases (proxy via Variable Cost)
    annual_purchases = q * vc

    # Corporate hurdle rate
    hurdle_rate = metrics.get('wacc', 0.10)

    st.write(f"**🔗 Opportunity Cost (WACC):** {hurdle_rate:.2%}")

    tab1, tab2 = st.tabs(["💰 Cash Flow Impact", "⚖️ Discount vs. Cost of Capital"])

    # =================================================
    # TAB 1 — Liquidity Impact
    # =================================================
    with tab1:
        st.subheader("Liquidity Optimization")

        new_ap_days = st.slider(
            "Target Payment Terms (Days)",
            0, 150,
            int(current_ap_days),
            key="ap_slider"
        )

        # Cash released or trapped
        cash_impact = ((new_ap_days - current_ap_days) / 365) * annual_purchases

        # Value creation using WACC
        value_benefit = cash_impact * hurdle_rate

        c1, c2 = st.columns(2)

        c1.metric(
            "Net Cash Impact",
            f"€ {cash_impact:,.2f}",
            delta=f"{new_ap_days - current_ap_days} Days Shift"
        )

        c2.metric(
            "Annual Value Effect",
            f"€ {value_benefit:,.2f}"
        )

        if new_ap_days > current_ap_days:
            st.success("Extended supplier credit increases retained liquidity.")
        elif new_ap_days < current_ap_days:
            st.warning("Shorter payment terms reduce available working capital.")

    # =================================================
    # TAB 2 — Early Payment Discount Evaluator
    # =================================================
    with tab2:
        st.subheader("Early Payment Discount (EPD) Evaluator")

        col1, col2, col3 = st.columns(3)

        epd_pct = col1.number_input(
            "Discount Offered (%)",
            value=2.0,
            min_value=0.0,
            max_value=15.0,
            step=0.1,
            key="epd_pct"
        ) / 100

        epd_days = col2.number_input(
            "Discount Period (Days)",
            value=10,
            key="epd_days"
        )

        net_days = col3.number_input(
            "Full Term (Days)",
            value=30,
            key="net_days"
        )

        if net_days > epd_days and epd_pct > 0:

            # Implied annualized return formula
            implied_rate = (
                (epd_pct / (1 - epd_pct)) *
                (365 / (net_days - epd_days))
            )

            st.divider()
            st.write(f"**Implied Annual Return from Discount:** {implied_rate:.2%}")
            st.write(f"**Your Internal Cost of Capital (WACC):** {hurdle_rate:.2%}")

            if implied_rate > hurdle_rate:
                st.success("✅ TAKE THE DISCOUNT — return exceeds cost of capital.")
            else:
                st.error("🚨 DELAY PAYMENT — retaining cash is more valuable.")

        else:
            st.info("Enter valid discount structure to evaluate.")

    # -------------------------------------------------
    # GLOBAL SYNC
    # -------------------------------------------------
    st.divider()

    if st.button("Sync Target Days to Global Strategy"):
        st.session_state.ap_days = new_ap_days
        st.success(f"Global Payables Days updated to {new_ap_days} days.")
