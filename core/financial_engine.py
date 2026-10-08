from dataclasses import dataclass
from typing import Dict, Any, Optional, Sequence

from core.models import CompanyState
from core.investment_company_impact import InvestmentCompanyImpact


# ============================================================
# INCOME STATEMENT
# ============================================================

@dataclass(frozen=True)
class IncomeStatement:
    revenue: float
    cogs: float
    gross_profit: float
    fixed_opex: float
    ebitda: float
    depreciation: float
    ebit: float
    interest_expense: float
    ebt: float
    tax: float
    net_profit: float


# ============================================================
# WORKING CAPITAL
# ============================================================

@dataclass(frozen=True)
class WorkingCapitalMetrics:
    ar: float
    inventory: float
    ap: float
    nwc: float
    wc_cash_impact: float


# ============================================================
# FINANCIAL STATEMENTS
# ============================================================

@dataclass(frozen=True)
class FinancialStatements:
    income_statement: IncomeStatement
    working_capital: WorkingCapitalMetrics
    principal_payments: float
    fcfe: float


# ============================================================
# VARIANCE / IMPACT
# ============================================================

@dataclass(frozen=True)
class VarianceImpact:
    revenue_delta: float
    price_effect: float
    volume_effect: float

    gross_profit_delta: float
    ebitda_delta: float
    net_profit_delta: float

    nwc_cash_impact_delta: float
    fcfe_delta: float

    # Investment bridge
    investment_revenue_delta: float
    investment_variable_cost_delta: float
    investment_fixed_opex_delta: float
    investment_depreciation_delta: float
    investment_nwc_delta: float

    investment_initial_capex: float
    investment_initial_nwc_requirement: float
    investment_initial_funding_requirement: float

    investment_operating_cash_flow_delta: float
    investment_cash_impact: float


# ============================================================
# FINANCIAL PROJECTION
# ============================================================

@dataclass(frozen=True)
class FinancialProjection:
    baseline: FinancialStatements
    projected: FinancialStatements
    impact: VarianceImpact

    investment_impacts: tuple = ()


# ============================================================
# CORE FINANCIAL ENGINE
# ============================================================

