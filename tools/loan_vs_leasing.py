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


def _parse_percent_input(raw_value, label):
    """Parse a user-entered percentage; blank is intentionally not a rate."""
    raw = str(raw_value).strip().replace("%", "").replace(",", ".")
    if not raw:
        return None
    try:
        value = float(raw)
    except (TypeError, ValueError):
        raise ValueError(f"{label}: enter a valid percentage, e.g. 6.5")
    if value < 0 or value > 100:
        raise ValueError(f"{label}: the percentage must be between 0 and 100.")
    return value / 100.0


def _allocation_with_custom_internal_cash(base_allocation, internal_cash_to_use):
    """Return a funding-allocation-like object without mutating project/source data."""
    from types import SimpleNamespace

    available = max(0.0, float(base_allocation.available_internal_cash))
    capex = max(0.0, float(base_allocation.total_capex))
    working_capital = max(0.0, float(base_allocation.working_capital_need))
    total_need = capex + working_capital
    internal_used = min(max(0.0, float(internal_cash_to_use)), available, total_need)

    # Allocate internal cash to working capital first, then CAPEX, consistently.
    internal_wc = min(working_capital, internal_used)
    internal_capex = min(capex, max(0.0, internal_used - internal_wc))
    external_wc = max(0.0, working_capital - internal_wc)
    external_capex = max(0.0, capex - internal_capex)

    return SimpleNamespace(
        total_capex=capex,
        working_capital_need=working_capital,
        available_internal_cash=available,
        internal_cash_to_working_capital=internal_wc,
        internal_cash_to_capex=internal_capex,
        external_capex_required=external_capex,
        external_working_capital_required=external_wc,
        total_external_funding_required=external_capex + external_wc,
    )


