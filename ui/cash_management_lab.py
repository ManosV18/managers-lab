from dataclasses import dataclass
from typing import Any, Dict, Iterable, List, Mapping, Optional, Sequence, Tuple

import pandas as pd
import streamlit as st


MONTHS = [
    "Month 1",
    "Month 2",
    "Month 3",
    "Month 4",
    "Month 5",
    "Month 6",
]

AR_CANDIDATE_KEYS = (
    "wc_ar_candidate",
    "receivables_candidate",
)

AP_CANDIDATE_KEYS = (
    "wc_ap_candidate",
    "payables_candidate",
)

INVENTORY_CANDIDATE_KEYS = (
    "wc_inv_candidate",
    "wc_inventory_candidate",
    "inventory_candidate",
)


@dataclass(frozen=True)
class CashEvent:
    month: str
    label: str
    amount: float
    kind: str


@dataclass(frozen=True)
class CashPlanResult:
    dataframe: pd.DataFrame
    events: Tuple[CashEvent, ...]


# ---------------------------------------------------------------------
# Generic helpers
# ---------------------------------------------------------------------

def _as_float(value: Any, default: float = 0.0) -> float:
    try:
        if value is None:
            return default
        return float(value)
    except (TypeError, ValueError):
        return default


def _decision_changes(decision: Any) -> Mapping[str, Any]:
    changes = getattr(decision, "changes", None)

    if isinstance(changes, Mapping):
        return changes

    return {}


def _decision_metadata(decision: Any) -> Mapping[str, Any]:
    for attr in ("metadata", "meta", "details", "assumptions"):
        value = getattr(decision, attr, None)

        if isinstance(value, Mapping):
            return value

    return {}


def _all_decisions() -> Sequence[Any]:
    plan = st.session_state.get("decision_plan")

    if plan is None:
        return ()

    decisions = getattr(plan, "decisions", None)

    if decisions is None:
        return ()

    try:
        return tuple(decisions)
    except TypeError:
        return ()


def _find_plan_decision_by_change(
    change_key: str,
) -> Optional[Any]:

    decisions = _all_decisions()

    for decision in reversed(tuple(decisions)):
        changes = _decision_changes(decision)

        if change_key in changes:
            return decision

    return None


def _find_decision(
    keys: Iterable[str],
) -> Optional[Any]:

    key_set = set(keys)

    for decision in reversed(tuple(_all_decisions())):

        decision_id = str(
            getattr(
                decision,
                "decision_id",
                "",
            )
            or ""
        )

        category = str(
            getattr(
                decision,
                "category",
                "",
            )
            or ""
        )

        name = str(
            getattr(
                decision,
                "name",
                "",
            )
            or ""
        )

        values = {
            decision_id,
            category,
            name,
        }

        if values.intersection(key_set):
            return decision

        changes = _decision_changes(decision)

        if (
            "ar_days" in changes
            and key_set.intersection(
                AR_CANDIDATE_KEYS
            )
        ):
            return decision

        if (
            "ap_days" in changes
            and key_set.intersection(
                AP_CANDIDATE_KEYS
            )
        ):
            return decision

        if (
            any(
                key in changes
                for key in (
                    "inventory_days",
                    "inventory_event",
                    "inventory_change",
                )
            )
            and key_set.intersection(
                INVENTORY_CANDIDATE_KEYS
            )
        ):
            return decision

    # Session-state candidates are fallback only.
    # They must NOT override a selected Current Decision Plan decision.
    for key in keys:

        candidate = st.session_state.get(
            key
        )

        if candidate is not None:
            return candidate

    return None


# ---------------------------------------------------------------------
# Baseline / projected CompanyState
# ---------------------------------------------------------------------

def _get_baseline_state() -> Any:

    try:
        from core.baseline_repository import (
            BaselineRepository,
        )

        from core.state_builder import (
            StateBuilder,
        )

        repository = BaselineRepository()

        baseline = repository.get_baseline()

        builder = StateBuilder()

        return builder.build(
            baseline
        )

    except Exception:
        pass

    try:
        from core.state_builder import (
            StateBuilder,
        )

        builder = StateBuilder()

        return builder.build()

    except Exception:
        return None


