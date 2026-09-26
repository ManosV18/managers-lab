from __future__ import annotations

from typing import Any, Dict, Iterable, List, Mapping, Optional, Sequence

import pandas as pd
import streamlit as st

from core.decision_plan import DecisionPlan


# =========================================================
# CONSTANTS
# =========================================================

MONTHS = [f"Month {i}" for i in range(1, 7)]

WC_AR_CANDIDATE = "wc_ar_candidate"
WC_AP_CANDIDATE = "wc_ap_candidate"

# Stable Cash Management session-state keys.
CASH_MONTHLY_OPEX_KEY = "cash_management_monthly_opex"
CASH_MONTHLY_DEBT_KEY = "cash_management_monthly_debt"
CASH_MINIMUM_CASH_KEY = "cash_management_minimum_cash"

# Simple owner-manager assumptions for EXISTING balances.
# These are deliberately editable in the UI.
DEFAULT_EXISTING_AR_PROFILE = {
    0: 0.40,  # This month
    1: 0.40,  # Next month
    2: 0.20,  # Month 3 onward
}

DEFAULT_EXISTING_AP_PROFILE = {
    0: 0.40,  # This month
    1: 0.40,  # Next month
    2: 0.20,  # Month 3 onward
}


# =========================================================
# GENERIC HELPERS
# =========================================================

def _get_attr(
    obj: Any,
    names: Sequence[str],
    default: Any = None,
) -> Any:

    if obj is None:
        return default

    if isinstance(obj, Mapping):
        for name in names:
            if name in obj:
                return obj[name]

    for name in names:
        try:
            value = getattr(obj, name)
        except Exception:
            continue

        if value is not None:
            return value

    return default


def _to_float(
    value: Any,
    default: float = 0.0,
) -> float:

    try:
        if value is None:
            return default

        if isinstance(value, str):
            value = (
                value
                .replace(",", "")
                .replace("€", "")
                .strip()
            )

        return float(value)

    except (TypeError, ValueError, OverflowError):
        return default


def _money(value: Any) -> str:
    return f"€{_to_float(value):,.0f}"


def _normalise_pct(value: Any) -> float:

    value = _to_float(value)

    if abs(value) > 1:
        value /= 100.0

    return value


# =========================================================
# STATE HELPERS
# =========================================================

def _get_baseline_state() -> Any:

    return (
        st.session_state.get("baseline_state")
        or st.session_state.get("locked_baseline")
        or st.session_state.get("baseline")
    )


def _get_current_plan() -> Any:

    plan = st.session_state.get("decision_plan")

    if isinstance(plan, DecisionPlan):
        return plan

    plan = DecisionPlan.create(
        plan_id="main_plan",
        name="Current Decision Plan",
    )

    st.session_state.decision_plan = plan

    return plan


def _all_decisions(plan: Any) -> List[Any]:

    if plan is None:
        return []

    decisions = getattr(plan, "decisions", None)

    if decisions is None:
        return []

    if isinstance(decisions, Mapping):
        return list(decisions.values())

    try:
        return list(decisions)
    except Exception:
        return []


def _decision_change(decision: Any) -> Any:

    return _get_attr(
        decision,
        (
            "change",
            "decision",
            "decision_change",
            "change_spec",
        ),
        None,
    )


# =========================================================
# DECISION LOOKUP
# =========================================================

def _find_decision(
    decisions: Iterable[Any],
    candidate_key: str,
) -> Any:

    for decision in decisions:

        values = [
            _get_attr(
                decision,
                (
                    "candidate_key",
                    "key",
                    "decision_key",
                    "id",
                    "name",
                ),
                None,
            ),
            _get_attr(
                _decision_change(decision),
                (
                    "candidate_key",
                    "key",
                    "decision_key",
                    "id",
                    "name",
                ),
                None,
            ),
        ]

        for value in values:

            if str(value) == candidate_key:
                return decision

        changes = _get_attr(
            decision,
            ("changes",),
            None,
        )

        if isinstance(changes, Mapping):

            if candidate_key == WC_AP_CANDIDATE:

                if any(
                    key in changes
                    for key in (
                        "ap_days",
                        "target_ap_days",
                        "new_ap_days",
                    )
                ):
                    return decision

            if candidate_key == WC_AR_CANDIDATE:

                if any(
                    key in changes
                    for key in (
                        "ar_days",
                        "target_ar_days",
                        "new_ar_days",
                        "collection_schedule",
                        "collection_profile",
                    )
                ):
                    return decision

    return None


def _selected_ar_decision() -> Any:

    plan = _get_current_plan()

    decision = _find_decision(
        _all_decisions(plan),
        WC_AR_CANDIDATE,
    )

    if decision is not None:
        return decision

    return st.session_state.get(
        WC_AR_CANDIDATE
    )


