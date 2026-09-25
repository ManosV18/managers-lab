from dataclasses import dataclass
from typing import Any, Dict, List, Mapping, Optional, Sequence, Tuple

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


# =====================================================================
# GENERIC HELPERS
# =====================================================================


def _as_float(
    value: Any,
    default: float = 0.0,
) -> float:
    try:
        if value is None:
            return default

        return float(value)

    except (TypeError, ValueError):
        return default


def _decision_changes(
    decision: Any,
) -> Mapping[str, Any]:

    if decision is None:
        return {}

    changes = getattr(
        decision,
        "changes",
        None,
    )

    if isinstance(changes, Mapping):
        return changes

    return {}


def _decision_metadata(
    decision: Any,
) -> Mapping[str, Any]:

    if decision is None:
        return {}

    for attr in (
        "metadata",
        "meta",
        "details",
        "assumptions",
    ):

        value = getattr(
            decision,
            attr,
            None,
        )

        if isinstance(value, Mapping):
            return value

    return {}


def _all_decisions() -> Sequence[Any]:

    plan = st.session_state.get(
        "decision_plan"
    )

    if plan is None:
        return ()

    decisions = getattr(
        plan,
        "decisions",
        None,
    )

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

    for decision in reversed(
        tuple(decisions)
    ):

        changes = _decision_changes(
            decision
        )

        if change_key in changes:
            return decision

    return None


# =====================================================================
# BASELINE / PROJECTED COMPANY STATE
# =====================================================================


def _get_baseline_state() -> Any:

    try:

        from core.baseline_repository import (
            BaselineRepository,
        )

        from core.state_builder import (
            StateBuilder,
        )

        repository = BaselineRepository()

        baseline = (
            repository.get_baseline()
        )

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


# =====================================================================
# COMPANY STATE HELPERS
# =====================================================================


