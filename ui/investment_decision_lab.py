import streamlit as st
import pandas as pd

from core.investment_decision import InvestmentDecision
from tools.investment_decision import (
    CompanyStateContext,
    InvestmentAssumptions,
    evaluate_investment,
    calculate_exit_option,
    calculate_tornado_sensitivity,
)


# ============================================================================
# INVESTMENT LAB
# ============================================================================

def render_investment_lab(
    baseline_state,
    decision_plan,
):
    """
    Investment Decision Lab.

    The lab evaluates a project independently against the locked
    company baseline.

    Evaluation does NOT automatically add the investment to the
    DecisionPlan. The user must explicitly choose to add it.
    """

    st.title("Investment Decision Lab")
    st.caption(
        "Evaluate an investment project against the locked company baseline."
    )

    # ------------------------------------------------------------------------
    # BASELINE GUARD
    # ------------------------------------------------------------------------

    if baseline_state is None:
        st.warning(
            "No locked company baseline is available. "
            "Lock the company baseline before using the Investment Lab."
        )
        return

    # ------------------------------------------------------------------------
    # COMPANY BASELINE CONTEXT
    # ------------------------------------------------------------------------

    st.subheader("Company Baseline")

    drivers = baseline_state.drivers
    capital_structure = baseline_state.capital_structure
    working_capital = baseline_state.working_capital

    company_price = drivers.price
    company_variable_cost = drivers.variable_cost_per_unit
    company_fixed_costs = drivers.fixed_opex

    company_tax_rate = capital_structure.tax_rate
    company_wacc = capital_structure.wacc

    company_ar_days = working_capital.ar_days
    company_inventory_days = working_capital.inventory_days
    company_ap_days = working_capital.ap_days

    company_fixed_assets = drivers.fixed_assets
    company_depreciation = drivers.depreciation

    baseline_col1, baseline_col2, baseline_col3 = st.columns(3)

    with baseline_col1:
        st.metric(
            "Selling Price",
            f"€{company_price:,.2f}",
        )

        st.metric(
            "Variable Cost / Unit",
            f"€{company_variable_cost:,.2f}",
        )

        st.metric(
            "Fixed Opex",
            f"€{company_fixed_costs:,.0f}",
        )

    with baseline_col2:
        st.metric(
            "Tax Rate",
            f"{company_tax_rate:.1%}",
        )

        st.metric(
            "WACC",
            f"{company_wacc:.1%}",
        )

        st.metric(
            "Fixed Assets",
            f"€{company_fixed_assets:,.0f}",
        )

    with baseline_col3:
        st.metric(
            "AR Days",
            f"{company_ar_days:.0f}",
        )

        st.metric(
            "Inventory Days",
            f"{company_inventory_days:.0f}",
        )

        st.metric(
            "AP Days",
            f"{company_ap_days:.0f}",
        )

    st.info(
        "Tax rate, WACC and working-capital policies are inherited from "
        "the locked company baseline. They are not project-level assumptions."
    )

    # ------------------------------------------------------------------------
    # COMPANY CONTEXT
    # ------------------------------------------------------------------------

    context = CompanyStateContext(
        price=company_price,
        variable_cost_per_unit=company_variable_cost,
        fixed_costs=company_fixed_costs,
        tax_rate=company_tax_rate,
        wacc=company_wacc,
        ar_days=company_ar_days,
        inventory_days=company_inventory_days,
        ap_days=company_ap_days,
        fixed_assets=company_fixed_assets,
        depreciation=company_depreciation,
    )

    # ------------------------------------------------------------------------
    # PROJECT DEFINITION
    # ------------------------------------------------------------------------

    st.divider()
    st.subheader("Investment Project")

    project_col1, project_col2 = st.columns(2)

    with project_col1:

        project_name = st.text_input(
            "Investment Name",
            value="New Investment",
            key="investment_project_name",
        )

        initial_investment = st.number_input(
            "Initial Investment (€)",
            min_value=0.0,
            value=100000.0,
            step=5000.0,
            key="investment_initial_investment",
        )

        project_years = st.number_input(
            "Project Life (Years)",
            min_value=1,
            value=5,
            step=1,
            key="investment_project_years",
        )

        depreciation_years = st.number_input(
            "Depreciation Life (Years)",
            min_value=1,
            value=5,
            step=1,
            key="investment_depreciation_years",
        )

        units = st.number_input(
            "Annual Units",
            min_value=0.0,
            value=2000.0,
            step=100.0,
            key="investment_units",
        )

    with project_col2:

        incremental_fixed_costs = st.number_input(
            "Incremental Fixed Costs (€ / Year)",
            min_value=0.0,
            value=35000.0,
            step=5000.0,
            key="investment_fixed_costs",
        )

        annual_volume_growth = st.number_input(
            "Annual Volume Growth (%)",
            value=0.0,
            step=1.0,
            key="investment_volume_growth",
        ) / 100.0

        annual_price_growth = st.number_input(
            "Annual Price Growth (%)",
            value=0.0,
            step=1.0,
            key="investment_price_growth",
        ) / 100.0

        annual_variable_cost_growth = st.number_input(
            "Annual Variable Cost Growth (%)",
            value=0.0,
            step=1.0,
            key="investment_variable_cost_growth",
        ) / 100.0

        annual_fixed_cost_growth = st.number_input(
            "Annual Fixed Cost Growth (%)",
            value=0.0,
            step=1.0,
            key="investment_fixed_cost_growth",
        ) / 100.0

    # ------------------------------------------------------------------------
    # PROJECT-SPECIFIC OPERATING ASSUMPTIONS
    # ------------------------------------------------------------------------

    st.subheader("Project-Specific Economics")

    st.caption(
        "Use these only when the investment's economics differ from the "
        "existing company baseline."
    )

    override_col1, override_col2 = st.columns(2)

    with override_col1:

        use_price_override = st.checkbox(
            "Use project-specific selling price",
            value=False,
            key="investment_use_price_override",
        )

        if use_price_override:

            price_override = st.number_input(
                "Project Selling Price (€ / Unit)",
                min_value=0.0,
                value=float(company_price),
                step=1.0,
                key="investment_price_override",
            )

        else:

            price_override = None

            st.caption(
                f"Using company baseline: €{company_price:,.2f}"
            )

    with override_col2:

        use_vc_override = st.checkbox(
            "Use project-specific variable cost",
            value=False,
            key="investment_use_vc_override",
        )

        if use_vc_override:

            variable_cost_override = st.number_input(
                "Project Variable Cost (€ / Unit)",
                min_value=0.0,
                value=float(company_variable_cost),
                step=1.0,
                key="investment_variable_cost_override",
            )

        else:

            variable_cost_override = None

            st.caption(
                f"Using company baseline: €{company_variable_cost:,.2f}"
            )

    # ------------------------------------------------------------------------
    # SALVAGE / EXIT
    # ------------------------------------------------------------------------

    st.subheader("Terminal Value")

    terminal_col1, terminal_col2 = st.columns(2)

    with terminal_col1:

        salvage_value = st.number_input(
            "Salvage Value (€)",
            min_value=0.0,
            value=0.0,
            step=5000.0,
            key="investment_salvage_value",
        )

    with terminal_col2:

        allow_exit_after_year_1 = st.checkbox(
            "Allow exit after Year 1",
            value=False,
            key="investment_allow_exit",
        )

    exit_value = 0.0
    exit_cost = 0.0

    if allow_exit_after_year_1:

        exit_col1, exit_col2 = st.columns(2)

        with exit_col1:

            exit_value = st.number_input(
                "Exit Value (€)",
                min_value=0.0,
                value=0.0,
                step=5000.0,
                key="investment_exit_value",
            )

        with exit_col2:

            exit_cost = st.number_input(
                "Exit Cost (€)",
                min_value=0.0,
                value=0.0,
                step=1000.0,
                key="investment_exit_cost",
            )

    # ------------------------------------------------------------------------
    # BUILD ASSUMPTIONS
    # ------------------------------------------------------------------------

    assumptions = InvestmentAssumptions(
        initial_investment=initial_investment,
        project_years=int(project_years),
        units=units,
        depreciation_years=int(depreciation_years),
        incremental_fixed_costs=incremental_fixed_costs,
        annual_volume_growth=annual_volume_growth,
        annual_price_growth=annual_price_growth,
        annual_variable_cost_growth=annual_variable_cost_growth,
        annual_fixed_cost_growth=annual_fixed_cost_growth,
        salvage_value=salvage_value,
        price_override=price_override,
        variable_cost_override=variable_cost_override,
        allow_exit_after_year_1=allow_exit_after_year_1,
        exit_value=exit_value,
        exit_cost=exit_cost,
    )

    # ------------------------------------------------------------------------
    # EVALUATE
    # ------------------------------------------------------------------------

    st.divider()

    evaluate_button = st.button(
        "Evaluate Investment",
        type="primary",
        use_container_width=True,
        key="evaluate_investment_button",
    )

    if evaluate_button:

        result = evaluate_investment(
            assumptions=assumptions,
            context=context,
        )

        st.session_state["investment_result"] = result
        st.session_state["investment_assumptions"] = assumptions
        st.session_state["investment_context"] = context

    # ------------------------------------------------------------------------
    # GET STORED RESULT
    # ------------------------------------------------------------------------

    result = st.session_state.get(
        "investment_result"
    )

    if result is None:
        return

    assumptions = st.session_state.get(
        "investment_assumptions",
        assumptions,
    )

    context = st.session_state.get(
        "investment_context",
        context,
    )

    # ------------------------------------------------------------------------
    # EXECUTIVE RESULT
    # ------------------------------------------------------------------------

    st.divider()
    st.subheader("Investment Economics")

    result_col1, result_col2, result_col3 = st.columns(3)

    with result_col1:

        st.metric(
            "NPV",
            f"€{result.npv:,.0f}",
        )

    with result_col2:

        st.metric(
            "IRR",
            f"{result.irr:.1%}",
        )

    with result_col3:

        if result.payback_years == float("inf"):

            payback_display = "N/A"

        else:

            payback_display = (
                f"{result.payback_years:.2f} years"
            )

        st.metric(
            "Payback",
            payback_display,
        )

    # ------------------------------------------------------------------------
    # INTERPRETATION
    # ------------------------------------------------------------------------

    if result.npv > 0:

        st.success(
            "The investment creates positive value at the company's "
            "baseline WACC."
        )

    elif result.npv < 0:

        st.error(
            "The investment destroys value at the company's "
            "baseline WACC."
        )

    else:

        st.warning(
            "The investment is approximately value-neutral at the "
            "company's baseline WACC."
        )

    # ------------------------------------------------------------------------
    # YEAR-1 IMPACT
    # ------------------------------------------------------------------------

    if result.year_1_impact is not None:

        impact = result.year_1_impact

        st.subheader("Year-1 Company Impact")

        impact_col1, impact_col2, impact_col3 = st.columns(3)

        with impact_col1:

            st.metric(
                "Revenue Δ",
                f"€{impact.incremental_revenue:,.0f}",
            )

            st.metric(
                "Variable Cost Δ",
                f"€{impact.incremental_variable_cost:,.0f}",
            )

            st.metric(
                "Fixed Opex Δ",
                f"€{impact.incremental_fixed_costs:,.0f}",
            )

            st.metric(
                "EBIT Δ",
                f"€{impact.incremental_ebit:,.0f}",
            )

        with impact_col2:

            st.metric(
                "Depreciation Δ",
                f"€{impact.incremental_depreciation:,.0f}",
            )

            st.metric(
                "Tax Δ",
                f"€{impact.incremental_tax:,.0f}",
            )

            st.metric(
                "Net Profit Δ",
                f"€{impact.incremental_net_profit:,.0f}",
            )

            st.metric(
                "Operating CF Δ",
                f"€{impact.incremental_operating_cash_flow:,.0f}",
            )

        with impact_col3:

            st.metric(
                "AR Δ",
                f"€{impact.incremental_ar:,.0f}",
            )

            st.metric(
                "Inventory Δ",
                f"€{impact.incremental_inventory:,.0f}",
            )

            st.metric(
                "AP Δ",
                f"€{impact.incremental_ap:,.0f}",
            )

            st.metric(
                "Incremental NWC",
                f"€{impact.incremental_nwc:,.0f}",
            )

        funding_col1, funding_col2, funding_col3 = st.columns(3)

        with funding_col1:

            st.metric(
                "Initial CAPEX",
                f"€{impact.initial_capex:,.0f}",
            )

        with funding_col2:

            st.metric(
                "Initial NWC Requirement",
                f"€{impact.initial_nwc_requirement:,.0f}",
            )

        with funding_col3:

            st.metric(
                "Initial Funding Requirement",
                f"€{impact.initial_funding_requirement:,.0f}",
            )

    # ------------------------------------------------------------------------
    # PROJECT CASH FLOW
    # ------------------------------------------------------------------------

    st.divider()
    st.subheader("Project Cash Flows")

    cash_flow_rows = []

    for year in result.yearly_cash_flows:

        cash_flow_rows.append(
            {
                "Year": year.year,
                "Units": year.units,
                "Revenue": year.revenue,
                "Variable Cost": year.variable_cost_total,
                "Fixed Costs": year.incremental_fixed_costs,
                "Depreciation": year.depreciation,
                "EBIT": year.operating_profit,
                "Tax": year.tax,
                "Operating CF": year.operating_cash_flow,
                "NWC": year.incremental_nwc,
                "WC Cash Flow": year.working_capital_cash_flow,
                "Salvage": year.salvage_value,
                "Project Cash Flow": year.project_cash_flow,
            }
        )

    cash_flow_df = pd.DataFrame(
        cash_flow_rows
    )

    st.dataframe(
        cash_flow_df,
        use_container_width=True,
        hide_index=True,
    )

    # ------------------------------------------------------------------------
    # FLEXIBILITY / EXIT OPTION
    # ------------------------------------------------------------------------

    if allow_exit_after_year_1:

        st.divider()
        st.subheader("Flexibility Analysis")

        downside_volume_pct = st.slider(
            "Downside Volume Shock (%)",
            min_value=0.0,
            max_value=50.0,
            value=20.0,
            step=5.0,
            key="investment_downside_volume",
        ) / 100.0

        exit_result = calculate_exit_option(
            assumptions=assumptions,
            context=context,
            downside_volume_pct=downside_volume_pct,
        )

        flex_col1, flex_col2, flex_col3 = st.columns(3)

        with flex_col1:

            st.metric(
                "Continue Value",
                f"€{exit_result['downside_continue_value']:,.0f}",
            )

        with flex_col2:

            st.metric(
                "Exit Value",
                f"€{exit_result['downside_exit_value']:,.0f}",
            )

        with flex_col3:

            st.metric(
                "Value of Flexibility",
                f"€{exit_result['value_of_flexibility']:,.0f}",
            )

        if exit_result["value_of_flexibility"] > 0:

            st.success(
                "The exit option has positive economic value under "
                "the selected downside scenario."
            )

        else:

            st.info(
                "Under the selected downside scenario, continuing the "
                "project has at least as much value as exiting."
            )

    # ------------------------------------------------------------------------
    # TORNADO SENSITIVITY
    # ------------------------------------------------------------------------

    st.divider()
    st.subheader("NPV Sensitivity")

    sensitivity_pct = st.slider(
        "Sensitivity Range",
        min_value=5.0,
        max_value=30.0,
        value=10.0,
        step=5.0,
        key="investment_tornado_range",
    ) / 100.0

    tornado_results = calculate_tornado_sensitivity(
        assumptions=assumptions,
        context=context,
        variation_pct=sensitivity_pct,
    )

    if tornado_results:

        tornado_rows = []

        for driver in tornado_results:

            tornado_rows.append(
                {
                    "Driver": driver.driver_name,
                    "Low NPV": driver.low_npv,
                    "Base NPV": driver.base_npv,
                    "High NPV": driver.high_npv,
                    "NPV Range": driver.range_span,
                }
            )

        tornado_df = pd.DataFrame(
            tornado_rows
        )

        st.dataframe(
            tornado_df.style.format(
                {
                    "Low NPV": "€{:,.0f}",
                    "Base NPV": "€{:,.0f}",
                    "High NPV": "€{:,.0f}",
                    "NPV Range": "€{:,.0f}",
                }
            ),
            use_container_width=True,
            hide_index=True,
        )

        st.caption(
            "WACC remains a sensitivity driver because it affects the "
            "investment valuation, but it is inherited from the company "
            "baseline rather than entered as a project assumption."
        )

    # ------------------------------------------------------------------------
    # ADD TO DECISION PLAN
    # ------------------------------------------------------------------------

    st.divider()
    st.subheader("Decision Plan")

    st.caption(
        "Evaluating the investment does not automatically add it to the "
        "current Decision Plan. Add it explicitly when you want the "
        "investment to become part of the company decision scenario."
    )

    add_to_plan = st.button(
        "Add Investment to Decision Plan",
        type="secondary",
        use_container_width=True,
        key="add_investment_to_plan_button",
    )

    if add_to_plan:

        investment_decision = InvestmentDecision.create(
            decision_id="investment_1",
            name=project_name,
            description=(
                "Investment project evaluated against the locked "
                "company baseline."
            ),
            assumptions=assumptions,
        )

        decision_plan.add_decision(
            investment_decision
        )

        st.success(
            f"Investment '{project_name}' was added to the Decision Plan."
        )
