# tools/loan_vs_leasing.py

import streamlit as st
import plotly.graph_objects as go

from core.financial_engine import FinancialEngine
from core.decision_plan import DecisionPlan
from core.investment_decision import InvestmentDecision
from core.investment_funding import InvestmentFundingAllocator
from core.investment_integration import InvestmentIntegration


# =========================================================
# FORMATTING
# =========================================================

def format_number_gr(value):
    return f"{value:,.0f}"


# =========================================================
# EXISTING FINANCING CALCULATION (ILLUSTRATIVE COMPARISON)
# =========================================================

def pmt_basic(rate, nper, pv, fv=0, when=0):
    if nper <= 0:
        return 0.0

    if rate == 0:
        return -(pv + fv) / nper

    factor = (1 + rate) ** nper
    payment = (pv * rate * factor) / (factor - 1)

    if when == 1:
        payment = payment / (1 + rate)

    return payment


def calculate_final_burden(
    loan_rate,
    wc_rate,
    duration_years,
    property_value,
    loan_financing_percent,
    leasing_financing_percent,
    add_expenses_loan,
    add_expenses_leasing,
    residual_value_leasing,
    depreciation_years,
    tax_rate,
    pay_when,
):
    months = 12
    n_months = int(duration_years * months)

    if n_months <= 0:
        return 0, 0, 0.0, 0.0

    acquisition_cost_loan = property_value + add_expenses_loan
    acquisition_cost_lease = property_value + add_expenses_leasing

    wc_loan = (
        property_value
        - property_value * loan_financing_percent
        + add_expenses_loan
    )
    wc_lease = (
        property_value
        - property_value * leasing_financing_percent
        + add_expenses_leasing
    )

    monthly_loan = pmt_basic(
        loan_rate / months,
        n_months,
        property_value * loan_financing_percent,
        0,
        pay_when,
    )
    monthly_lease = pmt_basic(
        loan_rate / months,
        n_months,
        property_value * leasing_financing_percent,
        0,
        pay_when,
    )
    monthly_wc_loan = pmt_basic(
        wc_rate / months, n_months, wc_loan, 0, pay_when
    )
    monthly_wc_lease = pmt_basic(
        wc_rate / months, n_months, wc_lease, 0, pay_when
    )

    total_monthly_loan = monthly_loan + monthly_wc_loan
    total_monthly_lease = monthly_lease + monthly_wc_lease

    total_interest_loan = (
        total_monthly_loan * n_months
    ) - property_value
    total_interest_lease = (
        total_monthly_lease * n_months
    ) - property_value

    total_cost_loan = total_interest_loan + property_value
    total_cost_lease = total_interest_lease + property_value

    depreciation_loan = (
        acquisition_cost_loan / depreciation_years * duration_years
    )
    depreciation_lease = (
        acquisition_cost_lease / depreciation_years * duration_years
    ) + residual_value_leasing

    deductible_loan = total_interest_loan + depreciation_loan
    deductible_lease = (
        monthly_wc_lease * n_months - wc_lease + depreciation_lease
    )

    tax_benefit_loan = deductible_loan * tax_rate
    tax_benefit_lease = deductible_lease * tax_rate

    final_loan = total_cost_loan - tax_benefit_loan
    final_lease = total_cost_lease - tax_benefit_lease

    return (
        round(final_loan),
        round(final_lease),
        total_monthly_loan,
        total_monthly_lease,
    )


def _preview_first_year_interest(
    asset_principal,
    working_capital_principal,
    asset_rate,
    working_capital_rate,
    duration_years,
    pay_when,
):
    """Interest expense for the illustrative comparison only."""
    asset_schedule = FinancialEngine._year_one_financing_schedule(
        principal=max(0.0, float(asset_principal)),
        annual_rate=max(0.0, float(asset_rate)),
        duration_years=max(1, int(duration_years)),
        pay_when=pay_when,
    )
    wc_schedule = FinancialEngine._year_one_financing_schedule(
        principal=max(0.0, float(working_capital_principal)),
        annual_rate=max(0.0, float(working_capital_rate)),
        duration_years=max(1, int(duration_years)),
        pay_when=pay_when,
    )
    return (
        asset_schedule["interest_expense"]
        + wc_schedule["interest_expense"]
    )


