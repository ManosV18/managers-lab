def show_unit_cost_app():
    st.title("📦 Unit Production Cost Calculator")
    st.caption(
        "This tool estimates **average unit costs** under normal production "
        "and overtime conditions, to support **pricing, capacity, and acceptance decisions**."
    )

    st.header("🔢 Input Data")

    sales_regular = st.number_input(
        "Daily Sales (units – regular hours)",
        value=1000
    )
    st.caption(
        "Units produced and sold during normal operating hours."
    )

    sales_overtime = st.number_input(
        "Daily Sales (units – overtime)",
        value=100
    )
    st.caption(
        "Additional units produced during overtime or extended shifts."
    )

    raw_material_cost = st.number_input(
        "Daily Raw Material Cost (€)",
        value=1500.0
    )
    st.caption(
        "Total material cost for all units produced (shared across regular and overtime production)."
    )

    operating_cost_regular = st.number_input(
        "Operating Cost (regular hours) (€)",
        value=4000.0
    )
    st.caption(
        "Energy, maintenance, and overhead costs incurred during normal operating hours."
    )

    operating_cost_overtime = st.number_input(
        "Operating Cost (overtime) (€)",
        value=400.0
    )
    st.caption(
        "Incremental operating costs caused specifically by overtime production."
    )

    labor_cost_regular = st.number_input(
        "Labor Cost (regular hours) (€)",
        value=8000.0
    )
    st.caption(
        "Wages and salaries paid for regular working hours."
    )

    labor_cost_overtime = st.number_input(
        "Labor Cost (overtime) (€)",
        value=1200.0
    )
    st.caption(
        "Additional labor cost due to overtime pay or shift premiums."
    )

    if st.button("Calculate Costs"):
        avg_total, avg_regular, avg_overtime = calculate_unit_costs(
            sales_regular,
            sales_overtime,
            raw_material_cost,
            operating_cost_regular,
            operating_cost_overtime,
            labor_cost_regular,
            labor_cost_overtime
        )

        st.markdown("---")
        st.subheader("📊 Results")

        st.metric(
            "🔹 Average Unit Cost (Total)",
            f"{avg_total:.2f} €"
        )
        st.caption(
            "Average cost per unit across **all production**, useful for profitability benchmarks."
        )

        st.metric(
            "🟢 Unit Cost (Regular Hours)",
            f"{avg_regular:.2f} €"
        )
        st.caption(
            "Cost per unit produced during normal operations. "
            "This is the **baseline cost** for pricing and margin analysis."
        )

        st.metric(
            "🕐 Unit Cost (Overtime Hours)",
            f"{avg_overtime:.2f} €"
        )
        st.caption(
            "Cost per unit produced during overtime. "
            "**Use this metric when deciding whether to accept additional orders, "
            "run overtime, or quote special prices for extra capacity.**"
        )
