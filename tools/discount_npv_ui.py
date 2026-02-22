def show_discount_npv_ui():
    st.header("💳 Cash Discount – Strategic NPV Analysis")
    st.info("Analyze the trade-off between margin loss (discount) and cash acceleration.")

    # 1. FETCH DATA FROM ENGINE & SESSION STATE
    metrics = compute_core_metrics()
    base_sales = metrics['revenue']
    # COGS = Συνολικό Μεταβλητό Κόστος (Variable Cost * Volume)
    base_cogs = st.session_state.get('variable_cost', 0.0) * st.session_state.get('volume', 0)
    # WACC = Interest Rate + Risk Premium (5%)
    base_wacc = st.session_state.get('interest_rate', 0.10) + 0.05

    # 2. PARAMETERS IN COLUMNS
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📈 Core Financials")
        current_sales = st.number_input("Current Annual Sales (€)", value=float(base_sales))
        extra_sales = st.number_input("Extra Sales from Discount (€)", value=current_sales * 0.1)
        cogs = st.number_input("Total COGS (€)", value=float(base_cogs))
        wacc = st.number_input("Cost of Capital / WACC (%)", value=float(base_wacc * 100)) / 100

    with col2:
        st.subheader("🎯 Discount Strategy")
        discount_trial = st.number_input("Proposed Discount (%)", value=2.0) / 100
        prc_clients_take_disc = st.number_input("% Revenue Expected to Take Discount", value=40.0) / 100
        new_days_cash_payment = st.number_input("Target Discount Days (e.g., 10 days)", value=10)
        avg_days_pay_suppliers = st.number_input("Supplier Payment Days", value=30)

    st.divider()
    
    # 3. RECEIVABLE SEGMENTATION
    st.subheader("📊 Current Receivable Segmentation")
    s1, s2, s3 = st.columns(3)
    fast_pct = s1.number_input("Fast Payers (%)", value=30.0) / 100
    fast_dso = s1.number_input("Fast DSO (days)", value=45)
    med_pct = s2.number_input("Med Payers (%)", value=40.0) / 100
    med_dso = s2.number_input("Med DSO (days)", value=75)
    slow_pct = s3.number_input("Slow Payers (%)", value=30.0) / 100
    slow_dso = s3.number_input("Slow DSO (days)", value=120)

    allocation_mode = st.radio("Targeting Logic", ["Proportional", "Slow Payers First", "Fast Payers First"], horizontal=True)

    if st.button("🚀 Calculate Policy Impact", use_container_width=True):
        if abs((fast_pct + med_pct + slow_pct) - 1.0) > 0.01:
            st.error("Segmentation must sum to 100%.")
            return

        # Segmentation Logic
        segments = [{"pct": fast_pct, "dso": fast_dso}, {"pct": med_pct, "dso": med_dso}, {"pct": slow_pct, "dso": slow_dso}]
        if allocation_mode == "Slow Payers First": segments.sort(key=lambda x: x["dso"], reverse=True)
        elif allocation_mode == "Fast Payers First": segments.sort(key=lambda x: x["dso"])

        remaining = prc_clients_take_disc
        weighted_take_dso = 0
        weighted_no_take_dso = 0
        for seg in segments:
            take = min(seg["pct"], remaining)
            weighted_take_dso += take * seg["dso"]
            weighted_no_take_dso += (seg["pct"] - take) * seg["dso"]
            remaining -= take

        eff_take = weighted_take_dso / prc_clients_take_disc if prc_clients_take_disc > 0 else 0
        eff_no_take = weighted_no_take_dso / (1 - prc_clients_take_disc) if prc_clients_take_disc < 1 else 0

        # CALL CALCULATION ENGINE
        res = calculate_discount_npv(current_sales, extra_sales, discount_trial, prc_clients_take_disc, 
                                     eff_take, eff_no_take, new_days_cash_payment, cogs, wacc, avg_days_pay_suppliers)

        # 4. RESULTS DISPLAY
        st.divider()
        m1, m2, m3 = st.columns(3)
        m1.metric("DSO Shift", f"{res['avg_current_collection_days']} → {res['new_avg_collection_period']}", 
                  f"{res['new_avg_collection_period'] - res['avg_current_collection_days']:.1f} days")
        m2.metric("Cash Released", f"{res['free_capital']:,.2f} €")
        
        delta_label = "Value Creation" if res['npv'] > 0 else "Value Loss"
        m3.metric("NPV Outcome", f"{res['npv']:,.2f} €", delta=delta_label, 
                  delta_color="normal" if res['npv'] > 0 else "inverse")

        # 5. VISUAL BREAKDOWN (Gains vs Costs)
        st.subheader("💎 Economic Breakdown")
        b1, b2 = st.columns(2)
        with b1:
            st.write("#### Positive Impact")
            st.write(f"✅ Yield from Released Capital: **{res['profit_from_free_capital']:,.2f} €**")
            st.write(f"✅ Margin from Incremental Sales: **{res['profit_from_extra_sales']:,.2f} €**")
        with b2:
            st.write("#### Negative Impact")
            st.error(f"❌ Direct Cost of Discount: **{res['discount_cost']:,.2f} €**")
            st.write(f"📊 Net Economic Value: **{res['npv']:,.2f} €**")

        st.divider()

        # 6. THRESHOLD & OPTIMUM ANALYSIS
        
        st.subheader("🧠 Strategic Decision Thresholds")
        
        df_thresholds = pd.DataFrame({
            "Indicator": ["Maximum Sustainable Discount", "Mathematically Optimal Discount"],
            "Description": ["The 'Break-even' discount. Beyond this, you lose value.", "The discount that maximizes the Net Present Value."],
            "Value": [f"{res['max_discount']}%", f"{res['optimum_discount']}%"]
        })
        st.table(df_thresholds)
        
        if res['npv'] > 0:
            st.success(f"🏆 **Verdict: APPROVE.** The strategic benefit of cash acceleration and volume growth ({res['profit_from_free_capital'] + res['profit_from_extra_sales']:,.2f} €) outweighs the discount cost ({res['discount_cost']:,.2f} €).")
        else:
            st.error(f"🚨 **Verdict: REJECT.** This discount policy is too aggressive. You are paying more for liquidity than it's worth to your cost of capital structure.")