def _get_projected_state(
    baseline_state: Any,
) -> Any:

    plan = st.session_state.get(
        "decision_plan"
    )

    if baseline_state is None:
        return None

    if plan is None:
        return baseline_state

    try:
        from core.decision_evaluator import (
            DecisionEvaluator,
        )

        evaluator = DecisionEvaluator()

        result = evaluator.evaluate(
            baseline_state,
            plan,
        )

        if hasattr(
            result,
            "projected_state",
        ):
            return result.projected_state

        return result

    except Exception:
        return baseline_state


# ---------------------------------------------------------------------
# CompanyState helpers
# ---------------------------------------------------------------------

def _working_capital_terms(
    state: Any,
) -> Tuple[float, float, float]:

    if state is None:
        return 0.0, 0.0, 0.0

    wc = getattr(
        state,
        "working_capital",
        None,
    )

    if wc is None:
        return 0.0, 0.0, 0.0

    return (
        _as_float(
            getattr(
                wc,
                "ar_days",
                0.0,
            )
        ),
        _as_float(
            getattr(
                wc,
                "inventory_days",
                0.0,
            )
        ),
        _as_float(
            getattr(
                wc,
                "ap_days",
                0.0,
            )
        ),
    )


def _annual_operating_values(
    state: Any,
) -> Tuple[float, float, float]:

    if state is None:
        return 0.0, 0.0, 0.0

    drivers = getattr(
        state,
        "drivers",
        None,
    )

    if drivers is None:
        return 0.0, 0.0, 0.0

    price = _as_float(
        getattr(
            drivers,
            "price",
            0.0,
        )
    )

    volume = _as_float(
        getattr(
            drivers,
            "volume",
            0.0,
        )
    )

    variable_cost = _as_float(
        getattr(
            drivers,
            "variable_cost_per_unit",
            0.0,
        )
    )

    fixed_opex = _as_float(
        getattr(
            drivers,
            "fixed_opex",
            0.0,
        )
    )

    revenue = price * volume

    cogs = variable_cost * volume

    return (
        revenue,
        cogs,
        fixed_opex,
    )


def _opening_cash(
    state: Any,
) -> float:

    if state is None:
        return 0.0

    drivers = getattr(
        state,
        "drivers",
        None,
    )

    if drivers is None:
        return 0.0

    return _as_float(
        getattr(
            drivers,
            "opening_cash",
            0.0,
        )
    )


def _annual_debt_service(
    state: Any,
) -> float:

    if state is None:
        return 0.0

    capital = getattr(
        state,
        "capital_structure",
        None,
    )

    if capital is None:
        return 0.0

    return _as_float(
        getattr(
            capital,
            "annual_debt_service",
            0.0,
        )
    )


# ---------------------------------------------------------------------
# Generic schedule helpers
# ---------------------------------------------------------------------

def _normalise_schedule(
    value: Any,
) -> Optional[List[float]]:

    if value is None:
        return None

    if isinstance(
        value,
        Mapping,
    ):

        result = []

        for month in MONTHS:

            result.append(
                _as_float(
                    value.get(
                        month,
                        value.get(
                            month.lower(),
                            0.0,
                        ),
                    )
                )
            )

        return result

    if isinstance(
        value,
        (
            list,
            tuple,
        ),
    ):

        result = [
            _as_float(x)
            for x in value
        ]

        if len(result) >= 6:
            return result[:6]

        return result + [
            0.0
        ] * (
            6 - len(result)
        )

    return None


def _extract_schedule_from_decision(
    decision: Any,
    schedule_keys: Sequence[str],
) -> Optional[List[float]]:

    if decision is None:
        return None

    changes = _decision_changes(
        decision
    )

    metadata = _decision_metadata(
        decision
    )

    containers = (
        changes,
        metadata,
    )

    for container in containers:

        for key in schedule_keys:

            if key not in container:
                continue

            schedule = _normalise_schedule(
                container[key]
            )

            if schedule is not None:
                return schedule

    return None