def _working_capital_terms(
    state: Any,
) -> Tuple[float, float, float]:

    if state is None:
        return 0.0, 0.0, 0.0

    working_capital = getattr(
        state,
        "working_capital",
        None,
    )

    if working_capital is None:
        return 0.0, 0.0, 0.0

    return (
        _as_float(
            getattr(
                working_capital,
                "ar_days",
                0.0,
            )
        ),
        _as_float(
            getattr(
                working_capital,
                "inventory_days",
                0.0,
            )
        ),
        _as_float(
            getattr(
                working_capital,
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

    revenue = (
        price * volume
    )

    cogs = (
        variable_cost * volume
    )

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


# =====================================================================
# GENERIC SCHEDULE HELPERS
# =====================================================================


def _normalise_schedule(
    value: Any,
) -> Optional[List[float]]:

    if value is None:
        return None

    if isinstance(
        value,
        Mapping,
    ):

        result: List[float] = []

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
        (list, tuple),
    ):

        result = [
            _as_float(item)
            for item in value
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

    for container in (
        changes,
        metadata,
    ):

        for key in schedule_keys:

            if key not in container:
                continue

            schedule = (
                _normalise_schedule(
                    container[key]
                )
            )

            if schedule is not None:
                return schedule

    return None


# =====================================================================
# RECEIVABLES COLLECTION PROFILE
# =====================================================================


def _normalise_collection_schedule(
    value: Any,
) -> Optional[List[float]]:

    if value is None:
        return None

    if isinstance(
        value,
        Mapping,
    ):

        candidates = [
            (
                "month_0_pct",
                "month0_pct",
                "same_month_pct",
                "same_month",
            ),
            (
                "month_1_pct",
                "month1_pct",
                "next_month_pct",
                "next_month",
            ),
            (
                "month_2_pct",
                "month2_pct",
                "month_plus_2_pct",
                "month_2",
            ),
        ]

        result: List[float] = []

        for keys in candidates:

            amount = None

            for key in keys:

                if key in value:
                    amount = value[key]
                    break

            result.append(
                _as_float(
                    amount,
                    0.0,
                )
            )

        total = sum(result)

        if total <= 0.0:
            return None

        if total > 1.000001:

            result = [
                item / 100.0
                for item in result
            ]

            total = sum(result)

        if total <= 0.0:
            return None

        return [
            item / total
            for item in result
        ]

    if isinstance(
        value,
        (list, tuple),
    ):

        if len(value) < 3:
            return None

        result = [
            _as_float(value[0]),
            _as_float(value[1]),
            _as_float(value[2]),
        ]

        total = sum(result)

        if total <= 0.0:
            return None

        if total > 1.000001:

            result = [
                item / 100.0
                for item in result
            ]

            total = sum(result)

        if total <= 0.0:
            return None

        return [
            item / total
            for item in result
        ]

    return None


def _extract_collection_schedule_from_decision(
    decision: Any,
) -> Optional[List[float]]:

    if decision is None:
        return None

    changes = _decision_changes(
        decision
    )

    metadata = _decision_metadata(
        decision
    )

    schedule_keys = (
        "collection_schedule",
        "collection_profile",
        "ar_collection_schedule",
        "receivables_schedule",
        "cash_collection_schedule",
    )

    for container in (
        changes,
        metadata,
    ):

        for key in schedule_keys:

            if key not in container:
                continue

            schedule = (
                _normalise_collection_schedule(
                    container[key]
                )
            )

            if schedule is not None:
                return schedule

    return None


def _build_collection_cash_schedule(
    annual_revenue: float,
    opening_ar_balance: float,
    collection_schedule: Sequence[float],
) -> List[float]:
    """
    Build six-month customer collections.

    Two components are modelled separately:

    1. Opening AR
       Existing receivables are collected using the selected
       management collection profile.

    2. New sales cohorts
       Each month's projected revenue is collected according to
       the same average profile.

    This is an average management timing model.
    It is not invoice-level ageing.
    """

    annual_revenue = max(
        0.0,
        _as_float(
            annual_revenue
        ),
    )

    opening_ar_balance = max(
        0.0,
        _as_float(
            opening_ar_balance
        ),
    )

    schedule = [
        _as_float(value)
        for value in collection_schedule[:3]
    ]

    if len(schedule) < 3:

        schedule += [
            0.0
        ] * (
            3 - len(schedule)
        )

    total = sum(schedule)

    if total <= 0.0:

        return [
            0.0
            for _ in MONTHS
        ]

    schedule = [
        value / total
        for value in schedule
    ]

    monthly_revenue = (
        annual_revenue / 12.0
    )

    collections = [
        0.0
        for _ in MONTHS
    ]

    # -------------------------------------------------------------
    # OPENING AR
    # -------------------------------------------------------------

    for lag in range(3):

        target_month = lag

        if target_month >= len(
            collections
        ):
            continue

        collections[target_month] += (
            opening_ar_balance
            * schedule[lag]
        )

    # -------------------------------------------------------------
    # NEW SALES COHORTS
    # -------------------------------------------------------------

    for source_month in range(
        len(MONTHS)
    ):

        for lag in range(3):

            target_month = (
                source_month + lag
            )

            if target_month >= len(
                collections
            ):
                continue

            collections[target_month] += (
                monthly_revenue
                * schedule[lag]
            )

    return collections


# =====================================================================
# PAYMENT DAYS
# =====================================================================


def _schedule_from_payment_days(
    annual_amount: float,
    payment_days: float,
    opening_balance: float = 0.0,
) -> List[float]:
    """
    Convert payment terms into a six-month cash payment schedule.

    The schedule represents actual cash payment timing.

    It is used as a fallback when no explicit payment timing
    decision exists.
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

    # -------------------------------------------------------------
    # OPENING PAYABLES
    # -------------------------------------------------------------

    if opening_balance > 0.0:

        if lag_months <= 0.0:

            schedule[0] += (
                opening_balance
            )

        else:

            full_months = int(
                lag_months
            )

            if full_months < len(
                MONTHS
            ):

                schedule[
                    full_months
                ] += opening_balance

    # -------------------------------------------------------------
    # NEW MONTHLY PURCHASES / COGS
    # -------------------------------------------------------------

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
            lower_target + 1
        )

        lower_amount = (
            monthly_amount
            * (1.0 - fraction)
        )

        upper_amount = (
            monthly_amount
            * fraction
        )

        if fraction <= 0.000001:

            if lower_target < len(
                MONTHS
            ):

                schedule[
                    lower_target
                ] += monthly_amount

        else:

            if lower_target < len(
                MONTHS
            ):

                schedule[
                    lower_target
                ] += lower_amount

            if upper_target < len(
                MONTHS
            ):

                schedule[
                    upper_target
                ] += upper_amount

    return schedule


# =====================================================================
# CURRENT DECISION PLAN
# =====================================================================


def _selected_ar_decision() -> Optional[Any]:

    return _find_plan_decision_by_change(
        "ar_days"
    )


def _selected_ap_decision() -> Optional[Any]:

    return _find_plan_decision_by_change(
        "ap_days"
    )


def _selected_inventory_decision() -> Optional[Any]:

    for key in (
        "inventory_days",
        "inventory_event",
        "inventory_change",
    ):

        decision = (
            _find_plan_decision_by_change(
                key
            )
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


# =====================================================================
# FUTURE PURCHASING DECISION HOOK
# =====================================================================


def _selected_purchasing_decision() -> Optional[Any]:
    """
    Future integration point.

    When the Inventory / Purchasing Lab becomes active,
    its purchasing decision can be connected here.

    The Cash Management layer should receive the purchasing
    decision and convert it into supplier cash timing.

    It must NOT independently calculate an economic order
    quantity or create a second inventory model.
    """

    for key in (
        "purchase_amount",
        "purchases",
        "purchase_schedule",
        "purchasing_decision",
        "inventory_purchase",
    ):

        decision = (
            _find_plan_decision_by_change(
                key
            )
        )

        if decision is not None:
            return decision

    return None


# =====================================================================
# MAIN CASH PLAN BUILDER
# =====================================================================


def build_cash_plan(
    baseline_state: Any = None,
    projected_state: Any = None,
) -> CashPlanResult:

    if baseline_state is None:

        baseline_state = (
            _get_baseline_state()
        )

    if projected_state is None:

        projected_state = (
            _get_projected_state(
                baseline_state
            )
        )

    # =============================================================
    # BASELINE TERMS
    # =============================================================

    (
        baseline_ar_days,
        baseline_inventory_days,
        baseline_ap_days,
    ) = _working_capital_terms(
        baseline_state
    )

    # =============================================================
    # PROJECTED TERMS
    # =============================================================

    (
        projected_ar_days,
        projected_inventory_days,
        projected_ap_days,
    ) = _working_capital_terms(
        projected_state
    )

    # =============================================================
    # BASELINE OPERATING VALUES
    # =============================================================

    (
        baseline_annual_revenue,
        baseline_annual_cogs,
        baseline_annual_fixed_opex,
    ) = _annual_operating_values(
        baseline_state
    )

    # =============================================================
    # PROJECTED OPERATING VALUES
    # =============================================================

    (
        projected_annual_revenue,
        projected_annual_cogs,
        projected_annual_fixed_opex,
    ) = _annual_operating_values(
        projected_state
    )

    opening_cash = _opening_cash(
        baseline_state
    )

    annual_debt_service = (
        _annual_debt_service(
            projected_state
        )
    )

    # =============================================================
    # RECEIVABLES
    # =============================================================

    selected_ar_decision = (
        _selected_ar_decision()
    )

    explicit_ar_collection_schedule = (
        _extract_collection_schedule_from_decision(
            selected_ar_decision
        )
    )

    selected_ar_days = (
        _decision_ar_days(
            selected_ar_decision
        )
    )

    # Existing AR belongs to the baseline.
    #
    # Therefore it must be calculated from baseline revenue
    # and baseline AR days, not from projected revenue.

    opening_ar_balance = (
        baseline_annual_revenue
        * baseline_ar_days
        / 365.0
    )

    if (
        explicit_ar_collection_schedule
        is not None
    ):

        ar_schedule = (
            _build_collection_cash_schedule(
                annual_revenue=(
                    projected_annual_revenue
                ),
                opening_ar_balance=(
                    opening_ar_balance
                ),
                collection_schedule=(
                    explicit_ar_collection_schedule
                ),
            )
        )

        ar_source = (
            "Current Decision Plan — "
            "selected collection profile"
        )

        ar_timing_method = (
            "Average collection profile"
        )

    elif selected_ar_days is not None:

        ar_schedule = (
            _schedule_from_payment_days(
                projected_annual_revenue,
                selected_ar_days,
                opening_balance=(
                    opening_ar_balance
                ),
            )
        )

        ar_source = (
            "Current Decision Plan — "
            "selected AR decision "
            f"({selected_ar_days:.0f} days)"
        )

        ar_timing_method = (
            "AR-days fallback"
        )

    else:

        ar_schedule = (
            _schedule_from_payment_days(
                projected_annual_revenue,
                projected_ar_days,
                opening_balance=(
                    opening_ar_balance
                ),
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
    # PAYABLES / PURCHASE CASH TIMING
    # =============================================================
    #
    # IMPORTANT:
    #
    # Inventory is NOT treated as a separate cash outflow.
    #
    # The economic chain is:
    #
    #     Purchase requirement
    #          ↓
    #     Supplier terms
    #          ↓
    #     Supplier payment
    #          ↓
    #     Cash outflow
    #
    # Until the Purchasing / Inventory Decision is connected,
    # projected COGS is used as the monthly purchasing proxy.
    #
    # This is deliberately a temporary timing assumption and
    # prevents double counting of inventory + supplier payments.
    # =============================================================

    selected_ap_decision = (
        _selected_ap_decision()
    )

    selected_ap_days = (
        _decision_ap_days(
            selected_ap_decision
        )
    )

    opening_ap_balance = (
        baseline_annual_cogs
        * baseline_ap_days
        / 365.0
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

    if explicit_ap_schedule is not None:

        supplier_payment_schedule = (
            explicit_ap_schedule
        )

        ap_source = (
            "Current Decision Plan — "
            "explicit supplier payment schedule"
        )

        ap_timing_method = (
            "Explicit payment schedule"
        )

    elif selected_ap_days is not None:

        supplier_payment_schedule = (
            _schedule_from_payment_days(
                projected_annual_cogs,
                selected_ap_days,
                opening_balance=(
                    opening_ap_balance
                ),
            )
        )

        ap_source = (
            "Current Decision Plan — "
            "selected AP decision "
            f"({selected_ap_days:.0f} days)"
        )

        ap_timing_method = (
            "AP-days timing"
        )

    else:

        supplier_payment_schedule = (
            _schedule_from_payment_days(
                projected_annual_cogs,
                projected_ap_days,
                opening_balance=(
                    opening_ap_balance
                ),
            )
        )

        ap_source = (
            "Projected CompanyState fallback "
            f"({projected_ap_days:.0f} days)"
        )

        ap_timing_method = (
            "Projected AP-days timing"
        )

    # =============================================================
    # FUTURE PURCHASING DECISION STATUS
    # =============================================================

    purchasing_decision = (
        _selected_purchasing_decision()
    )

    purchasing_source = (
        "Projected COGS used as temporary "
        "purchasing proxy"
    )

    if purchasing_decision is not None:

        purchasing_source = (
            "Current Decision Plan — "
            "Purchasing Decision detected"
        )

        # ---------------------------------------------------------
        # We intentionally do NOT yet override the cash schedule
        # here.
        #
        # The Purchasing / Inventory Lab must first define the
        # exact purchase-decision structure:
        #
        # purchase amount
        # purchase month
        # supplier terms
        #
        # Once that structure is fixed, this is the only place
        # that needs to be connected.
        # ---------------------------------------------------------

    # =============================================================
    # FIXED CASH OUTFLOWS
    # =============================================================

    monthly_fixed_opex = (
        projected_annual_fixed_opex
        / 12.0
    )

    monthly_debt_service = (
        annual_debt_service
        / 12.0
    )

    # =============================================================
    # MONTHLY CASH ROLL-FORWARD
    # =============================================================

    rows: List[
        Dict[str, Any]
    ] = []

    events: List[
        CashEvent
    ] = []

    cash = opening_cash

    for index, month in enumerate(
        MONTHS
    ):

        collections = _as_float(
            (
                ar_schedule[index]
                if index < len(
                    ar_schedule
                )
                else 0.0
            )
        )

        supplier_payments = _as_float(
            (
                supplier_payment_schedule[index]
                if index < len(
                    supplier_payment_schedule
                )
                else 0.0
            )
        )

        fixed_opex = (
            monthly_fixed_opex
        )

        debt_service = (
            monthly_debt_service
        )

        # ---------------------------------------------------------
        # NO SEPARATE INVENTORY CASH OUTFLOW
        #
        # Supplier payments are the cash outflow generated by
        # purchasing activity.
        # ---------------------------------------------------------

        net_cash_change = (
            collections
            - supplier_payments
            - fixed_opex
            - debt_service
        )

        opening_month_cash = cash

        cash += net_cash_change

        events.extend(
            [
                CashEvent(
                    month=month,
                    label="Customer collections",
                    amount=collections,
                    kind="inflow",
                ),
                CashEvent(
                    month=month,
                    label="Supplier payments",
                    amount=supplier_payments,
                    kind="outflow",
                ),
                CashEvent(
                    month=month,
                    label="Fixed operating costs",
                    amount=fixed_opex,
                    kind="outflow",
                ),
                CashEvent(
                    month=month,
                    label="Debt service",
                    amount=debt_service,
                    kind="outflow",
                ),
            ]
        )

        rows.append(
            {
                "Month": month,
                "Opening Cash": (
                    opening_month_cash
                ),
                "Customer Collections": (
                    collections
                ),
                "Supplier Payments": (
                    supplier_payments
                ),
                "Fixed Opex": (
                    fixed_opex
                ),
                "Debt Service": (
                    debt_service
                ),
                "Net Cash Change": (
                    net_cash_change
                ),
                "Closing Cash": cash,
            }
        )

    dataframe = pd.DataFrame(
        rows
    )

    # =============================================================
    # METADATA
    # =============================================================

    dataframe.attrs[
        "ar_source"
    ] = ar_source

    dataframe.attrs[
        "ar_timing_method"
    ] = ar_timing_method

    dataframe.attrs[
        "ap_source"
    ] = ap_source

    dataframe.attrs[
        "ap_timing_method"
    ] = ap_timing_method

    dataframe.attrs[
        "purchasing_source"
    ] = purchasing_source

    dataframe.attrs[
        "selected_ar_days"
    ] = selected_ar_days

    dataframe.attrs[
        "selected_ap_days"
    ] = selected_ap_days

    dataframe.attrs[
        "projected_ar_days"
    ] = projected_ar_days

    dataframe.attrs[
        "projected_ap_days"
    ] = projected_ap_days

    dataframe.attrs[
        "baseline_ar_days"
    ] = baseline_ar_days

    dataframe.attrs[
        "baseline_ap_days"
    ] = baseline_ap_days

    dataframe.attrs[
        "collection_schedule"
    ] = explicit_ar_collection_schedule

    dataframe.attrs[
        "collection_cash_schedule"
    ] = ar_schedule

    dataframe.attrs[
        "opening_ar_balance"
    ] = opening_ar_balance

    dataframe.attrs[
        "opening_ap_balance"
    ] = opening_ap_balance

    dataframe.attrs[
        "baseline_annual_revenue"
    ] = baseline_annual_revenue

    dataframe.attrs[
        "projected_annual_revenue"
    ] = projected_annual_revenue

    dataframe.attrs[
        "baseline_annual_cogs"
    ] = baseline_annual_cogs

    dataframe.attrs[
        "projected_annual_cogs"
    ] = projected_annual_cogs

    dataframe.attrs[
        "purchasing_decision_detected"
    ] = purchasing_decision is not None

    return CashPlanResult(
        dataframe=dataframe,
        events=tuple(events),
    )


# =====================================================================
# UI
# =====================================================================


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

    st.info(
        "Cash Management is a management planning estimate. "
        "Customer collections are based on the collection profile "
        "selected in the Receivables Decision. Supplier payments "
        "represent the cash timing of purchasing activity. "
        "Inventory is not shown as a separate cash outflow, "
        "to avoid double counting."
    )

    # =============================================================
    # RECEIVABLES STATUS
    # =============================================================

    if selected_ar_decision is not None:

        schedule = (
            _extract_collection_schedule_from_decision(
                selected_ar_decision
            )
        )

        if schedule is not None:

            st.success(
                "Customer collection timing is driven by the "
                "collection profile in the Current Decision Plan."
            )

        elif selected_ar_days is not None:

            st.warning(
                "The selected Receivables Decision does not "
                "contain a collection profile. Cash Management "
                "is using the AR-days fallback "
                f"({selected_ar_days:.0f} days)."
            )

    else:

        st.caption(
            "No Receivables Decision is currently selected "
            "in the Current Decision Plan. Cash Management "
            "is using the projected CompanyState "
            f"({projected_ar_days:.0f} days)."
        )

    # =============================================================
    # PURCHASING STATUS
    # =============================================================

    purchasing_decision = (
        _selected_purchasing_decision()
    )

    if purchasing_decision is None:

        st.caption(
            "Purchasing timing is currently based on projected "
            "COGS and AP terms. The Inventory / Purchasing "
            "Decision will later replace this temporary proxy."
        )

    else:

        st.info(
            "A Purchasing / Inventory Decision is present in "
            "the Current Decision Plan. Its exact purchase "
            "schedule will be connected to supplier payment "
            "timing once the Purchasing Decision structure is "
            "finalised."
        )

    # =============================================================
    # KEY METRICS
    # =============================================================

    min_cash = float(
        df["Closing Cash"].min()
    )

    min_cash_month = str(
        df.loc[
            df["Closing Cash"].idxmin(),
            "Month",
        ]
    )

    final_cash = float(
        df["Closing Cash"].iloc[-1]
    )

    col1, col2, col3 = st.columns(3)

    with col1:

        st.metric(
            "Opening Cash",
            (
                f"€{float(df['Opening Cash'].iloc[0]):,.0f}"
            ),
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

    # =============================================================
    # CASH TABLE
    # =============================================================

    display_df = df.copy()

    money_columns = [
        "Opening Cash",
        "Customer Collections",
        "Supplier Payments",
        "Fixed Opex",
        "Debt Service",
        "Net Cash Change",
        "Closing Cash",
    ]

    for column in money_columns:

        if column in display_df.columns:

            display_df[column] = (
                display_df[column]
                .map(
                    lambda value:
                    f"€{value:,.0f}"
                )
            )

    st.dataframe(
        display_df,
        use_container_width=True,
        hide_index=True,
    )

    # =============================================================
    # ASSUMPTIONS
    # =============================================================

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
            "AP timing method:",
            df.attrs.get(
                "ap_timing_method",
                "",
            ),
        )

        st.write(
            "Purchasing:",
            df.attrs.get(
                "purchasing_source",
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

        baseline_ap_days = _as_float(
            df.attrs.get(
                "baseline_ap_days",
                0.0,
            )
        )

        projected_ap_days = _as_float(
            df.attrs.get(
                "projected_ap_days",
                0.0,
            )
        )

        st.write(
            "Baseline AP days:",
            f"{baseline_ap_days:.0f}",
        )

        st.write(
            "Projected AP days:",
            f"{projected_ap_days:.0f}",
        )

        opening_ar_balance = _as_float(
            df.attrs.get(
                "opening_ar_balance",
                0.0,
            )
        )

        opening_ap_balance = _as_float(
            df.attrs.get(
                "opening_ap_balance",
                0.0,
            )
        )

        st.write(
            "Opening AR:",
            f"€{opening_ar_balance:,.0f}",
        )

        st.write(
            "Opening AP:",
            f"€{opening_ap_balance:,.0f}",
        )

        if selected_ar_days is not None:

            st.write(
                "Selected AR decision:",
                f"{selected_ar_days:.1f} days",
            )

        schedule = df.attrs.get(
            "collection_schedule"
        )

        if schedule is not None:

            st.write(
                "Average collection profile:"
            )

            schedule_df = pd.DataFrame(
                {
                    "Timing": [
                        "Same month",
                        "Next month",
                        "Month +2",
                    ],
                    "Collection %": [
                        (
                            f"{schedule[0] * 100:.1f}%"
                        ),
                        (
                            f"{schedule[1] * 100:.1f}%"
                        ),
                        (
                            f"{schedule[2] * 100:.1f}%"
                        ),
                    ],
                }
            )

            st.dataframe(
                schedule_df,
                use_container_width=True,
                hide_index=True,
            )

            st.caption(
                "The profile is an average collection pattern "
                "for the customer base. It is applied to both "
                "opening AR and new sales. It is not an "
                "invoice-level ageing model."
            )

        st.caption(
            "Inventory is currently not treated as a separate "
            "cash outflow. Purchasing activity is represented "
            "through supplier payments. The future Purchasing "
            "Decision will determine the actual purchase amount "
            "and timing."
        )

    # =============================================================
    # CASH CHART
    # =============================================================

    chart_df = df.set_index(
        "Month"
    )[[
        "Closing Cash"
    ]]

    st.line_chart(
        chart_df
    )
