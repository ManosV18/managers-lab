from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Optional

import pandas as pd


# =========================================================
# RESULT CONTRACT
# =========================================================

@dataclass(frozen=True)
class WorkingCapitalAnalysisResult:
    """
    Analytical result derived from transaction-level data.

    This is NOT a CompanyState and does NOT modify the baseline.

    The result can be used by the UI to present measured operating
    working-capital metrics before the manager decides whether
    to use them in the Baseline Snapshot.
    """

    ar_days: Optional[float]
    inventory_days: Optional[float]
    ap_days: Optional[float]

    cash_conversion_cycle: Optional[float]

    top_customer_pct: Optional[float]
    customer_hhi: Optional[float]

    top_supplier_pct: Optional[float]
    supplier_hhi: Optional[float]


# =========================================================
# HELPERS
# =========================================================

def _safe_float(
    value: Any,
    default: Optional[float] = None,
) -> Optional[float]:

    try:
        if value is None:
            return default

        result = float(value)

        if pd.isna(result):
            return default

        return result

    except (TypeError, ValueError):
        return default


def _weighted_days_from_transactions(
    df: pd.DataFrame,
    *,
    start_date_col: str,
    end_date_col: str,
    weight_col: str,
    reference_date: Any,
) -> float:

    if df.empty:
        return 0.0

    data = df.copy()

    data[start_date_col] = pd.to_datetime(
        data[start_date_col],
        errors="coerce",
    )

    data[end_date_col] = pd.to_datetime(
        data[end_date_col],
        errors="coerce",
    )

    data[weight_col] = pd.to_numeric(
        data[weight_col],
        errors="coerce",
    )

    data = data.dropna(
        subset=[
            start_date_col,
            weight_col,
        ]
    )

    if data.empty:
        return 0.0

    reference = pd.Timestamp(reference_date)

    # Open transactions are measured up to the analysis date.
    data[end_date_col] = data[end_date_col].fillna(reference)

    data = data[
        data[end_date_col] >= data[start_date_col]
    ]

    if data.empty:
        return 0.0

    durations = (
        data[end_date_col]
        - data[start_date_col]
    ).dt.days

    weights = data[weight_col].abs()

    total_weight = weights.sum()

    if total_weight <= 0:
        return 0.0

    return float(
        (durations * weights).sum()
        / total_weight
    )


# =========================================================
# CONCENTRATION
# =========================================================

def _concentration_metrics(
    df: pd.DataFrame,
    *,
    entity_col: str,
    amount_col: str,
) -> tuple[Optional[float], Optional[float]]:

    if df.empty:
        return None, None

    data = df.copy()

    data[amount_col] = pd.to_numeric(
        data[amount_col],
        errors="coerce",
    )

    data = data.dropna(
        subset=[
            entity_col,
            amount_col,
        ]
    )

    if data.empty:
        return None, None

    mix = (
        data.groupby(entity_col)[amount_col]
        .sum()
        .abs()
    )

    total = mix.sum()

    if total <= 0:
        return None, None

    shares = mix / total

    top_entity_pct = float(
        shares.max() * 100.0
    )

    hhi = float(
        (shares ** 2).sum() * 10000.0
    )

    return top_entity_pct, hhi


# =========================================================
# MAIN ANALYSIS
# =========================================================

def analyze_working_capital(
    *,
    ar_df: Optional[pd.DataFrame] = None,
    ap_df: Optional[pd.DataFrame] = None,
    inventory_df: Optional[pd.DataFrame] = None,
    reference_date: Any,
) -> WorkingCapitalAnalysisResult:
    """
    Calculate measured working-capital operating metrics
    from transaction-level data.

    This function is pure analytical logic.

    It does NOT:
        - create a CompanyState
        - modify a CompanyState
        - modify the BaselineRepository
        - modify Streamlit session state
        - create Decisions
    """

    ar_days: Optional[float] = None
    ap_days: Optional[float] = None
    inventory_days: Optional[float] = None

    top_customer_pct: Optional[float] = None
    customer_hhi: Optional[float] = None

    top_supplier_pct: Optional[float] = None
    supplier_hhi: Optional[float] = None

    # -----------------------------------------------------
    # AR
    # -----------------------------------------------------

    if ar_df is not None:

        ar_days = _weighted_days_from_transactions(
            ar_df,
            start_date_col="invoice_date",
            end_date_col="payment_date",
            weight_col="amount",
            reference_date=reference_date,
        )

        (
            top_customer_pct,
            customer_hhi,
        ) = _concentration_metrics(
            ar_df,
            entity_col="customer_id",
            amount_col="amount",
        )

    # -----------------------------------------------------
    # AP
    # -----------------------------------------------------

    if ap_df is not None:

        ap_days = _weighted_days_from_transactions(
            ap_df,
            start_date_col="invoice_date",
            end_date_col="payment_date",
            weight_col="amount",
            reference_date=reference_date,
        )

        (
            top_supplier_pct,
            supplier_hhi,
        ) = _concentration_metrics(
            ap_df,
            entity_col="supplier_id",
            amount_col="amount",
        )

    # -----------------------------------------------------
    # INVENTORY
    # -----------------------------------------------------

    if inventory_df is not None:

        inventory_days = _weighted_days_from_transactions(
            inventory_df,
            start_date_col="receipt_date",
            end_date_col="sale_date",
            weight_col="quantity",
            reference_date=reference_date,
        )

    # -----------------------------------------------------
    # CASH CONVERSION CYCLE
    # -----------------------------------------------------

    ccc = None

    if (
        ar_days is not None
        and inventory_days is not None
        and ap_days is not None
    ):

        ccc = (
            ar_days
            + inventory_days
            - ap_days
        )

    return WorkingCapitalAnalysisResult(
        ar_days=_safe_float(ar_days),
        inventory_days=_safe_float(
            inventory_days
        ),
        ap_days=_safe_float(ap_days),
        cash_conversion_cycle=_safe_float(ccc),
        top_customer_pct=_safe_float(
            top_customer_pct
        ),
        customer_hhi=_safe_float(
            customer_hhi
        ),
        top_supplier_pct=_safe_float(
            top_supplier_pct
        ),
        supplier_hhi=_safe_float(
            supplier_hhi
        ),
    )
