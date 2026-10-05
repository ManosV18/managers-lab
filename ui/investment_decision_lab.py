from dataclasses import dataclass
from typing import List, Dict, Optional
import numpy as np
import numpy_financial as npf


# ---------------------------------------------------------------------------
# 1. Company State Context (Baseline Integration)
# ---------------------------------------------------------------------------
@dataclass(frozen=True)
class CompanyStateContext:
    """
    Το υφιστάμενο πλαίσιο της εταιρείας (Locked Baseline).
    Το Investment Lab τραβάει από εδώ τα defaults για να μην ξαναρωτάει τον χρήστη.
    """
    variable_cost_per_unit: float
    tax_rate: float
    wacc: float
    price: float = 0.0
    fixed_costs: float = 0.0


# ---------------------------------------------------------------------------
# 2. Investment Assumptions & Overrides
# ---------------------------------------------------------------------------
@dataclass(frozen=True)
class InvestmentAssumptions:
    """
    Παραδοχές Επένδυσης με defaults από το CompanyStateContext.
    """
    initial_investment: float
    project_years: int
    units: float

    # Νέες μεταβλητές που αφορούν αποκλειστικά το Project
    annual_volume_growth: float = 0.0
    annual_price_growth: float = 0.0
    annual_variable_cost_growth: float = 0.0
    annual_fixed_cost_growth: float = 0.0

    working_capital: float = 0.0
    salvage_value: float = 0.0
    fixed_costs: float = 0.0

    # Τιμή πώλησης (αν είναι νέο προϊόν, αλλιώς default από baseline)
    price: Optional[float] = None

    # Overrides: Αν None, χρησιμοποιούνται τα defaults του CompanyState Context
    override_variable_cost_per_unit: Optional[float] = None
    override_tax_rate: Optional[float] = None
    override_wacc: Optional[float] = None

    def get_effective_variable_cost(self, context: CompanyStateContext) -> float:
        if self.override_variable_cost_per_unit is not None:
            return self.override_variable_cost_per_unit
        return context.variable_cost_per_unit

    def get_effective_tax_rate(self, context: CompanyStateContext) -> float:
        if self.override_tax_rate is not None:
            return self.override_tax_rate
        return context.tax_rate

    def get_effective_wacc(self, context: CompanyStateContext) -> float:
        if self.override_wacc is not None:
            return self.override_wacc
        return context.wacc

    def get_effective_price(self, context: CompanyStateContext) -> float:
        if self.price is not None:
            return self.price
        return context.price


# ---------------------------------------------------------------------------
# 3. Output Data Structures
# ---------------------------------------------------------------------------
@dataclass(frozen=True)
class InvestmentYear:
    year: int
    units: float
    price: float
    revenue: float
    variable_cost_per_unit: float
    variable_cost_total: float
    fixed_costs: float
    operating_profit: float  # EBIT
    tax: float
    operating_cash_flow: float  # NOPAT + Addbacks
    working_capital_change: float
    salvage_value: float
    project_cash_flow: float


@dataclass(frozen=True)
class InvestmentResult:
    npv: float
    irr: float
    payback_years: float
    initial_investment: float
    total_project_cash_flow: float
    yearly_cash_flows: List[InvestmentYear]


