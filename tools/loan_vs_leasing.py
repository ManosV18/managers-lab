# tools/loan_vs_leasing.py

import streamlit as st
import plotly.graph_objects as go

from core.financial_engine import FinancialEngine
from core.decision_plan import DecisionPlan
from core.investment_decision import InvestmentDecision


# =========================================================
# FORMATTING
# =========================================================

def format_number_gr(value):
    return f"{value:,.0f}"


# =========================================================
# FINANCIAL CALCULATIONS (STRICT & CORRECTED)
# =========================================================

def pmt_basic(rate, nper, pv, fv=0, when=0):
    """
    Standard financial PMT calculation (equivalent to Excel PMT).
    rate: periodic interest rate
    nper: total number of payment periods
    pv: present value / principal amount
    fv: future value (default 0)
    when: 0 = end of period, 1 = beginning of period
    """
    if rate == 0:
        return -(pv + fv) / nper

    factor = (1 + rate) ** nper
    payment = (pv * rate * factor) / (factor - 1)

    if when == 1:
        payment = payment / (1 + rate)

    return -payment  # Return positive periodic cash outflow


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
    """
    Rigorous calculation of total net financial burden for Loan vs Leasing.
    Properly handles financing percentages, working capital financing components,
    depreciation bases, tax deductibility, and residual value elements.
    """
    months = 12
    n_months = int(duration_years * months)
    if n_months <= 0:
        n_months = 12

    # Periodic rates
    monthly_loan_rate = loan_rate / months
    monthly_wc_rate = wc_rate / months

    # 1. Principal amounts financed
    loan_principal = property_value * loan_financing_percent
    lease_principal = property_value * leasing_financing_percent

    # 2. Self-funded down payments / unfinanced acquisition expenses
    # For a loan, any gap plus acquisition expenses require funding/working capital
    unfinanced_loan_capex = max(0.0, property_value - loan_principal) + add_expenses_loan
    unfinanced_lease_capex = max(0.0, property_value - lease_principal) + add_expenses_leasing

    # 3. Monthly debt/lease service installments
    monthly_payment_loan = pmt_basic(monthly_loan_rate, n_months, loan_principal, 0, pay_when)
    monthly_payment_lease = pmt_basic(monthly_loan_rate, n_months, lease_principal, -residual_value_leasing, pay_when)

    # 4. Monthly servicing for unfinanced capital/expenses (using working capital rate)
    monthly_wc_service_loan = pmt_basic(monthly_wc_rate, n_months, unfinanced_loan_capex, 0, pay_when)
    monthly_wc_service_lease = pmt_basic(monthly_wc_rate, n_months, unfinanced_lease_capex, 0, pay_when)

    total_monthly_loan = monthly_payment_loan + monthly_wc_service_loan
    total_monthly_lease = monthly_payment_lease + monthly_wc_service_lease

    # Total nominal payments over duration
    total_nominal_loan = total_monthly_loan * n_months + unfinanced_loan_capex
    total_nominal_lease = total_monthly_lease * n_months + unfinanced_lease_capex + residual_value_leasing

    # 5. Acquisition bases and Tax Shields (Depreciation & Interest)
    # Total asset acquisition cost including expenses
    acquisition_cost_loan = property_value + add_expenses_loan
    acquisition_cost_lease = property_value + add_expenses_leasing

    # Annual depreciation (Straight-line over depreciation_years, scaled to duration)
    annual_depr_loan = acquisition_cost_loan / max(1.0, float(depreciation_years))
    total_depr_loan = annual_depr_loan * duration_years

    # For leasing, lease payments are generally tax-deductible operating expenses (or depreciation + interest equivalent).
    # We estimate tax deductions: total lease payments plus any capitalized expenses depreciation / residual adjustments.
    total_interest_equivalent_loan = (monthly_payment_loan * n_months) - loan_principal
    total_interest_equivalent_lease = (monthly_payment_lease * n_months) - lease_principal

    # Tax deductible expenses base over the duration:
    # Loan: Interest paid + Depreciation of total acquisition cost
    deductible_loan = total_interest_equivalent_loan + total_depr_loan

    # Leasing: Lease installments paid (operating lease expense model) + residual adjustments if applicable
    deductible_lease = (monthly_payment_lease * n_months) + (monthly_wc_service_lease * n_months)

    tax_benefit_loan = deductible_loan * tax_rate
    tax_benefit_lease = deductible_lease * tax_rate

    # Net final burden = Total nominal cash outflows minus tax shields
    final_loan = total_nominal_loan - tax_benefit_loan
    final_lease = total_nominal_lease - tax_benefit_lease

    return (
        round(final_loan, 2),
        round(final_lease, 2),
        total_monthly_loan,
        total_monthly_lease,
    )