# ---------------------------------------------------------------------
# Legacy payment-days schedule
# ---------------------------------------------------------------------

def _schedule_from_payment_days(
    annual_amount: float,
    payment_days: float,
    opening_balance: float = 0.0,
) -> List[float]:
    """
    Legacy fallback used when no collection profile exists.

    This is intentionally NOT the preferred AR mechanism.

    New Receivables decisions should provide a collection_profile,
    allowing Cash Management to use the explicit management policy
    rather than infer timing from average AR days alone.
    """

    annual_amount = max(
        0.0,
        _as_float(
            annual_amount
        ),
    )

    payment_days = max(
        0.0,
        _as_float(
            payment_days
        ),
    )

    opening_balance = max(
        0.0,
        _as_float(
            opening_balance
        ),
    )

    monthly_amount = (
        annual_amount / 12.0
    )

    days_per_month = (
        365.0 / 12.0
    )

    lag_months = (
        payment_days
        / days_per_month
    )

    schedule = [
        0.0
        for _ in MONTHS
    ]

    if (
        opening_balance > 0.0
        and lag_months > 0.0
    ):

        full_months = int(
            lag_months
        )

        remaining = (
            opening_balance
        )

        for month_index in range(
            min(
                full_months,
                len(MONTHS),
            )
        ):

            if monthly_amount <= 0.0:
                break

            amount = min(
                monthly_amount,
                remaining,
            )

            schedule[
                month_index
            ] += amount

            remaining -= amount

            if remaining <= 0.01:
                break

        if (
            remaining > 0.01
            and full_months < len(MONTHS)
        ):
            schedule[
                full_months
            ] += remaining

    elif opening_balance > 0.0:

        schedule[0] += (
            opening_balance
        )

    if monthly_amount <= 0.0:
        return schedule

    if lag_months <= 0.0:

        for index in range(
            len(MONTHS)
        ):
            schedule[index] += (
                monthly_amount
            )

        return schedule

    lower_lag = int(
        lag_months
    )

    fraction = (
        lag_months
        - lower_lag
    )

    for source_index in range(
        len(MONTHS)
    ):

        lower_target = (
            source_index
            + lower_lag
        )

        upper_target = (
            lower_target
            + 1
        )

        if fraction <= 0.000001:

            if (
                lower_target
                < len(MONTHS)
            ):
                schedule[
                    lower_target
                ] += monthly_amount

            continue

        lower_amount = (
            monthly_amount
            * (1.0 - fraction)
        )

        upper_amount = (
            monthly_amount
            * fraction
        )

        if (
            lower_target
            < len(MONTHS)
        ):
            schedule[
                lower_target
            ] += lower_amount

        if (
            upper_target
            < len(MONTHS)
        ):
            schedule[
                upper_target
            ] += upper_amount

    return schedule


# ---------------------------------------------------------------------
# Collection profile
# ---------------------------------------------------------------------

def _normalise_collection_profile(
    value: Any,
) -> Optional[Dict[str, float]]:
    """
    Normalise the management-level two-policy collection profile.

    Expected structure:

        {
            "new_policy_pct": 0.40,
            "new_policy_days": 10,
            "old_policy_pct": 0.60,
            "old_policy_days": 90,
        }

    The profile is deliberately simple.

    It is NOT customer-level aging.
    It is NOT an invoice forecast.
    It is a management assumption describing how future sales
    are expected to convert into cash.
    """

    if not isinstance(
        value,
        Mapping,
    ):
        return None

    new_pct = _as_float(
        value.get(
            "new_policy_pct",
            value.get(
                "new_pct",
                value.get(
                    "adoption",
                    0.0,
                ),
            ),
        )
    )

    new_days = _as_float(
        value.get(
            "new_policy_days",
            value.get(
                "new_days",
                0.0,
            ),
        )
    )

    old_pct = _as_float(
        value.get(
            "old_policy_pct",
            value.get(
                "old_pct",
                1.0 - new_pct,
            ),
        )
    )

    old_days = _as_float(
        value.get(
            "old_policy_days",
            value.get(
                "old_days",
                0.0,
            ),
        )
    )

    # Accept percentages entered as 40 instead of 0.40.
    if new_pct > 1.0:
        new_pct /= 100.0

    if old_pct > 1.0:
        old_pct /= 100.0

    new_pct = max(
        0.0,
        min(
            1.0,
            new_pct,
        ),
    )

    old_pct = max(
        0.0,
        min(
            1.0,
            old_pct,
        ),
    )

    total_pct = (
        new_pct + old_pct
    )

    if total_pct <= 0.0:
        return None

    # Normalise only the weights.
    # This prevents rounding in the source decision from
    # distorting the collection schedule.
    new_pct /= total_pct
    old_pct /= total_pct

    new_days = max(
        0.0,
        new_days,
    )

    old_days = max(
        0.0,
        old_days,
    )

    return {
        "new_policy_pct": new_pct,
        "new_policy_days": new_days,
        "old_policy_pct": old_pct,
        "old_policy_days": old_days,
    }


