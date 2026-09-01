import streamlit as st
import plotly.graph_objects as go

def show_monthly_survival():
    s = st.session_state

    st.header("📅 Monthly Cash Coverage Analysis")
    st.info("Evaluate whether this month's expected cash inflows are sufficient to cover this month's cash obligations.")

    # --- BASELINE FROM HOME (CONVERTED TO MONTHLY) ---
    b_price          = float(s.get("price", 150.0))
    b_vc             = float(s.get("variable_cost", 100.0))
    b_monthly_volume = float(s.get("volume", 12000)) / 12
    b_monthly_fc     = float(s.get("fixed_cost", 450000.0)) / 12
    b_monthly_debt   = float(s.get("annual_debt_service", 70000.0)) / 12

    # --- SEASONALITY & CASH COLLECTION SETTINGS ---
    st.subheader("💰 Monthly Cash Inflows")
    col_c1, col_c2 = st.columns(2)

    with col_c1:
        season_factor = st.slider(
            "Monthly Sales Level (100% = Average Month)",
            min_value=30, max_value=250, value=100, step=5,
            help="150% = Strong month, 70% = Weak month."
        )
        cash_collection_pct = st.slider(
            "Cash Collected This Month (% of Current Sales)",
            0, 100, 20,
            help="E.g., 20% upfront/, 80% on credit to be collected later."
        )

    with col_c2:
        past_collections = st.number_input(
            "Collections from Previous Invoices ($)",
            value=0.0,
            help="Money from previous months' sales arriving in your bank THIS month."
        )
        st.info(
            f"This month's  = {cash_collection_pct}% of today's sales "
            f"+ ${past_collections:,.0f} from past invoices."
        )

    multiplier = season_factor / 100

    # --- MONTHLY CONTROLS ---
    st.subheader("🕹️ Monthly Controls")
    c1, c2, c3 = st.columns(3)

    with c1:
        sim_price = st.number_input("Unit Price ($)", value=b_price)
        sim_vc    = st.number_input("Variable Cost ($)", value=b_vc)

    with c2:
        sim_fc   = st.number_input("Monthly Fixed Costs ($)", value=b_monthly_fc)
        sim_debt = st.number_input("Monthly Debt Service ($)", value=b_monthly_debt)

    with c3:
        sim_volume = st.number_input(
            "Forecasted Volume for this Month",
            value=b_monthly_volume * multiplier
        )

    # --- CALCULATIONS ---
    # What you must pay this month
    total_cash_outflow = sim_fc + sim_debt

    # What cash comes in this month
    current_sales_cash_in = (sim_volume * sim_price) * (cash_collection_pct / 100)
    total_monthly_cash_in = current_sales_cash_in + past_collections

    # How many units needed to cover bills with cash collected now
    cash_contribution_per_unit = (sim_price * (cash_collection_pct / 100)) - sim_vc

    if cash_contribution_per_unit <= 0:
        cash_bep = None
    else:
        cash_bep = (total_cash_outflow - past_collections) / cash_contribution_per_unit

    # Surplus or deficit after paying bills
    cash_gap = total_monthly_cash_in - total_cash_outflow

    # --- RESULTS DASHBOARD ---
    st.divider()
    res1, res2, res3 = st.columns(3)

    res1.metric("Cash Outflow", f"${total_cash_outflow:,.0f}")
    res2.metric("Cash Inflows",       f"${total_monthly_cash_in:,.0f}")

    delta_color = "normal" if cash_gap >= 0 else "inverse"
    res3.metric("Monthly Cash Balance", f"${cash_gap:,.0f}",
                delta="Surplus" if cash_gap >= 0 else "Deficit",
                delta_color=delta_color)

    # --- VISUALIZATION ---
    if cash_bep and cash_bep > 0:
        fig = go.Figure()
        fig.add_bar(
            name="Units Needed (Cash Basis)",
            x=["Monthly Target"], y=[cash_bep],
            marker_color="#ef4444"
        )
        fig.add_bar(
            name="Forecasted Units",
            x=["Monthly Target"], y=[sim_volume],
            marker_color="#3b82f6"
        )
        fig.update_layout(
            barmode="group", height=350, template="plotly_dark",
            margin=dict(t=30, b=20), yaxis_title="Units"
        )
        st.plotly_chart(fig, use_container_width=True)

    # --- VERDICT ---
    st.subheader("💡 Cash Position Assessment")

    if total_monthly_cash_in < total_cash_outflow:
        st.error(
            f"""
    ### Monthly Cash Shortfall

    **Expected Cash Inflows:** ${total_monthly_cash_in:,.0f}

    **Cash Obligations:** ${total_cash_outflow:,.0f}

    **Projected Cash Shortfall:** ${abs(cash_gap):,.0f}

    *Includes ${past_collections:,.0f} collected from previous invoices.*
    """
        )
    else:
        st.success(
            f"""
    ### Cash Obligations Covered

    **Expected Cash Inflows:** ${total_monthly_cash_in:,.0f}

    **Cash Obligations:** ${total_cash_outflow:,.0f}

    **Projected Cash Surplus:** ${cash_gap:,.0f}
    """
        )
    
    # --- WHAT SHOULD I DO NEXT? ---
    with st.expander("🔍 Decision Options"):
        if cash_bep is None:
            st.error(
                f"""
            ### Negative Cash Contribution per Unit

            **Cash Collected per Unit:** ${sim_price * cash_collection_pct / 100:,.0f}

            **Variable Cost per Unit:** ${sim_vc:,.0f}

            **Cash Contribution per Unit:** Negative

            Each additional unit sold reduces available cash because the cash collected immediately is lower than the variable cost required to produce or deliver the unit.

            ### Recommended Actions

            - Increase the percentage of cash collected at the time of sale.
            - Reduce variable cost per unit.
            - Improve customer payment terms before increasing sales volume.
            """
            )
        else:
            gap_units = cash_bep - sim_volume
            if gap_units > 0:
                extra_revenue = gap_units * sim_price
                st.markdown(
                    f"You need {gap_units:,.0f} more units this month to cover your bills in cash. "
                    f"That is ${extra_revenue:,.0f} in additional revenue."
                )
                st.markdown("Options to close the gap:")
                st.markdown(
                    f"- Chase past invoices: every ${past_collections + sim_price:,.0f} collected "
                    f"from old invoices replaces one unit of sales needed this month."
                )
                if cash_collection_pct < 50:
                    improvement = (sim_volume * sim_price * 0.1)
                    st.markdown(
                        f"- Increase cash collection rate by 10%: "
                        f"that unlocks ${improvement:,.0f} in immediate cash."
                    )
                st.markdown(
                    f"- Defer non-critical fixed costs: "
                    f"pushing 10% of fixed costs (${sim_fc * 0.1:,.0f}) to next month "
                    f"reduces the gap immediately."
                )
            else:
                surplus_units = abs(gap_units)
                st.success(
                    f"You are {surplus_units:,.0f} units ahead of your cash break-even. "
                    f"You have a cash buffer this month. Net surplus: ${cash_gap:,.0f}"
                )

    st.divider()
    if st.button("⬅️ Back to Hub", use_container_width=True):
        st.session_state.flow_step = "home"
        st.session_state.selected_tool = None
        st.rerun()