# =========================================================
# BASELINE FINANCIALS
# =========================================================

def get_baseline_financials(baseline_state):
    return FinancialEngine.calculate_statements(baseline_state)


# =========================================================
# HELPER FOR FINANCING TRANSFER TO INVESTMENT PROJECT
# =========================================================

def _transfer_financing_to_investment(
    investment_assumptions,
    financing_preview,
):
    """
    Attach the selected financing option to the active investment project
    and save/update it in the Current Decision Plan.
    """
    plan = st.session_state.get("decision_plan")
    if not isinstance(plan, DecisionPlan):
        plan = DecisionPlan.create(
            plan_id="main_plan",
            name="Current Decision Plan",
        )
    project_id = st.session_state.get(
        "investment_decision_id",
        "investment_project",
    )
    existing_project = next(
        (
            item
            for item in plan.decisions
            if (
                isinstance(item, InvestmentDecision)
                and item.id == project_id
            )
        ),
        None,
    )
    metadata = (
        dict(existing_project.metadata)
        if existing_project is not None
        else {}
    )
    metadata["financing_decision"] = {
        "selected_option": financing_preview["selected_option"],
        "annual_payment": financing_preview["annual_payment"],
        "final_burden": financing_preview["final_burden"],
        "financing_inputs": dict(
            financing_preview.get("financing_inputs", {})
        ),
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
            else "Investment project with integrated financing structure."
        ),
        assumptions=investment_assumptions,
        metadata=metadata,
    )
    st.session_state.decision_plan = plan.add(project)


# =========================================================
# DECISION LAB UI
# =========================================================

