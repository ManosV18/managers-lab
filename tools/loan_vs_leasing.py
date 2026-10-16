# tools/loan_vs_leasing.py
"""Loan-vs-leasing decision lab linked to the active investment project."""

import math
import streamlit as st
import plotly.graph_objects as go

from core.financial_engine import FinancialEngine
from core.decision_plan import DecisionPlan
from core.investment_decision import InvestmentDecision
from core.investment_funding import InvestmentFundingAllocator
from core.investment_integration import InvestmentIntegration


def format_number_gr(value):
    return f"{value:,.0f}"


def _monthly_payment(principal, annual_rate, months, pay_when=0, future_value=0.0):
    """Positive monthly payment for an amortising balance with optional balloon."""
    principal = max(0.0, float(principal))
    annual_rate = max(0.0, float(annual_rate))
    future_value = min(principal, max(0.0, float(future_value)))
    months = max(1, int(months))
    r = annual_rate / 12.0
    if r == 0:
        return max(0.0, (principal - future_value) / months)
    factor = (1.0 + r) ** months
    payment = (principal * r * factor - future_value * r) / (factor - 1.0)
    if pay_when == 1:
        payment /= 1.0 + r
    return max(0.0, payment)


def _financing_schedule(principal, annual_rate, duration_years, pay_when=0, future_value=0.0):
    """Monthly amortisation; returns year-one and full-term financing measures."""
    principal = max(0.0, float(principal))
    annual_rate = max(0.0, float(annual_rate))
    years = max(1.0, float(duration_years))
    months = max(1, int(round(years * 12)))
    residual = min(principal, max(0.0, float(future_value)))
    rate = annual_rate / 12.0

    if principal <= 0:
        return {
            "monthly_payment": 0.0, "year1_interest": 0.0,
            "year1_principal": 0.0, "year1_payment": 0.0,
            "total_interest": 0.0, "total_payments": 0.0,
            "year1_ending_balance": 0.0,
        }

    payment = _monthly_payment(principal, annual_rate, months, pay_when, residual)
    balance = principal
    total_interest = 0.0
    total_payments = 0.0
    year1_interest = 0.0
    year1_payments = 0.0
    year1_ending_balance = principal

    for month in range(1, months + 1):
        if pay_when == 1:
            # Annuity due: payment at the beginning of the period, then interest accrues.
            balance = max(0.0, balance - payment)
            interest = balance * rate
            balance += interest
        else:
            interest = balance * rate
            balance += interest
            balance = max(0.0, balance - payment)

        total_interest += interest
        total_payments += payment
        if month <= 12:
            year1_interest += interest
            year1_payments += payment
            year1_ending_balance = balance

    # The residual/balloon is paid at maturity, after the final scheduled instalment.
    total_payments += residual
    if months <= 12:
        year1_payments += residual
        year1_ending_balance = max(0.0, year1_ending_balance - residual)

    # Reconcile small floating-point drift to the contracted balloon.
    total_principal_repaid = max(0.0, principal - residual)
    year1_principal = max(0.0, principal - year1_ending_balance)
    if months <= 12:
        year1_principal = principal

    return {
        "monthly_payment": payment,
        "year1_interest": year1_interest,
        "year1_principal": year1_principal,
        "year1_payment": year1_payments,
        "total_interest": total_interest,
        "total_payments": total_payments,
        "year1_ending_balance": year1_ending_balance,
        "total_principal_repaid": total_principal_repaid,
    }


def get_baseline_financials(baseline_state):
    return FinancialEngine.calculate_statements(baseline_state)


def get_investment_funding_allocation(baseline_state, investment_assumptions):
    """Recalculate the funding gap from the active investment assumptions + company baseline."""
    project_id = st.session_state.get("investment_decision_id", "investment_project")
    plan = st.session_state.get("decision_plan")
    existing_project = None

    if isinstance(plan, DecisionPlan):
        existing_project = next(
            (
                item for item in plan.decisions
                if isinstance(item, InvestmentDecision) and item.id == project_id
            ),
            None,
        )

    metadata = dict(existing_project.metadata) if existing_project is not None else {}
    project = InvestmentDecision.create(
        decision_id=project_id,
        name=existing_project.name if existing_project is not None else "Investment Project",
        description=(
            existing_project.description if existing_project is not None
            else "Investment project with attached financing."
        ),
        assumptions=investment_assumptions,
        metadata=metadata,
    )
    _, impact = InvestmentIntegration.evaluate(baseline_state, project)
    return InvestmentFundingAllocator.allocate(baseline_state, [impact])


