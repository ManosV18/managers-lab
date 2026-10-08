from dataclasses import dataclass
from typing import Dict, Any, Optional, Sequence

from core.models import CompanyState
from core.investment_company_impact import InvestmentCompanyImpact


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


@dataclass(frozen=True)
class WorkingCapitalMetrics:
    ar: float
    inventory: float
    ap: float
    nwc: float
    wc_cash_impact: float


@dataclass(frozen=True)
class FinancialStatements:
    income_statement: IncomeStatement
    working_capital: WorkingCapitalMetrics
    principal_payments: float
    fcfe: float


@dataclass(frozen=True)
class VarianceImpact:
    """
    Financial Impact Layer.

    Connects CompanyState driver changes and investment
    Year-1 impacts with financial results.
    """

    revenue_delta: float
    price_effect: float
    volume_effect: float
    gross_profit_delta: float
    ebitda_delta: float
    net_profit_delta: float
    nwc_cash_impact_delta: float
    fcfe_delta: float

    # Investment-specific incremental impact.
    investment_revenue_delta: float = 0.0
    investment_variable_cost_delta: float = 0.0
    investment_fixed_opex_delta: float = 0.0
    investment_depreciation_delta: float = 0.0
    investment_nwc_delta: float = 0.0
    investment_initial_capex: float = 0.0
    investment_initial_nwc_requirement: float = 0.0
    investment_initial_funding_requirement: float = 0.0
    investment_operating_cash_flow_delta: float = 0.0
    investment_cash_impact: float = 0.0


@dataclass(frozen=True)
class FinancialProjection:
    baseline: FinancialStatements
    projected: FinancialStatements
    impact: VarianceImpact

    # Detailed investment bridge.
    investment_impacts: tuple[InvestmentCompanyImpact, ...] = ()


