import streamlit as st
import plotly.graph_objects as go
from core.engine import calculate_metrics

def show_growth_funding_needed():
    st.header("📈 Growth & Funding Strategy")
    st.caption("""
    Growth usually requires more than higher sales.

    This Decision Lab estimates whether future growth can be financed internally or whether additional external capital will be required.
    """)

    with st.expander("💡 What decision does this tool support?", expanded=True):
        st.markdown("""
    Growing companies often run out of cash before they run out of profit.

    This Decision Lab estimates how much additional funding will be required to support a chosen growth target.

    The objective is not to maximize growth, but to identify a sustainable growth rate that the business can finance.
    """)

    s = st.session_state
    m = s.get("metrics", {})

    if not s.get('baseline_locked', False):
        st.warning("🔒 Access Denied: Please lock your Baseline in Home to enable Growth Modeling.")
        return

    # 1. USE ENGINE NET PROFIT DIRECTLY
    current_sales     = float(m.get('revenue', 0.0))
    net_profit        = float(m.get('net_profit', 0.0))
    net_profit_margin = net_profit / current_sales if current_sales > 0 else 0

    st.caption(
        f"Current business performance: **${net_profit:,.0f}** net profit "
        f"({net_profit_margin:.2%} net margin)."
    )

    # 2. GROWTH SCENARIO INPUTS
    st.subheader("🚀 Growth Scenario")
    c_in1, c_in2 = st.columns(2)
    target_growth_pct = c_in1.slider("Planned Revenue Growth (%)", 0.0, 100.0, 20.0, key="afn_growth_sl") / 100
    retention_rate    = c_in2.slider("Earnings Retention (%)", 0, 100, 100, key="afn_retention_sl") / 100

    delta_sales     = current_sales * target_growth_pct
    new_total_sales = current_sales + delta_sales
    growth_volume   = float(s.get('volume', 12000)) * (1 + target_growth_pct)

    # 3. AFN FORMULA
    assets_ratio      = 0.65
    liabilities_ratio = 0.15

    required_assets   = assets_ratio * delta_sales
    spontaneous_liabs = liabilities_ratio * delta_sales
    internal_funding  = net_profit_margin * new_total_sales * retention_rate
    afn               = required_assets - spontaneous_liabs - internal_funding

    # 4. RESULTS
    st.divider()
    m1, m2, m3 = st.columns(3)
    m1.metric("Projected Revenue",      f"${new_total_sales:,.0f}")
    m2.metric("Internal Funding Capacity", f"${internal_funding:,.0f}")

    afn_val = max(0, afn)
    m3.metric("Additional Funding Required", f"${afn_val:,.0f}",
              delta="Capital Needed" if afn > 0 else "Self-Funded",
              delta_color="inverse" if afn > 0 else "normal")

    # ── WHY IS AFN POSITIVE/NEGATIVE? ─────────────────────
    with st.expander("🔍 Where does the funding gap come from?"):
        st.markdown(
            f"The AFN formula has three components:\n\n"
            f"• **Asset requirement:** Growing by {target_growth_pct:.0%} requires "
            f"**${required_assets:,.0f}** in new assets (at 65 cents per dollar of new revenue — "
            f"inventory, receivables, equipment).\n\n"
            f"• **Spontaneous financing:** Suppliers and accruals automatically cover "
            f"**${spontaneous_liabs:,.0f}** of that (15 cents per dollar).\n\n"
            f"• **Retained earnings:** Your retained profit covers **${internal_funding:,.0f}** "
            f"(net margin {net_profit_margin:.1%} × new sales × {retention_rate:.0%} retention).\n\n"
        )
        if afn > 0:
            st.error(
                f"The gap of **${afn:,.0f}** must come from external sources — "
                f"bank debt, equity raise, or asset sales. "
                f"If you can't secure this, the growth rate is too aggressive."
            )
        else:
            st.success(
                f"Internal cash generation exceeds asset requirements. "
                f"You can self-fund this growth without external capital. "
                f"Excess of **${abs(afn):,.0f}** can be used for dividends or debt reduction."
            )

    # 5. WATERFALL CHART
    fig = go.Figure(go.Waterfall(
        measure=["relative", "relative", "relative", "total"],
        x=["Additional Assets", "Operating Liabilities", "Retained Earnings", "External Funding"],
        y=[required_assets, -spontaneous_liabs, -internal_funding, 0],
        text=[f"+{required_assets:,.0f}", f"-{spontaneous_liabs:,.0f}",
              f"-{internal_funding:,.0f}", f"{afn:,.0f}"],
        textposition="outside",
        connector={"line": {"color": "#64748b"}},
        decreasing={"marker": {"color": "#00CC96"}},
        increasing={"marker": {"color": "#EF553B"}},
        totals={"marker": {"color": "#1E3A8A"}}
    ))
    fig.update_layout(height=400, margin=dict(l=20, r=20, t=20, b=20))
    st.plotly_chart(fig, use_container_width=True)

    # 6. VERDICT
    st.subheader("💡 Strategic Verdict")
    if afn > 0:
        st.error(f"**External Capital Required:** You need **${afn:,.0f}** in external capital to sustain this growth rate.")
    else:
        st.success("**Growth Can Be Financed Internally:** Enough net profit to self-fund this growth. No external capital required.")

    # 7. CASH CRUNCH WARNING
    st.divider()
    st.subheader("⚠️ Growth Cash Flow Reality Check")
    st.caption(
        "Profit does not automatically translate into cash.\n\n"
        "This section shows whether your planned growth generates cash or consumes it."
    )

    growth_m = calculate_metrics(
        price=float(s.get('price', 150.0)),
        volume=growth_volume,
        variable_cost=float(s.get('variable_cost', 100.0)),
        fixed_cost=float(s.get('fixed_cost', 450000.0)) * (1 + target_growth_pct * 0.15),
        ar_days=int(s.get('ar_days', 90)),
        inv_days=int(s.get('inv_days', 75)),
        ap_days=int(s.get('ap_days', 45)),
        annual_debt_service=float(s.get('annual_debt_service', 70000.0)) * (1 + target_growth_pct * 0.15),
        opening_cash=float(s.get('opening_cash', 150000.0)),
        total_debt=float(s.get('total_debt', 500000.0)) * (1 + target_growth_pct * 0.15),
        fixed_assets=float(s.get('fixed_assets', 800000.0)),
        target_profit=float(s.get('target_profit_goal', 200000.0)),
        tax_rate=float(s.get('tax_rate', 22.0)),
        annual_interest=float(s.get('annual_interest_only', 25000.0)) * (1 + target_growth_pct * 0.15),
        equity=float(s.get('equity', 500000.0)),
        depreciation=float(s.get('depreciation', 50000.0))
    )

    growth_net_profit = growth_m.get('net_profit', 0.0)
    growth_nwc        = growth_m.get('net_working_capital', 0.0)
    
    # Παίρνουμε το σωστό baseline που κλείδωσε ο χρήστης στο Home
    baseline_nwc      = s.get('original_baseline_nwc', growth_nwc)
    
    wc_impact         = growth_nwc - baseline_nwc
    
    growth_ds        = float(s.get('annual_debt_service', 70000.0)) * (1 + target_growth_pct * 0.15)
    growth_interest  = float(s.get('annual_interest_only', 25000.0)) * (1 + target_growth_pct * 0.15)
    growth_principal = growth_ds - growth_interest
    growth_fcf       = growth_net_profit + float(s.get('depreciation', 50000.0)) - growth_principal - wc_impact

    g1, g2, g3 = st.columns(3)
    g1.metric("Net Profit at Growth", f"${growth_net_profit:,.0f}",
              delta=f"{growth_net_profit - net_profit:+,.0f} vs baseline")
    g2.metric("Working Capital Investment", f"${wc_impact:,.0f}",
              delta="cash tied up in operations",
              delta_color="inverse" if wc_impact > 0 else "normal")
    g3.metric("Free Cash Flow", f"${growth_fcf:,.0f}",
              delta="positive" if growth_fcf > 0 else "cash crunch",
              delta_color="normal" if growth_fcf > 0 else "inverse")

    if growth_net_profit > 0 and growth_fcf < 0:
        st.error(
            f"**Growth Trap:** Accounting profit remains positive "
            f"(**${growth_net_profit:,.0f}** net profit), but Free Cash Flow falls to "
            f"**${growth_fcf:,.0f}**.\n\n"
            f"Growth requires an additional **${wc_impact:,.0f}** of working capital, "
            f"which absorbs cash faster than operations generate it. "
            f"Without additional financing, this growth path is unlikely to be sustainable."
        )
    elif growth_fcf > 0:
        st.success(
            f"**Sustainable Growth:** Both P&L and cash flow are positive at this growth rate. "
            f"FCF: **${growth_fcf:,.0f}**"
        )
    else:
        st.warning("Growth scenario results in losses. Consider a lower growth rate.")

    # ── WHY IS CASH NEGATIVE EVEN IF PROFIT IS POSITIVE? ──
    with st.expander("🔍 Why profitable growth can still create a cash shortage"):
        st.markdown(
            f"Growth consumes cash in three ways:\n\n"
            f"• **Working Capital expansion:** As revenue grows, you need more cash "
            f"tied up in receivables and inventory. At {target_growth_pct:.0%} growth, "
            f"WC absorbed **${wc_impact:,.0f}** extra.\n\n"
            f"• **Debt service:** Higher debt from financing growth costs "
            f"**${growth_principal:,.0f}** in principal repayment — this doesn't "
            f"appear in P&L but drains cash.\n\n"
            f"• **Timing mismatch:** You pay suppliers and employees now, "
            f"but collect from customers in {int(s.get('ar_days', 90))} days. "
            f"The faster you grow, the bigger this gap becomes."
        )
        if growth_fcf < 0:
            # Find the growth rate where FCF turns positive
            st.markdown("**What should I do next?**")
            actions = []
            if wc_impact > growth_fcf * -1:
                ar_days = int(s.get('ar_days', 90))
                daily_rev_growth = growth_m.get('revenue', 0) / 365
                actions.append(
                    f"• **Reduce AR days** (currently {ar_days} days) — "
                    f"every 10-day reduction at growth volume unlocks "
                    f"**${daily_rev_growth*10:,.0f}**"
                )
            if growth_principal > 0:
                actions.append(
                    f"• **Negotiate debt terms** — reducing principal repayment "
                    f"by 20% would recover **${growth_principal*0.2:,.0f}** in FCF"
                )
            actions.append(
                f"• **Match growth to financing capacity** — reduce the planned growth "
                f"from {target_growth_pct:.0%} until Free Cash Flow remains positive "
                f"without requiring additional external financing."
                )            
                
            for a in actions:
                st.markdown(a)

    st.divider()
    if st.button("⬅️ Back to Hub", use_container_width=True):
        st.session_state.flow_step = "home"
        st.session_state.selected_tool = None
        st.rerun()