def _illustrative_profit_after_interest(
    baseline_profit,
    baseline_ebt,
    tax_rate,
    interest_expense,
):
    """Reduce profit by interest, accounting for the associated tax effect."""
    tax_before_at_selected_rate = max(0.0, baseline_ebt * tax_rate)
    tax_after_interest = max(
        0.0, (baseline_ebt - interest_expense) * tax_rate
    )
    return baseline_profit - interest_expense + (
        tax_before_at_selected_rate - tax_after_interest
    )


# =========================================================
# BASELINE FINANCIALS
# =========================================================

def get_baseline_financials(baseline_state):
    return FinancialEngine.calculate_statements(baseline_state)


def get_investment_funding_allocation(
    baseline_state,
    investment_assumptions,
):
    """Calculate the investment's uncovered CAPEX and initial NWC needs."""
    project_id = st.session_state.get(
        "investment_decision_id", "investment_project"
    )
    plan = st.session_state.get("decision_plan")
    existing_project = None

    if isinstance(plan, DecisionPlan):
        existing_project = next(
            (
                item
                for item in plan.decisions
                if isinstance(item, InvestmentDecision) and item.id == project_id
            ),
            None,
        )

    metadata = (
        dict(existing_project.metadata)
        if existing_project is not None
        else {}
    )
    project = InvestmentDecision.create(
        decision_id=project_id,
        name=(
            existing_project.name
            if existing_project is not None
            else "Investment Project"
        ),
        description=(
            existing_project.description
            if existing_project is not None
            else "Investment project with attached financing."
        ),
        assumptions=investment_assumptions,
        metadata=metadata,
    )
    _, impact = InvestmentIntegration.evaluate(baseline_state, project)
    return InvestmentFundingAllocator.allocate(baseline_state, [impact])


# =========================================================
# HELPER FOR FINANCING TRANSFER
# =========================================================

def _transfer_financing_to_investment(
    investment_assumptions,
    financing_preview,
    funding_allocation,
):
    """Attach financing terms and the actual funding allocation to the project."""
    if funding_allocation is None:
        raise ValueError(
            "The investment funding allocation could not be calculated. "
            "Reopen the Investment Decision Lab and try again."
        )

    plan = st.session_state.get("decision_plan")
    if not isinstance(plan, DecisionPlan):
        plan = DecisionPlan.create(
            plan_id="main_plan",
            name="Current Decision Plan",
        )

    project_id = st.session_state.get(
        "investment_decision_id", "investment_project"
    )
    existing_project = next(
        (
            item
            for item in plan.decisions
            if isinstance(item, InvestmentDecision) and item.id == project_id
        ),
        None,
    )
    metadata = (
        dict(existing_project.metadata)
        if existing_project is not None
        else {}
    )

    allocation_data = {
        "external_capex_required": float(
            funding_allocation.external_capex_required
        ),
        "external_working_capital_required": float(
            funding_allocation.external_working_capital_required
        ),
        "total_external_funding_required": float(
            funding_allocation.total_external_funding_required
        ),
    }

    # Store a copy of the funding need calculated by the allocator.
    # The financial engine uses this instead of the illustrative property-value inputs.
    metadata["financing_decision"] = {
        "selected_option": financing_preview["selected_option"],
        "annual_payment": financing_preview["annual_payment"],
        "final_burden": financing_preview["final_burden"],
        "financing_inputs": dict(
            financing_preview.get("financing_inputs", {})
        ),
        "funding_allocation": allocation_data,
        "source": "loan_vs_leasing",
    }

    project = InvestmentDecision.create(
        decision_id=project_id,
        name=(
            existing_project.name
            if existing_project is not None
            else "Investment Project"
        ),
        description=(
            existing_project.description
            if existing_project is not None
            else "Investment project with attached financing."
        ),
        assumptions=investment_assumptions,
        metadata=metadata,
    )
    st.session_state.decision_plan = plan.add(project)


