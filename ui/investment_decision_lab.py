from dataclasses import dataclass
from typing import List, Dict, Optional

import numpy as np
import numpy_financial as npf
import streamlit as st


# ============================================================================
# 1. COMPANY STATE CONTEXT
# ============================================================================

@dataclass(frozen=True)
class CompanyStateContext:
    """
    Locked Baseline της εταιρείας.

    Το Investment Lab κληρονομεί τα company economics και
    working-capital policies του Locked Baseline.
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


# ============================================================================
# 2. INVESTMENT ASSUMPTIONS
# ============================================================================

@dataclass(frozen=True)
class InvestmentAssumptions:
    """
    Παραδοχές της επενδυτικής πρότασης.

    Company economics χρησιμοποιούνται ως defaults.
    Overrides επιτρέπονται μόνο όπου η επένδυση έχει
    διαφορετικά economics.
    """

    initial_investment: float
    project_years: int
    units: float

    depreciation_years: int

    incremental_fixed_costs: float = 0.0

    annual_volume_growth: float = 0.0
    annual_price_growth: float = 0.0
    annual_variable_cost_growth: float = 0.0
    annual_fixed_cost_growth: float = 0.0

    salvage_value: float = 0.0

    price_override: Optional[float] = None
    variable_cost_override: Optional[float] = None
    tax_rate_override: Optional[float] = None
    wacc_override: Optional[float] = None

    allow_exit_after_year_1: bool = False
    exit_value: float = 0.0
    exit_cost: float = 0.0

    def get_effective_price(
        self,
        context: CompanyStateContext,
    ) -> float:
        return (
            self.price_override
            if self.price_override is not None
            else context.price
        )

    def get_effective_variable_cost(
        self,
        context: CompanyStateContext,
    ) -> float:
        return (
            self.variable_cost_override
            if self.variable_cost_override is not None
            else context.variable_cost_per_unit
        )

    def get_effective_tax_rate(
        self,
        context: CompanyStateContext,
    ) -> float:
        return (
            self.tax_rate_override
            if self.tax_rate_override is not None
            else context.tax_rate
        )

    def get_effective_wacc(
        self,
        context: CompanyStateContext,
    ) -> float:
        return (
            self.wacc_override
            if self.wacc_override is not None
            else context.wacc
        )

    def get_incremental_depreciation(
        self,
        year: int,
    ) -> float:

        if self.depreciation_years <= 0:
            return 0.0

        if year <= 0:
            return 0.0

        if year > self.depreciation_years:
            return 0.0

        return (
            self.initial_investment
            / self.depreciation_years
        )


# ============================================================================
# 3. INVESTMENT YEAR
# ============================================================================

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


# ============================================================================
# 4. YEAR-1 COMPANY IMPACT
# ============================================================================

@dataclass(frozen=True)
class InvestmentYear1Impact:

    incremental_units: float

    incremental_revenue: float
    incremental_variable_cost: float
    incremental_fixed_costs: float

    incremental_depreciation: float
    incremental_ebit: float
    incremental_tax: float
    incremental_net_profit: float

    incremental_ar: float
    incremental_inventory: float
    incremental_ap: float
    incremental_nwc: float

    incremental_fixed_assets: float

    initial_capex: float
    initial_nwc_requirement: float
    initial_funding_requirement: float

    incremental_operating_cash_flow: float


# ============================================================================
# 5. INVESTMENT RESULT
# ============================================================================

@dataclass(frozen=True)
class InvestmentResult:

    npv: float
    irr: float
    payback_years: float

    initial_investment: float
    total_project_cash_flow: float

    yearly_cash_flows: List[InvestmentYear]

    year_1_impact: Optional[
        InvestmentYear1Impact
    ] = None


# ============================================================================
# 6. COMPANY IMPACT
# ============================================================================

@dataclass(frozen=True)
class InvestmentCompanyImpact:

    """
    Company-level changes generated by an accepted investment.

    revenue_delta και variable_cost_delta είναι τα authoritative
    incremental economics.

    volume_delta είναι πληροφοριακό και δεν πρέπει να χρησιμοποιείται
    για να ξαναϋπολογίσει revenue όταν υπάρχει explicit investment price.
    """

    volume_delta: float
    revenue_delta: float
    variable_cost_delta: float
    fixed_opex_delta: float
    fixed_assets_delta: float
    depreciation_delta: float


# ============================================================================
# 7. WORKING CAPITAL
# ============================================================================

def calculate_incremental_working_capital(
    revenue: float,
    variable_cost_total: float,
    context: CompanyStateContext,
) -> Dict[str, float]:

    incremental_ar = (
        revenue
        * context.ar_days
        / 365.0
    )

    incremental_inventory = (
        variable_cost_total
        * context.inventory_days
        / 365.0
    )

    incremental_ap = (
        variable_cost_total
        * context.ap_days
        / 365.0
    )

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


# ============================================================================
# 8. CORE FINANCIAL CALCULATIONS
# ============================================================================

def calculate_npv(
    cash_flows: List[float],
    discount_rate: float,
) -> float:

    return float(
        npf.npv(
            discount_rate,
            cash_flows,
        )
    )


def calculate_irr(
    cash_flows: List[float],
) -> float:

    try:

        value = float(
            npf.irr(cash_flows)
        )

        return (
            value
            if not np.isnan(value)
            else 0.0
        )

    except Exception:
        return 0.0


def calculate_payback(
    cash_flows: List[float],
) -> float:

    cumulative = 0.0

    for i, cf in enumerate(cash_flows):

        cumulative += cf

        if cumulative >= 0:

            if i == 0:
                return 0.0

            previous = cumulative - cf

            fraction = (
                (-previous) / cf
                if cf != 0
                else 0.0
            )

            return (i - 1) + fraction

    return float("inf")


# ============================================================================
# 9. YEAR-1 IMPACT
# ============================================================================

def build_investment_year1_impact(
    assumptions: InvestmentAssumptions,
    context: CompanyStateContext,
) -> InvestmentYear1Impact:

    units = assumptions.units

    price = assumptions.get_effective_price(
        context
    )

    variable_cost_per_unit = (
        assumptions.get_effective_variable_cost(
            context
        )
    )

    incremental_fixed_costs = (
        assumptions.incremental_fixed_costs
    )

    tax_rate = (
        assumptions.get_effective_tax_rate(
            context
        )
    )

    revenue = (
        units
        * price
    )

    variable_cost_total = (
        units
        * variable_cost_per_unit
    )

    depreciation = (
        assumptions.get_incremental_depreciation(
            year=1
        )
    )

    ebit = (
        revenue
        - variable_cost_total
        - incremental_fixed_costs
        - depreciation
    )

    tax = max(
        0.0,
        ebit * tax_rate,
    )

    net_profit = (
        ebit
        - tax
    )

    operating_cash_flow = (
        net_profit
        + depreciation
    )

    wc = calculate_incremental_working_capital(
        revenue=revenue,
        variable_cost_total=variable_cost_total,
        context=context,
    )

    initial_capex = (
        assumptions.initial_investment
    )

    initial_nwc = wc["nwc"]

    funding_requirement = (
        initial_capex
        + initial_nwc
    )

    return InvestmentYear1Impact(

        incremental_units=units,

        incremental_revenue=revenue,

        incremental_variable_cost=(
            variable_cost_total
        ),

        incremental_fixed_costs=(
            incremental_fixed_costs
        ),

        incremental_depreciation=(
            depreciation
        ),

        incremental_ebit=ebit,

        incremental_tax=tax,

        incremental_net_profit=net_profit,

        incremental_ar=wc["ar"],

        incremental_inventory=wc["inventory"],

        incremental_ap=wc["ap"],

        incremental_nwc=initial_nwc,

        incremental_fixed_assets=(
            initial_capex
        ),

        initial_capex=initial_capex,

        initial_nwc_requirement=initial_nwc,

        initial_funding_requirement=(
            funding_requirement
        ),

        incremental_operating_cash_flow=(
            operating_cash_flow
        ),
    )


# ============================================================================
# 10. INVESTMENT CASH FLOWS
# ============================================================================

def build_investment_cash_flows(
    assumptions: InvestmentAssumptions,
    context: CompanyStateContext,
) -> List[InvestmentYear]:

    yearly_flows = []

    curr_units = assumptions.units

    curr_price = (
        assumptions.get_effective_price(
            context
        )
    )

    curr_vc_per_unit = (
        assumptions.get_effective_variable_cost(
            context
        )
    )

    curr_fixed_cost = (
        assumptions.incremental_fixed_costs
    )

    tax_rate = (
        assumptions.get_effective_tax_rate(
            context
        )
    )

    # ------------------------------------------------------------------
    # INITIAL NWC
    # ------------------------------------------------------------------

    year_1_revenue = (
        curr_units
        * curr_price
    )

    year_1_vc_total = (
        curr_units
        * curr_vc_per_unit
    )

    year_1_wc = (
        calculate_incremental_working_capital(
            revenue=year_1_revenue,
            variable_cost_total=year_1_vc_total,
            context=context,
        )
    )

    initial_nwc = year_1_wc["nwc"]

    initial_outlay = -(
        assumptions.initial_investment
        + initial_nwc
    )

    # ------------------------------------------------------------------
    # YEAR 0
    # ------------------------------------------------------------------

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

            working_capital_cash_flow=(
                -initial_nwc
            ),

            salvage_value=0.0,

            project_cash_flow=(
                initial_outlay
            ),
        )
    )

    # ------------------------------------------------------------------
    # YEARS 1...N
    # ------------------------------------------------------------------

    prev_nwc = initial_nwc

    for y in range(
        1,
        assumptions.project_years + 1,
    ):

        if y > 1:

            curr_units *= (
                1.0
                + assumptions.annual_volume_growth
            )

            curr_price *= (
                1.0
                + assumptions.annual_price_growth
            )

            curr_vc_per_unit *= (
                1.0
                + assumptions.annual_variable_cost_growth
            )

            curr_fixed_cost *= (
                1.0
                + assumptions.annual_fixed_cost_growth
            )

        revenue = (
            curr_units
            * curr_price
        )

        vc_total = (
            curr_units
            * curr_vc_per_unit
        )

        depreciation = (
            assumptions.get_incremental_depreciation(
                year=y
            )
        )

        ebit = (
            revenue
            - vc_total
            - curr_fixed_cost
            - depreciation
        )

        tax = max(
            0.0,
            ebit * tax_rate,
        )

        nopat = (
            ebit
            - tax
        )

        ocf = (
            nopat
            + depreciation
        )

        wc = (
            calculate_incremental_working_capital(
                revenue=revenue,
                variable_cost_total=vc_total,
                context=context,
            )
        )

        curr_nwc = wc["nwc"]

        if y == assumptions.project_years:

            wc_change = curr_nwc

            salvage = (
                assumptions.salvage_value
            )

        else:

            wc_change = -(
                curr_nwc
                - prev_nwc
            )

            salvage = 0.0

        prev_nwc = curr_nwc

        total_cf = (
            ocf
            + wc_change
            + salvage
        )

        yearly_flows.append(
            InvestmentYear(

                year=y,

                units=curr_units,

                price=curr_price,

                revenue=revenue,

                variable_cost_per_unit=(
                    curr_vc_per_unit
                ),

                variable_cost_total=(
                    vc_total
                ),

                incremental_fixed_costs=(
                    curr_fixed_cost
                ),

                depreciation=depreciation,

                operating_profit=ebit,

                tax=tax,

                operating_cash_flow=ocf,

                incremental_ar=wc["ar"],

                incremental_inventory=(
                    wc["inventory"]
                ),

                incremental_ap=wc["ap"],

                incremental_nwc=curr_nwc,

                working_capital_cash_flow=(
                    wc_change
                ),

                salvage_value=salvage,

                project_cash_flow=total_cf,
            )
        )

    return yearly_flows


# ============================================================================
# 11. EVALUATE INVESTMENT
# ============================================================================

def evaluate_investment(
    assumptions: InvestmentAssumptions,
    context: CompanyStateContext,
) -> InvestmentResult:

    yearly_structs = (
        build_investment_cash_flows(
            assumptions,
            context,
        )
    )

    cash_flows = [
        year.project_cash_flow
        for year in yearly_structs
    ]

    wacc = (
        assumptions.get_effective_wacc(
            context
        )
    )

    npv_value = calculate_npv(
        cash_flows,
        wacc,
    )

    irr_value = calculate_irr(
        cash_flows
    )

    payback_value = calculate_payback(
        cash_flows
    )

    total_cf = sum(cash_flows)

    year_1_impact = (
        build_investment_year1_impact(
            assumptions,
            context,
        )
    )

    return InvestmentResult(

        npv=npv_value,

        irr=irr_value,

        payback_years=payback_value,

        initial_investment=(
            assumptions.initial_investment
        ),

        total_project_cash_flow=total_cf,

        yearly_cash_flows=yearly_structs,

        year_1_impact=year_1_impact,
    )


# ============================================================================
# 12. COMPANY IMPACT BUILDER
# ============================================================================

def build_investment_company_impact(
    impact: InvestmentYear1Impact,
) -> InvestmentCompanyImpact:

    return InvestmentCompanyImpact(

        volume_delta=(
            impact.incremental_units
        ),

        revenue_delta=(
            impact.incremental_revenue
        ),

        variable_cost_delta=(
            impact.incremental_variable_cost
        ),

        fixed_opex_delta=(
            impact.incremental_fixed_costs
        ),

        fixed_assets_delta=(
            impact.initial_capex
        ),

        depreciation_delta=(
            impact.incremental_depreciation
        ),
    )


# ============================================================================
# 13. TORNADO SENSITIVITY
# ============================================================================

@dataclass
class TornadoDriver:

    driver_name: str
    base_npv: float
    low_npv: float
    high_npv: float
    range_span: float


def _copy_assumptions_with(
    assumptions: InvestmentAssumptions,
    **kwargs,
) -> InvestmentAssumptions:

    data = {
        field_name: getattr(
            assumptions,
            field_name,
        )
        for field_name
        in assumptions.__dataclass_fields__
    }

    data.update(kwargs)

    return InvestmentAssumptions(
        **data
    )


def calculate_tornado_sensitivity(
    assumptions: InvestmentAssumptions,
    context: CompanyStateContext,
    variation_pct: float = 0.10,
) -> List[TornadoDriver]:

    base_result = evaluate_investment(
        assumptions,
        context,
    )

    base_npv = base_result.npv

    drivers = [
        (
            "Selling Price",
            "price_override",
            assumptions.get_effective_price(context),
        ),
        (
            "Volume",
            "units",
            assumptions.units,
        ),
        (
            "Variable Cost / Unit",
            "variable_cost_override",
            assumptions.get_effective_variable_cost(context),
        ),
        (
            "Initial Investment",
            "initial_investment",
            assumptions.initial_investment,
        ),
        (
            "Incremental Fixed Costs",
            "incremental_fixed_costs",
            assumptions.incremental_fixed_costs,
        ),
        (
            "WACC",
            "wacc_override",
            assumptions.get_effective_wacc(context),
        ),
    ]

    results = []

    for display_name, field_name, value in drivers:

        if value is None:
            continue

        if value == 0:
            continue

        if field_name == "price_override":
            low_kwargs = {
                "price_override":
                    value * (1.0 - variation_pct)
            }

            high_kwargs = {
                "price_override":
                    value * (1.0 + variation_pct)
            }

        elif field_name == "variable_cost_override":

            low_kwargs = {
                "variable_cost_override":
                    value * (1.0 - variation_pct)
            }

            high_kwargs = {
                "variable_cost_override":
                    value * (1.0 + variation_pct)
            }

        elif field_name == "wacc_override":

            low_kwargs = {
                "wacc_override":
                    max(
                        0.0,
                        value * (1.0 - variation_pct),
                    )
            }

            high_kwargs = {
                "wacc_override":
                    value * (1.0 + variation_pct)
            }

        else:

            low_kwargs = {
                field_name:
                    value * (1.0 - variation_pct)
            }

            high_kwargs = {
                field_name:
                    value * (1.0 + variation_pct)
            }

        low_assumptions = (
            _copy_assumptions_with(
                assumptions,
                **low_kwargs,
            )
        )

        high_assumptions = (
            _copy_assumptions_with(
                assumptions,
                **high_kwargs,
            )
        )

        low_npv = evaluate_investment(
            low_assumptions,
            context,
        ).npv

        high_npv = evaluate_investment(
            high_assumptions,
            context,
        ).npv

        results.append(
            TornadoDriver(

                driver_name=display_name,

                base_npv=base_npv,

                low_npv=min(
                    low_npv,
                    high_npv,
                ),

                high_npv=max(
                    low_npv,
                    high_npv,
                ),

                range_span=abs(
                    high_npv
                    - low_npv
                ),
            )
        )

    results.sort(
        key=lambda x: x.range_span,
        reverse=True,
    )

    return results


# ============================================================================
# 14. EXIT FLEXIBILITY
# ============================================================================

def calculate_exit_option(
    assumptions: InvestmentAssumptions,
    context: CompanyStateContext,
    downside_volume_pct: float = 0.0,
) -> Dict[str, float]:

    base_result = evaluate_investment(
        assumptions,
        context,
    )

    base_cash_flows = [
        year.project_cash_flow
        for year in base_result.yearly_cash_flows
    ]

    wacc = (
        assumptions.get_effective_wacc(
            context
        )
    )

    base_continue_value = calculate_npv(
        base_cash_flows,
        wacc,
    )

    if not assumptions.allow_exit_after_year_1:

        return {
            "continue_value":
                base_continue_value,

            "exit_value":
                0.0,

            "value_with_exit_option":
                base_continue_value,

            "value_of_flexibility":
                0.0,

            "downside_continue_value":
                base_continue_value,

            "downside_exit_value":
                0.0,
        }

    downside_units = (
        assumptions.units
        * (
            1.0
            - downside_volume_pct
        )
    )

    downside_assumptions = (
        _copy_assumptions_with(
            assumptions,
            units=downside_units,
        )
    )

    downside_result = (
        evaluate_investment(
            downside_assumptions,
            context,
        )
    )

    downside_cash_flows = [
        year.project_cash_flow
        for year
        in downside_result.yearly_cash_flows
    ]

    downside_continue_value = calculate_npv(
        downside_cash_flows,
        wacc,
    )

    if len(downside_cash_flows) < 2:

        return {
            "continue_value":
                base_continue_value,

            "exit_value":
                0.0,

            "value_with_exit_option":
                base_continue_value,

            "value_of_flexibility":
                0.0,

            "downside_continue_value":
                downside_continue_value,

            "downside_exit_value":
                0.0,
        }

    year_1_cf = (
        downside_cash_flows[1]
    )

    net_exit_value = (
        assumptions.exit_value
        - assumptions.exit_cost
    )

    exit_cash_flow_year_1 = (
        year_1_cf
        + net_exit_value
    )

    downside_exit_value = (
        downside_cash_flows[0]
        + (
            exit_cash_flow_year_1
            / (1.0 + wacc)
        )
    )

    value_with_exit_option = max(
        downside_continue_value,
        downside_exit_value,
    )

    value_of_flexibility = max(
        0.0,
        downside_exit_value
        - downside_continue_value,
    )

    return {

        "continue_value":
            base_continue_value,

        "exit_value":
            downside_exit_value,

        "value_with_exit_option":
            value_with_exit_option,

        "value_of_flexibility":
            value_of_flexibility,

        "downside_continue_value":
            downside_continue_value,

        "downside_exit_value":
            downside_exit_value,
    }


# ============================================================================
# 15. STREAMLIT UI
# ============================================================================

def render_investment_decision_lab(
    baseline_state=None,
):

    st.title("📊 Investment Decision Lab")

    st.markdown(
        "Evaluate an investment using incremental cash flows, "
        "NPV, IRR, Payback and decision-driver sensitivity."
    )

    st.divider()

    # ========================================================================
    # BASELINE
    # ========================================================================

    if baseline_state is not None:

        baseline_price = float(
            baseline_state.drivers.price
        )

        baseline_variable_cost = float(
            baseline_state.drivers.variable_cost_per_unit
        )

        baseline_fixed_opex = float(
            baseline_state.drivers.fixed_opex
        )

        baseline_fixed_assets = float(
            baseline_state.drivers.fixed_assets
        )

        baseline_depreciation = float(
            baseline_state.drivers.depreciation
        )

        baseline_tax_rate = float(
            baseline_state.capital_structure.tax_rate
        )

        baseline_wacc = float(
            baseline_state.capital_structure.wacc
        )

        baseline_ar_days = float(
            baseline_state.working_capital.ar_days
        )

        baseline_inventory_days = float(
            baseline_state.working_capital.inventory_days
        )

        baseline_ap_days = float(
            baseline_state.working_capital.ap_days
        )

    else:

        baseline_price = 0.0
        baseline_variable_cost = 0.0
        baseline_fixed_opex = 0.0
        baseline_fixed_assets = 0.0
        baseline_depreciation = 0.0
        baseline_tax_rate = 0.0
        baseline_wacc = 0.0
        baseline_ar_days = 0.0
        baseline_inventory_days = 0.0
        baseline_ap_days = 0.0

    # ========================================================================
    # INVESTMENT INPUTS
    # ========================================================================

    st.subheader("Investment Proposal")

    col1, col2 = st.columns(2)

    with col1:

        initial_investment = st.number_input(
            "Initial CAPEX",
            min_value=0.0,
            value=0.0,
            step=10000.0,
            help="Initial capital expenditure of the investment.",
        )

        project_years = st.number_input(
            "Project Years",
            min_value=1,
            value=5,
            step=1,
        )

        units = st.number_input(
            "Year-1 Incremental Units",
            min_value=0.0,
            value=0.0,
            step=1000.0,
            help="Additional units generated by the investment.",
        )

    with col2:

        depreciation_years = st.number_input(
            "Useful Life / Depreciation Years",
            min_value=1,
            value=10,
            step=1,
            help="Useful life of the new CAPEX.",
        )

        incremental_fixed_costs = st.number_input(
            "Year-1 Incremental Fixed Costs",
            min_value=0.0,
            value=0.0,
            step=1000.0,
            help=(
                "Additional fixed operating costs created "
                "by the investment. Existing company fixed "
                "opex is not entered again."
            ),
        )

        salvage_value = st.number_input(
            "Terminal Salvage Value",
            min_value=0.0,
            value=0.0,
            step=1000.0,
        )

    # ========================================================================
    # COMPANY BASELINE
    # ========================================================================

    st.subheader("Company Baseline")

    c1, c2, c3, c4 = st.columns(4)

    with c1:
        st.metric(
            "Price / Unit",
            f"€{baseline_price:,.2f}",
        )

    with c2:
        st.metric(
            "Variable Cost / Unit",
            f"€{baseline_variable_cost:,.2f}",
        )

    with c3:
        st.metric(
            "Tax Rate",
            f"{baseline_tax_rate * 100:.1f}%",
        )

    with c4:
        st.metric(
            "WACC",
            f"{baseline_wacc * 100:.1f}%",
        )

    wc1, wc2, wc3 = st.columns(3)

    with wc1:
        st.metric(
            "AR Days",
            f"{baseline_ar_days:.0f}",
        )

    with wc2:
        st.metric(
            "Inventory Days",
            f"{baseline_inventory_days:.0f}",
        )

    with wc3:
        st.metric(
            "AP Days",
            f"{baseline_ap_days:.0f}",
        )

    st.caption(
        "Working capital for the investment is derived from "
        "the company's existing working-capital policies."
    )

    # ========================================================================
    # GROWTH
    # ========================================================================

    st.subheader("Project Growth Assumptions")

    g1, g2, g3, g4 = st.columns(4)

    with g1:

        volume_growth = (
            st.number_input(
                "Annual Volume Growth %",
                value=0.0,
                step=1.0,
            )
            / 100.0
        )

    with g2:

        price_growth = (
            st.number_input(
                "Annual Price Growth %",
                value=0.0,
                step=1.0,
            )
            / 100.0
        )

    with g3:

        variable_cost_growth = (
            st.number_input(
                "Annual Variable Cost Growth %",
                value=0.0,
                step=1.0,
            )
            / 100.0
        )

    with g4:

        fixed_cost_growth = (
            st.number_input(
                "Annual Fixed Cost Growth %",
                value=0.0,
                step=1.0,
            )
            / 100.0
        )

    # ========================================================================
    # OVERRIDES
    # ========================================================================

    st.subheader("Investment Economics")

    use_price_override = st.checkbox(
        "Investment uses a different selling price"
    )

    price_override = None

    if use_price_override:

        price_override = st.number_input(
            "Investment Selling Price / Unit",
            min_value=0.0,
            value=float(baseline_price),
            step=0.10,
        )

    use_vc_override = st.checkbox(
        "Investment uses a different variable cost"
    )

    variable_cost_override = None

    if use_vc_override:

        variable_cost_override = st.number_input(
            "Investment Variable Cost / Unit",
            min_value=0.0,
            value=float(baseline_variable_cost),
            step=0.10,
        )

    use_tax_override = st.checkbox(
        "Investment uses a different tax rate"
    )

    tax_rate_override = None

    if use_tax_override:

        tax_rate_override = (
            st.number_input(
                "Investment Tax Rate %",
                min_value=0.0,
                max_value=100.0,
                value=float(
                    baseline_tax_rate * 100.0
                ),
                step=1.0,
            )
            / 100.0
        )

    use_wacc_override = st.checkbox(
        "Investment uses a different WACC"
    )

    wacc_override = None

    if use_wacc_override:

        wacc_override = (
            st.number_input(
                "Investment WACC %",
                min_value=0.0,
                max_value=100.0,
                value=float(
                    baseline_wacc * 100.0
                ),
                step=0.5,
            )
            / 100.0
        )

    # ========================================================================
    # FLEXIBILITY
    # ========================================================================

    st.subheader("Project Flexibility")

    allow_exit = st.checkbox(
        "Allow Exit after Year 1",
        help=(
            "Tests whether management can limit downside "
            "by stopping the investment after Year 1."
        ),
    )

    exit_value = 0.0
    exit_cost = 0.0
    downside_volume_pct = 0.0

    if allow_exit:

        e1, e2, e3 = st.columns(3)

        with e1:

            exit_value = st.number_input(
                "Recoverable Exit Value",
                min_value=0.0,
                value=0.0,
                step=1000.0,
            )

        with e2:

            exit_cost = st.number_input(
                "Exit / Shutdown Cost",
                min_value=0.0,
                value=0.0,
                step=1000.0,
            )

        with e3:

            downside_volume_pct = (
                st.number_input(
                    "Year-1 Volume Downside %",
                    min_value=0.0,
                    max_value=100.0,
                    value=20.0,
                    step=5.0,
                )
                / 100.0
            )

    # ========================================================================
    # EVALUATE
    # ========================================================================

    if st.button(
        "▶ Evaluate Investment",
        type="primary",
        use_container_width=True,
    ):

        context = CompanyStateContext(

            price=baseline_price,

            variable_cost_per_unit=(
                baseline_variable_cost
            ),

            fixed_costs=baseline_fixed_opex,

            tax_rate=baseline_tax_rate,

            wacc=baseline_wacc,

            ar_days=baseline_ar_days,

            inventory_days=(
                baseline_inventory_days
            ),

            ap_days=baseline_ap_days,

            fixed_assets=baseline_fixed_assets,

            depreciation=baseline_depreciation,
        )

        assumptions = InvestmentAssumptions(

            initial_investment=(
                initial_investment
            ),

            project_years=int(
                project_years
            ),

            units=units,

            depreciation_years=int(
                depreciation_years
            ),

            incremental_fixed_costs=(
                incremental_fixed_costs
            ),

            annual_volume_growth=(
                volume_growth
            ),

            annual_price_growth=(
                price_growth
            ),

            annual_variable_cost_growth=(
                variable_cost_growth
            ),

            annual_fixed_cost_growth=(
                fixed_cost_growth
            ),

            salvage_value=(
                salvage_value
            ),

            price_override=(
                price_override
            ),

            variable_cost_override=(
                variable_cost_override
            ),

            tax_rate_override=(
                tax_rate_override
            ),

            wacc_override=(
                wacc_override
            ),

            allow_exit_after_year_1=(
                allow_exit
            ),

            exit_value=(
                exit_value
            ),

            exit_cost=(
                exit_cost
            ),
        )

        result = evaluate_investment(
            assumptions,
            context,
        )

        # ====================================================================
        # RESULTS
        # ====================================================================

        st.divider()

        st.subheader("Investment Decision")

        r1, r2, r3 = st.columns(3)

        with r1:

            st.metric(
                "NPV",
                f"€{result.npv:,.0f}",
            )

        with r2:

            st.metric(
                "IRR",
                f"{result.irr * 100:.1f}%",
            )

        with r3:

            if np.isinf(
                result.payback_years
            ):

                payback_text = (
                    "Not recovered"
                )

            else:

                payback_text = (
                    f"{result.payback_years:.2f} years"
                )

            st.metric(
                "Payback",
                payback_text,
            )

        # ====================================================================
        # DECISION SIGNAL
        # ====================================================================

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
                "is value-neutral at the selected discount rate."
            )

        # ====================================================================
        # YEAR-1 COMPANY IMPACT
        # ====================================================================

        if result.year_1_impact is not None:

            impact = result.year_1_impact

            st.divider()

            st.subheader(
                "Year-1 Impact on Existing Company"
            )

            st.caption(
                "Incremental effect if the investment is accepted. "
                "This is not a separate company state."
            )

            i1, i2, i3, i4 = st.columns(4)

            with i1:

                st.metric(
                    "Revenue Δ",
                    f"€{impact.incremental_revenue:,.0f}",
                )

            with i2:

                st.metric(
                    "Variable Cost Δ",
                    f"€{impact.incremental_variable_cost:,.0f}",
                )

            with i3:

                st.metric(
                    "Fixed Opex Δ",
                    f"€{impact.incremental_fixed_costs:,.0f}",
                )

            with i4:

                st.metric(
                    "EBIT Δ",
                    f"€{impact.incremental_ebit:,.0f}",
                )

            i5, i6, i7, i8 = st.columns(4)

            with i5:

                st.metric(
                    "Depreciation Δ",
                    f"€{impact.incremental_depreciation:,.0f}",
                )

            with i6:

                st.metric(
                    "Net Profit Δ",
                    f"€{impact.incremental_net_profit:,.0f}",
                )

            with i7:

                st.metric(
                    "NWC Δ",
                    f"€{impact.incremental_nwc:,.0f}",
                )

            with i8:

                st.metric(
                    "Operating CF Δ",
                    f"€{impact.incremental_operating_cash_flow:,.0f}",
                )

            st.subheader(
                "Funding Requirement"
            )

            f1, f2, f3 = st.columns(3)

            with f1:

                st.metric(
                    "Initial CAPEX",
                    f"€{impact.initial_capex:,.0f}",
                )

            with f2:

                st.metric(
                    "Initial NWC",
                    f"€{impact.initial_nwc_requirement:,.0f}",
                )

            with f3:

                st.metric(
                    "Initial Funding Requirement",
                    f"€{impact.initial_funding_requirement:,.0f}",
                )

        # ====================================================================
        # PROJECT FLEXIBILITY
        # ====================================================================

        if allow_exit:

            exit_analysis = calculate_exit_option(
                assumptions,
                context,
                downside_volume_pct=(
                    downside_volume_pct
                ),
            )

            st.divider()

            st.subheader(
                "Project Flexibility"
            )

            st.caption(
                f"Downside test: Year-1 volume "
                f"{downside_volume_pct * 100:.0f}% below plan."
            )

            x1, x2, x3 = st.columns(3)

            with x1:

                st.metric(
                    "Continue Value",
                    f"€{exit_analysis['downside_continue_value']:,.0f}",
                )

            with x2:

                st.metric(
                    "Exit Value",
                    f"€{exit_analysis['downside_exit_value']:,.0f}",
                )

            with x3:

                st.metric(
                    "Value of Flexibility",
                    f"€{exit_analysis['value_of_flexibility']:,.0f}",
                )

            if (
                exit_analysis[
                    "value_of_flexibility"
                ]
                > 0
            ):

                st.success(
                    "💡 Under the downside scenario, "
                    "the ability to exit after Year 1 has economic value."
                )

            else:

                st.caption(
                    "Under this downside scenario, continuing "
                    "the project has at least as much value as exiting."
                )

        # ====================================================================
        # YEARLY CASH FLOWS
        # ====================================================================

        st.divider()

        st.subheader(
            "Project Cash Flow"
        )

        rows = []

        for year in result.yearly_cash_flows:

            rows.append(
                {
                    "Year": year.year,
                    "Units": year.units,
                    "Price": year.price,
                    "Revenue": year.revenue,
                    "Variable Cost": (
                        year.variable_cost_total
                    ),
                    "Incremental Fixed Costs": (
                        year.incremental_fixed_costs
                    ),
                    "Depreciation": (
                        year.depreciation
                    ),
                    "EBIT": (
                        year.operating_profit
                    ),
                    "Tax": year.tax,
                    "Operating Cash Flow": (
                        year.operating_cash_flow
                    ),
                    "Incremental NWC": (
                        year.incremental_nwc
                    ),
                    "Working Capital Cash Flow": (
                        year.working_capital_cash_flow
                    ),
                    "Salvage": (
                        year.salvage_value
                    ),
                    "Project Cash Flow": (
                        year.project_cash_flow
                    ),
                }
            )

        st.dataframe(
            rows,
            use_container_width=True,
        )

        # ====================================================================
        # TORNADO
        # ====================================================================

        st.divider()

        st.subheader(
            "Decision Drivers — NPV Sensitivity"
        )

        tornado = (
            calculate_tornado_sensitivity(
                assumptions,
                context,
            )
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

        else:

            st.caption(
                "No non-zero drivers available for sensitivity analysis."
            )
