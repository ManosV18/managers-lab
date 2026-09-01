"""
diagnostics/concentration.py

Concentration Risk Diagnostic.

Analyzes concentration within a dataset using:
    - Herfindahl-Hirschman Index (HHI)
    - Gini coefficient
    - Pareto concentration
    - Top-item concentration
    - Customer / buyer dependency
    - Qualitative buyer risk

Architecture:
    Diagnostics explain the company.

This module is:
    - read-only
    - deterministic
    - independent of Streamlit
    - independent of DecisionPlan
    - independent of DecisionEvaluator
    - independent of FinancialEngine

Expected dataset columns:
    Name
    Value
"""

from dataclasses import dataclass
from typing import Any

import numpy as np
import pandas as pd


# =========================================================
# CONSTANTS
# =========================================================

CONCENTRATION_THRESHOLD = 0.25

HHI_LOW_THRESHOLD = 1500
HHI_MODERATE_THRESHOLD = 2500

PARETO_TARGET_PCT = 80.0


# =========================================================
# RESULT MODELS
# =========================================================

@dataclass(frozen=True)
class ConcentrationMetrics:
    """
    Quantitative concentration metrics.

    HHI:
        Sum of squared market/value shares expressed
        on the 0-10,000 scale.

    Gini:
        Distribution inequality measure between 0 and 1.

    Pareto:
        Percentage and number of items required to
        account for at least 80% of total value.
    """

    hhi: float
    gini: float

    pareto_items_pct: float
    pareto_count: int

    total_items: int
    total_value: float

    status: str
    risk_level: str

    top_item_pct: float
    top_item_name: str


@dataclass(frozen=True)
class CustomerDependencyResult:
    """
    Assessment of whether the largest customer creates
    material concentration exposure.
    """

    material_concentration: bool
    top_customer_pct: float
    threshold: float


@dataclass(frozen=True)
class BuyerRiskResult:
    """
    Qualitative buyer / investor concentration risk.

    The score reflects the absence of:
        - contractual lock-in
        - team ownership
        - high switching costs
    """

    risk_level: str
    score: int
    status: str


@dataclass(frozen=True)
class ConcentrationDiagnosticResult:
    """
    Complete concentration diagnostic.

    This is the business-facing result returned by the
    diagnostic layer.
    """

    metrics: ConcentrationMetrics
    customer_dependency: CustomerDependencyResult
    buyer_risk: BuyerRiskResult


# =========================================================
# VALIDATION
# =========================================================

def _validate_dataframe(
    df: pd.DataFrame,
) -> None:
    """
    Validate the input dataset.
    """

    if not isinstance(df, pd.DataFrame):
        raise TypeError(
            "Concentration diagnostic expects "
            "a pandas DataFrame."
        )

    required_columns = {
        "Name",
        "Value",
    }

    missing_columns = (
        required_columns
        - set(df.columns)
    )

    if missing_columns:
        raise ValueError(
            "Concentration diagnostic requires "
            f"columns: {sorted(required_columns)}. "
            f"Missing: {sorted(missing_columns)}."
        )


# =========================================================
# CONCENTRATION METRICS
# =========================================================