def _transfer_financing_to_investment(investment_assumptions, financing_preview, funding_allocation):
    if funding_allocation is None:
        raise ValueError("The investment funding requirement could not be calculated.")

    selected_option = financing_preview.get("selected_option")
    if selected_option not in ("Loan", "Leasing"):
        raise ValueError("Select Loan or Leasing before transferring the decision.")

    total_required = float(funding_allocation.total_external_funding_required)
    if total_required <= 0:
        raise ValueError("The project has no external funding gap. No financing is required.")

    plan = st.session_state.get("decision_plan")
    if not isinstance(plan, DecisionPlan):
        plan = DecisionPlan.create(plan_id="main_plan", name="Current Decision Plan")

    project_id = st.session_state.get("investment_decision_id", "investment_project")
    existing_project = next(
        (
            item for item in plan.decisions
            if isinstance(item, InvestmentDecision) and item.id == project_id
        ),
        None,
    )
    metadata = dict(existing_project.metadata) if existing_project is not None else {}

    financing_inputs = dict(financing_preview["financing_inputs"])
    selected_fee_key = "loan_fees" if selected_option == "Loan" else "leasing_fees"
    financing_costs = max(0.0, float(financing_inputs.get(selected_fee_key, 0.0)))
    allocation_data = {
        "external_capex_required": float(funding_allocation.external_capex_required),
        "external_working_capital_required": float(
            funding_allocation.external_working_capital_required
        ),
        "external_financing_costs_required": financing_costs,
        "total_external_funding_required": total_required + financing_costs,
    }
    metadata["financing_decision"] = {
        "selected_option": selected_option,
        "annual_payment": float(financing_preview["annual_payment"]),
        "final_burden": float(financing_preview["final_burden"]),
        "financing_inputs": financing_inputs,
        "funding_allocation": allocation_data,
        "source": "loan_vs_leasing",
    }

    project = InvestmentDecision.create(
        decision_id=project_id,
        name=existing_project.name if existing_project is not None else "Investment Project",
        description=(
            existing_project.description if existing_project is not None
            else "Investment project with attached financing."
        ),
        assumptions=investment_assumptions,
        metadata=metadata,
    )
    st.session_state.decision_plan = plan.add(project)


def _option_schedule(capex, working_capital, inputs, option):
    duration = inputs["duration_years"]
    pay_when = inputs["pay_when"]
    wc = _financing_schedule(
        working_capital, inputs["wc_rate"], duration, pay_when, 0.0
    )
    if option == "Loan":
        asset_rate = inputs["loan_rate"]
        residual = 0.0
        fee = inputs["loan_fees"]
    else:
        asset_rate = inputs["leasing_rate"]
        residual = min(capex, inputs["leasing_residual_value"])
        fee = inputs["leasing_fees"]

    # Transaction costs are assumed to be financed alongside CAPEX so they are
    # reflected in the principal, interest and integrated projection.
    asset_principal = capex + fee
    asset = _financing_schedule(asset_principal, asset_rate, duration, pay_when, residual)
    year1_payment = asset["year1_payment"] + wc["year1_payment"]
    year1_interest = asset["year1_interest"] + wc["year1_interest"]
    total_interest = asset["total_interest"] + wc["total_interest"]
    total_payments = asset["total_payments"] + wc["total_payments"]

    # Under the simplified finance-lease treatment, the leased asset is depreciated
    # over the selected period; financing fees are not depreciated.
    depreciable_base = max(0.0, capex - residual) if option == "Leasing" else capex
    depreciation = depreciable_base / max(1, inputs["depreciation_years"])
    depreciation_tax_shield = depreciation * inputs["tax_rate"] * min(
        duration, inputs["depreciation_years"]
    )
    interest_tax_shield = total_interest * inputs["tax_rate"]
    final_burden = max(
        0.0,
        total_payments
        - interest_tax_shield
        - depreciation_tax_shield,
    )
    return {
        "financed_amount": asset_principal + working_capital,
        "year1_payment": year1_payment,
        "year1_interest": year1_interest,
        "total_interest": total_interest,
        "total_payments": total_payments,
        "final_burden": final_burden,
        "fee": fee,
        "asset_schedule": asset,
        "wc_schedule": wc,
    }