def _extract_collection_profile(
    decision: Any,
) -> Optional[Dict[str, float]]:
    """
    Read collection_profile from the selected AR decision.

    It can live either in decision.changes or in decision.metadata.
    """

    if decision is None:
        return None

    changes = _decision_changes(
        decision
    )

    metadata = _decision_metadata(
        decision
    )

    for container in (
        changes,
        metadata,
    ):

        for key in (
            "collection_profile",
            "collection_policy",
        ):

            if key not in container:
                continue

            profile = _normalise_collection_profile(
                container[key]
            )

            if profile is not None:
                return profile

    return None


def _collection_schedule_from_profile(
    annual_revenue: float,
    collection_profile: Mapping[str, float],
) -> List[float]:
    """
    Build a six-month management-level collection schedule from
    the two-bucket collection policy.

    Example:

        40% of sales -> 10 days
        60% of sales -> 90 days

    The monthly sales cohort is split into the two policy groups,
    and each group is shifted according to its payment period.

    This is intentionally a planning estimate.

    It does not attempt to reconstruct invoice-level aging.
    """

    annual_revenue = max(
        0.0,
        _as_float(
            annual_revenue
        ),
    )

    monthly_revenue = (
        annual_revenue / 12.0
    )

    if monthly_revenue <= 0.0:
        return [
            0.0
            for _ in MONTHS
        ]

    new_pct = _as_float(
        collection_profile.get(
            "new_policy_pct",
            0.0,
        )
    )

    old_pct = _as_float(
        collection_profile.get(
            "old_policy_pct",
            0.0,
        )
    )

    new_days = _as_float(
        collection_profile.get(
            "new_policy_days",
            0.0,
        )
    )

    old_days = _as_float(
        collection_profile.get(
            "old_policy_days",
            0.0,
        )
    )

    schedule = [
        0.0
        for _ in MONTHS
    ]

    def add_cohort(
        source_index: int,
        cohort_amount: float,
        payment_days: float,
    ) -> None:

        if cohort_amount <= 0.0:
            return

        days_per_month = (
            365.0 / 12.0
        )

        lag_months = (
            max(
                0.0,
                payment_days,
            )
            / days_per_month
        )

        lower_lag = int(
            lag_months
        )

        fraction = (
            lag_months
            - lower_lag
        )

        lower_target = (
            source_index
            + lower_lag
        )

        upper_target = (
            lower_target
            + 1
        )

        # Immediate collection.
        if lag_months <= 0.0:

            if source_index < len(
                schedule
            ):
                schedule[
                    source_index
                ] += cohort_amount

            return

        # Whole-month timing.
        if fraction <= 0.000001:

            if lower_target < len(
                schedule
            ):
                schedule[
                    lower_target
                ] += cohort_amount

            return

        # Fractional timing between two months.
        lower_amount = (
            cohort_amount
            * (1.0 - fraction)
        )

        upper_amount = (
            cohort_amount
            * fraction
        )

        if lower_target < len(
            schedule
        ):
            schedule[
                lower_target
            ] += lower_amount

        if upper_target < len(
            schedule
        ):
            schedule[
                upper_target
            ] += upper_amount

    for source_index in range(
        len(MONTHS)
    ):

        monthly_new = (
            monthly_revenue
            * new_pct
        )

        monthly_old = (
            monthly_revenue
            * old_pct
        )

        add_cohort(
            source_index,
            monthly_new,
            new_days,
        )

        add_cohort(
            source_index,
            monthly_old,
            old_days,
        )

    return schedule