def calculate_concentration_metrics(
    df_clean: pd.DataFrame,
) -> tuple[ConcentrationMetrics, pd.DataFrame]:
    """
    Calculate quantitative concentration metrics.

    Parameters
    ----------
    df_clean:
        DataFrame containing:
            Name
            Value

    Returns
    -------
    tuple
        (
            ConcentrationMetrics,
            sorted DataFrame with Share_Pct,
            Cum_Sum and Cum_Pct
        )

    Notes
    -----
    HHI is calculated on the 0-10,000 scale.

    Example:
        A single item representing 100% of value
        produces HHI = 10,000.

        Ten equally sized items produce HHI = 1,000.
    """

    _validate_dataframe(
        df_clean
    )

    # -----------------------------------------------------
    # CLEAN INPUT
    # -----------------------------------------------------

    df = df_clean[
        ["Name", "Value"]
    ].copy()

    df["Value"] = pd.to_numeric(
        df["Value"],
        errors="coerce",
    )

    df = df.dropna(
        subset=["Value"]
    )

    df = df[
        df["Value"] > 0
    ]

    # -----------------------------------------------------
    # EMPTY DATA
    # -----------------------------------------------------

    if (
        df.empty
        or df["Value"].sum() <= 0
    ):

        metrics = ConcentrationMetrics(
            hhi=0.0,
            gini=0.0,
            pareto_items_pct=0.0,
            pareto_count=0,
            total_items=0,
            total_value=0.0,
            status="No Data",
            risk_level="none",
            top_item_pct=0.0,
            top_item_name="-",
        )

        empty_df = pd.DataFrame(
            columns=[
                "Name",
                "Value",
                "Share_Pct",
                "Cum_Sum",
                "Cum_Pct",
            ]
        )

        return metrics, empty_df

    # -----------------------------------------------------
    # SORT
    # -----------------------------------------------------

    df = (
        df
        .sort_values(
            by="Value",
            ascending=False,
        )
        .reset_index(drop=True)
    )

    total_value = float(
        df["Value"].sum()
    )

    total_items = int(
        len(df)
    )

    # -----------------------------------------------------
    # VALUE SHARE
    # -----------------------------------------------------

    df["Share_Pct"] = (
        df["Value"]
        / total_value
    ) * 100.0

    # -----------------------------------------------------
    # HHI
    # -----------------------------------------------------

    hhi = float(
        np.sum(
            df["Share_Pct"] ** 2
        )
    )

    # -----------------------------------------------------
    # PARETO
    # -----------------------------------------------------

    df["Cum_Sum"] = (
        df["Value"]
        .cumsum()
    )

    df["Cum_Pct"] = (
        df["Cum_Sum"]
        / total_value
    ) * 100.0

    items_to_80 = df[
        df["Cum_Pct"]
        >= PARETO_TARGET_PCT
    ].index.min()

    if pd.notna(items_to_80):

        pareto_count = int(
            items_to_80 + 1
        )

    else:

        pareto_count = total_items

    pareto_items_pct = (
        pareto_count
        / total_items
    ) * 100.0

    # -----------------------------------------------------
    # GINI
    # -----------------------------------------------------

    values = df[
        "Value"
    ].to_numpy(
        dtype=float
    )

    n = len(values)

    if (
        n > 1
        and np.mean(values) > 0
    ):

        diff_matrix = np.abs(
            values[:, None]
            - values
        )

        gini = float(
            np.sum(diff_matrix)
            / (
                2
                * (n ** 2)
                * np.mean(values)
            )
        )

    else:

        gini = 0.0

    # -----------------------------------------------------
    # RISK CLASSIFICATION
    # -----------------------------------------------------

    if hhi < HHI_LOW_THRESHOLD:

        status = (
            "Low Risk "
            "(Well Diversified)"
        )

        risk_level = "low"

    elif hhi <= HHI_MODERATE_THRESHOLD:

        status = (
            "Moderate Risk "
            "(Moderate Concentration)"
        )

        risk_level = "moderate"

    else:

        status = (
            "High Risk "
            "(Highly Concentrated)"
        )

        risk_level = "high"

    # -----------------------------------------------------
    # TOP ITEM
    # -----------------------------------------------------

    top_item_pct = float(
        df.loc[0, "Share_Pct"]
        / 100.0
    )

    top_item_name = str(
        df.loc[0, "Name"]
    )

    # -----------------------------------------------------
    # RESULT
    # -----------------------------------------------------

    metrics = ConcentrationMetrics(
        hhi=hhi,
        gini=gini,
        pareto_items_pct=float(
            pareto_items_pct
        ),
        pareto_count=pareto_count,
        total_items=total_items,
        total_value=total_value,
        status=status,
        risk_level=risk_level,
        top_item_pct=top_item_pct,
        top_item_name=top_item_name,
    )

    return metrics, df


# =========================================================
# RAW TEXT PROCESSING
# =========================================================

def process_raw_text(
    text_input: str,
) -> pd.DataFrame:
    """
    Convert a pasted list of values into a clean
    Name / Value DataFrame.

    Accepted examples:

        120000
        €85000
        $45000
        125,000

    Invalid or non-positive values are ignored.
    """

    if not isinstance(
        text_input,
        str,
    ):
        raise TypeError(
            "text_input must be a string."
        )

    if not text_input.strip():

        return pd.DataFrame(
            columns=[
                "Name",
                "Value",
            ]
        )

    lines = (
        text_input
        .strip()
        .splitlines()
    )

    data = []

    for i, line in enumerate(lines):

        val_str = (
            line
            .replace("$", "")
            .replace("€", "")
            .replace(",", "")
            .strip()
        )

        try:

            value = float(
                val_str
            )

        except (
            TypeError,
            ValueError,
        ):

            continue

        if value > 0:

            data.append(
                {
                    "Name": (
                        f"Item {i + 1}"
                    ),
                    "Value": value,
                }
            )

    return pd.DataFrame(
        data,
        columns=[
            "Name",
            "Value",
        ],
    )