def render_loan_vs_leasing_lab(baseline_state):
    st.header("🏦 Loan vs Leasing Lab")
    st.write(
        "Review the existing project and company figures, then change any financing "
        "assumption you want to test. Changes in this screen are scenario inputs only; "
        "they do not overwrite the original diagnosis or investment assumptions."
    )

    investment_result = st.session_state.get("investment_result")
    investment_assumptions = st.session_state.get("investment_assumptions")
    project_available = investment_result is not None and investment_assumptions is not None

    baseline_financials = get_baseline_financials(baseline_state)
    baseline_is = baseline_financials.income_statement
    baseline_fcfe = baseline_financials.fcfe
    baseline_profit = baseline_is.net_profit
    tax_rate = float(baseline_state.capital_structure.tax_rate)

    base_allocation = None
    allocation_error = None
    if project_available:
        try:
            base_allocation = get_investment_funding_allocation(
                baseline_state, investment_assumptions
            )
        except Exception as exc:
            allocation_error = str(exc)

    if base_allocation is None:
        st.warning("An evaluated investment project is required to calculate the funding gap.")
        if allocation_error:
            st.error(f"Funding calculation failed: {allocation_error}")
        return

    original_internal_cash = min(
        float(base_allocation.available_internal_cash),
        float(base_allocation.internal_cash_to_working_capital)
        + float(base_allocation.internal_cash_to_capex),
    )

    # All editable assumptions live in this screen's own session-state keys.
    defaults = {
        "ll_loan_rate_text": "",
        "ll_leasing_rate_text": "",
        "ll_wc_rate_text": "",
        "ll_internal_cash": float(original_internal_cash),
        "ll_duration_years": 15,
        "ll_payment_timing": "End of Month",
        "ll_depreciation_years": 30,
        "ll_expenses_loan": 0.0,
        "ll_expenses_leasing": 0.0,
        "ll_residual_value": 0.0,
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

    if st.button("Επαναφορά στις τιμές του έργου", key="ll_reset_to_project"):
        for key, value in defaults.items():
            st.session_state[key] = (
                float(original_internal_cash) if key == "ll_internal_cash" else value
            )
        st.rerun()

    st.subheader("1. Στοιχεία από το έργο και τη διάγνωση")
    c1, c2, c3 = st.columns(3)
    c1.metric("CAPEX έργου", f"€{float(base_allocation.total_capex):,.0f}")
    c2.metric("Αρχικές ανάγκες κεφαλαίου κίνησης", f"€{float(base_allocation.working_capital_need):,.0f}")
    c3.metric("Εσωτερικά κεφάλαια διαθέσιμα πάνω από το αποθεματικό", f"€{float(base_allocation.available_internal_cash):,.0f}")
    st.caption(
        "Τα παραπάνω προέρχονται από το έργο και τη διάγνωση. Δεν αλλάζουν από τις "
        "παρακάτω δοκιμές χρηματοδότησης."
    )

    st.subheader("2. Παράμετροι σεναρίου χρηματοδότησης")
    st.caption(
        "Συμπλήρωσε τα επιτόκια που σου έχουν προσφερθεί ή που θέλεις να εξετάσεις. "
        "Δεν προεπιλέγονται επιτόκια, επειδή δεν είναι γνωστά εκ των προτέρων. "
        "Μπορείς να κρατήσεις τις υπόλοιπες τιμές όπως εμφανίζονται ή να τις αλλάξεις."
    )
    rate_col1, rate_col2, rate_col3 = st.columns(3)
    with rate_col1:
        loan_rate_text = st.text_input(
            "Επιτόκιο δανείου (%)", key="ll_loan_rate_text",
            placeholder="π.χ. 6,5", help="Υποχρεωτικό για τη σύγκριση."
        )
    with rate_col2:
        leasing_rate_text = st.text_input(
            "Επιτόκιο / κόστος leasing (%)", key="ll_leasing_rate_text",
            placeholder="π.χ. 7,0", help="Υποχρεωτικό για τη σύγκριση."
        )
    with rate_col3:
        wc_rate_text = st.text_input(
            "Επιτόκιο χρηματοδότησης κεφαλαίου κίνησης (%)", key="ll_wc_rate_text",
            placeholder="π.χ. 8,0", help="Υποχρεωτικό για τη σύγκριση."
        )

    internal_col, duration_col, timing_col = st.columns(3)
    with internal_col:
        internal_cash_to_use = st.number_input(
            "Εσωτερικά κεφάλαια που θα χρησιμοποιηθούν (€)",
            min_value=0.0,
            max_value=float(base_allocation.available_internal_cash),
            step=1000.0,
            key="ll_internal_cash",
            help="Αλλάζει μόνο το σενάριο και όχι το αρχικό ταμειακό υπόλοιπο ή το αποθεματικό της διάγνωσης.",
        )
    with duration_col:
        duration_years = st.number_input(
            "Διάρκεια χρηματοδότησης (έτη)", min_value=1, max_value=50,
            key="ll_duration_years"
        )
    with timing_col:
        pay_timing = st.radio(
            "Χρόνος καταβολής δόσης", ["Beginning of Month", "End of Month"],
            key="ll_payment_timing"
        )
    pay_when = 1 if pay_timing == "Beginning of Month" else 0

    tax_col, depreciation_col = st.columns(2)
    with tax_col:
        st.metric("Φορολογικός συντελεστής (από τη διάγνωση)", f"{tax_rate * 100:.2f}%")
    with depreciation_col:
        depreciation_years = st.number_input(
            "Περίοδος απόσβεσης παγίου (έτη)", min_value=1, max_value=100,
            key="ll_depreciation_years",
            help="Παραδοχή για την ενδεικτική φορολογική επίδραση· δεν αλλάζει τις παραδοχές του έργου."
        )

    with st.expander("Πρόσθετες παραδοχές συναλλαγής"):
        fee_col1, fee_col2 = st.columns(2)
        with fee_col1:
            loan_fees = st.number_input(
                "Έξοδα δανείου (€)", min_value=0.0, step=500.0,
                key="ll_expenses_loan"
            )
        with fee_col2:
            leasing_fees = st.number_input(
                "Έξοδα leasing (€)", min_value=0.0, step=500.0,
                key="ll_expenses_leasing"
            )
        residual_value = st.number_input(
            "Υπολειμματική / τελική καταβολή leasing (€)",
            min_value=0.0, step=500.0, key="ll_residual_value",
            help="Τελική καταβολή στη λήξη· περιορίζεται στο CAPEX που χρηματοδοτείται."
        )

    effective_allocation = _allocation_with_custom_internal_cash(
        base_allocation, internal_cash_to_use
    )
    internal_actual = (
        effective_allocation.internal_cash_to_working_capital
        + effective_allocation.internal_cash_to_capex
    )
    st.subheader("3. Χρηματοδοτικό κενό του σεναρίου")
    gap_col1, gap_col2, gap_col3 = st.columns(3)
    gap_col1.metric("Εσωτερικά κεφάλαια που χρησιμοποιούνται", f"€{internal_actual:,.0f}")
    gap_col2.metric("Εξωτερική χρηματοδότηση CAPEX", f"€{effective_allocation.external_capex_required:,.0f}")
    gap_col3.metric("Συνολικό εξωτερικό χρηματοδοτικό κενό", f"€{effective_allocation.total_external_funding_required:,.0f}")

    try:
        loan_rate = _parse_percent_input(loan_rate_text, "Επιτόκιο δανείου")
        leasing_rate = _parse_percent_input(leasing_rate_text, "Επιτόκιο leasing")
        wc_rate = _parse_percent_input(wc_rate_text, "Επιτόκιο κεφαλαίου κίνησης")
    except ValueError as exc:
        st.error(str(exc))
        return

    if loan_rate is None or leasing_rate is None or wc_rate is None:
        st.info("Για να εμφανιστεί η σύγκριση Loan vs Leasing, συμπλήρωσε και τα τρία επιτόκια. Δεν χρησιμοποιούνται αυτόματες ή υποθετικές τιμές επιτοκίων.")
        return

    inputs = {
        "loan_rate": loan_rate,
        "leasing_rate": leasing_rate,
        "wc_rate": wc_rate,
        "duration_years": float(duration_years),
        "pay_when": pay_when,
        "tax_rate": tax_rate,
        "depreciation_years": int(depreciation_years),
        "loan_fees": float(loan_fees),
        "leasing_fees": float(leasing_fees),
        "leasing_residual_value": float(residual_value),
    }

    st.divider()
    st.subheader("Loan vs Leasing — σύγκριση με βάση το πραγματικό χρηματοδοτικό κενό")
    capex_required = float(effective_allocation.external_capex_required)
    wc_required = float(effective_allocation.external_working_capital_required)
    total_required = float(effective_allocation.total_external_funding_required)
    if total_required <= 0:
        st.success("Με την επιλεγμένη χρήση εσωτερικών κεφαλαίων, το έργο δεν έχει εξωτερικό χρηματοδοτικό κενό.")
        return

    loan = _option_schedule(capex_required, wc_required, inputs, "Loan")
    leasing = _option_schedule(capex_required, wc_required, inputs, "Leasing")

    col_loan, col_lease = st.columns(2)
    with col_loan:
        st.markdown("#### 🏦 Δάνειο")
        st.metric("Συνολικό ποσό χρηματοδότησης", f"€{loan['financed_amount']:,.0f}")
        st.caption(f"Χρηματοδοτικό κενό: €{total_required:,.0f} · έξοδα δανείου που χρηματοδοτούνται: €{loan_fees:,.0f}")
        st.metric("Εκτιμώμενο συνολικό κόστος μετά φόρων", f"€{loan['final_burden']:,.0f}")
        st.caption(f"Πληρωμές 1ου έτους: €{loan['year1_payment']:,.0f} · τόκοι 1ου έτους: €{loan['year1_interest']:,.0f}")
    with col_lease:
        st.markdown("#### 📄 Leasing")
        st.metric("Συνολικό ποσό χρηματοδότησης", f"€{leasing['financed_amount']:,.0f}")
        st.caption(f"Χρηματοδοτικό κενό: €{total_required:,.0f} · έξοδα leasing που χρηματοδοτούνται: €{leasing_fees:,.0f}")
        st.metric("Εκτιμώμενο συνολικό κόστος μετά φόρων", f"€{leasing['final_burden']:,.0f}")
        st.caption(f"Πληρωμές 1ου έτους: €{leasing['year1_payment']:,.0f} · τόκοι 1ου έτους: €{leasing['year1_interest']:,.0f}")

    fig = go.Figure(go.Bar(
        x=["Loan", "Leasing"],
        y=[loan["final_burden"], leasing["final_burden"]],
        text=[f"€{loan['final_burden']:,.0f}", f"€{leasing['final_burden']:,.0f}"],
        textposition="auto",
    ))
    fig.update_layout(height=280, margin=dict(l=10, r=10, t=20, b=10), yaxis_title="Εκτιμώμενο συνολικό κόστος μετά φόρων (€)")
    st.plotly_chart(fig, use_container_width=True)
    st.caption(
        "Η σύγκριση είναι ενδεικτική: μοντελοποιεί αποπληρωτέο δάνειο έναντι υποχρέωσης "
        "finance leasing και υπολογίζει απλοποιημένα τη φορολογική επίδραση. Οι όροι μιας "
        "πραγματικής σύμβασης leasing μπορεί να διαφέρουν. Η χρηματοδότηση δεν μεταβάλλει "
        "το NPV, IRR ή Payback του έργου."
    )

    st.divider()
    st.subheader("Επίδραση κατά το πρώτο έτος")
    loan_profit = _profit_after_financing_interest(baseline_profit, baseline_is.ebt, tax_rate, loan["year1_interest"])
    lease_profit = _profit_after_financing_interest(baseline_profit, baseline_is.ebt, tax_rate, leasing["year1_interest"])
    consequence_rows = [
        ("Ετήσιες πληρωμές χρηματοδότησης", loan["year1_payment"], leasing["year1_payment"]),
        ("Έξοδα τόκων", loan["year1_interest"], leasing["year1_interest"]),
        ("Ενδεικτικά καθαρά κέρδη εταιρείας", loan_profit, lease_profit),
        ("Ταμειακή ροή μετά την εξυπηρέτηση χρηματοδότησης", baseline_fcfe - loan["year1_payment"], baseline_fcfe - leasing["year1_payment"]),
    ]
    for label, loan_value, lease_value in consequence_rows:
        c1, c2, c3 = st.columns([1.6, 1, 1])
        c1.caption(label)
        c2.metric("Δάνειο", f"€{loan_value:,.0f}")
        c3.metric("Leasing", f"€{lease_value:,.0f}")

    st.divider()
    st.subheader("Επιλογή χρηματοδότησης")
    selected_option = st.radio(
        "Επίλεξε επιλογή", ["Καμία απόφαση", "Loan", "Leasing"],
        horizontal=True, key="ll_selected_option"
    )
    if selected_option == "Καμία απόφαση":
        st.caption("Δεν θα μεταφερθεί απόφαση χρηματοδότησης στο επενδυτικό έργο.")
        return

    chosen = loan if selected_option == "Loan" else leasing
    financing_inputs = dict(inputs)
    financing_inputs["selected_option"] = selected_option
    st.session_state.loan_leasing_decision_preview = {
        "decision_type": "loan_vs_leasing",
        "selected_option": selected_option,
        "annual_payment": chosen["year1_payment"],
        "final_burden": chosen["final_burden"],
        "year_1_profit_before_decision": baseline_profit,
        "year_1_profit_after_decision": loan_profit if selected_option == "Loan" else lease_profit,
        "year_1_cash_before_decision": baseline_fcfe,
        "year_1_cash_after_decision": baseline_fcfe - chosen["year1_payment"],
        "baseline_version": baseline_state.version,
        "financing_scope": "investment_project",
        "linked_investment_assumptions": investment_assumptions,
        "financing_inputs": financing_inputs,
    }

    st.divider()
    st.subheader("Μεταφορά χρηματοδότησης στο επενδυτικό έργο")
    st.caption("Η επιλεγμένη χρηματοδότηση συνδέεται με το υπάρχον έργο· δεν προστίθεται δεύτερη επενδυτική απόφαση.")
    if st.button(
        "Μεταφορά επιλεγμένης χρηματοδότησης στο έργο",
        use_container_width=True, type="primary",
        disabled=not project_available,
        key="transfer_financing_to_investment",
    ):
        try:
            _transfer_financing_to_investment(
                investment_assumptions=investment_assumptions,
                financing_preview=st.session_state.loan_leasing_decision_preview,
                funding_allocation=effective_allocation,
            )
            st.success("Η χρηματοδότηση συνδέθηκε με το επενδυτικό έργο.")
        except Exception as exc:
            st.error(f"Σφάλμα κατά τη μεταφορά χρηματοδότησης: {exc}")