# ---------------------------------------------------------------------
# Selected Decision Plan decisions
# ---------------------------------------------------------------------

def _selected_ar_decision() -> Optional[Any]:
    """
    Only the AR decision actually present in the Current Decision Plan
    is authoritative for Cash Management.
    """

    return _find_plan_decision_by_change(
        "ar_days"
    )


def _selected_ap_decision() -> Optional[Any]:
    """
    Only the AP decision actually present in the Current Decision Plan
    is authoritative for Cash Management.
    """

    return _find_plan_decision_by_change(
        "ap_days"
    )


def _selected_inventory_decision() -> Optional[Any]:

    for key in (
        "inventory_days",
        "inventory_event",
        "inventory_change",
    ):

        decision = _find_plan_decision_by_change(
            key
        )

        if decision is not None:
            return decision

    return None


def _decision_ar_days(
    decision: Any,
) -> Optional[float]:

    if decision is None:
        return None

    changes = _decision_changes(
        decision
    )

    if "ar_days" not in changes:
        return None

    return _as_float(
        changes["ar_days"],
        default=0.0,
    )


def _decision_ap_days(
    decision: Any,
) -> Optional[float]:

    if decision is None:
        return None

    changes = _decision_changes(
        decision
    )

    if "ap_days" not in changes:
        return None

    return _as_float(
        changes["ap_days"],
        default=0.0,
    )


# ---------------------------------------------------------------------
# Main cash-plan builder
# ---------------------------------------------------------------------