class FinancialEngine:
    """
    LOCKED Financial Engine v2.

    Canonical company financial engine with optional integration
    of Year-1 InvestmentCompanyImpact objects.

    Core principles
    ---------------
    1. CompanyState remains the canonical representation
       of the existing company.

    2. Investment projects are NOT converted into changes
       of company price or variable cost per unit.

    3. Direct Decisions continue to flow through CompanyState.

    4. Investments enter the financial layer through their
       explicit Year-1 incremental impact.

    5. Investment economics remain multi-year and are evaluated
       by the investment engine. This class only integrates the
       Year-1 company impact.

    6. All calculations remain deterministic and side-effect free.

    Accounting cascade
    ------------------
        IS
         ↓
        WC
         ↓
        FCFE

    Investment integration
    ----------------------
        Existing Company
              +
        Investment Year-1 Impact
              ↓
        Integrated Financial Statements
    """

    DAYS_IN_YEAR: float = 365.0

    # ------------------------------------------------------------------
    # CORE COMPANY CALCULATION
    # ------------------------------------------------------------------

    @classmethod
    def calculate_statements(
        cls,
        state: CompanyState,
        prior_nwc: Optional[float] = None,
    ) -> FinancialStatements:
        """
        Calculate the financial statements of a CompanyState.

        This method deliberately knows nothing about investments.

        If prior_nwc is omitted, current NWC is used as prior NWC,
        producing zero working-capital cash impact.
        """
        d = state.drivers
        wc = state.working_capital
        cap = state.capital_structure

        # --------------------------------------------------------------
        # 1. INCOME STATEMENT
        # --------------------------------------------------------------

        revenue = float(d.volume * d.price)
        cogs = float(
            d.volume * d.variable_cost_per_unit
        )

        gross_profit = revenue - cogs

        fixed_opex = float(d.fixed_opex)
        ebitda = gross_profit - fixed_opex

        depreciation = float(d.depreciation)
        ebit = ebitda - depreciation

        interest_expense = float(
            cap.annual_cash_interest_paid
        )

        ebt = ebit - interest_expense

        tax = max(
            0.0,
            ebt * cap.tax_rate,
        )

        net_profit = ebt - tax

        income_statement = IncomeStatement(
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
        )

        # --------------------------------------------------------------
        # 2. WORKING CAPITAL
        # --------------------------------------------------------------

        ar = (
            wc.ar_days / cls.DAYS_IN_YEAR
        ) * revenue

        inventory = (
            wc.inventory_days / cls.DAYS_IN_YEAR
        ) * cogs

        ap = (
            wc.ap_days / cls.DAYS_IN_YEAR
        ) * cogs

        current_nwc = (
            ar
            + inventory
            - ap
        )

        baseline_prior = (
            current_nwc
            if prior_nwc is None
            else float(prior_nwc)
        )

        wc_cash_impact = (
            baseline_prior
            - current_nwc
        )

        working_capital = WorkingCapitalMetrics(
            ar=ar,
            inventory=inventory,
            ap=ap,
            nwc=current_nwc,
            wc_cash_impact=wc_cash_impact,
        )

        # --------------------------------------------------------------
        # 3. FCFE
        # --------------------------------------------------------------

        principal = float(
            cap.principal_payments
        )

        fcfe = (
            net_profit
            + depreciation
            - principal
            + wc_cash_impact
        )

        return FinancialStatements(
            income_statement=income_statement,
            working_capital=working_capital,
            principal_payments=principal,
            fcfe=fcfe,
        )

    # ------------------------------------------------------------------
    # DIRECT DECISION VARIANCE
    # ------------------------------------------------------------------

    @classmethod
    def calculate_variance_impact(
        cls,
        baseline_state: CompanyState,
        projected_state: CompanyState,
    ) -> VarianceImpact:
        """
        Calculate the financial impact of direct CompanyState changes.

        This method intentionally does NOT integrate investments.
        """

        base_fin = cls.calculate_statements(
            baseline_state
        )

        projected_fin = cls.calculate_statements(
            projected_state,
            prior_nwc=base_fin.working_capital.nwc,
        )

        base_d = baseline_state.drivers
        proj_d = projected_state.drivers

        delta_price = (
            proj_d.price
            - base_d.price
        )

        delta_volume = (
            proj_d.volume
            - base_d.volume
        )

        price_effect = (
            base_d.volume
            * delta_price
        )

        volume_effect = (
            delta_volume
            * proj_d.price
        )

        revenue_delta = (
            projected_fin.income_statement.revenue
            - base_fin.income_statement.revenue
        )

        return VarianceImpact(
            revenue_delta=revenue_delta,
            price_effect=price_effect,
            volume_effect=volume_effect,
            gross_profit_delta=(
                projected_fin.income_statement.gross_profit
                - base_fin.income_statement.gross_profit
            ),
            ebitda_delta=(
                projected_fin.income_statement.ebitda
                - base_fin.income_statement.ebitda
            ),
            net_profit_delta=(
                projected_fin.income_statement.net_profit
                - base_fin.income_statement.net_profit
            ),
            nwc_cash_impact_delta=(
                projected_fin.working_capital.wc_cash_impact
            ),
            fcfe_delta=(
                projected_fin.fcfe
                - base_fin.fcfe
            ),
        )

    # ------------------------------------------------------------------
    # INVESTMENT HELPERS
    # ------------------------------------------------------------------

    @staticmethod
    def _validate_investment_impacts(
        investment_impacts: Sequence[
            InvestmentCompanyImpact
        ],
    ) -> tuple[InvestmentCompanyImpact, ...]:
        """
        Validate and freeze the supplied investment impacts.
        """

        impacts = tuple(investment_impacts)

        for impact in impacts:
            if not isinstance(
                impact,
                InvestmentCompanyImpact,
            ):
                raise TypeError(
                    "investment_impacts must contain only "
                    "InvestmentCompanyImpact objects."
                )

        return impacts

    @staticmethod
    def _aggregate_investment_impacts(
        investment_impacts: Sequence[
            InvestmentCompanyImpact
        ],
    ) -> Dict[str, float]:
        """
        Aggregate independent Year-1 investment impacts.

        Investments are evaluated against the same locked baseline.
        Therefore aggregation happens only at the explicit incremental
        impact layer.

        Project-specific price and variable cost are never blended
        into CompanyState.
        """

        impacts = tuple(investment_impacts)

        return {
            "revenue_delta": sum(
                impact.revenue_delta
                for impact in impacts
            ),
            "variable_cost_delta": sum(
                impact.variable_cost_delta
                for impact in impacts
            ),
            "fixed_opex_delta": sum(
                impact.fixed_opex_delta
                for impact in impacts
            ),
            "depreciation_delta": sum(
                impact.depreciation_delta
                for impact in impacts
            ),
            "ar_delta": sum(
                impact.ar_delta
                for impact in impacts
            ),
            "inventory_delta": sum(
                impact.inventory_delta
                for impact in impacts
            ),
            "ap_delta": sum(
                impact.ap_delta
                for impact in impacts
            ),
            "nwc_delta": sum(
                impact.nwc_delta
                for impact in impacts
            ),
            "initial_capex": sum(
                impact.initial_capex
                for impact in impacts
            ),
            "initial_nwc_requirement": sum(
                impact.initial_nwc_requirement
                for impact in impacts
            ),
            "initial_funding_requirement": sum(
                impact.initial_funding_requirement
                for impact in impacts
            ),
            "operating_cash_flow_delta": sum(
                impact.operating_cash_flow_delta
                for impact in impacts
            ),
            "project_cash_impact": sum(
                impact.project_cash_impact
                for impact in impacts
            ),
        }

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
        """
        Integrate Year-1 investment economics into the projected
        company financial statements.

        The projected CompanyState already contains the direct
        company decisions.

        Investment impacts are then added explicitly.

        This avoids blending project-specific economics into the
        company's canonical price and variable-cost drivers.
        """

        aggregated = cls._aggregate_investment_impacts(
            investment_impacts
        )

        base_is = projected_company_fin.income_statement
        base_wc = projected_company_fin.working_capital

        investment_revenue = aggregated["revenue_delta"]
        investment_cogs = aggregated["variable_cost_delta"]
        investment_fixed_opex = aggregated["fixed_opex_delta"]
        investment_depreciation = aggregated[
            "depreciation_delta"
        ]

        # --------------------------------------------------------------
        # INTEGRATED INCOME STATEMENT
        # --------------------------------------------------------------

        revenue = (
            base_is.revenue
            + investment_revenue
        )

        cogs = (
            base_is.cogs
            + investment_cogs
        )

        gross_profit = (
            revenue
            - cogs
        )

        fixed_opex = (
            base_is.fixed_opex
            + investment_fixed_opex
        )

        ebitda = (
            gross_profit
            - fixed_opex
        )

        depreciation = (
            base_is.depreciation
            + investment_depreciation
        )

        ebit = (
            ebitda
            - depreciation
        )

        # Investments are currently evaluated on an unlevered basis.
        # Therefore no project-specific interest is added here.
        interest_expense = (
            base_is.interest_expense
        )

        ebt = (
            ebit
            - interest_expense
        )

        tax_rate = (
            projected_state.capital_structure.tax_rate
        )

        tax = max(
            0.0,
            ebt * tax_rate,
        )

        modelled_net_profit = (
            ebt
            - tax
        )

        # --------------------------------------------------------------
        # RECONCILE WITH REPORTED BASELINE NET PROFIT
        # --------------------------------------------------------------

        baseline_modelled_np = (
            baseline_company_fin
            .income_statement
            .net_profit
        )

        modelled_net_profit_delta = (
            modelled_net_profit
            - baseline_modelled_np
        )

        reconciled_net_profit = (
            projected_state.net_profit
            if not investment_impacts
            else (
                projected_state.net_profit
                + (
                    modelled_net_profit
                    - (
                        projected_company_fin
                        .income_statement
                        .net_profit
                    )
                )
            )
        )

        integrated_is = IncomeStatement(
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
            net_profit=reconciled_net_profit,
        )

        # --------------------------------------------------------------
        # INTEGRATED WORKING CAPITAL
        # --------------------------------------------------------------

        integrated_ar = (
            base_wc.ar
            + aggregated["ar_delta"]
        )

        integrated_inventory = (
            base_wc.inventory
            + aggregated["inventory_delta"]
        )

        integrated_ap = (
            base_wc.ap
            + aggregated["ap_delta"]
        )

        integrated_nwc = (
            integrated_ar
            + integrated_inventory
            - integrated_ap
        )

        # Direct company WC cash impact already reflects the
        # baseline-to-company change.
        #
        # For the investment, the Year-1 company cash effect is
        # represented separately through project_cash_impact.
        #
        # Therefore the integrated WC cash impact here captures
        # the change in the actual end-of-Year-1 NWC balance.
        integrated_wc_cash_impact = (
            baseline_company_fin
            .working_capital
            .nwc
            - integrated_nwc
        )

        integrated_wc = WorkingCapitalMetrics(
            ar=integrated_ar,
            inventory=integrated_inventory,
            ap=integrated_ap,
            nwc=integrated_nwc,
            wc_cash_impact=integrated_wc_cash_impact,
        )

        # --------------------------------------------------------------
        # FCFE
        # --------------------------------------------------------------

        principal = (
            projected_company_fin.principal_payments
        )

        integrated_fcfe = (
            reconciled_net_profit
            + depreciation
            - principal
            + integrated_wc_cash_impact
        )

        return FinancialStatements(
            income_statement=integrated_is,
            working_capital=integrated_wc,
            principal_payments=principal,
            fcfe=integrated_fcfe,
        )

    # ------------------------------------------------------------------
    # CANONICAL PROJECTION
    # ------------------------------------------------------------------

    @classmethod
    def build_projection(
        cls,
        baseline_state: CompanyState,
        projected_state: CompanyState,
        investment_impacts: Sequence[
            InvestmentCompanyImpact
        ] = (),
    ) -> FinancialProjection:
        """
        Build a complete financial projection.

        Direct Decisions
        ----------------
        Projected CompanyState represents their effect.

        Investment Decisions
        --------------------
        InvestmentCompanyImpact objects represent their explicit
        Year-1 incremental effect.

        All items are evaluated against the same locked baseline.

        The CompanyState itself is never polluted with project-specific
        selling price or variable cost.
        """

        if not isinstance(
            baseline_state,
            CompanyState,
        ):
            raise TypeError(
                "baseline_state must be a CompanyState."
            )

        if not isinstance(
            projected_state,
            CompanyState,
        ):
            raise TypeError(
                "projected_state must be a CompanyState."
            )

        impacts = cls._validate_investment_impacts(
            investment_impacts
        )

        # --------------------------------------------------------------
        # BASELINE
        # --------------------------------------------------------------

        baseline_fin = cls.calculate_statements(
            baseline_state
        )

        # --------------------------------------------------------------
        # DIRECT COMPANY PROJECTION
        # --------------------------------------------------------------

        projected_company_fin = cls.calculate_statements(
            projected_state,
            prior_nwc=baseline_fin.working_capital.nwc,
        )

        # --------------------------------------------------------------
        # NO INVESTMENTS
        # --------------------------------------------------------------

        if not impacts:
            projected_is = (
                projected_company_fin
                .income_statement
            )

            modelled_net_profit_delta = (
                projected_is.net_profit
                - baseline_fin.income_statement.net_profit
            )

            reconciled_net_profit = (
                baseline_state.net_profit
                + modelled_net_profit_delta
            )

            reconciled_fcfe = (
                reconciled_net_profit
                + projected_is.depreciation
                - projected_company_fin.principal_payments
                + projected_company_fin
                .working_capital
                .wc_cash_impact
            )

            reconciled_income_statement = IncomeStatement(
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
            )

            projected_fin = FinancialStatements(
                income_statement=reconciled_income_statement,
                working_capital=projected_company_fin.working_capital,
                principal_payments=projected_company_fin.principal_payments,
                fcfe=reconciled_fcfe,
            )
        # --------------------------------------------------------------
        # INVESTMENT-INTEGRATED PROJECTION
        # --------------------------------------------------------------

        else:
            projected_fin = (
                cls._build_integrated_statements(
                    projected_company_fin=(
                        projected_company_fin
                    ),
                    baseline_company_fin=baseline_fin,
                    projected_state=projected_state,
                    investment_impacts=impacts,
                )
            )

        # --------------------------------------------------------------
        # IMPACT LAYER
        # --------------------------------------------------------------

        aggregated = cls._aggregate_investment_impacts(
            impacts
        )

        projected_is = projected_fin.income_statement

        price_effect = (
            baseline_state.drivers.volume
            * (
                projected_state.drivers.price
                - baseline_state.drivers.price
            )
        )

        volume_effect = (
            (
                projected_state.drivers.volume
                - baseline_state.drivers.volume
            )
            * projected_state.drivers.price
        )

        modelled_net_profit_delta = (
            projected_fin.income_statement.net_profit
            - baseline_fin.income_statement.net_profit
        )

        # Company-level FCFE delta.
        fcfe_delta = projected_fin.fcfe - baseline_fin.fcfe

        investment_cash_impact = (
            aggregated["project_cash_impact"]
        )

        impact = VarianceImpact(
            revenue_delta=(
                projected_is.revenue
                - baseline_fin.income_statement.revenue
            ),
            price_effect=price_effect,
            volume_effect=volume_effect,
            gross_profit_delta=(
                projected_is.gross_profit
                - baseline_fin.income_statement.gross_profit
            ),
            ebitda_delta=(
                projected_is.ebitda
                - baseline_fin.income_statement.ebitda
            ),
            net_profit_delta=modelled_net_profit_delta,
            nwc_cash_impact_delta=(
                projected_fin
                .working_capital
                .wc_cash_impact
            ),
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
                investment_cash_impact
            ),
        )

        return FinancialProjection(
            baseline=baseline_fin,
            projected=projected_fin,
            impact=impact,
            investment_impacts=impacts,
        )
