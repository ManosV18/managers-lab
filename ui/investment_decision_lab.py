from dataclasses import dataclass
from typing import List, Dict, Optional
import numpy as np
import numpy_financial as npf


# ---------------------------------------------------------------------------
# 1. Company State Context
# ---------------------------------------------------------------------------
@dataclass(frozen=True)
class CompanyStateContext:
    """
    Locked Baseline της εταιρείας.

    Το Investment Lab κληρονομεί από εδώ τα υφιστάμενα
    company economics και working-capital policies.
    """
    price: float
    variable_cost_per_unit: float
    fixed_costs: float

    tax_rate: float
    wacc: float

    ar_days: float
    inventory_days: float
    ap_days: float

    fixed_assets: float
    depreciation: float


# ---------------------------------------------------------------------------
# 2. Investment Assumptions
# ---------------------------------------------------------------------------
@dataclass(frozen=True)
class InvestmentAssumptions:
    """
    Παραδοχές της επενδυτικής πρότασης.

    Company economics χρησιμοποιούνται ως defaults.
    Overrides επιτρέπονται μόνο όπου η επένδυση έχει
    διαφορετικά economics.
    """
    # Investment proposal
    initial_investment: float
    project_years: int
    units: float

    # Useful life of new CAPEX
    depreciation_years: int

    # Incremental operating costs
    incremental_fixed_costs: float = 0.0

    # Project growth
    annual_volume_growth: float = 0.0
    annual_price_growth: float = 0.0
    annual_variable_cost_growth: float = 0.0
    annual_fixed_cost_growth: float = 0.0

    # Terminal value
    salvage_value: float = 0.0

    # Optional company-economics overrides
    price_override: Optional[float] = None
    variable_cost_override: Optional[float] = None
    tax_rate_override: Optional[float] = None
    wacc_override: Optional[float] = None

    # Project flexibility
    allow_exit_after_year_1: bool = False
    exit_value: float = 0.0
    exit_cost: float = 0.0

    def get_effective_price(self, context: CompanyStateContext) -> float:
        return (
            self.price_override
            if self.price_override is not None
            else context.price
        )

    def get_effective_variable_cost(self, context: CompanyStateContext) -> float:
        return (
            self.variable_cost_override
            if self.variable_cost_override is not None
            else context.variable_cost_per_unit
        )

    def get_effective_tax_rate(self, context: CompanyStateContext) -> float:
        return (
            self.tax_rate_override
            if self.tax_rate_override is not None
            else context.tax_rate
        )

    def get_effective_wacc(self, context: CompanyStateContext) -> float:
        return (
            self.wacc_override
            if self.wacc_override is not None
            else context.wacc
        )

    def get_incremental_depreciation(self, year: int) -> float:
        """
        Υπολογίζει την ετήσια απόσβεση.
        Η απόσβεση εφαρμόζεται ΜΟΝΟ κατά τη διάρκεια της ωφέλιμης ζωής (useful life).
        """
        if self.depreciation_years <= 0 or year <= 0:
            return 0.0

        if year > self.depreciation_years:
            return 0.0

        return self.initial_investment / self.depreciation_years


# ---------------------------------------------------------------------------
# 3. Investment Year
# ---------------------------------------------------------------------------
@dataclass(frozen=True)
class InvestmentYear:
    year: int

    units: float
    price: float
    revenue: float

    variable_cost_per_unit: float
    variable_cost_total: float

    incremental_fixed_costs: float
    depreciation: float

    operating_profit: float
    tax: float
    operating_cash_flow: float

    incremental_ar: float
    incremental_inventory: float
    incremental_ap: float
    incremental_nwc: float

    working_capital_cash_flow: float

    salvage_value: float
    project_cash_flow: float