def build_cash_plan(
    baseline_state: Any = None,
    projected_state: Any = None,
) -> CashPlanResult:

    if baseline_state is None:
        baseline_state = _get_baseline_state()

    if projected_state is None:
        projected_state = _get_projected_state(
            baseline_state
        )

    (
        baseline_ar_days,
        baseline_inventory_days,
        baseline_ap_days,
    ) = _working_capital_terms(
        baseline_state
    )

    (
        projected_ar_days,
        projected_inventory_days,
        projected_ap_days,
    ) = _working_capital_terms(
        projected_state
    )

    (
        annual_revenue,
        annual_cogs,
        annual_fixed_opex,
    ) = _annual_operating_values(
        projected_state
    )

    opening_cash = _opening_cash(
        baseline_state
    )

    annual_debt_service = _annual_debt_service(
        projected_state
    )

    # =============================================================
    # RECEIVABLES
    # =============================================================

    selected_ar_decision = (
        _selected_ar_decision()
    )

    explicit_ar_schedule = (
        _extract_schedule_from_decision(
            selected_ar_decision,
            (
                "collection_schedule",
                "ar_collection_schedule",
                "receivables_schedule",
                "cash_collection_schedule",
            ),
        )
    )

    collection_profile = (
        _extract_collection_profile(
            selected_ar_decision
        )
    )

    selected_ar_days = _decision_ar_days(
        selected_ar_decision
    )

    opening_ar_balance = (
        annual_revenue
        * baseline_ar_days
        / 365.0
    )

    if explicit_ar_schedule is not None:

        ar_schedule = (
            explicit_ar_schedule
        )

        ar_source = (
            "Current Decision Plan — "
            "explicit collection schedule"
        )

        ar_timing_method = (
            "Explicit collection schedule"
        )

    elif collection_profile is not None:

        ar_schedule = (
            _collection_schedule_from_profile(
                annual_revenue,
                collection_profile,
            )
        )

        new_pct = (
            collection_profile[
                "new_policy_pct"
            ]
            * 100.0
        )

        old_pct = (
            collection_profile[
                "old_policy_pct"
            ]
            * 100.0
        )

        new_days = (
            collection_profile[
                "new_policy_days"
            ]
        )

        old_days = (
            collection_profile[
                "old_policy_days"
            ]
        )

        ar_source = (
            "Current Decision Plan — "
            "selected collection policy "
            f"({new_pct:.0f}% at "
            f"{new_days:.0f} days / "
            f"{old_pct:.0f}% at "
            f"{old_days:.0f} days)"
        )

        ar_timing_method = (
            "Collection policy"
        )

    elif selected_ar_days is not None:

        # Compatibility fallback for decisions created before
        # collection_profile was introduced.
        ar_schedule = (
            _schedule_from_payment_days(
                annual_revenue,
                selected_ar_days,
                opening_balance=opening_ar_balance,
            )
        )

        ar_source = (
            "Current Decision Plan — "
            "selected AR decision "
            f"({selected_ar_days:.0f} days)"
        )

        ar_timing_method = (
            "Legacy AR-days fallback"
        )

    else:

        ar_schedule = (
            _schedule_from_payment_days(
                annual_revenue,
                projected_ar_days,
                opening_balance=opening_ar_balance,
            )
        )

        ar_source = (
            "Projected CompanyState fallback "
            f"({projected_ar_days:.0f} days)"
        )

        ar_timing_method = (
            "Projected AR-days fallback"
        )

    # =============================================================
    # PAYABLES
    # =============================================================

    selected_ap_decision = (
        _selected_ap_decision()
    )

    explicit_ap_schedule = (
        _extract_schedule_from_decision(
            selected_ap_decision,
            (
                "payment_schedule",
                "ap_payment_schedule",
                "payables_schedule",
                "cash_payment_schedule",
            ),
        )
    )

    selected_ap_days = _decision_ap_days(
        selected_ap_decision
    )

    opening_ap_balance = (
        annual_cogs
        * baseline_ap_days
        / 365.0
    )

    if explicit_ap_schedule is not None:

        ap_schedule = (
            explicit_ap_schedule
        )

        ap_source = (
            "Current Decision Plan — "
            "explicit payment schedule"
        )

    elif selected_ap_days is not None:

        ap_schedule = (
            _schedule_from_payment_days(
                annual_cogs,
                selected_ap_days,
                opening_balance=opening_ap_balance,
            )
        )

        ap_source = (
            "Current Decision Plan — "
            "selected AP decision "
            f"({selected_ap_days:.0f} days)"
        )

    else:

        ap_schedule = (
            _schedule_from_payment_days(
                annual_cogs,
                projected_ap_days,
                opening_balance=opening_ap_balance,
            )
        )

        ap_source = (
            "Projected CompanyState fallback "
            f"({projected_ap_days:.0f} days)"
        )

    # =============================================================
    # FIXED CASH OUTFLOWS
    # =============================================================

    monthly_fixed_opex = (
        annual_fixed_opex
        / 12.0
    )

    monthly_debt_service = (
        annual_debt_service
        / 12.0
    )

    # =============================================================
    # INVENTORY
    # =============================================================

    selected_inventory_decision = (
        _selected_inventory_decision()
    )

    inventory_schedule = (
        _extract_schedule_from_decision(
            selected_inventory_decision,
            (
                "inventory_cash_schedule",
                "inventory_schedule",
                "inventory_purchase_schedule",
            ),
        )
    )

    if inventory_schedule is None:

        inventory_schedule = [
            0.0
        ] * 6

    # =============================================================
    # ROLL-FORWARD
    # =============================================================

    rows: List[Dict[str, Any]] = []

    events: List[CashEvent] = []

    cash = opening_cash

    for index, month in enumerate(
        MONTHS
    ):

        collections = _as_float(
            ar_schedule[index]
            if index < len(
                ar_schedule
            )
            else 0.0
        )

        supplier_payments = _as_float(
            ap_schedule[index]
            if index < len(
                ap_schedule
            )
            else 0.0
        )

        inventory_cash = _as_float(
            inventory_schedule[index]
            if index < len(
                inventory_schedule
            )
            else 0.0
        )

        fixed_opex = (
            monthly_fixed_opex
        )

        debt_service = (
            monthly_debt_service
        )

        net_cash_change = (
            collections
            - supplier_payments
            - inventory_cash
            - fixed_opex
            - debt_service
        )

        opening_month_cash = cash

        cash = (
            cash
            + net_cash_change
        )

        events.append(
            CashEvent(
                month=month,
                label="Customer collections",
                amount=collections,
                kind="inflow",
            )
        )

        events.append(
            CashEvent(
                month=month,
                label="Supplier payments",
                amount=supplier_payments,
                kind="outflow",
            )
        )

        events.append(
            CashEvent(
                month=month,
                label="Inventory",
                amount=inventory_cash,
                kind="outflow",
            )
        )

        events.append(
            CashEvent(
                month=month,
                label="Fixed operating costs",
                amount=fixed_opex,
                kind="outflow",
            )
        )

        events.append(
            CashEvent(
                month=month,
                label="Debt service",
                amount=debt_service,
                kind="outflow",
            )
        )

        rows.append(
            {
                "Month": month,
                "Opening Cash": opening_month_cash,
                "Customer Collections": collections,
                "Supplier Payments": supplier_payments,
                "Inventory": inventory_cash,
                "Fixed Opex": fixed_opex,
                "Debt Service": debt_service,
                "Net Cash Change": net_cash_change,
                "Closing Cash": cash,
            }
        )

    dataframe = pd.DataFrame(
        rows
    )

    dataframe.attrs["ar_source"] = (
        ar_source
    )

    dataframe.attrs["ar_timing_method"] = (
        ar_timing_method
    )

    dataframe.attrs["ap_source"] = (
        ap_source
    )

    dataframe.attrs["collection_profile"] = (
        collection_profile
    )

    dataframe.attrs["selected_ar_days"] = (
        selected_ar_days
    )

    dataframe.attrs["selected_ap_days"] = (
        selected_ap_days
    )

    dataframe.attrs["projected_ar_days"] = (
        projected_ar_days
    )

    dataframe.attrs["baseline_ar_days"] = (
        baseline_ar_days
    )

    return CashPlanResult(
        dataframe=dataframe,
        events=tuple(events),
    )