def _selected_ap_decision() -> Any:

    plan = _get_current_plan()

    decision = _find_decision(
        _all_decisions(plan),
        WC_AP_CANDIDATE,
    )

    if decision is not None:
        return decision

    return st.session_state.get(
        WC_AP_CANDIDATE
    )


# =========================================================
# COMPANY ECONOMICS
# =========================================================

def _get_drivers(state: Any) -> Any:

    return _get_attr(
        state,
        ("drivers",),
        state,
    )


def _get_working_capital(state: Any) -> Any:

    return _get_attr(
        state,
        (
            "working_capital",
            "working_capital_policy",
        ),
        None,
    )


def _get_capital_structure(state: Any) -> Any:

    return _get_attr(
        state,
        ("capital_structure",),
        None,
    )


def _annual_revenue(state: Any) -> float:

    drivers = _get_drivers(state)

    volume = _get_attr(
        drivers,
        (
            "volume",
            "annual_volume",
        ),
        None,
    )

    price = _get_attr(
        drivers,
        (
            "price",
            "unit_price",
        ),
        None,
    )

    if volume is not None and price is not None:

        return (
            _to_float(volume)
            * _to_float(price)
        )

    return _to_float(
        _get_attr(
            drivers,
            (
                "revenue",
                "annual_revenue",
            ),
            0.0,
        )
    )


def _annual_cogs(state: Any) -> float:

    drivers = _get_drivers(state)

    volume = _get_attr(
        drivers,
        (
            "volume",
            "annual_volume",
        ),
        None,
    )

    variable_cost = _get_attr(
        drivers,
        (
            "variable_cost_per_unit",
            "variable_cost",
            "unit_variable_cost",
        ),
        None,
    )

    if volume is not None and variable_cost is not None:

        return (
            _to_float(volume)
            * _to_float(variable_cost)
        )

    return _to_float(
        _get_attr(
            drivers,
            (
                "cogs",
                "annual_cogs",
                "cost_of_goods_sold",
            ),
            0.0,
        )
    )


def _annual_fixed_opex(state: Any) -> float:

    drivers = _get_drivers(state)

    return _to_float(
        _get_attr(
            drivers,
            (
                "fixed_opex",
                "fixed_cost",
                "annual_fixed_opex",
                "opex",
            ),
            0.0,
        )
    )


def _opening_cash(state: Any) -> float:

    drivers = _get_drivers(state)

    return _to_float(
        _get_attr(
            drivers,
            (
                "opening_cash",
                "cash",
                "initial_cash",
            ),
            0.0,
        )
    )


def _annual_debt_service(state: Any) -> float:

    capital = _get_capital_structure(state)

    return _to_float(
        _get_attr(
            capital,
            (
                "annual_debt_service",
                "debt_service",
                "annual_loan_payment",
            ),
            0.0,
        )
    )


def _baseline_ar_days(state: Any) -> float:

    wc = _get_working_capital(state)

    return _to_float(
        _get_attr(
            wc,
            (
                "ar_days",
                "receivable_days",
                "accounts_receivable_days",
            ),
            0.0,
        )
    )


def _baseline_ap_days(state: Any) -> float:

    wc = _get_working_capital(state)

    return _to_float(
        _get_attr(
            wc,
            (
                "ap_days",
                "payable_days",
                "accounts_payable_days",
            ),
            0.0,
        )
    )


# =========================================================
# OPENING BALANCES
# =========================================================

def _opening_ar(state: Any) -> float:

    return (
        _annual_revenue(state)
        * _baseline_ar_days(state)
        / 365.0
    )


def _opening_ap(state: Any) -> float:

    return (
        _annual_cogs(state)
        * _baseline_ap_days(state)
        / 365.0
    )


# =========================================================
# DECISION VALUES
# =========================================================

def _decision_value(
    decision: Any,
    names: Sequence[str],
    default: Any = None,
) -> Any:

    if decision is None:
        return default

    value = _get_attr(
        decision,
        names,
        None,
    )

    if value is not None:
        return value

    changes = _get_attr(
        decision,
        ("changes",),
        None,
    )

    if isinstance(changes, Mapping):

        value = _get_attr(
            changes,
            names,
            None,
        )

        if value is not None:
            return value

    change = _decision_change(decision)

    value = _get_attr(
        change,
        names,
        None,
    )

    if value is not None:
        return value

    containers = (
        _get_attr(decision, ("payload",), None),
        _get_attr(decision, ("parameters",), None),
        _get_attr(decision, ("params",), None),
        _get_attr(decision, ("metadata",), None),
        _get_attr(change, ("payload",), None),
        _get_attr(change, ("parameters",), None),
        _get_attr(change, ("params",), None),
        _get_attr(change, ("metadata",), None),
    )

    for container in containers:

        if not isinstance(container, Mapping):
            continue

        value = _get_attr(
            container,
            names,
            None,
        )

        if value is not None:
            return value

    return default