# ---------------------------------------------------------------------------
# 4. Incremental Year-1 Company Impact
# ---------------------------------------------------------------------------
@dataclass(frozen=True)
class InvestmentYear1Impact:
    """
    Η καθαρή επίδραση της αποδεκτής επένδυσης στην υπάρχουσα εταιρεία
    κατά το πρώτο έτος.

    Αυτό είναι το bridge μεταξύ Investment Domain και CompanyState.
    """
    # Operating impact
    incremental_units: float
    incremental_revenue: float
    incremental_variable_cost: float
    incremental_fixed_costs: float

    # Accounting / operating impact
    incremental_depreciation: float
    incremental_ebit: float
    incremental_tax: float
    incremental_net_profit: float

    # Working capital
    incremental_ar: float
    incremental_inventory: float
    incremental_ap: float
    incremental_nwc: float

    # Investment / asset impact
    incremental_fixed_assets: float

    # Cash requirement / impact
    initial_capex: float
    initial_nwc_requirement: float
    initial_funding_requirement: float

    # Operating cash flow
    incremental_operating_cash_flow: float


# ---------------------------------------------------------------------------
# 5. Investment Result
# ---------------------------------------------------------------------------
@dataclass(frozen=True)
class InvestmentResult:
    npv: float
    irr: float
    payback_years: float
    initial_investment: float
    total_project_cash_flow: float
    yearly_cash_flows: List[InvestmentYear]

    year_1_impact: Optional[InvestmentYear1Impact] = None


# ---------------------------------------------------------------------------
# Helper Calculation Functions
# ---------------------------------------------------------------------------
def calculate_incremental_working_capital(
    revenue: float,
    variable_cost_total: float,
    context: CompanyStateContext,
) -> Dict[str, float]:
    """
    Υπολογισμός NWC της επένδυσης βάσει των Working Capital policies
    της εταιρείας (CompanyStateContext).
    """
    incremental_ar = (revenue * context.ar_days) / 365.0
    incremental_inventory = (variable_cost_total * context.inventory_days) / 365.0
    incremental_ap = (variable_cost_total * context.ap_days) / 365.0

    incremental_nwc = (
        incremental_ar
        + incremental_inventory
        - incremental_ap
    )

    return {
        "ar": incremental_ar,
        "inventory": incremental_inventory,
        "ap": incremental_ap,
        "nwc": incremental_nwc,
    }


def calculate_npv(cash_flows: List[float], discount_rate: float) -> float:
    """Υπολογισμός Net Present Value (NPV)."""
    return float(npf.npv(discount_rate, cash_flows))


def calculate_irr(cash_flows: List[float]) -> float:
    """Υπολογισμός Internal Rate of Return (IRR)."""
    try:
        val = float(npf.irr(cash_flows))
        return val if not np.isnan(val) else 0.0
    except Exception:
        return 0.0


def calculate_payback(cash_flows: List[float]) -> float:
    """Υπολογισμός Payback Period σε έτη."""
    cumulative = 0.0
    for i, cf in enumerate(cash_flows):
        cumulative += cf
        if cumulative >= 0:
            if i == 0:
                return 0.0
            prev_cum = cumulative - cf
            fraction = (-prev_cum) / cf if cf != 0 else 0.0
            return (i - 1) + fraction
    return float("inf")


