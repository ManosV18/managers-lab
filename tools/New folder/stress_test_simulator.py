import streamlit as st
import plotly.graph_objects as go
import pandas as pd

def show_stress_test_tool():
    st.header("🛡️ Strategic Stress Test")
    st.caption(
    """
    Test how your business reacts before reality forces the decision.

    This Decision Lab simulates revenue pressure, cost increases and cash collection delays
    to reveal the impact on profitability, liquidity and financial resilience.
    """
    )

    with st.expander("💡 What decision does this tool support?", expanded=True):
        st.markdown("""
    Many businesses discover problems after cash becomes tight.

    This Decision Lab helps management understand:
    • How much liquidity a downturn could consume
    • Whether profitability can survive operational shocks
    • Which variable creates the highest financial pressure

    The goal is not to predict the future, but to test decisions before they happen.
    """)

    s = st.session_state
    metrics = s.get("metrics", {})
    if not metrics:
        st.warning("⚠️ Complete and lock your company baseline before running stress scenarios.")
        return

    # --- BASELINE DATA ---
    price               = float(s.get('price', 150.0))
    vc                  = float(s.get('variable_cost', 100.0))
    volume              = float(s.get('volume', 12000))
    fixed_costs         = float(s.get('fixed_cost', 450000.0))
    current_cash        = float(s.get('opening_cash', 150000.0))
    annual_debt_service = float(s.get('annual_debt_service', 70000.0))
    annual_interest     = float(s.get('annual_interest_only', 25000.0))
    depreciation        = float(s.get('depreciation', 50000.0))
    tax_rate            = float(s.get('tax_rate', 22.0)) / 100
    ar_days             = int(s.get('ar_days', 90))

    # Baseline P&L for comparison
    baseline_ebit       = ((price - vc) * volume) - fixed_costs - depreciation
    baseline_ebt        = baseline_ebit - annual_interest
    baseline_net_profit = baseline_ebt * (1 - tax_rate) if baseline_ebt > 0 else baseline_ebt

    # --- SCENARIO PARAMETERS ---
    st.subheader("🎛️ Test Business Scenarios")
    c1, c2, c3 = st.columns(3)

    rev_shock  = c1.slider("Revenue Shock (%)", -60, 20, -25,
                           key=f"st_rev_{volume}") / 100
    dso_shock  = c2.slider("Customer Payment Delay (Days)", 0, 120, 30,
                           key=f"st_dso_{ar_days}")
    cost_shock = c3.slider("Variable Cost Spike (%)", 0, 50, 10,
                           key=f"st_vc_{vc}") / 100

    # --- IMPACT CALCULATIONS ---
    new_volume = volume * (1 + rev_shock)
    new_vc     = vc * (1 + cost_shock)
    new_rev    = new_volume * price

    liquidity_impact = (new_rev / 365) * dso_shock

    new_ebit       = ((price - new_vc) * new_volume) - fixed_costs - depreciation
    new_ebt        = new_ebit - annual_interest
    new_tax        = max(0, new_ebt * tax_rate)
    new_net_profit = new_ebt - new_tax

    monthly_cash_flow   = ((new_net_profit + depreciation - (annual_debt_service - annual_interest))/ 12)
    remaining_liquidity = current_cash - liquidity_impact + monthly_cash_flow

    # --- SCENARIO IMPACT SUMMARY ---
    st.divider()
    st.subheader("📊 Scenario Impact")
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("New Revenue", f"${new_rev:,.0f}",
              delta=f"{new_rev - price*volume:+,.0f} vs baseline")
    m2.metric("New Unit VC", f"${new_vc:,.2f}",
              delta=f"{cost_shock:.0%}", delta_color="inverse")
    m3.metric("Cash Locked by Delay", f"${liquidity_impact:,.0f}",
              delta_color="inverse",
              help="Cash trapped due to collection delays.")

    cash_delta = remaining_liquidity - current_cash
    m4.metric("Remaining Liquidity", f"${remaining_liquidity:,.0f}",
              delta=f"${cash_delta:,.0f}",
              delta_color="normal" if remaining_liquidity > 0 else "inverse")

    # ── WHY DID THIS HAPPEN? ───────────────────────────────
    with st.expander("🔍 Why did this happen?"):
        profit_delta = new_net_profit - baseline_net_profit
        drivers = []

        if rev_shock != 0:
            rev_impact = (new_rev - price * volume)
            cm = price - new_vc
            profit_impact = rev_impact * (cm / price) * (1 - tax_rate)
            drivers.append(
                f"• **Revenue shock ({rev_shock:.0%})** reduced volume by "
                f"{abs(volume - new_volume):,.0f} units → "
                f"P&L impact: **${profit_impact:,.0f}**"
            )

        if cost_shock != 0:
            cost_impact = -(new_vc - vc) * new_volume * (1 - tax_rate)
            drivers.append(
                f"• VC spike ({cost_shock:.0%}) increased unit cost by "
                f"${new_vc - vc:.2f} → "
                f"P&L impact: ${cost_impact:,.0f}"
            )
       
        if dso_shock > 0:
            drivers.append(
                f"• {dso_shock}-day collection delay froze "
                f"${liquidity_impact:,.0f} in receivables — "
                f"this doesn't affect P&L but drains cash immediately"
            )
            
        for d in drivers:
            st.markdown(d)

        st.markdown("**Net effect:**")
        st.markdown(
            f"Profit moved from ${baseline_net_profit:,.0f} "
            f"to ${new_net_profit:,.0f} ({profit_delta:+,.0f})"
        )
        st.markdown(
            f"Liquidity moved from ${current_cash:,.0f} "
            f"to ${remaining_liquidity:,.0f} ({cash_delta:+,.0f})"
        )
        
        if new_net_profit > 0 and remaining_liquidity < 0:
            st.warning(
                "⚠️ **Key insight:** The business is still profitable in this scenario "
                "but cash-negative. The DSO drain is the culprit — not the P&L."
            )

    # --- REMEDIES TABLE ---
    if remaining_liquidity < 0:
        st.error(f"🚨 **Liquidity Pressure Detected:** Funding gap of ${abs(remaining_liquidity):,.0f} detected.")
        st.subheader("📋 Strategic Response Options")
        gap      = abs(remaining_liquidity)
        daily_rev = (new_rev / 365) if new_rev > 0 else 1
        dso_reduction_needed = gap / daily_rev

        remedy_data = {
            "Strategy": ["DSO Optimization", "Debt Service Restructuring", "Capital Injection"],
            "Target Action": [
                f"Recover {int(dso_reduction_needed) + 1} days of credit",
                f"Defer ${gap:,.0f} of principal payments",
                f"Secure fresh funding of ${gap:,.0f}"
            ],
            "Impact": ["Immediate Liquidity", "Cash Preservation", "Instant Safety"]
        }
        st.table(pd.DataFrame(remedy_data))

        # ── WHAT SHOULD I DO NEXT? ─────────────────────────
        with st.expander("🔍 What should I do next? (Prioritized)"):
            st.markdown("Based on your specific shock combination:")
            actions = []

            if dso_shock > 0:
                dso_fix_cash = daily_rev * dso_shock
                actions.append(
                    f"**1. Fastest fix — collect faster:** "
                    f"The DSO drain is ${liquidity_impact:,.0f}. "
                    f"Recovering half the delay closes ${dso_fix_cash/2:,.0f} of the gap immediately."
                )

            if cost_shock > 0:
                vc_annual = (new_vc - vc) * new_volume
                actions.append(
                    f"**2. Protect margin — renegotiate supplier prices:** "
                    f"The VC spike added ${vc_annual:,.0f} in annual costs. "
                    f"A 50% offset saves ${vc_annual * 0.5:,.0f}."
                )
                        
            if rev_shock < -0.1:
                actions.append(
                    f"**3. Stop the volume bleed:** A {abs(rev_shock):.0%} revenue drop "
                    f"at your margin means you need {abs(rev_shock/(1-abs(rev_shock))):.0%} "
                    f"more volume just to break even. Focus on retaining existing customers first."
                )
            actions.append(
                f"**4. Emergency buffer:** If the crunch persists beyond 30 days, "
                f"arrange a revolving credit line of at least ${gap:,.0f} "
                f"before the situation becomes critical."
            )
            for a in actions:
                st.markdown(f"• {a}")

    # --- TORNADO CHART ---
    st.subheader("🌪️ Sensitivity Analysis (Tornado Chart)")

    dso_sens = (new_rev / 365) * (dso_shock * 0.1)
    vc_sens  = (new_volume * (new_vc * 0.1)) / 12
    vol_sens = ((price - new_vc) * (new_volume * 0.1)) / 12

    tornado_items = sorted([
        {"Variable": "Collection Delay (DSO)", "Impact": dso_sens},
        {"Variable": "Variable Cost Spike",    "Impact": vc_sens},
        {"Variable": "Sales Volume Drop",      "Impact": vol_sens}
    ], key=lambda x: x["Impact"])

    fig = go.Figure()
    fig.add_trace(go.Bar(
        y=[item["Variable"] for item in tornado_items],
        x=[item["Impact"] for item in tornado_items],
        orientation='h',
        marker_color='#ef4444'
    ))
    fig.update_layout(
        height=300, template="plotly_dark",
        margin=dict(l=10, r=10, t=30, b=10),
        xaxis_title="Potential Negative Impact on Monthly Cash ($)"
    )
    st.plotly_chart(fig, use_container_width=True)

    # ── WHY DOES THE TORNADO LOOK LIKE THIS? ──────────────
    with st.expander("🔍 Why does the Tornado look like this?"):
        biggest = tornado_items[-1]
        st.markdown(
            f"The Tornado shows which variable causes the **most damage per unit of change**. "
            f"In your current scenario, **{biggest['Variable']}** is the dominant risk "
            f"(${biggest['Impact']:,.0f} monthly impact per 10% change).\n\n"
            f"This means your business is most sensitive to changes in {biggest['Variable'].lower()}. "
            f"That's where you should focus your risk mitigation first."
        )

    st.divider()
    if st.button("⬅️ Return to Hub", use_container_width=True):
        s.flow_step = "home"
        st.rerun()
