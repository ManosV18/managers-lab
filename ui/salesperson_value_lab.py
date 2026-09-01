import pandas as pd
import plotly.express as px
import streamlit as st

from tools.salesperson_value_calculator import (
    calculate_released_capital,
    calculate_sales_team_metrics,
    calculate_salesperson_value,
)


def render_salesperson_value_lab(baseline_state=None):
    st.header("👤 Which Salespeople Create the Most Value?")

    st.info(
        "Sales is not just about generating revenue.\n\n"
        "Two salespeople can sell the same amount and still create very different value for the business.\n\n"
        "One salesperson may bring customers who pay quickly and generate healthy profits.\n"
        "Another may achieve similar sales but require far more cash to support those sales.\n\n"
        "This Decision Lab shows:\n"
        "• Which salespeople create the most economic value\n"
        "• How much cash each salesperson's customer portfolio ties up\n"
        "• The real contribution each salesperson makes after salaries, expenses and the cost of capital"
    )

    s = st.session_state

    # =========================================================
    # WACC RESOLUTION
    # =========================================================
    baseline_wacc = 0.0

    if baseline_state is not None:
        try:
            baseline_wacc = float(baseline_state.capital_structure.wacc)
        except (AttributeError, TypeError, ValueError):
            baseline_wacc = 0.0

    # Fallback to session state if baseline state object isn't present
    if baseline_wacc == 0.0:
        baseline_wacc = float(s.get("wacc_locked", s.get("wacc", 0.15)))
        if baseline_wacc > 1.0:
            baseline_wacc = baseline_wacc / 100.0

    use_baseline = st.checkbox("Use Company Baseline WACC", value=True)

    if use_baseline:
        wacc = baseline_wacc * 100.0
        st.caption(f"Using Company Baseline WACC: {wacc:.2f}%")
    else:
        wacc = st.number_input(
            "Custom WACC (%)",
            min_value=0.0,
            max_value=100.0,
            value=float(baseline_wacc * 100.0),
            step=0.5,
        )

    st.info(
        "Customer payment terms and inventory days should reflect the typical customers managed by each salesperson."
    )

    # =========================================================
    # DEFAULT DATA SETUP
    # =========================================================
    if "salesperson_cash_cost_df" not in s:
        s.salesperson_cash_cost_df = pd.DataFrame(
            [
                {
                    "Salesperson": "Salesperson A",
                    "Annual Sales ($)": 420000.0,
                    "Annual Gross Profit ($)": 84000.0,
                    "Avg Customer Payment Days": 90,
                    "Inventory Days": 50,
                    "Supplier Credit Days": 35,
                    "Annual Salary + Commissions ($)": 55000.0,
                    "Annual Expenses ($)": 8000.0,
                },
                {
                    "Salesperson": "Salesperson B",
                    "Annual Sales ($)": 280000.0,
                    "Annual Gross Profit ($)": 70000.0,
                    "Avg Customer Payment Days": 35,
                    "Inventory Days": 30,
                    "Supplier Credit Days": 35,
                    "Annual Salary + Commissions ($)": 48000.0,
                    "Annual Expenses ($)": 6000.0,
                },
            ]
        )

    # =========================================================
    # INPUT DATA EDITOR
    # =========================================================
    st.subheader("📋 Sales Team Data")
    st.caption(
        "Gross Profit is after discounts. "
        "Payment and inventory days reflect the typical customer profile each salesperson brings."
    )

    edited_df = st.data_editor(
        s.salesperson_cash_cost_df,
        num_rows="dynamic",
        use_container_width=True,
        key="salesperson_cash_cost_editor",
        column_config={
            "Annual Sales ($)": st.column_config.NumberColumn(
                "Annual Sales ($)", format="$%,.2f"
            ),
            "Annual Gross Profit ($)": st.column_config.NumberColumn(
                "Annual Gross Profit ($)", format="$%,.2f"
            ),
            "Annual Salary + Commissions ($)": st.column_config.NumberColumn(
                "Annual Salary + Commissions ($)", format="$%,.2f"
            ),
            "Annual Expenses ($)": st.column_config.NumberColumn(
                "Annual Expenses ($)", format="$%,.2f"
            ),
            "Avg Customer Payment Days": st.column_config.NumberColumn(
                "Avg Customer Payment Days", format="%d days"
            ),
            "Inventory Days": st.column_config.NumberColumn(
                "Inventory Days", format="%d days"
            ),
            "Supplier Credit Days": st.column_config.NumberColumn(
                "Supplier Credit Days", format="%d days"
            ),
        },
    )

    df = edited_df.copy()

    required_columns = [
        "Salesperson",
        "Annual Sales ($)",
        "Annual Gross Profit ($)",
        "Avg Customer Payment Days",
        "Inventory Days",
        "Supplier Credit Days",
        "Annual Salary + Commissions ($)",
        "Annual Expenses ($)",
    ]

    missing = [col for col in required_columns if col not in df.columns]
    if missing:
        st.error(f"Missing required columns: {', '.join(missing)}")
        return

    if df.empty:
        st.info("Add at least one salesperson to run the analysis.")
        return

    # =========================================================
    # CALCULATIONS
    # =========================================================
    result = calculate_salesperson_value(df=df, wacc=wacc)
    metrics = calculate_sales_team_metrics(result)

    # =========================================================
    # STRATEGIC VISUALIZATION
    # =========================================================
    st.divider()
    st.subheader("🎯 Salesperson Value Map")
    st.caption(
        "X-Axis: Cash Cycle (Days) | Y-Axis: True Salesperson Contribution ($) | Size: Sales Volume"
    )

    fig = px.scatter(
        result,
        x="Funding Gap Days",
        y="Economic Contribution ($)",
        size="Annual Sales ($)",
        color="Classification",
        hover_name="Salesperson",
        text="Salesperson",
        color_discrete_map={
            "High Value": "#10b981",
            "Stable": "#3b82f6",
            "Cash Heavy": "#f59e0b",
            "Value Destroyer": "#ef4444",
        },
        template="plotly_dark",
        size_max=40,
    )

    fig.add_hline(y=0, line_dash="dash", line_color="white", opacity=0.5)
    fig.update_layout(
        height=500,
        xaxis_title="Cash Cycle (Days) — Higher is slower cash",
        yaxis_title="True Salesperson Contribution ($) — Higher is better",
        margin=dict(l=20, r=20, t=40, b=20),
    )
    fig.update_traces(textposition="top center")
    st.plotly_chart(fig, use_container_width=True)

    # =========================================================
    # PORTFOLIO OVERVIEW
    # =========================================================
    st.divider()
    st.subheader("📊 Team Overview")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total Sales", f"${metrics['total_sales']:,.0f}")
    c2.metric("Total Gross Profit", f"${metrics['total_gross_profit']:,.0f}")
    c3.metric(
        "Annual Cost of Trapped Cash", f"${metrics['capital_cost']:,.0f}"
    )
    c4.metric(
        "True Salesperson Contribution",
        f"${metrics['economic_contribution']:,.0f}",
    )

    # =========================================================
    # DETAILED TABLE
    # =========================================================
    st.divider()
    st.subheader("🔍 Detailed Results")

    ui_display_df = result[
        [
            "Salesperson",
            "Annual Sales ($)",
            "Annual Gross Profit ($)",
            "Funding Gap Days",
            "Capital Locked ($)",
            "Capital Cost ($)",
            "Total People Cost ($)",
            "Economic Contribution ($)",
            "Contribution Margin %",
            "Classification",
        ]
    ].copy()

    ui_display_df["Contribution Margin %"] = ui_display_df[
        "Contribution Margin %"
    ].round(2)

    column_mapping = {
        "Funding Gap Days": "Cash Cycle (Days)",
        "Capital Locked ($)": "Cash Tied Up ($)",
        "Capital Cost ($)": "Annual Cost of Trapped Cash ($)",
        "Economic Contribution ($)": "True Salesperson Contribution ($)",
        "Contribution Margin %": "True Contribution Margin %",
    }

    ui_display_df.rename(columns=column_mapping, inplace=True)

    st.dataframe(
        ui_display_df.sort_values(
            by="True Salesperson Contribution ($)", ascending=False
        ).style.format(
            {
                "Annual Sales ($)": "${:,.2f}",
                "Annual Gross Profit ($)": "${:,.2f}",
                "Cash Tied Up ($)": "${:,.2f}",
                "Annual Cost of Trapped Cash ($)": "${:,.2f}",
                "Total People Cost ($)": "${:,.2f}",
                "True Salesperson Contribution ($)": "${:,.2f}",
                "True Contribution Margin %": "{:.2f}%",
            }
        ),
        use_container_width=True,
    )

    # =========================================================
    # STRATEGIC INSIGHTS
    # =========================================================
    st.divider()
    st.subheader("💡 Strategic Insight")
    worst = result.loc[result["Economic Contribution ($)"].idxmin()]
    best = result.loc[result["Economic Contribution ($)"].idxmax()]

    st.warning(
        f"⚠️ **{worst['Salesperson']}** manages a customer portfolio with an average cash cycle of "
        f"**{worst['Funding Gap Days']:.0f} days**.\n\n"
        f"The longer cash stays tied up, the lower the value this portfolio creates for the business."
    )
    st.success(
        f"✅ **{best['Salesperson']}** manages customers that generate healthy profits "
        f"while converting cash quickly.\n\n"
        f"This combination creates the strongest overall value for the business."
    )

    # =========================================================
    # WHAT-IF SIMULATION
    # =========================================================
    st.divider()
    st.subheader("🚀 How Much Cash Could Faster Collections Release?")
    reduction_days = st.slider(
        "Target: Reduce average customer payment days by:", 0, 60, 10
    )

    released_capital = calculate_released_capital(result, reduction_days)
    extra_contribution = released_capital * (wacc / 100.0)

    st.info(
        f"🎯 If customers paid {reduction_days} days sooner, your business would free up approximately "
        f"**${released_capital:,.0f}** in cash.\n\n"
        f"That lower financing requirement would improve annual business value by approximately "
        f"**${extra_contribution:,.0f}**."
    )

    # =========================================================
    # EXPORT
    # =========================================================
    st.divider()
    csv = ui_display_df.to_csv(index=False).encode("utf-8")
    st.download_button(
        "📥 Download Analysis",
        data=csv,
        file_name="salesperson_cash_cost.csv",
        mime="text/csv",
    )