def _profit_after_financing_interest(baseline_profit, baseline_ebt, tax_rate, interest):
    tax_before = max(0.0, baseline_ebt * tax_rate)
    tax_after = max(0.0, (baseline_ebt - interest) * tax_rate)
    return baseline_profit - interest + (tax_before - tax_after)


def render_loan_vs_leasing_lab(baseline_state):
    st.header("🏦 Loan vs Leasing Lab")
    st.info(
        "The funding amount comes from the active company diagnosis and investment project. "
        "The comparison below uses the project's actual uncovered CAPEX and working-capital "
        "need—not a separately entered property value."
    )

    investment_result = st.session_state.get("investment_result")
    investment_assumptions = st.session_state.get("investment_assumptions")
    project_available = investment_result is not None and investment_assumptions is not None

    baseline_financials = get_baseline_financials(baseline_state)
    baseline_is = baseline_financials.income_statement
    baseline_fcfe = baseline_financials.fcfe
    baseline_profit = baseline_is.net_profit

    funding_allocation = None
    allocation_error = None
    if project_available:
        try:
            funding_allocation = get_investment_funding_allocation(
                baseline_state, investment_assumptions
            )
        except Exception as exc:
            allocation_error = str(exc)

    st.subheader("Investment Funding Overview")
    if funding_allocation is None:
        st.warning(
            "An evaluated investment project is required to calculate the actual funding gap."
        )
        if allocation_error:
            st.error(f"Funding calculation failed: {allocation_error}")
    else:
        capex_col, wc_col = st.columns(2)
        capex_col.metric("Total Investment CAPEX", f"€{funding_allocation.total_capex:,.0f}")
        wc_col.metric(
            "Initial Working-Capital Need",
            f"€{funding_allocation.working_capital_need:,.0f}",
        )
        internal_allocated = (
            funding_allocation.internal_cash_to_working_capital
            + funding_allocation.internal_cash_to_capex
        )
        cash_col, allocated_col, gap_col = st.columns(3)
        cash_col.metric(
            "Internal Cash Available Above Reserve",
            f"€{funding_allocation.available_internal_cash:,.0f}",
        )
        allocated_col.metric("Internal Cash Allocated", f"€{internal_allocated:,.0f}")
        gap_col.metric(
            "Actual External Funding Required",
            f"€{funding_allocation.total_external_funding_required:,.0f}",
        )
        st.caption(
            "These values are recalculated from the baseline and investment assumptions. "
            "Loan and Leasing are compared against the same external funding gap."
        )

    st.divider()
    st.subheader("Financing Terms")
    rate_col, lease_rate_col, wc_rate_col, duration_col, timing_col = st.columns(5)
    with rate_col:
        loan_rate = st.number_input(
            "Loan Interest Rate (%)", min_value=0.0, max_value=100.0,
            value=6.0, step=0.25, key="ll_loan_rate"
        ) / 100
    with lease_rate_col:
        leasing_rate = st.number_input(
            "Leasing Rate (%)", min_value=0.0, max_value=100.0,
            value=6.5, step=0.25, key="ll_leasing_rate",
            help="Rate used to model a finance lease liability."
        ) / 100
    with wc_rate_col:
        wc_rate = st.number_input(
            "Working-Capital Loan Rate (%)", min_value=0.0, max_value=100.0,
            value=8.0, step=0.25, key="ll_wc_rate"
        ) / 100
    with duration_col:
        duration_years = st.number_input(
            "Duration (Years)", min_value=1, max_value=50,
            value=15, key="ll_duration_years"
        )
    with timing_col:
        pay_timing = st.radio(
            "Payment Timing", ["Beginning of Month", "End of Month"],
            key="ll_payment_timing"
        )
    pay_when = 1 if pay_timing == "Beginning of Month" else 0

    tax_col, depreciation_col = st.columns(2)
    tax_rate = float(baseline_state.capital_structure.tax_rate)
    with tax_col:
        st.metric("Corporate Tax Rate (from diagnosis)", f"{tax_rate * 100:.2f}%")
    with depreciation_col:
        depreciation_years = st.number_input(
            "Asset Depreciation Period (Years)", min_value=1, max_value=100,
            value=30, key="ll_depreciation_years",
            help="Used for the illustrative tax shield; project depreciation remains in the project model."
        )

    with st.expander("Additional transaction assumptions"):
        fees_col_loan, fees_col_lease = st.columns(2)
        with fees_col_loan:
            loan_fees = st.number_input(
                "Loan Transaction / Acquisition Costs (€)", min_value=0.0,
                value=0.0, step=1000.0, key="ll_expenses_loan"
            )
        with fees_col_lease:
            leasing_fees = st.number_input(
                "Leasing Transaction / Acquisition Costs (€)", min_value=0.0,
                value=0.0, step=1000.0, key="ll_expenses_leasing"
            )
        residual_value = st.number_input(
            "Leasing Residual / Balloon Value (€)", min_value=0.0,
            value=0.0, step=500.0, key="ll_residual_value",
            help="Balloon payment at the end of the term; capped at the CAPEX actually financed."
        )

    inputs = {
        "loan_rate": loan_rate,
        "leasing_rate": leasing_rate,
        "wc_rate": wc_rate,
        "duration_years": float(duration_years),
        "pay_when": pay_when,
        "tax_rate": tax_rate,
        "depreciation_years": int(depreciation_years),
        "loan_fees": loan_fees,
        "leasing_fees": leasing_fees,
        "leasing_residual_value": residual_value,
    }

    st.divider()
    st.subheader("Loan vs Leasing — Actual Project Funding")
    if funding_allocation is None:
        st.info("The comparison will be calculated when the investment project and funding gap are available.")
        return

    capex_required = float(funding_allocation.external_capex_required)
    wc_required = float(funding_allocation.external_working_capital_required)
    total_required = float(funding_allocation.total_external_funding_required)
    if total_required <= 0:
        st.success("The investment project has no external funding gap. Loan or Leasing is not required.")
        return

    loan = _option_schedule(capex_required, wc_required, inputs, "Loan")
    leasing = _option_schedule(capex_required, wc_required, inputs, "Leasing")

    col_loan, col_lease = st.columns(2)
    with col_loan:
        st.markdown("#### 🏦 Loan")
        st.metric("Total Amount Financed (including selected fees)", f"€{loan['financed_amount']:,.0f}")
        st.caption(f"Project funding gap: €{total_required:,.0f}; additional loan costs financed: €{loan_fees:,.0f}")
        st.metric("Estimated Total Burden After Tax", f"€{loan['final_burden']:,.0f}")
        st.caption(
            f"Year-1 payment: €{loan['year1_payment']:,.0f} · "
            f"Year-1 interest: €{loan['year1_interest']:,.0f}"
        )
    with col_lease:
        st.markdown("#### 📄 Leasing")
        st.metric("Total Amount Financed (including selected fees)", f"€{leasing['financed_amount']:,.0f}")
        st.caption(f"Project funding gap: €{total_required:,.0f}; additional leasing costs financed: €{leasing_fees:,.0f}")
        st.metric("Estimated Total Burden After Tax", f"€{leasing['final_burden']:,.0f}")
        st.caption(
            f"Year-1 payment: €{leasing['year1_payment']:,.0f} · "
            f"Year-1 interest: €{leasing['year1_interest']:,.0f}"
        )

    fig = go.Figure(
        go.Bar(
            x=["Loan", "Leasing"],
            y=[loan["final_burden"], leasing["final_burden"]],
            text=[f"€{loan['final_burden']:,.0f}", f"€{leasing['final_burden']:,.0f}"],
            textposition="auto",
        )
    )
    fig.update_layout(
        height=280, margin=dict(l=10, r=10, t=20, b=10),
        yaxis_title="Estimated Total Burden After Tax (€)",
    )
    st.plotly_chart(fig, use_container_width=True)

    st.caption(
        "Comparison assumptions: amortising loan versus finance-lease liability; "
        "working-capital need is financed separately at the working-capital rate. "
        "Tax shields are simplified estimates, not tax or accounting advice. "
        "The integrated projection uses the actual funding allocation and year-one "
        "interest/principal schedule; the project NPV, IRR and Payback are not recalculated "
        "by this financing comparison."
    )

    st.divider()
    st.subheader("First-Year Financing Consequence")
    left, loan_col, lease_col = st.columns([1.45, 1, 1])
    left.caption("MEASURE")
    loan_col.markdown("**🏦 Loan**")
    lease_col.markdown("**📄 Leasing**")

    def metric_row(label, loan_value, lease_value, fmt="€{:,.0f}"):
        c1, c2, c3 = st.columns([1.45, 1, 1])
        c1.caption(label)
        c2.metric(" ", fmt.format(loan_value), label_visibility="collapsed")
        c3.metric(" ", fmt.format(lease_value), label_visibility="collapsed")

    metric_row("Annual financing payment", loan["year1_payment"], leasing["year1_payment"])
    metric_row("Interest expense (year 1)", loan["year1_interest"], leasing["year1_interest"])
    loan_profit = _profit_after_financing_interest(
        baseline_profit, baseline_is.ebt, tax_rate, loan["year1_interest"]
    )
    lease_profit = _profit_after_financing_interest(
        baseline_profit, baseline_is.ebt, tax_rate, leasing["year1_interest"]
    )
    metric_row("Illustrative company net profit*", loan_profit, lease_profit)
    metric_row(
        "Company cash flow after debt service*",
        baseline_fcfe - loan["year1_payment"],
        baseline_fcfe - leasing["year1_payment"],
    )
    st.caption(
        "*Financing-only illustration against the baseline. The integrated projection "
        "adds the investment's operating impacts and handles initial project funding."
    )

    st.divider()
    st.subheader("🎯 Select the Financing Decision")
    selected_option = st.radio(
        "Choose one option", ["No financing decision", "Loan", "Leasing"],
        horizontal=True, key="ll_selected_option"
    )
    if selected_option == "No financing decision":
        st.caption("No financing decision will be attached to the investment project.")
        return

    chosen = loan if selected_option == "Loan" else leasing
    st.success(f"Selected decision: **{selected_option}**")
    selected_payment_col, selected_burden_col = st.columns(2)
    selected_payment_col.metric("Year-1 Financing Payment", f"€{chosen['year1_payment']:,.0f}")
    selected_burden_col.metric("Estimated Total Burden After Tax", f"€{chosen['final_burden']:,.0f}")

    financing_inputs = dict(inputs)
    financing_inputs["selected_option"] = selected_option
    st.session_state.loan_leasing_decision_preview = {
        "decision_type": "loan_vs_leasing",
        "selected_option": selected_option,
        "annual_payment": chosen["year1_payment"],
        "final_burden": chosen["final_burden"],
        "year_1_profit_before_decision": baseline_profit,
        "year_1_profit_after_decision": (
            loan_profit if selected_option == "Loan" else lease_profit
        ),
        "year_1_cash_before_decision": baseline_fcfe,
        "year_1_cash_after_decision": (
            baseline_fcfe - chosen["year1_payment"]
        ),
        "baseline_version": baseline_state.version,
        "financing_scope": "investment_project",
        "linked_investment_assumptions": investment_assumptions,
        "financing_inputs": financing_inputs,
    }

    st.divider()
    st.subheader("Transfer Financing to Investment Project")
    st.caption(
        "The selected option is attached to the existing investment decision; "
        "it is not added as a second, separate investment."
    )
    transfer_disabled = total_required <= 0 or not project_available
    if st.button(
        "Transfer Selected Financing to Investment Project",
        use_container_width=True,
        type="primary",
        disabled=transfer_disabled,
        key="transfer_financing_to_investment",
    ):
        try:
            _transfer_financing_to_investment(
                investment_assumptions=investment_assumptions,
                financing_preview=st.session_state.loan_leasing_decision_preview,
                funding_allocation=funding_allocation,
            )
            st.success(
                "Financing attached to the investment project and saved in the Current Decision Plan."
            )
        except Exception as exc:
            st.error(f"Error transferring financing: {exc}")
