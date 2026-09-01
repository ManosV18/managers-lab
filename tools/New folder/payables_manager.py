import streamlit as st

def calculate_supplier_credit_gain(SupplierCreditDays, Discount, CashPrc, CurrentSales, UnitPrice, TotalUnitCost, InterestRateOnDebt):
    # Όλα τα ποσοστά μπαίνουν ως decimals (0-1)
    average_cost_ratio = TotalUnitCost / UnitPrice if UnitPrice > 0 else 0

    # 1. Κέρδος από την έκπτωση
    discount_gain = CurrentSales * Discount * CashPrc

    # 2. Κόστος ευκαιρίας — χάνεις δωρεάν πίστωση προμηθευτή
    credit_benefit_lost = (
        (CurrentSales / (365 / SupplierCreditDays))
        * average_cost_ratio
        * CashPrc
        * InterestRateOnDebt
    )

    net_gain = discount_gain - credit_benefit_lost
    return discount_gain, credit_benefit_lost, net_gain


def show_payables_manager():
    st.header("🤝 Supplier Credit Analysis")
    st.info("Evaluate whether paying suppliers early for discounts creates more value "
            "than preserving supplier credit."
    )

    s = st.session_state
    m = s.get("metrics", {})

    # 1. INPUT PARAMETERS
    st.subheader("1. Credit & Financial Terms")
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("**Supplier Payment Terms**")
        SupplierCreditDays = st.number_input("📆 Credit Period (Days)", min_value=1, value=int(s.get('ap_days', 45)))
        Discount_pct       = st.number_input("💸 Early Payment Discount (%)", min_value=0.0, value=2.0)
        CashPrc_pct        = st.slider("% of Purchases Eligible for Discount", 0, 100, 50)

    with col2:
        st.markdown("**Internal Economics**")
        CurrentSales        = st.number_input("💰 Annual Supplier Spend ($)",
                                              min_value=0, value=int(m.get('revenue', 1800000)))
        InterestRateOnDebt_pct = st.number_input("🏦 Cost of Cash (%)",
                                                  min_value=0.0,
                                                  value=float(s.get('wacc_locked', 15.0)))

    # Convert to decimals for calculation
    unit_p   = float(s.get('price', 150.0))
    unit_c   = float(s.get('variable_cost', 100.0))
    Discount = Discount_pct / 100
    CashPrc  = CashPrc_pct / 100
    InterestRateOnDebt = InterestRateOnDebt_pct / 100

    discount_gain, credit_cost, net_gain = calculate_supplier_credit_gain(
        SupplierCreditDays, Discount, CashPrc,
        CurrentSales, unit_p, unit_c, InterestRateOnDebt
    )

    # 2. RESULTS DASHBOARD
    st.divider()
    st.subheader("2. Economic Impact")

    m1, m2, m3 = st.columns(3)
    m1.metric("Early Payment Benefit",   f"${discount_gain:,.0f}")
    m2.metric("Cost of Using Cash Early",  f"-${credit_cost:,.0f}",
              help="Interest cost of using your own cash instead of the supplier's free credit.")
    m3.metric("Net Economic Benefit",  f"${net_gain:,.0f}",
              delta=f"${net_gain:,.0f}",
              delta_color="normal" if net_gain >= 0 else "inverse")

    # 3. STRATEGIC ASSESSMENT
    st.subheader("💡 Supplier Payment Assessment")

    if net_gain > 0:
        st.success(
            f"""
    ### Cash Payment Creates Economic Value

    **Purchases Using Early Payment Discount:** {CashPrc_pct:.0f}%

    **Supplier Credit Period:** {SupplierCreditDays} days

    **Estimated Net Economic Benefit:** ${net_gain:,.0f}

    Based on your current assumptions, accepting the supplier's early payment discount creates greater economic value than preserving supplier credit.

    The estimated benefit exceeds the financing value of keeping the supplier credit outstanding.
    """
        )
    else:
        st.error(
            f"""
    ### Supplier Credit Creates Greater Economic Value

    **Purchases Using Early Payment Discount:** {CashPrc_pct:.0f}%

    **Supplier Credit Period:** {SupplierCreditDays} days

    **Estimated Economic Disadvantage of Paying Early:** ${abs(net_gain):,.0f}

    Based on your current assumptions, retaining supplier credit creates greater economic value than paying early to obtain the discount.

    The financing benefit of the supplier's interest-free credit exceeds the value of the discount offered.
    """
        )
    
    st.divider()
    if st.button("⬅️ Back to Hub", use_container_width=True):
        st.session_state.flow_step = "home"
        st.session_state.selected_tool = None
        st.rerun()