# ---------------------------------------------------------------------------
# 4. Core Calculation Engine
# ---------------------------------------------------------------------------
def build_investment_cash_flows(
    assumptions: InvestmentAssumptions,
    context: CompanyStateContext
) -> List[InvestmentYear]:
    """
    Κατασκευάζει τις ετήσιες ταμειακές ροές της επένδυσης.
    """
    yearly_flows: List[InvestmentYear] = []
    
    # Αρχικές τιμές 1ου έτους
    curr_units = assumptions.units
    curr_price = assumptions.get_effective_price(context)
    curr_vc_per_unit = assumptions.get_effective_variable_cost(context)
    curr_fixed_cost = assumptions.fixed_costs
    tax_rate = assumptions.get_effective_tax_rate(context)

    # Έτος 0: Αρχική εκροή επένδυσης + Κεφάλαιο Κίνησης
    initial_outlay = -(assumptions.initial_investment + assumptions.working_capital)
    yearly_flows.append(
        InvestmentYear(
            year=0,
            units=0,
            price=0,
            revenue=0,
            variable_cost_per_unit=0,
            variable_cost_total=0,
            fixed_costs=0,
            operating_profit=0,
            tax=0,
            operating_cash_flow=0,
            working_capital_change=-assumptions.working_capital,
            salvage_value=0,
            project_cash_flow=initial_outlay
        )
    )

    # Έτη 1 έως N
    for y in range(1, assumptions.project_years + 1):
        if y > 1:
            curr_units *= (1 + assumptions.annual_volume_growth)
            curr_price *= (1 + assumptions.annual_price_growth)
            curr_vc_per_unit *= (1 + assumptions.annual_variable_cost_growth)
            curr_fixed_cost *= (1 + assumptions.annual_fixed_cost_growth)

        revenue = curr_units * curr_price
        vc_total = curr_units * curr_vc_per_unit
        ebit = revenue - vc_total - curr_fixed_cost
        
        # Φόρος (αν EBIT > 0)
        tax = max(0.0, ebit * tax_rate)
        nopat = ebit - tax
        
        # Λειτουργική ταμειακή ροή
        ocf = nopat  # Μπορεί να προστεθεί depreciation αν οριστεί

        # Τελευταίο έτος: Επιστροφή Working Capital & Salvage Value
        wc_change = assumptions.working_capital if y == assumptions.project_years else 0.0
        salvage = assumptions.salvage_value if y == assumptions.project_years else 0.0

        total_cf = ocf + wc_change + salvage

        yearly_flows.append(
            InvestmentYear(
                year=y,
                units=curr_units,
                price=curr_price,
                revenue=revenue,
                variable_cost_per_unit=curr_vc_per_unit,
                variable_cost_total=vc_total,
                fixed_costs=curr_fixed_cost,
                operating_profit=ebit,
                tax=tax,
                operating_cash_flow=ocf,
                working_capital_change=wc_change,
                salvage_value=salvage,
                project_cash_flow=total_cf
            )
        )

    return yearly_flows


def calculate_npv(cash_flows: List[float], wacc: float) -> float:
    """Υπολογισμός Καθαρής Παρούσας Αξίας (NPV)."""
    return float(npf.npv(wacc, cash_flows))


def calculate_irr(cash_flows: List[float]) -> float:
    """Υπολογισμός Εσωτερικού Βαθμού Απόδοσης (IRR)."""
    try:
        val = float(npf.irr(cash_flows))
        return val if not np.isnan(val) else 0.0
    except Exception:
        return 0.0


def calculate_payback(cash_flows: List[float]) -> float:
    """Υπολογισμός Περιόδου Επανείσπραξης (Payback Period σε έτη)."""
    cum_cf = 0.0
    for i, cf in enumerate(cash_flows):
        cum_cf += cf
        if cum_cf >= 0:
            if i == 0:
                return 0.0
            prev_cum = cum_cf - cf
            # Γραμμική παρεμβολή εντός του έτους
            fraction = abs(prev_cum) / cf if cf != 0 else 0.0
            return (i - 1) + fraction
    return float('inf')  # Δεν αποσβένεται εντός της διάρκειας


def evaluate_investment(
    assumptions: InvestmentAssumptions,
    context: CompanyStateContext
) -> InvestmentResult:
    """
    Ενιαίος Evaluator: Παράγει τις ροές και υπολογίζει NPV, IRR, Payback.
    """
    yearly_structs = build_investment_cash_flows(assumptions, context)
    cfs = [y.project_cash_flow for y in yearly_structs]
    wacc = assumptions.get_effective_wacc(context)

    npv_val = calculate_npv(cfs, wacc)
    irr_val = calculate_irr(cfs)
    payback_val = calculate_payback(cfs)
    total_cf = sum(cfs)

    return InvestmentResult(
        npv=npv_val,
        irr=irr_val,
        payback_years=payback_val,
        initial_investment=assumptions.initial_investment,
        total_project_cash_flow=total_cf,
        yearly_cash_flows=yearly_structs
    )


# ---------------------------------------------------------------------------
# 5. Decision Drivers Engine (Tornado Sensitivity)
# ---------------------------------------------------------------------------
@dataclass
class TornadoDriver:
    driver_name: str
    base_npv: float
    low_npv: float
    high_npv: float
    range_span: float  # abs(high_npv - low_npv)


