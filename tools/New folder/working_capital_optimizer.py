import streamlit as st
import plotly.graph_objects as go
from core.working_capital_analysis import calculate_working_capital_analysis


def show_wc_optimizer():
    st.title("💰 Working Capital Optimization Lab")

    st.caption(
        """
        Is too much cash trapped inside your operating cycle?
        Simulate changes in collection speed, inventory turnover, or vendor terms 
        to calculate cash released and impact on FCFE.
        """
    )

    with st.expander("💡 What decision does this tool support?", expanded=True):
        st.markdown(
            """
            This Decision Lab tests **What-If scenarios** against your company baseline.
            It identifies exact liquidity released or consumed without altering the core baseline.
            """
        )

    s = st.session_state

    # 1. READ BASELINE METRICS
    base_ar_days = float(s.get("ar_days", s.get("input_ar_days", 36.5)))
    base_inv_days = float(s.get("inv_days", s.get("input_inv_days", 73.0)))
    base_ap_days = float(s.get("ap_days", s.get("input_ap_days", 36.5)))

    metrics = s.get("metrics", {})
    revenue = float(metrics.get("revenue", s.get("revenue", 100000.0)))
    cogs = float(metrics.get("cogs", s.get("cogs", 60000.0)))

    # 2. WHAT-IF CONTROLS (SLIDERS)
    st.subheader("⚙️ What-If Policy Adjustments")
    col1, col2, col3 = st.columns(3)

    with col1:
        target_ar = st.slider(
            "Target AR Days (Collection)",
            min_value=5.0,
            max_value=120.0,
            value=base_ar_days,
            step=1.0,
            help="Lower = Faster Cash Collection"
        )

    with col2:
        target_inv = st.slider(
            "Target Inventory Days (Holding)",
            min_value=5.0,
            max_value=180.0,
            value=base_inv_days,
            step=1.0,
            help="Lower = Leaner Inventory"
        )

    with col3:
        target_ap = st.slider(
            "Target AP Days (Payables)",
            min_value=5.0,
            max_value=120.0,
            value=base_ap_days,
            step=1.0,
            help="Higher = Longer Vendor Payment Terms"
        )

    # 3. CORE ENGINE CALCULATION
    analysis = calculate_working_capital_analysis(
        inventory_days=target_inv,
        receivables_days=target_ar,
        payables_days=target_ap,
        annual_revenue=revenue,
        annual_cogs=cogs,
        baseline_inventory_days=base_inv_days,
        baseline_receivables_days=base_ar_days,
        baseline_payables_days=base_ap_days
    )

    cash_released = analysis["cash_impact"]
    ccc_delta = analysis["ccc_change"]

    st.divider()

    # 4. KPI DASHBOARD
    st.subheader("📊 Scenario Impact & Cash Impact")
    kpi1, kpi2, kpi3, kpi4 = st.columns(4)

    kpi1.metric("Baseline NWC", f"€{analysis['baseline_working_capital']:,.0f}")
    kpi2.metric(
        "Projected NWC",
        f"€{analysis['working_capital']:,.0f}",
        delta=f"{-cash_released:,.0f} €",
        delta_color="inverse"
    )
    kpi3.metric(
        "Cash Released / Unlocked",
        f"€{cash_released:,.0f}",
        delta="Positive Release" if cash_released >= 0 else "Cash Trapped",
        delta_color="normal" if cash_released >= 0 else "inverse"
    )
    kpi4.metric(
        "Cash Conversion Cycle",
        f"{analysis['ccc']:.0f} Days",
        delta=f"{ccc_delta:.0f} Days",
        delta_color="inverse"
    )

    st.divider()

    # 5. VISUALIZATION & BREAKDOWN
    col_left, col_right = st.columns(2)

    with col_left:
        st.subheader("💼 NWC Component Comparison")
        labels = ['Working Capital Requirement']
        fig = go.Figure()
        fig.add_trace(go.Bar(
            name='Baseline NWC',
            x=labels,
            y=[analysis['baseline_working_capital']],
            marker_color='#64748b'
        ))
        fig.add_trace(go.Bar(
            name='Projected NWC',
            x=labels,
            y=[analysis['working_capital']],
            marker_color='#10b981' if cash_released >= 0 else '#ef4444'
        ))
        fig.update_layout(
            barmode='group',
            template="plotly_dark",
            height=350,
            margin=dict(l=20, r=20, t=30, b=20)
        )
        st.plotly_chart(fig, use_container_width=True)

    with col_right:
        st.subheader("💡 Strategic Insights")
        daily_rev = analysis["daily_revenue_basis"]
        daily_cogs = analysis["daily_cogs_basis"]

        st.info(
            f"""
            * **Daily Revenue Basis:** €{daily_rev:,.2f} / day  
            * **Daily COGS Basis:** €{daily_cogs:,.2f} / day  
            * **Largest Operational Time Driver:** `{analysis['largest_driver']['name']}` ({analysis['largest_driver']['days']:.0f} days)
            """
        )

        if cash_released > 0:
            st.success(
                f"🎯 **Decision Impact:** This scenario unlocks **€{cash_released:,.0f}** of free cash flow directly into FCFE without borrowing or external equity."
            )
        elif cash_released < 0:
            st.warning(
                f"⚠️ **Liquidity Risk:** This policy change absorbs **€{abs(cash_released):,.0f}** of operating cash."
            )

    # 6. NAVIGATION
    st.divider()
    if st.button("⬅️ Back to Hub", use_container_width=True):
        s.flow_step = "home"
        st.rerun()