# ---------------------------------------------------------------------
# UI Entry Point
# ---------------------------------------------------------------------

def render_cash_management_lab(
    baseline_state: Any = None,
) -> None:

    st.title(
        "💧 Cash Management"
    )

    st.caption(
        "See when cash comes in, when it goes out, "
        "and where pressure appears."
    )

    if baseline_state is None:

        baseline_state = (
            _get_baseline_state()
        )

    if baseline_state is None:

        st.warning(
            "Please set and confirm the Locked Baseline first."
        )

        return

    projected_state = (
        _get_projected_state(
            baseline_state
        )
    )

    result = build_cash_plan(
        baseline_state=baseline_state,
        projected_state=projected_state,
    )

    df = result.dataframe

    selected_ar_decision = (
        _selected_ar_decision()
    )

    selected_ar_days = (
        _decision_ar_days(
            selected_ar_decision
        )
    )

    collection_profile = (
        _extract_collection_profile(
            selected_ar_decision
        )
    )

    baseline_ar_days = _as_float(
        df.attrs.get(
            "baseline_ar_days",
            0.0,
        )
    )

    projected_ar_days = _as_float(
        df.attrs.get(
            "projected_ar_days",
            0.0,
        )
    )

    # -------------------------------------------------------------
    # Planning nature of the model
    # -------------------------------------------------------------

    st.info(
        "Cash Management is a management planning estimate. "
        "It uses the selected collection policy to estimate "
        "when sales turn into cash. It is not an invoice-level "
        "collection forecast or customer aging analysis."
    )

    # -------------------------------------------------------------
    # Receivables source message
    # -------------------------------------------------------------

    if (
        selected_ar_decision is not None
        and collection_profile is not None
    ):

        new_pct = (
            collection_profile[
                "new_policy_pct"
            ]
            * 100.0
        )

        old_pct = (
            collection_profile[
                "old_policy_pct"
            ]
            * 100.0
        )

        new_days = (
            collection_profile[
                "new_policy_days"
            ]
        )

        old_days = (
            collection_profile[
                "old_policy_days"
            ]
        )

        st.success(
            "Receivables timing is driven by the selected "
            "collection policy in the Current Decision Plan: "
            f"{new_pct:.0f}% of sales at approximately "
            f"{new_days:.0f} days and "
            f"{old_pct:.0f}% at approximately "
            f"{old_days:.0f} days."
        )

    elif (
        selected_ar_decision is not None
        and selected_ar_days is not None
    ):

        st.warning(
            "The selected AR decision does not contain a "
            "collection profile. Cash Management is using "
            f"the legacy {selected_ar_days:.0f}-day fallback. "
            "Recreate or update the Receivables decision to "
            "include its collection policy."
        )

    else:

        st.caption(
            "No receivables decision is currently selected "
            "in the Current Decision Plan. Cash Management "
            "is using the projected CompanyState "
            f"({projected_ar_days:.0f} days)."
        )

    # -------------------------------------------------------------
    # Key metrics
    # -------------------------------------------------------------

    min_cash = float(
        df[
            "Closing Cash"
        ].min()
    )

    min_cash_month = str(
        df.loc[
            df[
                "Closing Cash"
            ].idxmin(),
            "Month",
        ]
    )

    final_cash = float(
        df[
            "Closing Cash"
        ].iloc[-1]
    )

    col1, col2, col3 = (
        st.columns(3)
    )

    with col1:

        st.metric(
            "Opening Cash",
            f"€{float(df['Opening Cash'].iloc[0]):,.0f}",
        )

    with col2:

        st.metric(
            "Minimum Cash",
            f"€{min_cash:,.0f}",
        )

    with col3:

        st.metric(
            "Month 6 Cash",
            f"€{final_cash:,.0f}",
        )

    st.caption(
        f"Minimum cash occurs in {min_cash_month}."
    )

    # -------------------------------------------------------------
    # Main cash table
    # -------------------------------------------------------------

    display_df = df.copy()

    money_columns = [
        "Opening Cash",
        "Customer Collections",
        "Supplier Payments",
        "Inventory",
        "Fixed Opex",
        "Debt Service",
        "Net Cash Change",
        "Closing Cash",
    ]

    for column in money_columns:

        if column in display_df.columns:

            display_df[
                column
            ] = display_df[
                column
            ].map(
                lambda x: f"€{x:,.0f}"
            )

    st.dataframe(
        display_df,
        use_container_width=True,
        hide_index=True,
    )

    # -------------------------------------------------------------
    # Assumptions
    # -------------------------------------------------------------

    with st.expander(
        "Cash timing assumptions",
        expanded=False,
    ):

        st.write(
            "Receivables:",
            df.attrs.get(
                "ar_source",
                "",
            ),
        )

        st.write(
            "AR timing method:",
            df.attrs.get(
                "ar_timing_method",
                "",
            ),
        )

        st.write(
            "Payables:",
            df.attrs.get(
                "ap_source",
                "",
            ),
        )

        st.write(
            "Baseline AR days:",
            f"{baseline_ar_days:.0f}",
        )

        st.write(
            "Projected AR days:",
            f"{projected_ar_days:.0f}",
        )

        if selected_ar_days is not None:

            st.write(
                "Selected AR decision:",
                f"{selected_ar_days:.0f} days",
            )

        if collection_profile is not None:

            st.write(
                "New collection policy:",
                (
                    f"{collection_profile['new_policy_pct'] * 100:.0f}% "
                    f"at {collection_profile['new_policy_days']:.0f} days"
                ),
            )

            st.write(
                "Existing collection policy:",
                (
                    f"{collection_profile['old_policy_pct'] * 100:.0f}% "
                    f"at {collection_profile['old_policy_days']:.0f} days"
                ),
            )

    # -------------------------------------------------------------
    # Cash chart
    # -------------------------------------------------------------

    chart_df = df.set_index(
        "Month"
    )[[
        "Closing Cash"
    ]]

    st.line_chart(
        chart_df
    )