def _decision_ar_days(
    baseline_state: Any,
    decision: Any,
) -> float:

    baseline = _baseline_ar_days(
        baseline_state
    )

    value = _decision_value(
        decision,
        (
            "ar_days",
            "target_ar_days",
            "new_ar_days",
            "receivable_days",
        ),
        None,
    )

    if value is None:
        return baseline

    return _to_float(
        value,
        baseline,
    )


def _decision_ap_days(
    baseline_state: Any,
    decision: Any,
) -> float:

    baseline = _baseline_ap_days(
        baseline_state
    )

    value = _decision_value(
        decision,
        (
            "ap_days",
            "target_ap_days",
            "new_ap_days",
            "payable_days",
        ),
        None,
    )

    if value is None:
        return baseline

    return _to_float(
        value,
        baseline,
    )


# =========================================================
# COLLECTION PROFILE
# =========================================================

def _extract_collection_profile(
    source: Any,
) -> Optional[Dict[int, float]]:

    if source is None:
        return None

    candidates: List[Any] = [source]

    changes = _get_attr(
        source,
        ("changes",),
        None,
    )

    if changes is not None:
        candidates.append(changes)

    change = _decision_change(source)

    if change is not None:
        candidates.append(change)

    original_candidates = list(candidates)

    for obj in original_candidates:

        for container_name in (
            "payload",
            "parameters",
            "params",
            "metadata",
        ):

            container = _get_attr(
                obj,
                (container_name,),
                None,
            )

            if container is not None:
                candidates.append(container)

    # -----------------------------------------------------
    # FIRST: explicit collection schedule
    # -----------------------------------------------------

    for obj in candidates:

        if not isinstance(obj, Mapping):
            continue

        for name in (
            "collection_schedule",
            "collection_profile",
        ):

            nested = obj.get(name)

            if not isinstance(nested, Mapping):
                continue

            profile: Dict[int, float] = {}

            for key, value in nested.items():

                key_text = str(key)

                if not key_text.startswith(
                    "month_"
                ):
                    continue

                if not key_text.endswith(
                    "_pct"
                ):
                    continue

                try:
                    month_index = int(
                        key_text[
                            len("month_"):-len("_pct")
                        ]
                    )
                except ValueError:
                    continue

                profile[month_index] = (
                    _normalise_pct(value)
                )

            if profile:

                profile = {
                    index: value
                    for index, value
                    in profile.items()
                    if value >= 0
                }

                total = sum(
                    profile.values()
                )

                if total > 0:

                    return {
                        index: value / total
                        for index, value
                        in profile.items()
                    }

    # -----------------------------------------------------
    # SECOND: direct month_x_pct fields
    # -----------------------------------------------------

    profile: Dict[int, float] = {}

    for month_index in range(0, 6):

        key = f"month_{month_index}_pct"

        found = None

        for obj in candidates:

            if isinstance(obj, Mapping):

                if key in obj:
                    found = obj[key]
                    break

            value = _get_attr(
                obj,
                (key,),
                None,
            )

            if value is not None:
                found = value
                break

        if found is not None:

            profile[month_index] = (
                _normalise_pct(found)
            )

    if not profile:
        return None

    profile = {
        index: value
        for index, value
        in profile.items()
        if value >= 0
    }

    total = sum(
        profile.values()
    )

    if total <= 0:
        return None

    return {
        index: value / total
        for index, value
        in profile.items()
    }


def _get_collection_profile(
    decision: Any,
) -> Optional[Dict[int, float]]:

    profile = _extract_collection_profile(
        decision
    )

    if profile:
        return profile

    candidate = st.session_state.get(
        WC_AR_CANDIDATE
    )

    profile = _extract_collection_profile(
        candidate
    )

    if profile:
        return profile

    metadata = st.session_state.get(
        "wc_ar_candidate_meta"
    )

    profile = _extract_collection_profile(
        metadata
    )

    if profile:
        return profile

    return None


# =========================================================
# EXISTING BALANCE TIMING
# =========================================================

def _normalise_existing_profile(
    profile: Mapping[int, float],
) -> Dict[int, float]:

    values = {
        0: max(
            0.0,
            _normalise_pct(
                profile.get(0, 0.0)
            ),
        ),
        1: max(
            0.0,
            _normalise_pct(
                profile.get(1, 0.0)
            ),
        ),
        2: max(
            0.0,
            _normalise_pct(
                profile.get(2, 0.0)
            ),
        ),
    }

    total = sum(
        values.values()
    )

    if total <= 0:
        return dict(
            DEFAULT_EXISTING_AR_PROFILE
        )

    return {
        key: value / total
        for key, value in values.items()
    }