# ---------------------------------------------------------------------------
# 6. Year-1 Impact Builder
# ---------------------------------------------------------------------------
def build_investment_year1_impact(
    assumptions: InvestmentAssumptions,
    context: CompanyStateContext,
) -> InvestmentYear1Impact:
    """
    Μετατρέπει την επένδυση σε incremental Year-1 impact πάνω στην υπάρχουσα εταιρεία.
    """
    units = assumptions.units
    price = assumptions.get_effective_price(context)
    variable_cost_per_unit = assumptions.get_effective_variable_cost(context)
    incremental_fixed_costs = assumptions.incremental_fixed_costs
    tax_rate = assumptions.get_effective_tax_rate(context)

    revenue = units * price
    variable_cost_total = units * variable_cost_per_unit
    depreciation = assumptions.get_incremental_depreciation(year=1)

    ebit = (
        revenue
        - variable_cost_total
        - incremental_fixed_costs
        - depreciation
    )

    tax = max(0.0, ebit * tax_rate)
    net_profit = ebit - tax
    operating_cash_flow = net_profit + depreciation

    wc = calculate_incremental_working_capital(
        revenue=revenue,
        variable_cost_total=variable_cost_total,
        context=context,
    )

    incremental_nwc = wc["nwc"]
    initial_capex = assumptions.initial_investment
    initial_funding_requirement = initial_capex + incremental_nwc

    return InvestmentYear1Impact(
        incremental_units=units,
        incremental_revenue=revenue,
        incremental_variable_cost=variable_cost_total,
        incremental_fixed_costs=incremental_fixed_costs,
        incremental_depreciation=depreciation,
        incremental_ebit=ebit,
        incremental_tax=tax,
        incremental_net_profit=net_profit,
        incremental_ar=wc["ar"],
        incremental_inventory=wc["inventory"],
        incremental_ap=wc["ap"],
        incremental_nwc=incremental_nwc,
        incremental_fixed_assets=initial_capex,
        initial_capex=initial_capex,
        initial_nwc_requirement=incremental_nwc,
        initial_funding_requirement=initial_funding_requirement,
        incremental_operating_cash_flow=operating_cash_flow,
    )


# ---------------------------------------------------------------------------
# 7. Cash Flow Engine
# ---------------------------------------------------------------------------
def build_investment_cash_flows(
    assumptions: InvestmentAssumptions,
    context: CompanyStateContext,
) -> List[InvestmentYear]:
    """
    Κατασκευάζει τις ετήσιες χρηματικές ροές της επένδυσης.
    """
    yearly_flows: List[InvestmentYear] = []

    curr_units = assumptions.units
    curr_price = assumptions.get_effective_price(context)
    curr_vc_per_unit = assumptions.get_effective_variable_cost(context)
    curr_fixed_cost = assumptions.incremental_fixed_costs
    tax_rate = assumptions.get_effective_tax_rate(context)

    # Year 1 NWC για το αρχικό outlay του Year 0
    year_1_revenue = curr_units * curr_price
    year_1_vc_total = curr_units * curr_vc_per_unit

    year_1_wc = calculate_incremental_working_capital(
        revenue=year_1_revenue,
        variable_cost_total=year_1_vc_total,
        context=context,
    )
    initial_nwc = year_1_wc["nwc"]

    # Year 0 Initial Outlay
    initial_outlay = -(assumptions.initial_investment + initial_nwc)

    yearly_flows.append(
        InvestmentYear(
            year=0,
            units=0.0,
            price=0.0,
            revenue=0.0,
            variable_cost_per_unit=0.0,
            variable_cost_total=0.0,
            incremental_fixed_costs=0.0,
            depreciation=0.0,
            operating_profit=0.0,
            tax=0.0,
            operating_cash_flow=0.0,
            incremental_ar=0.0,
            incremental_inventory=0.0,
            incremental_ap=0.0,
            incremental_nwc=initial_nwc,
            working_capital_cash_flow=-initial_nwc,
            salvage_value=0.0,
            project_cash_flow=initial_outlay,
        )
    )

    # Subsequent Years
    prev_nwc = initial_nwc

    for y in range(1, assumptions.project_years + 1):
        if y > 1:
            curr_units *= (1.0 + assumptions.annual_volume_growth)
            curr_price *= (1.0 + assumptions.annual_price_growth)
            curr_vc_per_unit *= (1.0 + assumptions.annual_variable_cost_growth)
            curr_fixed_cost *= (1.0 + assumptions.annual_fixed_cost_growth)

        revenue = curr_units * curr_price
        vc_total = curr_units * curr_vc_per_unit
        depreciation = assumptions.get_incremental_depreciation(year=y)

        ebit = revenue - vc_total - curr_fixed_cost - depreciation
        tax = max(0.0, ebit * tax_rate)
        nopat = ebit - tax
        ocf = nopat + depreciation

        wc = calculate_incremental_working_capital(
            revenue=revenue,
            variable_cost_total=vc_total,
            context=context,
        )
        curr_nwc = wc["nwc"]

        # Terminal Year calculations
        if y == assumptions.project_years:
            wc_change = curr_nwc  # NWC Release στο τέλος του project
            salvage = assumptions.salvage_value
        else:
            wc_change = -(curr_nwc - prev_nwc)  # Investment in NWC
            salvage = 0.0

        prev_nwc = curr_nwc

        total_cf = ocf + wc_change + salvage

        yearly_flows.append(
            InvestmentYear(
                year=y,
                units=curr_units,
                price=curr_price,
                revenue=revenue,
                variable_cost_per_unit=curr_vc_per_unit,
                variable_cost_total=vc_total,
                incremental_fixed_costs=curr_fixed_cost,
                depreciation=depreciation,
                operating_profit=ebit,
                tax=tax,
                operating_cash_flow=ocf,
                incremental_ar=wc["ar"],
                incremental_inventory=wc["inventory"],
                incremental_ap=wc["ap"],
                incremental_nwc=curr_nwc,
                working_capital_cash_flow=wc_change,
                salvage_value=salvage,
                project_cash_flow=total_cf,
            )
        )

    return yearly_flows


