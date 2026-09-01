import plotly.graph_objects as go
import streamlit as st

from diagnostics.deal_economics import calculate_deal_economics


# ==========================================
# BASELINE EXTRACTION HELPERS
# ==========================================
def _get_baseline_wacc(baseline_state) -> float:
    try:
        return float(baseline_state.wacc)
    except AttributeError:
        return float(getattr(baseline_state, "wacc_pct", 8.0))


def _get_baseline_days(baseline_state):
    try:
        wc = baseline_state.working_capital
        return float(wc.inventory_days), float(wc.ar_days), float(wc.ap_days)
    except AttributeError:
        inv = float(getattr(baseline_state, "inventory_days", 45.0))
        ar = float(getattr(baseline_state, "ar_days", 30.0))
        ap = float(getattr(baseline_state, "ap_days", 60.0))
        return inv, ar, ap


# ==========================================
# MAIN RENDER FUNCTION
# ==========================================
def render_deal_auditor_lab(baseline_state):
    st.title("🤝 Deal Auditor Lab")

    st.markdown(
        """
        Evaluate the **True Economic Profitability** of a commercial customer deal.
        
        *Accounting Profit* only looks at `Revenue - COGS`. This tool factors in your 
        **WACC** and **Working Capital Terms** to reveal the invisible financing cost of capital tied up during the cash gap.
        """
    )

    # AUTO-EXTRACT BASELINE DEFAULTS
    default_wacc = _get_baseline_wacc(baseline_state)
    default_inv, default_ar, default_ap = _get_baseline_days(baseline_state)

    st.subheader("1. Deal Financials & Baseline Parameters")

    col1, col2 = st.columns(2)
    with col1:
        revenue = st.number_input(
            "Deal Revenue (€)",
            min_value=0.0,
            value=100000.0,
            step=5000.0,
            key="deal_revenue",
        )
        cost = st.number_input(
            "Direct COGS / Cost (€)",
            min_value=0.0,
            value=70000.0,
            step=5000.0,
            key="deal_cost",
        )

    with col2:
        wacc = st.number_input(
            "Company WACC / Cost of Capital (%)",
            min_value=0.0,
            max_value=100.0,
            value=default_wacc,
            step=0.5,
            key="deal_wacc",
            help="Pulled from baseline Company State by default.",
        )

    st.divider()
    st.subheader("2. Working Capital Terms (Deal Specific)")

    st.caption("Adjust the specific payment and holding terms for this deal to test 'What-if' scenarios.")

    c_inv, c_ar, c_ap = st.columns(3)
    with c_inv:
        days_inv = st.number_input(
            "Inventory Holding (Days)",
            min_value=0.0,
            max_value=365.0,
            value=default_inv,
            key="deal_days_inv",
        )
    with c_ar:
        days_ar = st.number_input(
            "Customer Credit / AR (Days)",
            min_value=0.0,
            max_value=365.0,
            value=default_ar,
            key="deal_days_ar",
        )
    with c_ap:
        days_ap = st.number_input(
            "Supplier Payment / AP (Days)",
            min_value=0.0,
            max_value=365.0,
            value=default_ap,
            key="deal_days_ap",
        )

    # EXECUTE DIAGNOSTIC CALCULATION
    results = calculate_deal_economics(
        revenue=revenue,
        cost=cost,
        days_inv=days_inv,
        days_ar=days_ar,
        days_ap=days_ap,
        wacc=wacc,
    )

    st.divider()
    st.subheader("📊 Diagnostic Audit Results")

    # METRICS DISPLAY
    m1, m2, m3, m4 = st.columns(4)

    m1.metric(
        label="Accounting Profit",
        value=f"€ {results['accounting_profit']:,.0f}",
        delta=f"Margin: {results['accounting_margin']:.1%}",
        delta_color="off",
    )

    m2.metric(
        label="Cash Gap (Funding Days)",
        value=f"{results['cash_gap']:.0f} Days",
        help="Formula: (Inventory Days + AR Days) - AP Days",
    )

    m3.metric(
        label="Financing Cost (Drag)",
        value=f"€ {results['financing_cost']:,.0f}",
        delta=f"-€ {results['financing_cost']:,.0f}" if results["financing_cost"] > 0 else None,
        delta_color="inverse",
        help="Financing Cost = Cost * WACC * (Cash Gap / 365)",
    )

    profit_diff = results["economic_profit"] - results["accounting_profit"]
    m4.metric(
        label=f"Economic Profit (Margin: {results['economic_margin']:.1%})",
        value=f"€ {results['economic_profit']:,.0f}",
        delta=f"€ {profit_diff:,.0f} vs Accounting",
        delta_color="normal" if profit_diff >= 0 else "inverse",
    )

    # INSIGHT CARDS
    if results["financing_cost"] > 0:
        st.warning(
            f"⚠️ Capital Drag Impact: Working Capital funding costs absorb **€{results['financing_cost']:,.0f}** "
            f"({(results['financing_cost'] / results['accounting_profit'] if results['accounting_profit'] > 0 else 0):.1%} of Accounting Profit)."
        )
    elif results["cash_gap"] < 0:
        st.success(
            f"💰 Negative Cash Gap: Suppliers are funding this deal for **{abs(results['cash_gap']):.0f} days**! "
            f"Financing drag is zero."
        )

    # CHART: ACCOUNTING VS ECONOMIC PROFIT BREAKDOWN
    fig = go.Figure()
    fig.add_trace(
        go.Bar(
            name="Accounting Profit",
            x=["Profit Comparison"],
            y=[results["accounting_profit"]],
            text=[f"€{results['accounting_profit']:,.0f}"],
            textposition="auto",
        )
    )
    fig.add_trace(
        go.Bar(
            name="Financing Cost (WACC Drag)",
            x=["Profit Comparison"],
            y=[-results["financing_cost"]],
            text=[f"-€{results['financing_cost']:,.0f}"],
            textposition="auto",
        )
    )
    fig.add_trace(
        go.Bar(
            name="True Economic Profit",
            x=["Profit Comparison"],
            y=[results["economic_profit"]],
            text=[f"€{results['economic_profit']:,.0f}"],
            textposition="auto",
        )
    )

    fig.update_layout(
        barmode="group",
        title="Accounting Profit vs. True Economic Profit",
        height=380,
        margin=dict(l=20, r=20, t=50, b=20),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    )

    st.plotly_chart(fig, use_container_width=True)