def _existing_profile_from_session(
    session_key: str,
    default_profile: Mapping[int, float],
) -> Dict[int, float]:

    stored = st.session_state.get(
        session_key
    )

    if isinstance(stored, Mapping):

        return _normalise_existing_profile(
            stored
        )

    return _normalise_existing_profile(
        default_profile
    )


def _render_existing_timing_inputs(
    title: str,
    session_key: str,
    default_profile: Mapping[int, float],
) -> Dict[int, float]:

    st.markdown(
        f"#### {title}"
    )

    st.caption(
        "Simple assumption for the existing balance. "
        "This is not invoice-level ageing."
    )

    profile = _existing_profile_from_session(
        session_key=session_key,
        default_profile=default_profile,
    )

    col1, col2, col3 = st.columns(3)

    with col1:

        month_1 = st.number_input(
            "This month %",
            min_value=0.0,
            max_value=100.0,
            value=float(
                profile[0] * 100.0
            ),
            step=5.0,
            format="%.0f",
            key=f"{session_key}_month_1",
        )

    with col2:

        month_2 = st.number_input(
            "Next month %",
            min_value=0.0,
            max_value=100.0,
            value=float(
                profile[1] * 100.0
            ),
            step=5.0,
            format="%.0f",
            key=f"{session_key}_month_2",
        )

    with col3:

        month_3 = st.number_input(
            "Month 3 onward %",
            min_value=0.0,
            max_value=100.0,
            value=float(
                profile[2] * 100.0
            ),
            step=5.0,
            format="%.0f",
            key=f"{session_key}_month_3",
        )

    raw_profile = {
        0: month_1 / 100.0,
        1: month_2 / 100.0,
        2: month_3 / 100.0,
    }

    total_pct = sum(
        raw_profile.values()
    )

    if abs(total_pct - 1.0) > 0.0001:

        st.warning(
            f"These assumptions currently total "
            f"{total_pct:.0%}. They must total 100%."
        )

    else:

        st.success(
            "Timing assumption totals 100%."
        )

    # Keep the exact user-entered values in session state.
    st.session_state[session_key] = raw_profile

    return raw_profile


def _existing_profile_is_valid(
    profile: Mapping[int, float],
) -> bool:

    total = sum(
        max(
            0.0,
            _to_float(
                profile.get(
                    key,
                    0.0,
                )
            ),
        )
        for key in (0, 1, 2)
    )

    return abs(total - 1.0) <= 0.0001


# =========================================================
# MONTHLY TIMING
# =========================================================

def _monthly_delay_allocation(
    days: float,
) -> Dict[int, float]:

    days = max(
        0.0,
        _to_float(days),
    )

    months = days / 30.0

    lower = int(months)

    fraction = months - lower

    if fraction <= 0:

        return {
            lower: 1.0
        }

    return {
        lower: 1.0 - fraction,
        lower + 1: fraction,
    }


# =========================================================
# NEW SALES COLLECTIONS
# =========================================================

def _build_new_sales_receipts(
    monthly_sales: Sequence[float],
    collection_profile: Mapping[int, float],
) -> List[float]:

    """
    Each month's sales form an independent cohort.

    The selected Receivables Decision collection profile
    is applied exactly once to each cohort.
    """

    horizon = len(
        monthly_sales
    )

    receipts = [
        0.0
        for _ in range(horizon)
    ]

    for cohort_month, sales in enumerate(
        monthly_sales
    ):

        sales = _to_float(
            sales
        )

        for delay, percentage in (
            collection_profile.items()
        ):

            target_month = (
                cohort_month
                + int(delay)
            )

            if not (
                0 <= target_month < horizon
            ):
                continue

            receipts[target_month] += (
                sales
                * _to_float(percentage)
            )

    return receipts


# =========================================================
# EXISTING AR
# =========================================================

def _build_existing_ar_receipts(
    opening_ar: float,
    existing_ar_profile: Mapping[int, float],
    horizon: int,
) -> List[float]:

    receipts = [
        0.0
        for _ in range(horizon)
    ]

    if not _existing_profile_is_valid(
        existing_ar_profile
    ):

        return receipts

    for delay, percentage in (
        existing_ar_profile.items()
    ):

        target_month = int(
            delay
        )

        if 0 <= target_month < horizon:

            receipts[target_month] += (
                opening_ar
                * _to_float(percentage)
            )

    return receipts


# =========================================================
# RECEIPTS
# =========================================================