def render_loan_vs_leasing_lab(baseline_state):

    st.header("🏦 Loan vs Leasing Lab")

    st.info(
        """
        Compare Loan versus Leasing financing structures and evaluate 
        their economic impact on company cash flows and profitability.
        The locked baseline remains unmodified.
        """
    )

    # Link analysis to active investment project if available
    investment_result = st.session_state.get("investment_result")
    investment_assumptions = st.session_state.get("investment_assumptions")
    project_available = (
        investment_result is not None
        and investment_assumptions is not None
    )

    if project_available:
        st.info(
            "🔗 Financing analysis is linked to the active investment project "
            "evaluated in the Investment Decision Lab. Selecting Loan or Leasing "
            "will attach the financing structure without altering project NPV, IRR, or Payback."
        )
    else:
        st.warning(
            "⚠️ No active evaluated investment project found. You can still compare "
            "Loan and Leasing options, but the choice will remain an unlinked corporate comparison."
        )

    # =====================================================
    # BASELINE FINANCIALS
    # =====================================================

    baseline_financials = get_baseline_financials(baseline_state)
    baseline_is = baseline_financials.income_statement
    baseline_fcfe = baseline_financials.fcfe
    baseline_profit = baseline_is.net_profit

    # =====================================================
    # INPUT PARAMETERS
    # =====================================================

    st.subheader("Financing Terms & Assumptions")

    col1, col2 = st.columns(2)

    with col1:
        loan_rate = (
            st.number_input(
                "Loan Interest Rate (%)",
                min_value=0.0,
                value=6.0,
                step=0.25,
            )
            / 100.0
        )

        wc_rate = (
            st.number_input(
                "Working Capital / Gap Interest Rate (%)",
                min_value=0.0,
                value=8.0,
                step=0.25,
            )
            / 100.0
        )

        duration_years = st.number_input(
            "Financing Duration (Years)",
            min_value=1,
            value=15,
            step=1,
        )

        pay_timing = st.radio(
            "Payment Timing",
            [
                "Beginning of Month",
                "End of Month",
            ],
        )

        pay_when = 1 if pay_timing == "Beginning of Month" else 0

        tax_rate = (
            st.number_input(
                "Corporate Tax Rate (%)",
                min_value=0.0,
                max_value=100.0,
                value=float(baseline_state.capital_structure.tax_rate * 100.0),
                step=1.0,
            )
            / 100.0
        )

    with col2:
        st.subheader("Asset / Investment Details")

        property_value = st.number_input(
            "Asset Commercial / Acquisition Value (€)",
            min_value=0.0,
            value=250000.0,
            step=10000.0,
        )

        loan_financing = (
            st.number_input(
                "Loan Financing Coverage (%)",
                min_value=0.0,
                max_value=100.0,
                value=70.0,
                step=5.0,
            )
            / 100.0
        )

        leasing_financing = (
            st.number_input(
                "Leasing Financing Coverage (%)",
                min_value=0.0,
                max_value=100.0,
                value=100.0,
                step=5.0,
            )
            / 100.0
        )

        add_expenses_loan = st.number_input(
            "Acquisition Expenses — Loan (€)",
            min_value=0.0,
            value=35000.0,
            step=1000.0,
        )

        add_expenses_leasing = st.number_input(
            "Acquisition Expenses — Leasing (€)",
            min_value=0.0,
            value=30000.0,
            step=1000.0,
        )

        residual_value = st.number_input(
            "Leasing Residual Value (€)",
            min_value=0.0,
            value=3530.0,
            step500=100.0 if "step500" in globals() else 500.0,
        )

        depreciation_years = st.number_input(
            "Depreciation Period (Years)",
            min_value=1,
            value=30,
            step=1,
        )

    st.divider()

    # =====================================================
    # CALCULATIONS
    # =====================================================

    (
        final_loan,
        final_leasing,
        monthly_loan,
        monthly_lease,
    ) = calculate_final_burden(
        loan_rate=loan_rate,
        wc_rate=wc_rate,
        duration_years=duration_years,
        property_value=property_value,
        loan_financing_percent=loan_financing,
        leasing_financing_percent=leasing_financing,
        add_expenses_loan=add_expenses_loan,
        add_expenses_leasing=add_expenses_leasing,
        residual_value_leasing=residual_value,
        depreciation_years=depreciation_years,
        tax_rate=tax_rate,
        pay_when=pay_when,
    )

    annual_payment_loan = abs(monthly_loan) * 12.0
    annual_payment_lease = abs(monthly_lease) * 12.0

    # =====================================================
    # YEAR-1 ECONOMIC CONSEQUENCES
    # =====================================================

    loan_profit_impact = baseline_profit - annual_payment_loan
    lease_profit_impact = baseline_profit - annual_payment_lease

    loan_cash_impact = baseline_fcfe - annual_payment_loan
    lease_cash_impact = baseline_fcfe - annual_payment_lease

    # =====================================================
    # COMPARISON DISPLAY & PLOT
    # =====================================================

    st.subheader("📊 Financing Burden Comparison")

    m1, m2 = st.columns(2)

    m1.metric(
        "Loan — Net Total Financing Burden",
        f"€{format_number_gr(final_loan)}",
    )

    m2.metric(
        "Leasing — Net Total Financing Burden",
        f"€{format_number_gr(final_leasing)}",
    )

    fig = go.Figure(
        go.Bar(
            x=["Loan", "Leasing"],
            y=[final_loan, final_leasing],
            text=[
                f"€{format_number_gr(final_loan)}",
                f"€{format_number_gr(final_leasing)}",
            ],
            textposition="auto",
            marker_color=["#1f77b4", "#ff7f0e"],
        )
    )

    fig.update_layout(
        height=320,
        yaxis_title="Total Net Financing Burden (€)",
        margin=dict(l=20, r=20, t=30, b=20),
    )

    st.plotly_chart(fig, use_container_width=True)

    # =====================================================
    # FIRST-YEAR CONSEQUENCES
    # =====================================================

    st.divider()
    st.subheader("📅 First-Year Economic Consequence")

    c1, c2 = st.columns(2)

    with c1:
        st.markdown("### 🏦 Loan Structure")
        st.metric(
            "Total Annual Financing Payment",
            f"€{annual_payment_loan:,.0f}",
        )
        st.metric(
            "Illustrative Net Profit After Financing",
            f"€{loan_profit_impact:,.0f}",
            delta=f"€{loan_profit_impact - baseline_profit:,.0f}",
        )
        st.metric(
            "Illustrative FCFE After Financing",
            f"€{loan_cash_impact:,.0f}",
            delta=f"€{loan_cash_impact - baseline_fcfe:,.0f}",
        )

    with c2:
        st.markdown("### 📄 Leasing Structure")
        st.metric(
            "Total Annual Financing Payment",
            f"€{annual_payment_lease:,.0f}",
        )
        st.metric(
            "Illustrative Net Profit After Financing",
            f"€{lease_profit_impact:,.0f}",
            delta=f"€{lease_profit_impact - baseline_profit:,.0f}",
        )
        st.metric(
            "Illustrative FCFE After Financing",
            f"€{lease_cash_impact:,.0f}",
            delta=f"€{lease_cash_impact - baseline_fcfe:,.0f}",
        )

    # =====================================================
    # SELECTION & PREVIEW
    # =====================================================

    st.divider()
    st.subheader("🎯 Select Financing Option")

    selected_option = st.radio(
        "Choose financing alternative",
        [
            "No financing decision",
            "Loan",
            "Leasing",
        ],
        horizontal=True,
    )

    if selected_option == "No financing decision":
        st.caption("No financing decision selected for the plan.")
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

    st.success(f"Selected Financing Decision: **{selected_option}**")

    p_col1, p_col2 = st.columns(2)
    p_col1.metric("Annual Installment Payment", f"€{annual_payment:,.0f}")
    p_col2.metric("Total Net Burden", f"€{final_burden:,.0f}")

    # Store session preview
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
        "Financing structure prepared and ready for integration "
        "into the Decision Plan / Control Tower."
    )

    # =====================================================
    # TRANSFER BUTTON TO INVESTMENT PROJECT
    # =====================================================

    st.divider()
    st.subheader("Transfer Financing to Investment Project")

    if project_available:
        st.caption(
            "Transfer the selected Loan or Leasing structure directly "
            "to the active investment project in the Decision Plan."
        )
    else:
        st.warning(
            "⚠️ Active investment project required to attach financing."
        )

    if st.button(
        "Transfer Selected Financing to Investment Project",
        use_container_width=True,
        type="primary",
        disabled=(
            not project_available
            or selected_option == "No financing decision"
        ),
        key="transfer_financing_to_investment",
    ):
        try:
            _transfer_financing_to_investment(
                investment_assumptions=investment_assumptions,
                financing_preview=st.session_state.loan_leasing_decision_preview,
            )
            st.success(
                "✅ Financing structure successfully attached to the investment project "
                "and saved in the Current Decision Plan."
            )
        except Exception as exc:
            st.error(f"Error transferring financing structure: {exc}")