# ---------------------------------------------------------------------------
# 8. Evaluation Entrypoint
# ---------------------------------------------------------------------------
def evaluate_investment(
    assumptions: InvestmentAssumptions,
    context: CompanyStateContext,
) -> InvestmentResult:
    """
    Κύρια συνάρτηση αξιολόγησης επένδυσης.
    """
    yearly_structs = build_investment_cash_flows(assumptions, context)
    cfs = [y.project_cash_flow for y in yearly_structs]

    wacc = assumptions.get_effective_wacc(context)

    npv_val = calculate_npv(cfs, wacc)
    irr_val = calculate_irr(cfs)
    payback_val = calculate_payback(cfs)
    total_cf = sum(cfs)

    year_1_impact = build_investment_year1_impact(assumptions, context)

    return InvestmentResult(
        npv=npv_val,
        irr=irr_val,
        payback_years=payback_val,
        initial_investment=assumptions.initial_investment,
        total_project_cash_flow=total_cf,
        yearly_cash_flows=yearly_structs,
        year_1_impact=year_1_impact,
    )


# ---------------------------------------------------------------------------
# 9. Company Integration Adapter Layer
# ---------------------------------------------------------------------------
@dataclass(frozen=True)
class InvestmentCompanyImpact:
    """
    Company-level changes generated by an accepted investment proposal.

    Semantic Contract:
    - revenue_delta & variable_cost_delta είναι τα AUTHORITATIVE incremental economics.
    - volume_delta είναι operational/πληροφοριακό impact και ΔΕΝ πρέπει να
      ξαναχρησιμοποιηθεί για επανυπολογισμό εσόδων όταν υπάρχουν explicit overrides.
    """
    volume_delta: float
    revenue_delta: float
    variable_cost_delta: float
    fixed_opex_delta: float
    fixed_assets_delta: float
    depreciation_delta: float


def build_investment_company_impact(
    impact: InvestmentYear1Impact,
) -> InvestmentCompanyImpact:
    """
    Adapter που μετατρέπει το InvestmentYear1Impact στο καθαρό boundary
    που χρειάζεται ο DecisionEvaluator / FinancialEngine της εταιρείας.
    """
    return InvestmentCompanyImpact(
        volume_delta=impact.incremental_units,
        revenue_delta=impact.incremental_revenue,
        variable_cost_delta=impact.incremental_variable_cost,
        fixed_opex_delta=impact.incremental_fixed_costs,
        fixed_assets_delta=impact.initial_capex,
        depreciation_delta=impact.incremental_depreciation,
    )