def _build_receipts(
    baseline_state: Any,
    ar_decision: Any,
    monthly_sales: Sequence[float],
    existing_ar_profile: Mapping[int, float],
) -> List[float]:

    horizon = len(
        monthly_sales
    )

    receipts = [
        0.0
        for _ in range(horizon)
    ]

    opening_ar = _opening_ar(
        baseline_state
    )

    existing_ar_receipts = (
        _build_existing_ar_receipts(
            opening_ar=opening_ar,
            existing_ar_profile=existing_ar_profile,
            horizon=horizon,
        )
    )

    collection_profile = (
        _get_collection_profile(
            ar_decision
        )
    )

    if collection_profile:

        new_sales_receipts = (
            _build_new_sales_receipts(
                monthly_sales=monthly_sales,
                collection_profile=collection_profile,
            )
        )

    else:

        ar_days = _decision_ar_days(
            baseline_state,
            ar_decision,
        )

        allocation = (
            _monthly_delay_allocation(
                ar_days
            )
        )

        new_sales_receipts = [
            0.0
            for _ in range(horizon)
        ]

        for cohort_month, sales in enumerate(
            monthly_sales
        ):

            for delay, percentage in (
                allocation.items()
            ):

                target_month = (
                    cohort_month
                    + int(delay)
                )

                if not (
                    0 <= target_month < horizon
                ):
                    continue

                new_sales_receipts[
                    target_month
                ] += (
                    sales
                    * percentage
                )

    for month_index in range(
        horizon
    ):

        receipts[month_index] = (
            existing_ar_receipts[
                month_index
            ]
            + new_sales_receipts[
                month_index
            ]
        )

    return receipts


# =========================================================
# EXISTING AP
# =========================================================

def _build_existing_ap_payments(
    opening_ap: float,
    existing_ap_profile: Mapping[int, float],
    horizon: int,
) -> List[float]:

    payments = [
        0.0
        for _ in range(horizon)
    ]

    if not _existing_profile_is_valid(
        existing_ap_profile
    ):

        return payments

    for delay, percentage in (
        existing_ap_profile.items()
    ):

        target_month = int(
            delay
        )

        if 0 <= target_month < horizon:

            payments[target_month] += (
                opening_ap
                * _to_float(percentage)
            )

    return payments


# =========================================================
# NEW PURCHASE PAYMENTS
# =========================================================

def _build_new_purchase_payments(
    monthly_purchases: Sequence[float],
    ap_days: float,
) -> List[float]:

    payments = [
        0.0
        for _ in monthly_purchases
    ]

    allocation = (
        _monthly_delay_allocation(
            ap_days
        )
    )

    for cohort_month, purchases in enumerate(
        monthly_purchases
    ):

        for delay, percentage in (
            allocation.items()
        ):

            target_month = (
                cohort_month
                + int(delay)
            )

            if not (
                0 <= target_month < len(
                    payments
                )
            ):
                continue

            payments[target_month] += (
                purchases
                * _to_float(percentage)
            )

    return payments


# =========================================================
# SUPPLIER PAYMENTS
# =========================================================

def _build_supplier_payments(
    baseline_state: Any,
    ap_decision: Any,
    monthly_purchases: Sequence[float],
    existing_ap_profile: Mapping[int, float],
) -> List[float]:

    opening_ap = _opening_ap(
        baseline_state
    )

    existing_ap_payments = (
        _build_existing_ap_payments(
            opening_ap=opening_ap,
            existing_ap_profile=existing_ap_profile,
            horizon=len(monthly_purchases),
        )
    )

    ap_days = _decision_ap_days(
        baseline_state,
        ap_decision,
    )

    new_purchase_payments = (
        _build_new_purchase_payments(
            monthly_purchases=monthly_purchases,
            ap_days=ap_days,
        )
    )

    payments = [
        existing_ap_payments[i]
        + new_purchase_payments[i]
        for i in range(
            len(monthly_purchases)
        )
    ]

    return payments


# =========================================================
# CASH PLAN
# =========================================================