class FinancialEngine:
    """
    Canonical financial integration layer.

    Responsibilities
    ----------------
    1. Calculate company financial statements.
    2. Calculate direct decision impacts.
    3. Integrate Year-1 investment impacts.
    4. Produce one coherent projected financial state.

    Important architecture rule
    ----------------------------
    CompanyState.net_profit is the reported / locked baseline value.

    FinancialEngine calculates a modelled financial baseline independently.

    When producing an integrated projection, the engine does NOT use
    CompanyState.net_profit as an anchor for the projected modelled
    financial statements.

    The projected net profit is calculated from the integrated economics:

        Revenue
        - COGS
        - Fixed Opex
        - Depreciation
        - Interest
        - Tax
        = Net Profit

    This avoids mixing reported baseline profit with modelled incremental
    economics.
    """

    # ========================================================
    # BASIC FINANCIAL STATEMENTS
    # ========================================================

    @staticmethod
    def calculate_statements(
        state: CompanyState,
        prior_nwc: Optional[float] = None,
    ) -> FinancialStatements:

        revenue = (
            state.volume
            * state.price
        )

        cogs = (
            state.volume
            * state.variable_cost_per_unit
        )

        gross_profit = (
            revenue
            - cogs
        )

        fixed_opex = state.fixed_opex

        ebitda = (
            gross_profit
            - fixed_opex
        )

        depreciation = state.depreciation

        ebit = (
            ebitda
            - depreciation
        )

        interest_expense = (
            state.annual_cash_interest_paid
        )

        ebt = (
            ebit
            - interest_expense
        )

        tax = max(
            0.0,
            ebt * state.tax_rate,
        )

        net_profit = (
            ebt
            - tax
        )

        # ----------------------------------------------------
        # Working capital
        # ----------------------------------------------------

        ar = (
            state.ar_days
            / 365.0
            * revenue
        )

        inventory = (
            state.inventory_days
            / 365.0
            * cogs
        )

        ap = (
            state.ap_days
            / 365.0
            * cogs
        )

        nwc = (
            ar
            + inventory
            - ap
        )

        if prior_nwc is None:
            wc_cash_impact = 0.0
        else:
            wc_cash_impact = (
                prior_nwc
                - nwc
            )

        principal_payments = (
            state.principal_payments
        )

        fcfe = (
            net_profit
            + depreciation
            - principal_payments
            + wc_cash_impact
        )

        return FinancialStatements(
            income_statement=IncomeStatement(
                revenue=revenue,
                cogs=cogs,
                gross_profit=gross_profit,
                fixed_opex=fixed_opex,
                ebitda=ebitda,
                depreciation=depreciation,
                ebit=ebit,
                interest_expense=interest_expense,
                ebt=ebt,
                tax=tax,
                net_profit=net_profit,
            ),
            working_capital=WorkingCapitalMetrics(
                ar=ar,
                inventory=inventory,
                ap=ap,
                nwc=nwc,
                wc_cash_impact=wc_cash_impact,
            ),
            principal_payments=principal_payments,
            fcfe=fcfe,
        )

    # ========================================================
    # DIRECT COMPANY VARIANCE
    # ========================================================

    @classmethod
    def calculate_variance_impact(
        cls,
        baseline_state: CompanyState,
        projected_state: CompanyState,
    ) -> VarianceImpact:

        baseline = cls.calculate_statements(
            baseline_state
        )

        projected = cls.calculate_statements(
            projected_state,
            prior_nwc=baseline.working_capital.nwc,
        )

        baseline_is = baseline.income_statement
        projected_is = projected.income_statement

        baseline_wc = baseline.working_capital
        projected_wc = projected.working_capital

        revenue_delta = (
            projected_is.revenue
            - baseline_is.revenue
        )

        price_effect = (
            baseline_state.volume
            * (
                projected_state.price
                - baseline_state.price
            )
        )

        volume_effect = (
            (
                projected_state.volume
                - baseline_state.volume
            )
            * projected_state.price
        )

        gross_profit_delta = (
            projected_is.gross_profit
            - baseline_is.gross_profit
        )

        ebitda_delta = (
            projected_is.ebitda
            - baseline_is.ebitda
        )

        net_profit_delta = (
            projected_is.net_profit
            - baseline_is.net_profit
        )

        nwc_cash_impact_delta = (
            projected_wc.wc_cash_impact
            - baseline_wc.wc_cash_impact
        )

        fcfe_delta = (
            projected.fcfe
            - baseline.fcfe
        )

        return VarianceImpact(
            revenue_delta=revenue_delta,
            price_effect=price_effect,
            volume_effect=volume_effect,
            gross_profit_delta=gross_profit_delta,
            ebitda_delta=ebitda_delta,
            net_profit_delta=net_profit_delta,
            nwc_cash_impact_delta=nwc_cash_impact_delta,
            fcfe_delta=fcfe_delta,
            investment_revenue_delta=0.0,
            investment_variable_cost_delta=0.0,
            investment_fixed_opex_delta=0.0,
            investment_depreciation_delta=0.0,
            investment_nwc_delta=0.0,
            investment_initial_capex=0.0,
            investment_initial_nwc_requirement=0.0,
            investment_initial_funding_requirement=0.0,
            investment_operating_cash_flow_delta=0.0,
            investment_cash_impact=0.0,
        )

    # ========================================================
    # INVESTMENT VALIDATION
    # ========================================================

    @staticmethod
    def _validate_investment_impacts(
        investment_impacts: Sequence[
            InvestmentCompanyImpact
        ],
    ) -> None:

        for impact in investment_impacts:

            if not isinstance(
                impact,
                InvestmentCompanyImpact,
            ):
                raise TypeError(
                    "investment_impacts must contain "
                    "InvestmentCompanyImpact objects."
                )

    # ========================================================
    # AGGREGATE INVESTMENT IMPACTS
    # ========================================================

    @staticmethod
    def _aggregate_investment_impacts(
        investment_impacts: Sequence[
            InvestmentCompanyImpact
        ],
    ) -> Dict[str, float]:

        return {
            "revenue_delta": sum(
                x.revenue_delta
                for x in investment_impacts
            ),
            "variable_cost_delta": sum(
                x.variable_cost_delta
                for x in investment_impacts
            ),
            "fixed_opex_delta": sum(
                x.fixed_opex_delta
                for x in investment_impacts
            ),
            "depreciation_delta": sum(
                x.depreciation_delta
                for x in investment_impacts
            ),
            "ar_delta": sum(
                x.ar_delta
                for x in investment_impacts
            ),
            "inventory_delta": sum(
                x.inventory_delta
                for x in investment_impacts
            ),
            "ap_delta": sum(
                x.ap_delta
                for x in investment_impacts
            ),
            "nwc_delta": sum(
                x.nwc_delta
                for x in investment_impacts
            ),
            "initial_capex": sum(
                x.initial_capex
                for x in investment_impacts
            ),
            "initial_nwc_requirement": sum(
                x.initial_nwc_requirement
                for x in investment_impacts
            ),
            "initial_funding_requirement": sum(
                x.initial_funding_requirement
                for x in investment_impacts
            ),
            "operating_cash_flow_delta": sum(
                x.operating_cash_flow_delta
                for x in investment_impacts
            ),
            "project_cash_impact": sum(
                x.project_cash_impact
                for x in investment_impacts
            ),
        }

    # ========================================================
    # INTEGRATED FINANCIAL STATEMENTS
    # ========================================================

    @classmethod
    def _build_integrated_statements(
        cls,
        projected_company_fin: FinancialStatements,
        baseline_company_fin: FinancialStatements,
        projected_state: CompanyState,
        investment_impacts: Sequence[
            InvestmentCompanyImpact
        ],
    ) -> FinancialStatements:

        aggregated = (
            cls._aggregate_investment_impacts(
                investment_impacts
            )
        )

        # ----------------------------------------------------
        # Company economics + investment economics
        # ----------------------------------------------------

        company_is = (
            projected_company_fin.income_statement
        )

        investment_revenue = (
            aggregated["revenue_delta"]
        )

        investment_variable_cost = (
            aggregated["variable_cost_delta"]
        )

        investment_fixed_opex = (
            aggregated["fixed_opex_delta"]
        )

        investment_depreciation = (
            aggregated["depreciation_delta"]
        )

        integrated_revenue = (
            company_is.revenue
            + investment_revenue
        )

        integrated_cogs = (
            company_is.cogs
            + investment_variable_cost
        )

        integrated_gross_profit = (
            integrated_revenue
            - integrated_cogs
        )

        integrated_fixed_opex = (
            company_is.fixed_opex
            + investment_fixed_opex
        )

        integrated_ebitda = (
            integrated_gross_profit
            - integrated_fixed_opex
        )

        integrated_depreciation = (
            company_is.depreciation
            + investment_depreciation
        )

        integrated_ebit = (
            integrated_ebitda
            - integrated_depreciation
        )

        integrated_interest = (
            company_is.interest_expense
        )

        integrated_ebt = (
            integrated_ebit
            - integrated_interest
        )

        integrated_tax = max(
            0.0,
            integrated_ebt
            * projected_state.tax_rate,
        )

        # ----------------------------------------------------
        # IMPORTANT
        #
        # The integrated net profit is calculated directly
        # from the integrated financial statement.
        #
        # We do NOT anchor this to:
        #
        #     projected_state.net_profit
        #
        # because that is the reported CompanyState value,
        # whereas this projection is a modelled financial
        # statement.
        # ----------------------------------------------------

        integrated_net_profit = (
            integrated_ebt
            - integrated_tax
        )

        # ----------------------------------------------------
        # Working capital
        # ----------------------------------------------------

        company_wc = (
            projected_company_fin.working_capital
        )

        integrated_ar = (
            company_wc.ar
            + aggregated["ar_delta"]
        )

        integrated_inventory = (
            company_wc.inventory
            + aggregated["inventory_delta"]
        )

        integrated_ap = (
            company_wc.ap
            + aggregated["ap_delta"]
        )

        integrated_nwc = (
            integrated_ar
            + integrated_inventory
            - integrated_ap
        )

        integrated_wc_cash_impact = (
            baseline_company_fin
            .working_capital
            .nwc
            - integrated_nwc
        )

        # ----------------------------------------------------
        # FCFE
        # ----------------------------------------------------

        integrated_principal = (
            projected_company_fin.principal_payments
        )

        integrated_fcfe = (
            integrated_net_profit
            + integrated_depreciation
            - integrated_principal
            + integrated_wc_cash_impact
        )

        return FinancialStatements(
            income_statement=IncomeStatement(
                revenue=integrated_revenue,
                cogs=integrated_cogs,
                gross_profit=integrated_gross_profit,
                fixed_opex=integrated_fixed_opex,
                ebitda=integrated_ebitda,
                depreciation=integrated_depreciation,
                ebit=integrated_ebit,
                interest_expense=integrated_interest,
                ebt=integrated_ebt,
                tax=integrated_tax,
                net_profit=integrated_net_profit,
            ),
            working_capital=WorkingCapitalMetrics(
                ar=integrated_ar,
                inventory=integrated_inventory,
                ap=integrated_ap,
                nwc=integrated_nwc,
                wc_cash_impact=integrated_wc_cash_impact,
            ),
            principal_payments=integrated_principal,
            fcfe=integrated_fcfe,
        )

    # ========================================================
    # BUILD PROJECTION
    # ========================================================

    @classmethod
    def build_projection(
        cls,
        baseline_state: CompanyState,
        projected_state: CompanyState,
        investment_impacts: Sequence[
            InvestmentCompanyImpact
        ] = (),
    ) -> FinancialProjection:

        cls._validate_investment_impacts(
            investment_impacts
        )

        # ----------------------------------------------------
        # Baseline company financials
        # ----------------------------------------------------

        baseline_fin = cls.calculate_statements(
            baseline_state
        )

        # ----------------------------------------------------
        # Projected company financials
        #
        # prior_nwc is the locked baseline NWC so that
        # working-capital cash impact measures the change
        # from baseline.
        # ----------------------------------------------------

        projected_company_fin = cls.calculate_statements(
            projected_state,
            prior_nwc=baseline_fin.working_capital.nwc,
        )

        # ====================================================
        # NO INVESTMENT
        # ====================================================

        if not investment_impacts:

            projected_is = (
                projected_company_fin.income_statement
            )

            projected_wc = (
                projected_company_fin.working_capital
            )

            # -----------------------------------------------
            # Direct company modelled NP delta
            # -----------------------------------------------

            modelled_net_profit_delta = (
                projected_is.net_profit
                - baseline_fin.income_statement.net_profit
            )

            # -----------------------------------------------
            # Preserve the reported baseline NP only for the
            # no-investment reconciliation.
            #
            # This maintains the existing architecture:
            #
            # reported baseline NP
            # + modelled direct decision delta
            # -----------------------------------------------

            reconciled_net_profit = (
                baseline_state.net_profit
                + modelled_net_profit_delta
            )

            reconciled_fcfe = (
                reconciled_net_profit
                + projected_is.depreciation
                - projected_company_fin.principal_payments
                + projected_wc.wc_cash_impact
            )

            projected_fin = FinancialStatements(
                income_statement=IncomeStatement(
                    revenue=projected_is.revenue,
                    cogs=projected_is.cogs,
                    gross_profit=projected_is.gross_profit,
                    fixed_opex=projected_is.fixed_opex,
                    ebitda=projected_is.ebitda,
                    depreciation=projected_is.depreciation,
                    ebit=projected_is.ebit,
                    interest_expense=projected_is.interest_expense,
                    ebt=projected_is.ebt,
                    tax=projected_is.tax,
                    net_profit=reconciled_net_profit,
                ),
                working_capital=projected_wc,
                principal_payments=(
                    projected_company_fin.principal_payments
                ),
                fcfe=reconciled_fcfe,
            )

        # ====================================================
        # WITH INVESTMENT
        # ====================================================

        else:

            projected_fin = (
                cls._build_integrated_statements(
                    projected_company_fin=projected_company_fin,
                    baseline_company_fin=baseline_fin,
                    projected_state=projected_state,
                    investment_impacts=investment_impacts,
                )
            )

        # ====================================================
        # TOTAL IMPACT
        # ====================================================

        baseline_is = (
            baseline_fin.income_statement
        )

        projected_is = (
            projected_fin.income_statement
        )

        baseline_wc = (
            baseline_fin.working_capital
        )

        projected_wc = (
            projected_fin.working_capital
        )

        revenue_delta = (
            projected_is.revenue
            - baseline_is.revenue
        )

        price_effect = (
            baseline_state.volume
            * (
                projected_state.price
                - baseline_state.price
            )
        )

        volume_effect = (
            (
                projected_state.volume
                - baseline_state.volume
            )
            * projected_state.price
        )

        gross_profit_delta = (
            projected_is.gross_profit
            - baseline_is.gross_profit
        )

        ebitda_delta = (
            projected_is.ebitda
            - baseline_is.ebitda
        )

        modelled_net_profit_delta = (
            projected_is.net_profit
            - baseline_is.net_profit
        )

        nwc_cash_impact_delta = (
            projected_wc.wc_cash_impact
            - baseline_wc.wc_cash_impact
        )

        fcfe_delta = (
            projected_fin.fcfe
            - baseline_fin.fcfe
        )

        # ----------------------------------------------------
        # Investment bridge
        # ----------------------------------------------------

        aggregated = (
            cls._aggregate_investment_impacts(
                investment_impacts
            )
            if investment_impacts
            else {
                "revenue_delta": 0.0,
                "variable_cost_delta": 0.0,
                "fixed_opex_delta": 0.0,
                "depreciation_delta": 0.0,
                "nwc_delta": 0.0,
                "initial_capex": 0.0,
                "initial_nwc_requirement": 0.0,
                "initial_funding_requirement": 0.0,
                "operating_cash_flow_delta": 0.0,
                "project_cash_impact": 0.0,
            }
        )

        impact = VarianceImpact(
            revenue_delta=revenue_delta,
            price_effect=price_effect,
            volume_effect=volume_effect,
            gross_profit_delta=gross_profit_delta,
            ebitda_delta=ebitda_delta,
            net_profit_delta=modelled_net_profit_delta,
            nwc_cash_impact_delta=nwc_cash_impact_delta,
            fcfe_delta=fcfe_delta,
            investment_revenue_delta=(
                aggregated["revenue_delta"]
            ),
            investment_variable_cost_delta=(
                aggregated["variable_cost_delta"]
            ),
            investment_fixed_opex_delta=(
                aggregated["fixed_opex_delta"]
            ),
            investment_depreciation_delta=(
                aggregated["depreciation_delta"]
            ),
            investment_nwc_delta=(
                aggregated["nwc_delta"]
            ),
            investment_initial_capex=(
                aggregated["initial_capex"]
            ),
            investment_initial_nwc_requirement=(
                aggregated[
                    "initial_nwc_requirement"
                ]
            ),
            investment_initial_funding_requirement=(
                aggregated[
                    "initial_funding_requirement"
                ]
            ),
            investment_operating_cash_flow_delta=(
                aggregated[
                    "operating_cash_flow_delta"
                ]
            ),
            investment_cash_impact=(
                aggregated[
                    "project_cash_impact"
                ]
            ),
        )

        return FinancialProjection(
            baseline=baseline_fin,
            projected=projected_fin,
            impact=impact,
            investment_impacts=tuple(
                investment_impacts
            ),
        )