# =========================================================
# CUSTOMER DEPENDENCY
# =========================================================

def calculate_customer_dependency(metrics: dict):
    """
    Diagnose whether the largest customer creates
    material concentration exposure.
    """

    top_pct = float(
        metrics.get("top_item_pct", 0.0)
    )

    return {
        "material_concentration": (
            top_pct > CONCENTRATION_THRESHOLD
        ),
        "top_customer_pct": top_pct,
        "threshold": CONCENTRATION_THRESHOLD,
    }

# =========================================================
# BUYER / INVESTOR RISK
# =========================================================

def calculate_buyer_risk(
    top_pct: float,
    contractual_lock_in: bool,
    team_owned: bool,
    high_switching_cost: bool,
) -> BuyerRiskResult:
    """
    Evaluate qualitative buyer / investor concentration risk.

    Parameters
    ----------
    top_pct:
        Share of value/revenue represented by the
        largest customer or relationship.

    contractual_lock_in:
        Whether the relationship is contractually protected.

    team_owned:
        Whether the relationship is owned by the organization
        rather than one individual.

    high_switching_cost:
        Whether switching away from the relationship is costly.

    Logic
    -----
    If concentration is <= 25%, risk is considered low.

    Above 25%, each missing protection adds one risk point:

        no contractual lock-in  -> +1
        not team-owned          -> +1
        low switching cost      -> +1
    """

    try:

        top_pct = float(
            top_pct
        )

    except (
        TypeError,
        ValueError,
    ):

        raise TypeError(
            "top_pct must be numeric."
        )

    if not (
        0.0
        <= top_pct
        <= 1.0
    ):
        raise ValueError(
            "top_pct must be expressed "
            "as a decimal between 0 and 1."
        )

    if top_pct <= CONCENTRATION_THRESHOLD:

        return BuyerRiskResult(
            risk_level="low",
            score=0,
            status=(
                "Healthy Diversification"
            ),
        )

    high_risk_score = 0

    if not contractual_lock_in:

        high_risk_score += 1

    if not team_owned:

        high_risk_score += 1

    if not high_switching_cost:

        high_risk_score += 1

    if high_risk_score == 0:

        risk_level = "low"

        status = (
            "Defensible Concentration"
        )

    elif high_risk_score == 1:

        risk_level = "moderate"

        status = (
            "Manageable Diligence Risk"
        )

    else:

        risk_level = "high"

        status = (
            "High Valuation Risk"
        )

    return BuyerRiskResult(
        risk_level=risk_level,
        score=high_risk_score,
        status=status,
    )


# =========================================================
# COMPLETE DIAGNOSTIC
# =========================================================

def diagnose_concentration(
    df_clean: pd.DataFrame,
    *,
    contractual_lock_in: bool = False,
    team_owned: bool = False,
    high_switching_cost: bool = False,
) -> ConcentrationDiagnosticResult:
    """
    Run the complete concentration diagnostic.

    This is the preferred public entry point for UI
    and other application services.

    Parameters
    ----------
    df_clean:
        Dataset containing Name and Value.

    contractual_lock_in:
        Qualitative protection against concentration risk.

    team_owned:
        Whether the customer/relationship is institutionally
        owned rather than dependent on one individual.

    high_switching_cost:
        Whether the relationship has meaningful switching costs.

    Returns
    -------
    ConcentrationDiagnosticResult
    """

    metrics, _ = (
        calculate_concentration_metrics(
            df_clean
        )
    )

    customer_dependency = (
        calculate_customer_dependency(
            metrics
        )
    )

    buyer_risk = (
        calculate_buyer_risk(
            top_pct=metrics.top_item_pct,
            contractual_lock_in=(
                contractual_lock_in
            ),
            team_owned=team_owned,
            high_switching_cost=(
                high_switching_cost
            ),
        )
    )

    return ConcentrationDiagnosticResult(
        metrics=metrics,
        customer_dependency=(
            customer_dependency
        ),
        buyer_risk=buyer_risk,
    )