def _build_cash_plan(
    baseline_state: Any,
    ar_decision: Any,
    ap_decision: Any,
    monthly_opex: float,
    monthly_debt: float,
    existing_ar_profile: Mapping[int, float],
    existing_ap_profile: Mapping[int, float],
) -> Dict[str, List[float]]:

    annual_revenue = _annual_revenue(
        baseline_state
    )

    annual_cogs = _annual_cogs(
        baseline_state
    )

    monthly_sales = [
        annual_revenue / 12.0
        for _ in MONTHS
    ]

    # Until a formal purchasing decision exists,
    # monthly purchases are proxied by COGS / 12.
    monthly_purchases = [
        annual_cogs / 12.0
        for _ in MONTHS
    ]

    receipts = _build_receipts(
        baseline_state=baseline_state,
        ar_decision=ar_decision,
        monthly_sales=monthly_sales,
        existing_ar_profile=existing_ar_profile,
    )

    supplier_payments = (
        _build_supplier_payments(
            baseline_state=baseline_state,
            ap_decision=ap_decision,
            monthly_purchases=monthly_purchases,
            existing_ap_profile=existing_ap_profile,
        )
    )

    operating_expenses = [
        monthly_opex
        for _ in MONTHS
    ]

    debt_payments = [
        monthly_debt
        for _ in MONTHS
    ]

    net_cash_flow: List[float] = []
    ending_cash: List[float] = []

    cash = _opening_cash(
        baseline_state
    )

    for month_index in range(
        len(MONTHS)
    ):

        net = (
            receipts[month_index]
            - supplier_payments[month_index]
            - operating_expenses[month_index]
            - debt_payments[month_index]
        )

        cash += net

        net_cash_flow.append(
            net
        )

        ending_cash.append(
            cash
        )

    return {
        "receipts": receipts,
        "supplier_payments": supplier_payments,
        "operating_expenses": operating_expenses,
        "debt_payments": debt_payments,
        "net_cash_flow": net_cash_flow,
        "ending_cash": ending_cash,
        "monthly_sales": monthly_sales,
        "monthly_purchases": monthly_purchases,
    }


# =========================================================
# CASH MANAGEMENT ASSUMPTIONS
# =========================================================

def _get_cash_management_assumptions(
    baseline_state: Any,
) -> Dict[str, float]:

    default_monthly_opex = (
        _annual_fixed_opex(
            baseline_state
        )
        / 12.0
    )

    default_monthly_debt = (
        _annual_debt_service(
            baseline_state
        )
        / 12.0
    )

    monthly_opex = _to_float(
        st.session_state.get(
            CASH_MONTHLY_OPEX_KEY,
            default_monthly_opex,
        ),
        default_monthly_opex,
    )

    monthly_debt = _to_float(
        st.session_state.get(
            CASH_MONTHLY_DEBT_KEY,
            default_monthly_debt,
        ),
        default_monthly_debt,
    )

    minimum_cash = _to_float(
        st.session_state.get(
            CASH_MINIMUM_CASH_KEY,
            0.0,
        ),
        0.0,
    )

    return {
        "monthly_opex": monthly_opex,
        "monthly_debt": monthly_debt,
        "minimum_cash": minimum_cash,
    }


# =========================================================
# CASH MANAGEMENT RESULT
# =========================================================

def _interpret_cash_plan(
    cash_plan: Mapping[str, Sequence[float]],
    minimum_cash: float,
) -> Dict[str, Any]:
    """
    Interpret an already-built Cash Management plan.

    This is the single place where the six-month cash
    position is translated into executive metrics.
    """

    ending_cash = [
        _to_float(value)
        for value in cash_plan.get(
            "ending_cash",
            [],
        )
    ]

    minimum_cash = _to_float(
        minimum_cash
    )

    if not ending_cash:

        return {
            "lowest_projected_cash": 0.0,
            "lowest_cash_month": None,
            "minimum_cash_reserve": minimum_cash,
            "funding_required": 0.0,
            "cash_above_reserve": True,
            "ending_cash": [],
        }

    lowest_cash = min(
        ending_cash
    )

    lowest_month_index = ending_cash.index(
        lowest_cash
    )

    funding_required = max(
        0.0,
        minimum_cash - lowest_cash,
    )

    return {
        "lowest_projected_cash": lowest_cash,
        "lowest_cash_month": lowest_month_index + 1,
        "minimum_cash_reserve": minimum_cash,
        "funding_required": funding_required,
        "cash_above_reserve": funding_required <= 0.0,
        "ending_cash": ending_cash,
    }


def _store_cash_management_result(
    cash_plan: Mapping[str, Sequence[float]],
    minimum_cash: float,
) -> Dict[str, Any]:
    """
    Store the already-calculated Cash Management result
    for use by other V2 presentation layers.

    This function does NOT recalculate cash flows.
    It only interprets the existing cash_plan output.
    """

    result = _interpret_cash_plan(
        cash_plan=cash_plan,
        minimum_cash=minimum_cash,
    )

    st.session_state[
        "cash_management_result"
    ] = result

    return result