def calculate_tornado_sensitivity(
    assumptions: InvestmentAssumptions,
    context: CompanyStateContext,
    variation_pct: float = 0.10  # +/- 10%
) -> List[TornadoDriver]:
    """
    Υπολογίζει την ευαισθησία του NPV στις βασικές μεταβλητές (+/- 10%)
    και επιστρέφει ταξινομημένα τα αποτελέσματα για Tornado Chart.
    """
    base_result = evaluate_investment(assumptions, context)
    base_npv = base_result.npv

    # Μεταβλητές προς εξέταση
    drivers_to_test = [
        "price",
        "units",
        "override_variable_cost_per_unit",
        "initial_investment",
        "fixed_costs",
        "override_wacc"
    ]

    tornado_results: List[TornadoDriver] = []

    for driver in drivers_to_test:
        # Παίρνουμε την τρέχουσα τιμή
        val = getattr(assumptions, driver)
        if val is None:
            if driver == "override_variable_cost_per_unit":
                val = context.variable_cost_per_unit
            elif driver == "override_wacc":
                val = context.wacc
            elif driver == "price":
                val = context.price

        if val == 0 or val is None:
            continue

        # Δημιουργούμε Low & High σενάρια (+/- variation_pct)
        low_val = val * (1 - variation_pct)
        high_val = val * (1 + variation_pct)

        # Evaluate Low
        kwargs_low = {driver: low_val}
        assump_low = _copy_assumptions_with(assumptions, **kwargs_low)
        npv_low = evaluate_investment(assump_low, context).npv

        # Evaluate High
        kwargs_high = {driver: high_val}
        assump_high = _copy_assumptions_with(assumptions, **kwargs_high)
        npv_high = evaluate_investment(assump_high, context).npv

        span = abs(npv_high - npv_low)
        
        # Καθαρός τίτλος οδηγού
        display_name = driver.replace("override_", "").replace("_", " ").title()

        tornado_results.append(
            TornadoDriver(
                driver_name=display_name,
                base_npv=base_npv,
                low_npv=min(npv_low, npv_high),
                high_npv=max(npv_low, npv_high),
                range_span=span
            )
        )

    # Ταξινόμηση με βάση το εύρος επίδρασης (Largest impact first)
    tornado_results.sort(key=lambda x: x.range_span, reverse=True)
    return tornado_results


def _copy_assumptions_with(assumptions: InvestmentAssumptions, **kwargs) -> InvestmentAssumptions:
    """Helper για εύκολο mutation των frozen dataclasses."""
    d = {k: getattr(assumptions, k) for k in assumptions.__dataclass_fields__}
    d.update(kwargs)
    return InvestmentAssumptions(**d)


# ---------------------------------------------------------------------------
# 6. Verification / Quick Run (Testing against Excel logic)
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    print("=== MANAGERS LAB: INVESTMENT DECISION LAB CORE ENGINE ===")
    
    # 1. Έστω ότι το Locked CompanyState έχει ήδη αυτά τα δεδομένα:
    company_ctx = CompanyStateContext(
        variable_cost_per_unit=2.10,  # π.χ. $2.10/unit
        tax_rate=0.40,               # 40%
        wacc=0.12,                   # 12%
        price=3.00
    )
    print(f"\n[Context Loaded] Company Baseline VC: €{company_ctx.variable_cost_per_unit}, Tax: {company_ctx.tax_rate*100}%, WACC: {company_ctx.wacc*100}%")

    # 2. Ο χρήστης ορίζει ΜΟΝΟ τα νέα δεδομένα της επένδυσης
    proj_assump = InvestmentAssumptions(
        initial_investment=20000.0,   # $20,000 CapEx
        project_years=4,
        units=20000.0,
        fixed_costs=8000.0,
        working_capital=6000.0,
        salvage_value=10607.2,
        # Ο χρήστης ΔΕΝ έβαλε Price/VC/Tax/WACC -> Θα χρησιμοποιηθούν τα defaults του Company Context!
    )

    # 3. Εκτέλεση Αξιολόγησης
    res = evaluate_investment(proj_assump, company_ctx)

    print("\n--- RESULTS ---")
    print(f"NPV  (@ {company_ctx.wacc*100}% WACC): €{res.npv:,.2f}")
    print(f"IRR                   : {res.irr*100:.2f}%")
    print(f"Payback Period        : {res.payback_years:.2f} έτη")
    print(f"Total Net Cash Flow   : €{res.total_project_cash_flow:,.2f}")

    # 4. Εκτέλεση Tornado Analysis (Decision Drivers)
    print("\n--- DECISION DRIVERS (TORNADO ANALYSIS +/- 10%) ---")
    tornado = calculate_tornado_sensitivity(proj_assump, company_ctx)
    for t in tornado:
        print(f"• {t.driver_name:<25} | Range Impact: €{t.range_span:,.2f} [Min NPV: €{t.low_npv:,.2f} -> Max NPV: €{t.high_npv:,.2f}]")


