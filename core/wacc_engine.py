from math import isfinite
from typing import Dict, Any

from core.models import CompanyState


class WACCEngine:
    """
    WACC Calculation Engine.

    Responsibilities:
    - Calculate Cost of Equity using CAPM.
    - Calculate After-Tax Cost of Debt.
    - Calculate capital structure weights.
    - Calculate WACC.
    - Calculate ROIC spread versus WACC.
    - Return structured calculation results.

    Does NOT:
    - Modify CompanyState.
    - Create scenarios.
    - Persist WACC.
    - Perform Streamlit/UI operations.
    """

    # =========================================================
    # VALIDATION
    # =========================================================

    @staticmethod
    def _validate_finite(
        value: float,
        field_name: str
    ) -> float:

        value = float(value)

        if not isfinite(value):
            raise ValueError(
                f"{field_name} must be a finite number. "
                f"Received: {value}"
            )

        return value

    @staticmethod
    def _validate_non_negative(
        value: float,
        field_name: str
    ) -> float:

        value = WACCEngine._validate_finite(
            value,
            field_name
        )

        if value < 0.0:
            raise ValueError(
                f"{field_name} cannot be negative. "
                f"Received: {value}"
            )

        return value

    @staticmethod
    def _validate_rate(
        value: float,
        field_name: str
    ) -> float:

        value = WACCEngine._validate_finite(
            value,
            field_name
        )

        if value < 0.0:
            raise ValueError(
                f"{field_name} cannot be negative. "
                f"Received: {value}"
            )

        if value > 1.0:
            raise ValueError(
                f"{field_name} must be expressed as a decimal "
                f"between 0 and 1. Received: {value}"
            )

        return value

    # =========================================================
    # CAPM
    # =========================================================

    @classmethod
    def calculate_cost_of_equity(
        cls,
        risk_free_rate: float,
        beta: float,
        market_risk_premium: float
    ) -> float:

        risk_free_rate = cls._validate_rate(
            risk_free_rate,
            "Risk-free rate"
        )

        beta = cls._validate_finite(
            beta,
            "Beta"
        )

        market_risk_premium = cls._validate_rate(
            market_risk_premium,
            "Market risk premium"
        )

        if beta < 0.0:
            raise ValueError(
                f"Beta cannot be negative. Received: {beta}"
            )

        return (
            risk_free_rate
            + beta * market_risk_premium
        )

    # =========================================================
    # COST OF DEBT
    # =========================================================

    @classmethod
    def calculate_after_tax_cost_of_debt(
        cls,
        interest_rate: float,
        tax_rate: float
    ) -> float:

        interest_rate = cls._validate_rate(
            interest_rate,
            "Interest rate"
        )

        tax_rate = cls._validate_rate(
            tax_rate,
            "Tax rate"
        )

        return interest_rate * (1.0 - tax_rate)

    # =========================================================
    # CAPITAL STRUCTURE
    # =========================================================

    @classmethod
    def calculate_capital_weights(
        cls,
        market_equity: float,
        total_debt: float
    ) -> Dict[str, float]:

        market_equity = cls._validate_non_negative(
            market_equity,
            "Market equity"
        )

        total_debt = cls._validate_non_negative(
            total_debt,
            "Total debt"
        )

        total_capital = (
            market_equity
            + total_debt
        )

        if total_capital <= 0.0:
            raise ValueError(
                "Total capital must be greater than zero."
            )

        equity_weight = (
            market_equity
            / total_capital
        )

        debt_weight = (
            total_debt
            / total_capital
        )

        return {
            "equity_weight": equity_weight,
            "debt_weight": debt_weight,
            "total_capital": total_capital
        }

    # =========================================================
    # WACC
    # =========================================================

    @classmethod
    def calculate_wacc(
        cls,
        market_equity: float,
        total_debt: float,
        risk_free_rate: float,
        beta: float,
        market_risk_premium: float,
        interest_rate: float,
        tax_rate: float
    ) -> Dict[str, Any]:

        capital_weights = cls.calculate_capital_weights(
            market_equity=market_equity,
            total_debt=total_debt
        )

        cost_of_equity = cls.calculate_cost_of_equity(
            risk_free_rate=risk_free_rate,
            beta=beta,
            market_risk_premium=market_risk_premium
        )

        after_tax_cost_of_debt = (
            cls.calculate_after_tax_cost_of_debt(
                interest_rate=interest_rate,
                tax_rate=tax_rate
            )
        )

        equity_weight = capital_weights["equity_weight"]
        debt_weight = capital_weights["debt_weight"]

        wacc = (
            equity_weight * cost_of_equity
            + debt_weight * after_tax_cost_of_debt
        )

        return {
            "cost_of_equity": cost_of_equity,
            "pre_tax_cost_of_debt": interest_rate,
            "after_tax_cost_of_debt": after_tax_cost_of_debt,
            "equity_weight": equity_weight,
            "debt_weight": debt_weight,
            "total_capital": capital_weights["total_capital"],
            "wacc": wacc,
            "cost_of_equity_pct": cost_of_equity * 100.0,
            "pre_tax_cost_of_debt_pct": interest_rate * 100.0,
            "after_tax_cost_of_debt_pct": (
                after_tax_cost_of_debt * 100.0
            ),
            "equity_weight_pct": equity_weight * 100.0,
            "debt_weight_pct": debt_weight * 100.0,
            "wacc_pct": wacc * 100.0
        }

    # =========================================================
    # COMPANY STATE INTEGRATION
    # =========================================================

    @classmethod
    def calculate_from_baseline(
        cls,
        baseline: CompanyState,
        market_equity: float,
        risk_free_rate: float,
        beta: float,
        market_risk_premium: float,
        interest_rate: float
    ) -> Dict[str, Any]:

        if not isinstance(baseline, CompanyState):
            raise TypeError(
                "WACCEngine expects a CompanyState baseline."
            )

        total_debt = float(
            baseline.capital_structure.total_debt
        )

        tax_rate = float(
            baseline.capital_structure.tax_rate
        )

        result = cls.calculate_wacc(
            market_equity=market_equity,
            total_debt=total_debt,
            risk_free_rate=risk_free_rate,
            beta=beta,
            market_risk_premium=market_risk_premium,
            interest_rate=interest_rate,
            tax_rate=tax_rate
        )

        result["baseline_version"] = baseline.version
        result["baseline_wacc"] = (
            baseline.capital_structure.wacc
        )

        return result

    # =========================================================
    # ROIC SPREAD
    # =========================================================

    @classmethod
    def calculate_roic_spread(
        cls,
        roic: float,
        wacc: float
    ) -> Dict[str, Any]:

        roic = cls._validate_rate(
            roic,
            "ROIC"
        )

        wacc = cls._validate_rate(
            wacc,
            "WACC"
        )

        spread = roic - wacc

        if spread > 0.02:
            verdict = "value_creation"
        elif spread > 0.0:
            verdict = "marginal_value_creation"
        else:
            verdict = "value_destruction"

        return {
            "roic": roic,
            "wacc": wacc,
            "spread": spread,
            "roic_pct": roic * 100.0,
            "wacc_pct": wacc * 100.0,
            "spread_pct": spread * 100.0,
            "verdict": verdict
        }