def build_cash_management_summary(
    baseline_state: Any = None,
    ar_decision: Any = None,
    ap_decision: Any = None,
) -> Optional[Dict[str, Any]]:
    """
    Public presentation-layer interface for Cash Management.

    The Cash Management module remains the owner of the
    monthly cash calculation. Dashboard only consumes the
    summary returned here.

    If the Cash Management page has not yet been visited,
    stored assumptions fall back to the baseline defaults.
    """

    if baseline_state is None:
        baseline_state = _get_baseline_state()

    if baseline_state is None:
        return None

    if ar_decision is None:
        ar_decision = _selected_ar_decision()

    if ap_decision is None:
        ap_decision = _selected_ap_decision()

    assumptions = _get_cash_management_assumptions(
        baseline_state
    )

    existing_ar_profile = (
        _existing_profile_from_session(
            session_key="cash_existing_ar_profile",
            default_profile=DEFAULT_EXISTING_AR_PROFILE,
        )
    )

    existing_ap_profile = (
        _existing_profile_from_session(
            session_key="cash_existing_ap_profile",
            default_profile=DEFAULT_EXISTING_AP_PROFILE,
        )
    )

    if not _existing_profile_is_valid(
        existing_ar_profile
    ):
        return {
            "valid": False,
            "reason": (
                "Existing receivables timing assumptions "
                "must total 100%."
            ),
        }

    if not _existing_profile_is_valid(
        existing_ap_profile
    ):
        return {
            "valid": False,
            "reason": (
                "Existing payables timing assumptions "
                "must total 100%."
            ),
        }

    cash_plan = _build_cash_plan(
        baseline_state=baseline_state,
        ar_decision=ar_decision,
        ap_decision=ap_decision,
        monthly_opex=assumptions["monthly_opex"],
        monthly_debt=assumptions["monthly_debt"],
        existing_ar_profile=existing_ar_profile,
        existing_ap_profile=existing_ap_profile,
    )

    result = _interpret_cash_plan(
        cash_plan=cash_plan,
        minimum_cash=assumptions["minimum_cash"],
    )

    result.update(
        {
            "valid": True,
            "monthly_opex": assumptions["monthly_opex"],
            "monthly_debt": assumptions["monthly_debt"],
            "cash_plan": cash_plan,
        }
    )

    # Keep the same result available to the rest of V2.
    st.session_state[
        "cash_management_result"
    ] = result

    return result


# =========================================================
# UI
# =========================================================

