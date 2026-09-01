import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from tools.clv_calculator import (
    calculate_customer_value_analysis,
)


def render_clv_lab(baseline_state) -> None:
    st.title("👥 Customer Economics & CLV Lab")
    st.caption("Analyze Customer Lifetime Value (CLV), Acquisition Costs (CAC), and Portfolio Impact.")

    st.markdown("---")

    # =========================================================
    # BASELINE ASSUMPTIONS & GLOBAL INPUTS
    # =========================================================
    st.subheader("⚙️ Global Unit Economics & Discounting")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        price = st.number_input(
            "Average Price per Unit (€)",
            min_value=0.0,
            value=100.0,
            step=5.0,
            key="clv_price",
        )

    with col2:
        variable_cost = st.number_input(
            "Variable Cost per Unit (€)",
            min_value=0.0,
            value=60.0,
            step=5.0,
            key="clv_var_cost",
        )

    with col3:
        discount_rate = st.number_input(
            "Discount Rate / WACC (%)",
            min_value=0.0,
            max_value=50.0,
            value=10.0,
            step=0.5,
            key="clv_discount_rate",
        )

    with col4:
        realization_rate = st.slider(
            "Cash Realization Rate (%)",
            min_value=50,
            max_value=100,
            value=95,
            step=1,
            key="clv_realization_rate",
        ) / 100.0

    col_h1, col_h2 = st.columns(2)
    with col_h1:
        horizon_years = st.slider(
            "Analysis Horizon (Years)",
            min_value=1,
            max_value=10,
            value=5,
            step=1,
            key="clv_horizon",
        )
    with col_h2:
        num_customers = st.number_input(
            "Active Customer Portfolio Size",
            min_value=1,
            value=1000,
            step=50,
            key="clv_num_customers",
        )

    st.markdown("---")

    # =========================================================
    # SCENARIO COMPARISON INPUTS
    # =========================================================
    scen_col_a, scen_col_b = st.columns(2)

    with scen_col_a:
        st.subheader("🔴 Current Baseline Scenario (Scenario A)")
        cac_a = st.number_input(
            "CAC - Acquisition Cost (€)",
            min_value=0.0,
            value=150.0,
            step=10.0,
            key="cac_a",
        )
        purchases_a = st.number_input(
            "Orders per Year",
            min_value=0.1,
            value=3.0,
            step=0.5,
            key="purchases_a",
        )
        units_per_purchase_a = st.number_input(
            "Units per Order",
            min_value=0.1,
            value=1.0,
            step=0.1,
            key="units_a",
        )
        retention_rate_a = st.slider(
            "Annual Retention Rate (%)",
            min_value=0,
            max_value=100,
            value=70,
            step=5,
            key="retention_a",
        )

    with scen_col_b:
        st.subheader("🟢 Target / Optimized Scenario (Scenario B)")
        cac_b = st.number_input(
            "CAC - Acquisition Cost (€)",
            min_value=0.0,
            value=130.0,
            step=10.0,
            key="cac_b",
        )
        purchases_b = st.number_input(
            "Orders per Year",
            min_value=0.1,
            value=3.5,
            step=0.5,
            key="purchases_b",
        )
        units_per_purchase_b = st.number_input(
            "Units per Order",
            min_value=0.1,
            value=1.2,
            step=0.1,
            key="units_b",
        )
        retention_rate_b = st.slider(
            "Annual Retention Rate (%)",
            min_value=0,
            max_value=100,
            value=80,
            step=5,
            key="retention_b",
        )

    # =========================================================
    # ENGINE CALCULATION
    # =========================================================
    scenario_a_dict = {
        "cac": cac_a,
        "purchases": purchases_a,
        "units_per_purchase": units_per_purchase_a,
        "retention_rate": retention_rate_a,
    }

    scenario_b_dict = {
        "cac": cac_b,
        "purchases": purchases_b,
        "units_per_purchase": units_per_purchase_b,
        "retention_rate": retention_rate_b,
    }

    results = calculate_customer_value_analysis(
        price=price,
        variable_cost=variable_cost,
        scenario_a=scenario_a_dict,
        scenario_b=scenario_b_dict,
        discount_rate_pct=discount_rate,
        realization_rate=realization_rate,
        horizon_years=horizon_years,
        num_customers=num_customers,
    )

    st.markdown("---")

    # =========================================================
    # EXECUTIVE METRICS DISPLAY
    # =========================================================
    st.subheader("📊 Executive Summary & Value Creation")

    m_col1, m_col2, m_col3, m_col4 = st.columns(4)

    res_a = results["scenario_a"]
    res_b = results["scenario_b"]

    with m_col1:
        st.metric(
            label="CLV (Net Present Value)",
            value=f"€{res_b['clv']:,.2f}",
            delta=f"€{res_b['clv'] - res_a['clv']:,.2f} vs Scenario A",
        )

    with m_col2:
        st.metric(
            label="LTV / CAC Ratio",
            value=f"{res_b['ltv_cac_ratio']:.2f}x",
            delta=f"{res_b['ltv_cac_ratio'] - res_a['ltv_cac_ratio']:.2f}x vs Scenario A",
        )

    with m_col3:
        payback_b_str = (
            f"Year {res_b['payback_year']}"
            if res_b['payback_year']
            else "Not in Horizon"
        )
        st.metric(
            label="CAC Payback Period",
            value=payback_b_str,
            delta=f"Classification: {res_b['classification']}",
        )

    with m_col4:
        st.metric(
            label="Incremental Portfolio Value",
            value=f"€{results['incremental_value']:,.2f}",
            delta=f"{results['retention_improvement']:+.1f}% Retention",
        )

    # =========================================================
    # VISUALIZATION - CUMULATIVE NPV COMPARISON
    # =========================================================
    st.markdown("### 📈 Cumulative Cash Flow Trajectory (Net CLV)")

    df_a = pd.DataFrame(res_a["yearly_data"])
    df_b = pd.DataFrame(res_b["yearly_data"])

    # Prepend Year 0 for initial CAC
    df_a_plot = pd.concat([pd.DataFrame([{"Year": 0, "Cumulative_NPV": -cac_a}]), df_a], ignore_index=True)
    df_b_plot = pd.concat([pd.DataFrame([{"Year": 0, "Cumulative_NPV": -cac_b}]), df_b], ignore_index=True)

    fig = go.Figure()

    fig.add_trace(
        go.Scatter(
            x=df_a_plot["Year"],
            y=df_a_plot["Cumulative_NPV"],
            mode="lines+markers",
            name="Scenario A (Baseline)",
            line=dict(color="#EF553B", width=3),
        )
    )

    fig.add_trace(
        go.Scatter(
            x=df_b_plot["Year"],
            y=df_b_plot["Cumulative_NPV"],
            mode="lines+markers",
            name="Scenario B (Target)",
            line=dict(color="#00CC96", width=3),
        )
    )

    fig.add_hline(y=0, line_dash="dash", line_color="gray", annotation_text="Breakeven Line")

    fig.update_layout(
        xaxis_title="Year",
        yaxis_title="Cumulative NPV per Customer (€)",
        hovermode="x unified",
        margin=dict(l=20, r=20, t=30, b=20),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    )

    st.plotly_chart(fig, use_container_width=True)

    # =========================================================
    # DETAILED CASH FLOW TABLES
    # =========================================================
    with st.expander("📋 Detailed Year-by-Year Cash Flow Breakdown"):
        t_col1, t_col2 = st.columns(2)

        with t_col1:
            st.markdown("**Scenario A Schedule (€)**")
            st.dataframe(
                df_a.style.format(
                    {
                        "Annual_Cash_Flow": "€{:,.2f}",
                        "Discounted_Cash_Flow": "€{:,.2f}",
                        "Cumulative_NPV": "€{:,.2f}",
                    }
                ),
                use_container_width=True,
            )

        with t_col2:
            st.markdown("**Scenario B Schedule (€)**")
            st.dataframe(
                df_b.style.format(
                    {
                        "Annual_Cash_Flow": "€{:,.2f}",
                        "Discounted_Cash_Flow": "€{:,.2f}",
                        "Cumulative_NPV": "€{:,.2f}",
                    }
                ),
                use_container_width=True,
            )
