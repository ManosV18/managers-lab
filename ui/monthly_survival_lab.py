import streamlit as st
import plotly.graph_objects as go
from diagnostics.monthly_survival import calculate_monthly_survival


def render_monthly_survival_lab(baseline_state, projected_state=None):
    st.header("📅 Monthly Cash Coverage Analysis")
    st.info(
        "Evaluate whether this month's expected cash inflows are sufficient to cover "
        "this month's cash obligations based on your locked Baseline."
    )

    # --- CANONICAL BASELINE DEFAULT VALUES ---
    b_drivers = baseline_state.drivers
    b_capital = baseline_state.capital_structure

    b_price = float(b_drivers.price)
    b_vc = float(b_drivers.variable_cost_per_unit)
    b_monthly_volume = float(b_drivers.volume) / 12.0
    b_monthly_fc = float(b_drivers.fixed_opex) / 12.0
    b_monthly_debt = float(b_capital.annual_debt_service) / 12.0

    # --- SEASONALITY & CASH COLLECTION CONTROLS ---
    st.subheader("💰 Monthly Cash Inflows")
    col_c1, col_c2 = st.columns(2)

    with col_c1:
        season_factor = st.slider(
            "Monthly Sales Level (100% = Average Month)",
            min_value=30,
            max_value=250,
            value=100,
            step=5,
            help="150% = Strong month, 70% = Weak month.",
        )
        cash_collection_pct = st.slider(
            "Cash Collected This Month (% of Current Sales)",
            min_value=0,
            max_value=100,
            value=20,
            help="E.g., 20% upfront, 80% on credit to be collected later.",
        )

    with col_c2:
        past_collections = st.number_input(
            "Collections from Previous Invoices (€)",
            value=0.0,
            step=1000.0,
            help="Money from previous months' sales arriving in your bank THIS month.",
        )
        st.info(
            f"This month's cash in = {cash_collection_pct}% of today's sales "
            f"+ €{past_collections:,.0f} from past invoices."
        )

    multiplier = season_factor / 100.0

    # --- MONTHLY OPERATING CONTROLS ---
    st.subheader("🕹️ Monthly Controls")
    c1, c2, c3 = st.columns(3)

    with c1:
        sim_price = st.number_input("Unit Price (€)", value=b_price)
        sim_vc = st.number_input("Variable Cost (€)", value=b_vc)

    with c2:
        sim_fc = st.number_input("Monthly Fixed Costs (€)", value=b_monthly_fc)
        sim_debt = st.number_input("Monthly Debt Service (€)", value=b_monthly_debt)

    with c3:
        sim_volume = st.number_input(
            "Forecasted Volume for this Month",
            value=b_monthly_volume * multiplier,
        )

    # --- RUN DIAGNOSTIC LOGIC ---
    result = calculate_monthly_survival(
        baseline_state=baseline_state,
        projected_state=projected_state,
        season_factor=season_factor,
        cash_collection_pct=cash_collection_pct,
        past_collections=past_collections,
        sim_price=sim_price,
        sim_vc=sim_vc,
        sim_fc=sim_fc,
        sim_debt=sim_debt,
        sim_volume=sim_volume,
    )

    total_cash_outflow = result["total_cash_outflow"]
    total_monthly_cash_in = result["total_monthly_cash_in"]
    cash_gap = result["cash_gap"]
    cash_bep = result["cash_bep"]
    cash_contribution_per_unit = result["cash_contribution_per_unit"]

    # --- RESULTS DASHBOARD ---
    st.divider()
    res1, res2, res3 = st.columns(3)

    res1.metric("Cash Outflow", f"€{total_cash_outflow:,.0f}")
    res2.metric("Cash Inflows", f"€{total_monthly_cash_in:,.0f}")

    delta_color = "normal" if cash_gap >= 0 else "inverse"
    res3.metric(
        "Monthly Cash Balance",
        f"€{cash_gap:,.0f}",
        delta="Surplus" if cash_gap >= 0 else "Deficit",
        delta_color=delta_color,
    )

    # --- VISUALIZATION ---
    if cash_bep is not None and cash_bep > 0:
        fig = go.Figure()
        fig.add_bar(
            name="Units Needed (Cash Basis)",
            x=["Monthly Target"],
            y=[cash_bep],
            marker_color="#ef4444",
        )
        fig.add_bar(
            name="Forecasted Units",
            x=["Monthly Target"],
            y=[sim_volume],
            marker_color="#3b82f6",
        )
        fig.update_layout(
            barmode="group",
            height=350,
            template="plotly_dark",
            margin=dict(t=30, b=20),
            yaxis_title="Units",
        )
        st.plotly_chart(fig, use_container_width=True)

    # --- VERDICT ---
    st.subheader("💡 Cash Position Assessment")

    if total_monthly_cash_in < total_cash_outflow:
        st.error(
            f"""
            ### Monthly Cash Shortfall
            
            **Expected Cash Inflows:** €{total_monthly_cash_in:,.0f}  
            **Cash Obligations:** €{total_cash_outflow:,.0f}  
            **Projected Cash Shortfall:** €{abs(cash_gap):,.0f}  
            
            *Includes €{past_collections:,.0f} collected from previous invoices.*
            """
        )
    else:
        st.success(
            f"""
            ### Cash Obligations Covered
            
            **Expected Cash Inflows:** €{total_monthly_cash_in:,.0f}  
            **Cash Obligations:** €{total_cash_outflow:,.0f}  
            **Projected Cash Surplus:** €{cash_gap:,.0f}
            """
        )

    # --- Management Responses ---
    with st.expander("🔍 Management Responses"):
        if cash_bep is None:
            st.error(
                f"""
                ### Negative Cash Contribution per Unit
                
                **Cash Collected per Unit:** €{(sim_price * cash_collection_pct / 100.0):,.2f}  
                **Variable Cost per Unit:** €{sim_vc:,.2f}  
                **Cash Contribution per Unit:** Negative ({cash_contribution_per_unit:,.2f})  
                
                Each additional unit sold reduces available cash because the cash collected immediately 
                is lower than the variable cost required to deliver the unit.
                
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
                    f"You need **{gap_units:,.0f} more units** this month to cover your bills in cash. "
                    f"That represents **€{extra_revenue:,.0f}** in additional revenue."
                )
                st.markdown("##### Options to close the gap:")
                st.markdown(
                    f"- **Chase past invoices:** Every **€{past_collections + sim_price:,.0f}** "
                    "collected from old invoices replaces one unit of sales needed this month."
                )
                if cash_collection_pct < 50:
                    improvement = sim_volume * sim_price * 0.10
                    st.markdown(
                        f"- **Increase cash collection rate by 10%:** "
                        f"Unlocks **€{improvement:,.0f}** in immediate cash."
                    )
                st.markdown(
                    f"- **Defer non-critical fixed costs:** Pushing 10% of fixed costs "
                    f"(**€{sim_fc * 0.10:,.0f}**) to next month reduces the gap immediately."
                )
            else:
                surplus_units = abs(gap_units)
                st.success(
                    f"You are **{surplus_units:,.0f} units** ahead of your cash break-even. "
                    f"You have a net cash buffer of **€{cash_gap:,.0f}** this month."
                )