def render_cash_management_lab(
    baseline_state: Any = None,
) -> None:

    if baseline_state is None:

        baseline_state = (
            _get_baseline_state()
        )

    if baseline_state is None:

        st.warning(
            "Baseline company state is not available."
        )

        return

    # =====================================================
    # CURRENT DECISIONS
    # =====================================================

    ar_decision = (
        _selected_ar_decision()
    )

    ap_decision = (
        _selected_ap_decision()
    )

    # =====================================================
    # HEADER
    # =====================================================

    st.subheader(
        "Cash Management"
    )

    st.caption(
        "This is the timing layer that turns your "
        "Receivables, Supplier and operating decisions "
        "into a monthly cash view."
    )

    # =====================================================
    # CASH ASSUMPTIONS
    # =====================================================

    st.markdown(
        "### Cash assumptions"
    )

    col1, col2 = st.columns(2)

    default_monthly_opex = (
        _annual_fixed_opex(
            baseline_state
        )
        / 12.0
    )

    default_monthly_debt = (
        _annual_debt_service(
            baseline_state
        )
        / 12.0
    )

    with col1:

        monthly_opex = st.number_input(
            "Average monthly operating expenses",
            min_value=0.0,
            value=float(
                st.session_state.get(
                    CASH_MONTHLY_OPEX_KEY,
                    default_monthly_opex,
                )
            ),
            step=1000.0,
            format="%.0f",
            key=CASH_MONTHLY_OPEX_KEY,
            help=(
                "Average monthly operating expenses "
                "excluding supplier payments and loan payments."
            ),
        )

    with col2:

        monthly_debt = st.number_input(
            "Monthly loan installments & interest",
            min_value=0.0,
            value=float(
                st.session_state.get(
                    CASH_MONTHLY_DEBT_KEY,
                    default_monthly_debt,
                )
            ),
            step=1000.0,
            format="%.0f",
            key=CASH_MONTHLY_DEBT_KEY,
        )

    minimum_cash = st.number_input(
        "Minimum cash reserve to maintain",
        min_value=0.0,
        value=float(
            st.session_state.get(
                CASH_MINIMUM_CASH_KEY,
                0.0,
            )
        ),
        step=5000.0,
        format="%.0f",
        key=CASH_MINIMUM_CASH_KEY,
        help=(
            "Cash level you want to keep available at all times."
        ),
    )

    # =====================================================
    # CURRENT POLICIES
    # =====================================================

    current_ar_days = (
        _decision_ar_days(
            baseline_state,
            ar_decision,
        )
    )

    current_ap_days = (
        _decision_ap_days(
            baseline_state,
            ap_decision,
        )
    )

    collection_profile = (
        _get_collection_profile(
            ar_decision
        )
    )

    # =====================================================
    # EXISTING BALANCES
    # =====================================================

    st.markdown(
        "### Existing balances"
    )

    st.caption(
        "We use a simple timing assumption for balances "
        "already outstanding. You do not need to enter "
        "invoice-by-invoice ageing."
    )

    existing_ar_profile = (
        _render_existing_timing_inputs(
            title="Existing Receivables",
            session_key="cash_existing_ar_profile",
            default_profile=DEFAULT_EXISTING_AR_PROFILE,
        )
    )

    existing_ap_profile = (
        _render_existing_timing_inputs(
            title="Existing Payables",
            session_key="cash_existing_ap_profile",
            default_profile=DEFAULT_EXISTING_AP_PROFILE,
        )
    )

    existing_profiles_valid = (
        _existing_profile_is_valid(
            existing_ar_profile
        )
        and _existing_profile_is_valid(
            existing_ap_profile
        )
    )

    # =====================================================
    # FUTURE TRANSACTIONS
    # =====================================================

    st.markdown(
        "### Future transactions"
    )

    # -----------------------------------------------------
    # RECEIVABLES
    # -----------------------------------------------------

    if collection_profile:

        profile_text = " / ".join(
            f"Month {int(delay) + 1}: "
            f"{percentage:.0%}"
            for delay, percentage
            in sorted(
                collection_profile.items()
            )
        )

        st.success(
            "New sales collection timing from "
            f"Receivables Decision: {profile_text}"
        )

    else:

        st.caption(
            "New sales collection timing: "
            f"approximately "
            f"{current_ar_days:.0f} days"
        )

    # -----------------------------------------------------
    # SUPPLIERS
    # -----------------------------------------------------

    st.caption(
        "New purchase payment timing from Supplier "
        f"Decision: approximately "
        f"{current_ap_days:.0f} days"
    )

    # =====================================================
    # BUILD CASH PLAN
    # =====================================================

    if not existing_profiles_valid:

        st.warning(
            "Please make sure both existing receivables "
            "and existing payables timing assumptions "
            "total 100%."
        )

        return

    cash_plan = _build_cash_plan(
        baseline_state=baseline_state,
        ar_decision=ar_decision,
        ap_decision=ap_decision,
        monthly_opex=monthly_opex,
        monthly_debt=monthly_debt,
        existing_ar_profile=existing_ar_profile,
        existing_ap_profile=existing_ap_profile,
    )

    # =====================================================
    # CASH OUTLOOK
    # =====================================================

    st.markdown(
        "### Six-month cash outlook"
    )

    table = pd.DataFrame(
        {
            "": [
                "Opening cash",
                "Receipts",
                "Supplier payments",
                "Operating expenses",
                "Loan payments & interest",
                "Net cash flow",
                "Ending cash balance",
            ],
            **{
                month: [
                    (
                        cash_plan[
                            "ending_cash"
                        ][i - 1]
                        if i > 0
                        else _opening_cash(
                            baseline_state
                        )
                    ),
                    cash_plan[
                        "receipts"
                    ][i],
                    cash_plan[
                        "supplier_payments"
                    ][i],
                    cash_plan[
                        "operating_expenses"
                    ][i],
                    cash_plan[
                        "debt_payments"
                    ][i],
                    cash_plan[
                        "net_cash_flow"
                    ][i],
                    cash_plan[
                        "ending_cash"
                    ][i],
                ]
                for i, month
                in enumerate(MONTHS)
            },
        }
    )

    st.dataframe(
        table.style.format(
            {
                month: "€{:,.0f}"
                for month in MONTHS
            }
        ),
        use_container_width=True,
        hide_index=True,
    )

    # =====================================================
    # CASH POSITION
    # =====================================================

    cash_management_result = (
        _store_cash_management_result(
            cash_plan=cash_plan,
            minimum_cash=minimum_cash,
        )
    )

    lowest_cash = (
        cash_management_result[
            "lowest_projected_cash"
        ]
    )

    lowest_month_index = (
        cash_management_result[
            "lowest_cash_month"
        ] - 1
    )

    funding_required = (
        cash_management_result[
            "funding_required"
        ]
    )

    col1, col2, col3 = st.columns(3)

    with col1:

        st.metric(
            "Lowest projected cash",
            _money(lowest_cash),
            f"Month {lowest_month_index + 1}",
        )

    with col2:

        st.metric(
            "Minimum cash reserve",
            _money(
                cash_management_result[
                    "minimum_cash_reserve"
                ]
            ),
        )

    with col3:

        st.metric(
            "Funding required",
            _money(funding_required),
        )

    # =====================================================
    # INTERPRETATION
    # =====================================================

    if funding_required > 0:

        st.warning(
            "The projected cash balance falls below the "
            "minimum reserve during the six-month period. "
            f"The estimated funding requirement is "
            f"{_money(funding_required)}."
        )

    else:

        st.success(
            "The projected cash balance remains above "
            "the minimum reserve throughout the six-month period."
        )


# =========================================================
# COMPATIBILITY ALIAS
# =========================================================

show_cash_management_lab = (
    render_cash_management_lab
)