# ---------------------------------------------------------------------------
# 7. Streamlit UI
# ---------------------------------------------------------------------------

import streamlit as st


def render_investment_decision_lab(
    baseline_state=None,
):
    st.title("📊 Investment Decision Lab")

    st.markdown(
        "Evaluate a proposed investment using NPV, IRR, "
        "Payback and decision-driver sensitivity."
    )

    st.divider()

    # ---------------------------------------------------------
    # BASELINE DEFAULTS
    # ---------------------------------------------------------

    baseline_price = (
        baseline_state.drivers.price
        if baseline_state is not None
        else 0.0
    )

    baseline_variable_cost = (
        baseline_state.drivers.variable_cost_per_unit
        if baseline_state is not None
        else 0.0
    )

    baseline_tax_rate = (
        baseline_state.capital_structure.tax_rate
        if baseline_state is not None
        else 0.0
    )

    baseline_wacc = (
        baseline_state.capital_structure.wacc
        if baseline_state is not None
        else 0.0
    )

    # ---------------------------------------------------------
    # INVESTMENT INPUTS
    # ---------------------------------------------------------

    st.subheader("Investment Assumptions")

    col1, col2 = st.columns(2)

    with col1:

        initial_investment = st.number_input(
            "Initial Investment",
            min_value=0.0,
            value=0.0,
            step=1000.0,
        )

        project_years = st.number_input(
            "Project Years",
            min_value=1,
            value=5,
            step=1,
        )

        units = st.number_input(
            "Annual Units",
            min_value=0.0,
            value=0.0,
            step=1000.0,
        )

    with col2:

        fixed_costs = st.number_input(
            "Annual Fixed Costs",
            min_value=0.0,
            value=0.0,
            step=1000.0,
        )

        working_capital = st.number_input(
            "Initial Working Capital",
            min_value=0.0,
            value=0.0,
            step=1000.0,
        )

        salvage_value = st.number_input(
            "Salvage Value",
            min_value=0.0,
            value=0.0,
            step=1000.0,
        )

    # ---------------------------------------------------------
    # PROJECT GROWTH
    # ---------------------------------------------------------

    st.subheader("Project Growth Assumptions")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        volume_growth = st.number_input(
            "Annual Volume Growth %",
            value=0.0,
            step=1.0,
        ) / 100

    with col2:
        price_growth = st.number_input(
            "Annual Price Growth %",
            value=0.0,
            step=1.0,
        ) / 100

    with col3:
        variable_cost_growth = st.number_input(
            "Annual Variable Cost Growth %",
            value=0.0,
            step=1.0,
        ) / 100

    with col4:
        fixed_cost_growth = st.number_input(
            "Annual Fixed Cost Growth %",
            value=0.0,
            step=1.0,
        ) / 100

    # ---------------------------------------------------------
    # COMPANY DEFAULTS
    # ---------------------------------------------------------

    st.subheader("Company Baseline Defaults")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            "Baseline Price",
            f"€{baseline_price:,.2f}",
        )

    with col2:
        st.metric(
            "Baseline Variable Cost",
            f"€{baseline_variable_cost:,.2f}",
        )

    with col3:
        st.metric(
            "Baseline Tax Rate",
            f"{baseline_tax_rate * 100:.1f}%",
        )

    with col4:
        st.metric(
            "Baseline WACC",
            f"{baseline_wacc * 100:.1f}%",
        )
    
    # ---------------------------------------------------------
    # OPTIONAL OVERRIDES
    # ---------------------------------------------------------

    st.subheader("Project Overrides")

    use_price_override = st.checkbox(
        "Override Selling Price / Unit"
    )

    price = None

    if use_price_override:

        price = st.number_input(
            "Project Selling Price / Unit",
            min_value=0.0,
            value=float(baseline_price),
            step=0.10,
        )

    use_vc_override = st.checkbox(
        "Override Variable Cost / Unit"
    )

    override_vc = None

    if use_vc_override:

        override_vc = st.number_input(
            "Project Variable Cost / Unit",
            min_value=0.0,
            value=float(baseline_variable_cost),
            step=0.10,
        )

    use_tax_override = st.checkbox(
        "Override Tax Rate"
    )

    override_tax = None

    if use_tax_override:

        override_tax = st.number_input(
            "Project Tax Rate %",
            min_value=0.0,
            max_value=100.0,
            value=float(baseline_tax_rate * 100),
            step=1.0,
        ) / 100

    use_wacc_override = st.checkbox(
        "Override WACC"
    )

    override_wacc = None

    if use_wacc_override:

        override_wacc = st.number_input(
            "Project WACC %",
            min_value=0.0,
            max_value=100.0,
            value=float(baseline_wacc * 100),
            step=0.5,
        ) / 100

    # ---------------------------------------------------------
    # EVALUATION
    # ---------------------------------------------------------

    if st.button(
        "▶ Evaluate Investment",
        type="primary",
        use_container_width=True,
    ):

        context = CompanyStateContext(
            variable_cost_per_unit=baseline_variable_cost,
            tax_rate=baseline_tax_rate,
            wacc=baseline_wacc,
            price=baseline_price,
            fixed_costs=(
                baseline_state.drivers.fixed_opex
                if baseline_state is not None
                else 0.0
            ),
        )

        assumptions = InvestmentAssumptions(
            initial_investment=initial_investment,
            project_years=int(project_years),
            units=units,
            annual_volume_growth=volume_growth,
            annual_price_growth=price_growth,
            annual_variable_cost_growth=variable_cost_growth,
            annual_fixed_cost_growth=fixed_cost_growth,
            working_capital=working_capital,
            salvage_value=salvage_value,
            fixed_costs=fixed_costs,
            price=price,
            override_variable_cost_per_unit=override_vc,
            override_tax_rate=override_tax,
            override_wacc=override_wacc,
        )

        result = evaluate_investment(
            assumptions,
            context,
        )

        # -----------------------------------------------------
        # RESULTS
        # -----------------------------------------------------

        st.divider()

        st.subheader("Investment Decision")

        c1, c2, c3 = st.columns(3)

        with c1:
            st.metric(
                "NPV",
                f"€{result.npv:,.0f}",
            )

        with c2:
            st.metric(
                "IRR",
                f"{result.irr * 100:.1f}%",
            )

        with c3:

            if np.isinf(result.payback_years):

                payback_text = "Not recovered"

            else:

                payback_text = (
                    f"{result.payback_years:.2f} years"
                )

            st.metric(
                "Payback",
                payback_text,
            )

        # -----------------------------------------------------
        # DECISION SIGNAL
        # -----------------------------------------------------

        if result.npv > 0:

            st.success(
                "🟢 Positive NPV — the project creates "
                "value at the selected discount rate."
            )

        elif result.npv < 0:

            st.error(
                "🔴 Negative NPV — the project destroys "
                "value at the selected discount rate."
            )

        else:

            st.warning(
                "🟡 NPV is approximately zero — the project "
                "is at the value-neutral threshold."
            )

        # -----------------------------------------------------
        # YEARLY CASH FLOWS
        # -----------------------------------------------------

        st.subheader("Project Cash Flow")

        rows = []

        for year in result.yearly_cash_flows:

            rows.append(
                {
                    "Year": year.year,
                    "Units": year.units,
                    "Price": year.price,
                    "Revenue": year.revenue,
                    "Variable Cost": year.variable_cost_total,
                    "Fixed Costs": year.fixed_costs,
                    "EBIT": year.operating_profit,
                    "Tax": year.tax,
                    "Operating Cash Flow": year.operating_cash_flow,
                    "Working Capital": year.working_capital_change,
                    "Salvage": year.salvage_value,
                    "Project Cash Flow": year.project_cash_flow,
                }
            )

        st.dataframe(
            rows,
            use_container_width=True,
        )

        # -----------------------------------------------------
        # TORNADO ANALYSIS
        # -----------------------------------------------------

        st.subheader(
            "Decision Drivers — NPV Sensitivity"
        )

        tornado = calculate_tornado_sensitivity(
            assumptions,
            context,
        )

        if tornado:

            tornado_rows = [
                {
                    "Driver": t.driver_name,
                    "Low NPV": t.low_npv,
                    "Base NPV": t.base_npv,
                    "High NPV": t.high_npv,
                    "Impact Range": t.range_span,
                }
                for t in tornado
            ]

            st.dataframe(
                tornado_rows,
                use_container_width=True,
            )