# =========================================================
# DECISION LAB
# =========================================================

def render_loan_vs_leasing_lab(baseline_state):
    st.header("🏦 Loan vs Leasing Lab")

    st.info(
        """
        Compare a new Loan or Leasing decision and see its economic consequence.

        The locked baseline is not changed. The financing comparison below is
        illustrative; the integrated projection uses the investment's actual
        uncovered CAPEX and initial working-capital requirement.
        """
    )

    investment_result = st.session_state.get("investment_result")
    investment_assumptions = st.session_state.get("investment_assumptions")
    project_available = (
        investment_result is not None and investment_assumptions is not None
    )

    if project_available:
        st.info(
            "Financing is evaluated for the investment project evaluated in the "
            "Investment Decision Lab. Selecting Loan/Leasing does not alter NPV, "
            "IRR, or Payback."
        )
    else:
        st.warning(
            "No evaluated investment project available. You can compare Loan "
            "and Leasing, but the choice will not be linked to a specific project."
        )

    # =====================================================
    # BASELINE
    # =====================================================
    baseline_financials = get_baseline_financials(baseline_state)
    baseline_is = baseline_financials.income_statement
    baseline_fcfe = baseline_financials.fcfe
    baseline_profit = baseline_is.net_profit

    # =====================================================
    # INPUTS
    # =====================================================
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Financing Terms")
        loan_rate = st.number_input("Loan Interest Rate (%)", value=6.0) / 100
        wc_rate = (
            st.number_input("Working Capital Interest Rate (%)", value=8.0)
            / 100
        )
        duration_years = st.number_input(
            "Duration (Years)", value=15, min_value=1
        )
        pay_timing = st.radio(
            "Payment Timing", ["Beginning of Month", "End of Month"]
        )
        pay_when = 1 if pay_timing == "Beginning of Month" else 0
        tax_rate = (
            st.number_input(
                "Corporate Tax Rate (%)",
                value=float(baseline_state.capital_structure.tax_rate * 100),
            )
            / 100
        )

    with col2:
        st.subheader("Investment Details")
        funding_allocation = None

        if project_available:
            try:
                funding_allocation = get_investment_funding_allocation(
                    baseline_state, investment_assumptions
                )
            except Exception as exc:
                st.error(f"Could not calculate the investment funding requirement: {exc}")

        if funding_allocation is not None:
            st.metric("Investment CAPEX", f"€{funding_allocation.total_capex:,.0f}")
            st.metric(
                "Initial Working-Capital Need",
                f"€{funding_allocation.working_capital_need:,.0f}",
            )
            st.metric(
                "Internal Cash Available Above Reserve",
                f"€{funding_allocation.available_internal_cash:,.0f}",
            )
            st.metric(
                "Internal Cash Allocated",
                f"€{(funding_allocation.internal_cash_to_working_capital + funding_allocation.internal_cash_to_capex):,.0f}",
            )
            st.metric(
                "External Funding Required",
                f"€{funding_allocation.total_external_funding_required:,.0f}",
            )

        st.caption(
            "The following property-value assumptions are used only for the "
            "illustrative Loan-versus-Leasing comparison. They do not determine "
            "the debt amount transferred to the integrated company projection."
        )
        property_value = st.number_input(
            "Property Commercial Value (€)", value=250000.0, min_value=0.0
        )
        loan_financing = (
            st.number_input("Loan Financing (%)", value=70.0, min_value=0.0, max_value=100.0)
            / 100
        )
        leasing_financing = (
            st.number_input("Leasing Financing (%)", value=100.0, min_value=0.0, max_value=100.0)
            / 100
        )
        add_expenses_loan = st.number_input(
            "Acquisition Expenses — Loan (€)", value=35000.0, min_value=0.0
        )
        add_expenses_leasing = st.number_input(
            "Acquisition Expenses — Leasing (€)", value=30000.0, min_value=0.0
        )
        residual_value = st.number_input(
            "Leasing Residual Value (€)", value=3530.0, min_value=0.0
        )
        depreciation_years = st.number_input(
            "Depreciation Period (Years)", value=30, min_value=1
        )

    st.divider()

    # =====================================================
    # ILLUSTRATIVE FINANCING CALCULATION
    # =====================================================
    (
        final_loan,
        final_leasing,
        monthly_loan,
        monthly_lease,
    ) = calculate_final_burden(
        loan_rate,
        wc_rate,
        duration_years,
        property_value,
        loan_financing,
        leasing_financing,
        add_expenses_loan,
        add_expenses_leasing,
        residual_value,
        depreciation_years,
        tax_rate,
        pay_when,
    )

    annual_payment_loan = abs(monthly_loan) * 12
    annual_payment_lease = abs(monthly_lease) * 12

    wc_loan = (
        property_value - property_value * loan_financing + add_expenses_loan
    )
    wc_lease = (
        property_value - property_value * leasing_financing + add_expenses_leasing
    )
    loan_interest_year = _preview_first_year_interest(
        property_value * loan_financing,
        wc_loan,
        loan_rate,
        wc_rate,
        duration_years,
        pay_when,
    )
    lease_interest_year = _preview_first_year_interest(
        property_value * leasing_financing,
        wc_lease,
        loan_rate,
        wc_rate,
        duration_years,
        pay_when,
    )

    # Profit is affected by interest and its tax effect, not by principal repayment.
    loan_profit_impact = _illustrative_profit_after_interest(
        baseline_profit, baseline_is.ebt, tax_rate, loan_interest_year
    )
    lease_profit_impact = _illustrative_profit_after_interest(
        baseline_profit, baseline_is.ebt, tax_rate, lease_interest_year
    )

    # This is only a financing-payment illustration; project CAPEX and loan proceeds
    # are handled separately by the integrated investment projection.
    loan_cash_impact = baseline_fcfe - annual_payment_loan
    lease_cash_impact = baseline_fcfe - annual_payment_lease

    # =====================================================
    # FINANCING COMPARISON
    # =====================================================
    st.subheader("📊 Financing Comparison")
    m1, m2 = st.columns(2)
    m1.metric("Loan — Net Financing Burden", f"€{format_number_gr(final_loan)}")
    m2.metric("Leasing — Net Financing Burden", f"€{format_number_gr(final_leasing)}")

    fig = go.Figure(
        go.Bar(
            x=["Loan", "Leasing"],
            y=[final_loan, final_leasing],
            text=[f"€{format_number_gr(final_loan)}", f"€{format_number_gr(final_leasing)}"],
            textposition="auto",
        )
    )
    fig.update_layout(height=300, yaxis_title="Total Financing Burden (€)")
    st.plotly_chart(fig, use_container_width=True)

    # =====================================================
    # YEAR-1 CONSEQUENCE
    # =====================================================
    st.divider()
    st.subheader("📅 First-Year Economic Consequence")
    c1, c2 = st.columns(2)

    with c1:
        st.markdown("### 🏦 Loan")
        st.metric("Total Annual Financing Payment", f"€{annual_payment_loan:,.0f}")
        st.metric(
            "Illustrative Net Profit",
            f"€{loan_profit_impact:,.0f}",
            delta=f"€{loan_profit_impact - baseline_profit:,.0f}",
        )
        st.metric(
            "Illustrative Cash Flow (before project CAPEX)",
            f"€{loan_cash_impact:,.0f}",
            delta=f"€{loan_cash_impact - baseline_fcfe:,.0f}",
        )

    with c2:
        st.markdown("### 📄 Leasing")
        st.metric("Total Annual Leasing Payment", f"€{annual_payment_lease:,.0f}")
        st.metric(
            "Illustrative Net Profit",
            f"€{lease_profit_impact:,.0f}",
            delta=f"€{lease_profit_impact - baseline_profit:,.0f}",
        )
        st.metric(
            "Illustrative Cash Flow (before project CAPEX)",
            f"€{lease_cash_impact:,.0f}",
            delta=f"€{lease_cash_impact - baseline_fcfe:,.0f}",
        )

    # =====================================================
    # DECISION SELECTION
    # =====================================================
    st.divider()
    st.subheader("🎯 Select the financing decision")
    selected_option = st.radio(
        "Choose one option",
        ["No financing decision", "Loan", "Leasing"],
        horizontal=True,
    )

    if selected_option == "No financing decision":
        st.caption("No Decision will be added to the Decision Plan.")
        return

    if selected_option == "Loan":
        annual_payment = annual_payment_loan
        final_burden = final_loan
        profit_after = loan_profit_impact
        cash_after = loan_cash_impact
    else:
        annual_payment = annual_payment_lease
        final_burden = final_leasing
        profit_after = lease_profit_impact
        cash_after = lease_cash_impact

    st.success(f"Selected decision: **{selected_option}**")
    st.metric("Total Annual Financing Payment", f"€{annual_payment:,.0f}")
    st.metric("Total Financing Burden", f"€{final_burden:,.0f}")

    # =====================================================
    # DECISION PREVIEW
    # =====================================================
    st.session_state.loan_leasing_decision_preview = {
        "decision_type": "loan_vs_leasing",
        "selected_option": selected_option,
        "annual_payment": annual_payment,
        "final_burden": final_burden,
        "year_1_profit_before_decision": baseline_profit,
        "year_1_profit_after_decision": profit_after,
        "year_1_cash_before_decision": baseline_fcfe,
        "year_1_cash_after_decision": cash_after,
        "baseline_version": baseline_state.version,
        "financing_scope": "investment_project" if project_available else "unlinked_comparison",
        "linked_investment_assumptions": investment_assumptions if project_available else None,
        "financing_inputs": {
            "loan_rate": loan_rate,
            "wc_rate": wc_rate,
            "duration_years": duration_years,
            "property_value": property_value,
            "loan_financing_percent": loan_financing,
            "leasing_financing_percent": leasing_financing,
            "add_expenses_loan": add_expenses_loan,
            "add_expenses_leasing": add_expenses_leasing,
            "residual_value_leasing": residual_value,
            "depreciation_years": depreciation_years,
            "tax_rate": tax_rate,
            "pay_when": pay_when,
        },
    }

    st.success(
        "Financing decision prepared. The integrated projection will recalculate "
        "interest and principal from the actual uncovered funding requirement."
    )

    # =====================================================
    # TRANSFER BUTTON TO INVESTMENT PROJECT
    # =====================================================
    st.divider()
    st.subheader("Transfer Financing to Investment Project")

    if project_available:
        st.caption(
            "Transfer the selected Loan or Leasing option to the investment project. "
            "The project is not added as a separate company decision."
        )
    else:
        st.warning("Active investment project required to attach financing.")

    if st.button(
        "Transfer Selected Financing to Investment Project",
        use_container_width=True,
        type="primary",
        disabled=(not project_available or funding_allocation is None),
        key="transfer_financing_to_investment",
    ):
        try:
            _transfer_financing_to_investment(
                investment_assumptions=investment_assumptions,
                financing_preview=st.session_state.loan_leasing_decision_preview,
                funding_allocation=funding_allocation,
            )
            st.success(
                "Financing attached to the investment project and saved in the "
                "Current Decision Plan."
            )
        except Exception as exc:
            st.error(f"Error transferring financing: {exc}")
