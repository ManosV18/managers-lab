from dataclasses import dataclass
from typing import Dict, Any, Optional
from core.models import CompanyState


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
    wc_cash_impact: float  # Θετικό = Απελευθέρωση ρευστών, Αρνητικό = Δέσμευση


@dataclass(frozen=True)
class FinancialStatements:
    income_statement: IncomeStatement
    working_capital: WorkingCapitalMetrics
    principal_payments: float
    fcfe: float


@dataclass(frozen=True)
class VarianceImpact:
    """
    Financial Impact Layer: Συνδέει τα Driver Changes με τα Financial Results.
    """
    revenue_delta: float
    price_effect: float
    volume_effect: float
    gross_profit_delta: float
    ebitda_delta: float
    net_profit_delta: float
    nwc_cash_impact_delta: float
    fcfe_delta: float


@dataclass(frozen=True)
class FinancialProjection:
    baseline: FinancialStatements
    projected: FinancialStatements
    impact: VarianceImpact


class FinancialEngine:
    """
    LOCKED Financial Engine v1 (Canonical Model Aligned):

    Financial Calculation Contract:
    1. Canonical Domain Names:
       - Drivers: variable_cost_per_unit, fixed_opex, depreciation
       - CapitalStructure: annual_cash_interest_paid, cost_of_debt, tax_rate, total_debt, wacc, principal_payments
       - WorkingCapitalPolicy: ar_days, inventory_days, ap_days
    2. Pure Functions: Χωρίς side-effects, πλήρως ντετερμινιστικό.
    3. Explicit Accounting Cascade: IS -> WC -> FCFE.
    4. Variance Reconciliation: Καθαρή απομόνωση Price vs Volume Effects.
    """

    DAYS_IN_YEAR: float = 365.0

    @classmethod
    def calculate_statements(
        cls,
        state: CompanyState,
        prior_nwc: Optional[float] = None
    ) -> FinancialStatements:
        """
        Υπολογίζει πλήρως τις οικονομικές καταστάσεις από ένα CompanyState.

        Αν δεν δοθεί prior_nwc, θεωρείται ότι NWC_prior = NWC_current
        (δηλαδή μηδενικό ταμειακό impact από μεταβολή κεφαλαίου κίνησης στο baseline).
        """
        d = state.drivers
        wc = state.working_capital
        cap = state.capital_structure

        # 1. INCOME STATEMENT CASCADE (Canonical Field Names)
        revenue = float(d.volume * d.price)
        cogs = float(d.volume * d.variable_cost_per_unit)
        gross_profit = revenue - cogs

        fixed_opex = float(d.fixed_opex)
        ebitda = gross_profit - fixed_opex

        depreciation = float(d.depreciation)
        ebit = ebitda - depreciation

        interest_expense = float(
            cap.annual_cash_interest_paid
        )
        ebt = ebit - interest_expense

        # Φόρος μόνο επί θετικών κερδών (Tax Shield floor στο 0.0)
        # Το tax_rate ανήκει στο CapitalStructure
        tax = max(0.0, ebt * cap.tax_rate)
        net_profit = ebt - tax

        is_statement = IncomeStatement(
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
            net_profit=net_profit
        )

        # 2. WORKING CAPITAL METRICS (Canonical Days Names -> Monetary Amounts)
        # AR = (ar_days / 365) * Revenue
        # Inventory = (inventory_days / 365) * COGS
        # AP = (ap_days / 365) * COGS
        ar = (wc.ar_days / cls.DAYS_IN_YEAR) * revenue
        inventory = (wc.inventory_days / cls.DAYS_IN_YEAR) * cogs
        ap = (wc.ap_days / cls.DAYS_IN_YEAR) * cogs

        current_nwc = (ar + inventory) - ap

        # Cash Impact = Prior NWC - Current NWC
        # (Αν το NWC αυξηθεί, δεσμεύεται ρευστότητα -> Αρνητικό Cash Impact)
        baseline_prior = current_nwc if prior_nwc is None else prior_nwc
        wc_cash_impact = baseline_prior - current_nwc

        wc_metrics = WorkingCapitalMetrics(
            ar=ar,
            inventory=inventory,
            ap=ap,
            nwc=current_nwc,
            wc_cash_impact=wc_cash_impact
        )

        # 3. FCFE CALCULATION (Simplified Financing Assumptions v1)
        # FCFE = Net Profit + D&A - Principal Payments + ΔNWC_impact
        principal = float(cap.principal_payments)
        fcfe = net_profit + depreciation - principal + wc_cash_impact

        return FinancialStatements(
            income_statement=is_statement,
            working_capital=wc_metrics,
            principal_payments=principal,
            fcfe=fcfe
        )

    @classmethod
    def calculate_variance_impact(
        cls,
        baseline_state: CompanyState,
        projected_state: CompanyState
    ) -> VarianceImpact:
        """
        Financial Variance & Reconciliation Layer:

        Αναλύει τη διαφορά μεταξύ Baseline και Projected State:
        - Price Effect = Volume_base * ΔPrice
        - Volume Effect = ΔVolume * Price_projected
        - GP, EBITDA, Net Profit & FCFE Bridges
        """
        base_fin = cls.calculate_statements(baseline_state)
        # Χρησιμοποιούμε το NWC του baseline ως prior για το projected
        # ώστε να καταγράψουμε την πραγματική ταμειακή επίπτωση της μεταβολής NWC
        proj_fin = cls.calculate_statements(projected_state, prior_nwc=base_fin.working_capital.nwc)

        base_d = baseline_state.drivers
        proj_d = projected_state.drivers

        # Revenue Breakdown: Price vs Volume Effect
        delta_p = proj_d.price - base_d.price
        delta_v = proj_d.volume - base_d.volume

        price_effect = base_d.volume * delta_p
        volume_effect = delta_v * proj_d.price
        revenue_delta = proj_fin.income_statement.revenue - base_fin.income_statement.revenue

        return VarianceImpact(
            revenue_delta=revenue_delta,
            price_effect=price_effect,
            volume_effect=volume_effect,
            gross_profit_delta=proj_fin.income_statement.gross_profit - base_fin.income_statement.gross_profit,
            ebitda_delta=proj_fin.income_statement.ebitda - base_fin.income_statement.ebitda,
            net_profit_delta=proj_fin.income_statement.net_profit - base_fin.income_statement.net_profit,
            nwc_cash_impact_delta=proj_fin.working_capital.wc_cash_impact,
            fcfe_delta=proj_fin.fcfe - base_fin.fcfe
        )

   
    @classmethod
    def build_projection(
        cls,
        baseline_state: CompanyState,
        projected_state: CompanyState,
    ) -> FinancialProjection:

        baseline_fin = cls.calculate_statements(
            baseline_state
        )

        projected_fin = cls.calculate_statements(
            projected_state,
            prior_nwc=baseline_fin.working_capital.nwc,
        )

        impact = cls.calculate_variance_impact(
            baseline_state,
            projected_state,
        )

        return FinancialProjection(
            baseline=baseline_fin,
            projected=projected_fin,
            impact=impact,
        )
