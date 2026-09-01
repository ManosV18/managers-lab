import streamlit as st
import pandas as pd
import plotly.express as px


def show_salesperson_value():
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

    # ==================================================
    # WACC
    # ==================================================
    use_baseline = st.checkbox(
        "Use Company Baseline WACC",
        value=True
    )

    if use_baseline:
        wacc = s.get("wacc_locked", s.get("wacc", 15.0))
        st.caption(f"Using Company Baseline WACC: {wacc:.2f}%")
    else:
        wacc = st.number_input(
            "Custom WACC (%)",
            min_value=0.0,
            max_value=100.0,
            value=float(s.get("wacc_locked", s.get("wacc", 15.0))),
            step=0.5
        )

    st.info(
        "Customer payment terms and inventory days should reflect the typical customers managed by each salesperson."
    )

    # ==================================================
    # DEFAULT DATA
    # ==================================================
    if "salesperson_cash_cost_df" not in s:
        s.salesperson_cash_cost_df = pd.DataFrame([
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
            }
        ])

    # ==================================================
    # USER INPUTS
    # ==================================================
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
        }
    )
    df = edited_df.copy()

    # ==================================================
    # CALCULATIONS (Internal Tech Logic)
    # ==================================================
    if len(df) > 0:
        df["Funding Gap Days"] = (
            df["Inventory Days"] +
            df["Avg Customer Payment Days"] -
            df["Supplier Credit Days"]
        )
        df["Daily Sales ($)"] = df["Annual Sales ($)"] / 365
        df["Capital Locked ($)"] = df["Daily Sales ($)"] * df["Funding Gap Days"]
        df["Capital Cost ($)"] = df["Capital Locked ($)"] * (wacc / 100)
        df["Total People Cost ($)"] = df["Annual Salary + Commissions ($)"] + df["Annual Expenses ($)"]
        df["Economic Contribution ($)"] = (
            df["Annual Gross Profit ($)"] -
            df["Capital Cost ($)"] -
            df["Total People Cost ($)"]
        )
        df["Contribution Margin %"] = (
            df["Economic Contribution ($)"] / df["Annual Sales ($)"]
        ) * 100

        def classify_salesperson(row):
            if row["Economic Contribution ($)"] < 0:
                return "Value Destroyer"
            elif row["Funding Gap Days"] > 80:
                return "Cash Heavy"
            elif row["Contribution Margin %"] > 10:
                return "High Value"
            else:
                return "Stable"

        df["Classification"] = df.apply(classify_salesperson, axis=1)

        # ==================================================
        # STRATEGIC VISUALIZATION (UI Labels Updated)
        # ==================================================
        st.divider()
        st.subheader("🎯 Salesperson Value Map")
        st.caption("X-Axis: Cash Cycle (Days) | Y-Axis: True Salesperson Contribution ($) | Size: Sales Volume")

        fig = px.scatter(
            df,
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
                "Value Destroyer": "#ef4444"
            },
            template="plotly_dark",
            size_max=40
        )

        fig.add_hline(y=0, line_dash="dash", line_color="white", opacity=0.5)
        fig.update_layout(
            height=500,
            xaxis_title="Cash Cycle (Days) — Higher is slower cash",
            yaxis_title="True Salesperson Contribution ($) — Higher is better",
            margin=dict(l=20, r=20, t=40, b=20)
        )
        fig.update_traces(textposition='top center')
        st.plotly_chart(fig, use_container_width=True)

        # ==================================================
        # PORTFOLIO OVERVIEW (UI Labels Updated)
        # ==================================================
        st.divider()
        st.subheader("📊 Team Overview")
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Total Sales", f"${df['Annual Sales ($)'].sum():,.0f}")
        c2.metric("Total Gross Profit", f"${df['Annual Gross Profit ($)'].sum():,.0f}")
        c3.metric("Annual Cost of Trapped Cash", f"${df['Capital Cost ($)'].sum():,.0f}")
        c4.metric("True Salesperson Contribution", f"${df['Economic Contribution ($)'].sum():,.0f}")

        # ==================================================
        # DETAILED TABLE (Internal Columns Mapped to UI Names)
        # ==================================================
        st.divider()
        st.subheader("🔍 Detailed Results")
        
        ui_display_df = df[[
            "Salesperson", "Annual Sales ($)", "Annual Gross Profit ($)",
            "Funding Gap Days", "Capital Locked ($)", "Capital Cost ($)",
            "Total People Cost ($)", "Economic Contribution ($)",
            "Contribution Margin %", "Classification"
        ]].copy()

        ui_display_df["Contribution Margin %"] = ui_display_df["Contribution Margin %"].round(2)

        column_mapping = {
            "Funding Gap Days": "Cash Cycle (Days)",
            "Capital Locked ($)": "Cash Tied Up ($)",
            "Capital Cost ($)": "Annual Cost of Trapped Cash ($)",
            "Economic Contribution ($)": "True Salesperson Contribution ($)",
            "Contribution Margin %": "True Contribution Margin %"
        }

        ui_display_df.rename(columns=column_mapping, inplace=True)

        st.dataframe(
            ui_display_df.sort_values(
                by="True Salesperson Contribution ($)", ascending=False
            ).style.format({
                "Annual Sales ($)": "${:,.2f}",
                "Annual Gross Profit ($)": "${:,.2f}",
                "Cash Tied Up ($)": "${:,.2f}",
                "Annual Cost of Trapped Cash ($)": "${:,.2f}",
                "Total People Cost ($)": "${:,.2f}",
                "True Salesperson Contribution ($)": "${:,.2f}",
                "True Contribution Margin %": "{:.2f}%"
            }),
            use_container_width=True
        )

        # ==================================================
        # STRATEGIC INSIGHTS (UI Business Tone)
        # ==================================================
        st.divider()
        st.subheader("💡 Strategic Insight")
        worst = df.loc[df["Economic Contribution ($)"].idxmin()]
        best = df.loc[df["Economic Contribution ($)"].idxmax()]

        st.warning(
            f"⚠️ **{worst['Salesperson']}** manages a customer portfolio with an average cash cycle of "
            f"**{worst['Funding Gap Days']} days**.\n\n"
            f"The longer cash stays tied up, the lower the value this portfolio creates for the business."
        )
        st.success(
            f"✅ **{best['Salesperson']}** manages customers that generate healthy profits "
            f"while converting cash quickly.\n\n"
            f"This combination creates the strongest overall value for the business."
        )
        # ==================================================
        # WHAT-IF SIMULATION (Business Wording)
        # ==================================================
        st.divider()
        st.subheader("🚀 How Much Cash Could Faster Collections Release?")
        reduction_days = st.slider(
            "Target: Reduce average customer payment days by:", 0, 60, 10
        )
        released_capital = (df["Daily Sales ($)"] * reduction_days).sum()
        extra_contribution = released_capital * (wacc / 100)
        st.info(
            f"🎯 If customers paid {reduction_days} days sooner, your business would free up approximately "
            f"**${released_capital:,.0f}** in cash.\n\n"
            f"That lower financing requirement would improve annual business value by approximately "
            f"**${extra_contribution:,.0f}**."
        )
        # ==================================================
        # EXPORT
        # ==================================================
        st.divider()
        csv = ui_display_df.to_csv(index=False).encode("utf-8")
        st.download_button(
            "📥 Download Analysis",
            data=csv,
            file_name="salesperson_cash_cost.csv",
            mime="text/csv"
        )
