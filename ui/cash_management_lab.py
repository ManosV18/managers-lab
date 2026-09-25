from dataclasses import dataclass
from typing import Any, Dict, List, Mapping, Optional, Sequence, Tuple

import pandas as pd
import streamlit as st


# =====================================================================
# PLANNING HORIZON
# =====================================================================

MONTHS = [
    "Month 1",
    "Month 2",
    "Month 3",
    "Month 4",
    "Month 5",
    "Month 6",
]


# =====================================================================
# DECISION CANDIDATE KEYS
# =====================================================================

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


# =====================================================================
# CASH EVENTS / RESULT
# =====================================================================

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

        result = float(value)

        if result != result:
            return default

        return result

    except (TypeError, ValueError, OverflowError):

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

    if isinstance(
        changes,
        Mapping,
    ):
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

        if isinstance(
            value,
            Mapping,
        ):
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

        if len(result) >= len(MONTHS):

            return result[:len(MONTHS)]

        return (
            result
            + [0.0]
            * (
                len(MONTHS)
                - len(result)
            )
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
    monthly_sales: Sequence[float],
    opening_ar_balance: float,
    collection_schedule: Sequence[float],
) -> Tuple[List[float], Dict[str, Any]]:
    """
    Build the customer collection schedule.

    Opening AR and each new sales cohort are handled separately.

    Example:

        Collection profile = 20% / 70% / 10%

        Month 1 sales = €150,000

        Month 1 collection = €30,000
        Month 2 collection = €105,000
        Month 3 collection = €15,000
    """

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

    while len(schedule) < 3:

        schedule.append(0.0)

    total = sum(schedule)

    if total <= 0.0:

        return (
            [0.0 for _ in MONTHS],
            {
                "opening_ar_collections": [
                    0.0 for _ in MONTHS
                ],
                "sales_cohort_collections": [
                    [0.0 for _ in MONTHS]
                    for _ in MONTHS
                ],
            },
        )

    schedule = [
        value / total
        for value in schedule
    ]

    sales = [
        max(
            0.0,
            _as_float(value),
        )
        for value in monthly_sales
    ]

    while len(sales) < len(MONTHS):

        sales.append(0.0)

    sales = sales[:len(MONTHS)]

    collections = [
        0.0
        for _ in MONTHS
    ]

    # -------------------------------------------------------------
    # OPENING AR
    # -------------------------------------------------------------

    opening_ar_collections = [
        0.0
        for _ in MONTHS
    ]

    for lag in range(3):

        target_month = lag

        if target_month >= len(
            MONTHS
        ):
            continue

        amount = (
            opening_ar_balance
            * schedule[lag]
        )

        opening_ar_collections[
            target_month
        ] += amount

        collections[
            target_month
        ] += amount

    # -------------------------------------------------------------
    # NEW SALES COHORTS
    # -------------------------------------------------------------

    sales_cohort_collections = [
        [
            0.0
            for _ in MONTHS
        ]
        for _ in MONTHS
    ]

    for source_month in range(
        len(MONTHS)
    ):

        source_sales = (
            sales[source_month]
        )

        if source_sales <= 0.0:
            continue

        for lag in range(3):

            target_month = (
                source_month + lag
            )

            if target_month >= len(
                MONTHS
            ):
                continue

            amount = (
                source_sales
                * schedule[lag]
            )

            sales_cohort_collections[
                source_month
            ][target_month] += amount

            collections[
                target_month
            ] += amount

    diagnostics = {
        "opening_ar_collections": (
            opening_ar_collections
        ),
        "sales_cohort_collections": (
            sales_cohort_collections
        ),
        "normalised_collection_profile": (
            schedule
        ),
        "monthly_sales_used": sales,
    }

    return (
        collections,
        diagnostics,
    )


# =====================================================================
# SUPPLIER PAYMENT TIMING
# =====================================================================

def _build_supplier_payment_schedule(
    monthly_purchases: Sequence[float],
    payment_days: float,
    opening_ap_balance: float = 0.0,
) -> Tuple[List[float], Dict[str, Any]]:
    """
    Convert purchasing activity into supplier cash payments.

    IMPORTANT:

        Inventory determines purchases.
        AP terms determine payment timing.

    This function therefore does NOT calculate inventory.

    Each purchase month is treated as a separate purchase cohort.

    Payment terms are converted using:

        365 / 12 days per month

    Examples:

        0 days
            → same month

        ~30 days
            → next month

        ~45 days
            → 50% next month
              50% following month

        ~60 days
            → two months later
    """

    payment_days = max(
        0.0,
        _as_float(
            payment_days
        ),
    )

    opening_ap_balance = max(
        0.0,
        _as_float(
            opening_ap_balance
        ),
    )

    purchases = [
        max(
            0.0,
            _as_float(value),
        )
        for value in monthly_purchases
    ]

    while len(purchases) < len(
        MONTHS
    ):

        purchases.append(0.0)

    purchases = purchases[
        :len(MONTHS)
    ]

    payments = [
        0.0
        for _ in MONTHS
    ]

    days_per_month = (
        365.0 / 12.0
    )

    lag_months = (
        payment_days
        / days_per_month
    )

    # =============================================================
    # OPENING AP
    # =============================================================

    if opening_ap_balance > 0.0:

        if payment_days <= 0.0:

            payments[0] += (
                opening_ap_balance
            )

        else:

            full_months = int(
                lag_months
            )

            fraction = (
                lag_months
                - full_months
            )

            first_target = (
                full_months
            )

            second_target = (
                full_months + 1
            )

            if fraction <= 0.000001:

                if first_target < len(
                    MONTHS
                ):

                    payments[
                        first_target
                    ] += (
                        opening_ap_balance
                    )

            else:

                if first_target < len(
                    MONTHS
                ):

                    payments[
                        first_target
                    ] += (
                        opening_ap_balance
                        * (1.0 - fraction)
                    )

                if second_target < len(
                    MONTHS
                ):

                    payments[
                        second_target
                    ] += (
                        opening_ap_balance
                        * fraction
                    )

    # =============================================================
    # PURCHASE COHORTS
    # =============================================================

    if payment_days <= 0.0:

        for index in range(
            len(MONTHS)
        ):

            payments[index] += (
                purchases[index]
            )

    else:

        full_months = int(
            lag_months
        )

        fraction = (
            lag_months
            - full_months
        )

        for source_month in range(
            len(MONTHS)
        ):

            purchase_amount = (
                purchases[source_month]
            )

            if purchase_amount <= 0.0:
                continue

            first_target = (
                source_month
                + full_months
            )

            second_target = (
                first_target + 1
            )

            if fraction <= 0.000001:

                if first_target < len(
                    MONTHS
                ):

                    payments[
                        first_target
                    ] += (
                        purchase_amount
                    )

            else:

                first_amount = (
                    purchase_amount
                    * (1.0 - fraction)
                )

                second_amount = (
                    purchase_amount
                    * fraction
                )

                if first_target < len(
                    MONTHS
                ):

                    payments[
                        first_target
                    ] += first_amount

                if second_target < len(
                    MONTHS
                ):

                    payments[
                        second_target
                    ] += second_amount

    # =============================================================
    # AP ROLL-FORWARD
    # =============================================================

    ending_ap = []

    balance = (
        opening_ap_balance
    )

    for index in range(
        len(MONTHS)
    ):

        balance += purchases[index]
        balance -= payments[index]

        ending_ap.append(
            max(
                0.0,
                balance,
            )
        )

    diagnostics = {
        "monthly_purchases": purchases,
        "supplier_payments": payments,
        "ending_ap": ending_ap,
        "payment_days": payment_days,
    }

    return (
        payments,
        diagnostics,
    )


# =====================================================================
# DECISION PLAN HELPERS
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
# PURCHASING DECISION
# =====================================================================

def _selected_purchasing_decision() -> Optional[Any]:
    """
    Detect a future Purchasing / Inventory decision.

    The important architectural rule is:

        Purchasing Decision
                 ↓
        monthly purchase amounts
                 ↓
        Supplier payment timing
                 ↓
        Monthly Cash Flow

    Cash Management must not create its own inventory model.
    """

    for key in (
        "purchase_amount",
        "purchases",
        "purchase_schedule",
        "monthly_purchases",
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


def _extract_purchase_schedule(
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

    purchase_keys = (
        "purchase_schedule",
        "monthly_purchases",
        "purchases",
        "supplier_purchases",
        "inventory_purchase_schedule",
    )

    for container in (
        changes,
        metadata,
    ):

        for key in purchase_keys:

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
    # WORKING CAPITAL TERMS
    # =============================================================

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

    # =============================================================
    # OPERATING VALUES
    # =============================================================

    (
        baseline_annual_revenue,
        baseline_annual_cogs,
        baseline_annual_fixed_opex,
    ) = _annual_operating_values(
        baseline_state
    )

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

    selected_ar_days = (
        _decision_ar_days(
            selected_ar_decision
        )
    )

    explicit_collection_schedule = (
        _extract_collection_schedule_from_decision(
            selected_ar_decision
        )
    )

    # Opening AR belongs to the locked baseline.
    opening_ar_balance = (
        max(
            0.0,
            baseline_annual_revenue
            * baseline_ar_days
            / 365.0,
        )
    )

    # Temporary six-month revenue profile.
    #
    # This is NOT a new revenue model.
    # It simply spreads projected annual revenue evenly across
    # the cash-timing horizon until a monthly operating profile
    # exists elsewhere.
    monthly_projected_revenue = (
        max(
            0.0,
            projected_annual_revenue,
        )
        / 12.0
    )

    monthly_sales = [
        monthly_projected_revenue
        for _ in MONTHS
    ]

    if explicit_collection_schedule is not None:

        (
            ar_schedule,
            ar_diagnostics,
        ) = _build_collection_cash_schedule(
            monthly_sales=monthly_sales,
            opening_ar_balance=opening_ar_balance,
            collection_schedule=(
                explicit_collection_schedule
            ),
        )

        ar_source = (
            "Current Decision Plan — "
            "collection profile"
        )

        ar_timing_method = (
            "Cohort-based collection timing"
        )

    elif selected_ar_days is not None:

        (
            ar_schedule,
            ar_diagnostics,
        ) = _build_supplier_payment_schedule(
            monthly_purchases=monthly_sales,
            payment_days=selected_ar_days,
            opening_ap_balance=opening_ar_balance,
        )

        ar_source = (
            "Current Decision Plan — "
            f"AR {selected_ar_days:.0f} days"
        )

        ar_timing_method = (
            "AR-days fallback"
        )

        # The helper above is mathematically usable as a lag
        # allocator, but its diagnostic names are AP-oriented.
        # Replace them with explicit AR metadata.
        ar_diagnostics = {
            "opening_ar_collections": [],
            "sales_cohort_collections": [],
            "normalised_collection_profile": None,
            "monthly_sales_used": monthly_sales,
        }

    else:

        (
            ar_schedule,
            ar_diagnostics,
        ) = _build_supplier_payment_schedule(
            monthly_purchases=monthly_sales,
            payment_days=projected_ar_days,
            opening_ap_balance=opening_ar_balance,
        )

        ar_source = (
            "Projected CompanyState fallback — "
            f"AR {projected_ar_days:.0f} days"
        )

        ar_timing_method = (
            "Projected AR-days fallback"
        )

        ar_diagnostics = {
            "opening_ar_collections": [],
            "sales_cohort_collections": [],
            "normalised_collection_profile": None,
            "monthly_sales_used": monthly_sales,
        }

    # =============================================================
    # PAYABLES
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
        max(
            0.0,
            baseline_annual_cogs
            * baseline_ap_days
            / 365.0,
        )
    )

    # -------------------------------------------------------------
    # FIRST PRIORITY:
    #
    # An explicit purchasing decision can provide actual monthly
    # purchases.
    # -------------------------------------------------------------

    purchasing_decision = (
        _selected_purchasing_decision()
    )

    explicit_purchase_schedule = (
        _extract_purchase_schedule(
            purchasing_decision
        )
    )

    if explicit_purchase_schedule is not None:

        monthly_purchases = (
            explicit_purchase_schedule
        )

        purchasing_source = (
            "Current Decision Plan — "
            "Purchasing Decision"
        )

    else:

        # ---------------------------------------------------------
        # TEMPORARY PROXY
        #
        # Until the Inventory / Purchasing Decision is connected,
        # projected COGS is used as the purchasing requirement.
        #
        # This is intentionally a proxy, not an inventory model.
        # ---------------------------------------------------------

        monthly_purchase_proxy = (
            max(
                0.0,
                projected_annual_cogs,
            )
            / 12.0
        )

        monthly_purchases = [
            monthly_purchase_proxy
            for _ in MONTHS
        ]

        purchasing_source = (
            "Projected COGS — temporary "
            "purchasing proxy"
        )

    # -------------------------------------------------------------
    # Explicit supplier cash schedule
    # -------------------------------------------------------------

    explicit_ap_schedule = (
        _extract_schedule_from_decision(
            selected_ap_decision,
            (
                "payment_schedule",
                "ap_payment_schedule",
                "payables_schedule",
                "cash_payment_schedule",
                "supplier_payment_schedule",
            ),
        )
    )

    if explicit_ap_schedule is not None:

        supplier_payment_schedule = (
            explicit_ap_schedule
        )

        ap_diagnostics = {
            "monthly_purchases": (
                monthly_purchases
            ),
            "supplier_payments": (
                explicit_ap_schedule
            ),
            "ending_ap": [],
            "payment_days": (
                selected_ap_days
                if selected_ap_days is not None
                else projected_ap_days
            ),
        }

        ap_source = (
            "Current Decision Plan — "
            "explicit supplier payment schedule"
        )

        ap_timing_method = (
            "Explicit supplier payment schedule"
        )

    else:

        effective_ap_days = (
            selected_ap_days
            if selected_ap_days is not None
            else projected_ap_days
        )

        (
            supplier_payment_schedule,
            ap_diagnostics,
        ) = _build_supplier_payment_schedule(
            monthly_purchases=monthly_purchases,
            payment_days=effective_ap_days,
            opening_ap_balance=opening_ap_balance,
        )

        if selected_ap_days is not None:

            ap_source = (
                "Current Decision Plan — "
                f"AP {selected_ap_days:.0f} days"
            )

            ap_timing_method = (
                "Purchase-cohort AP timing"
            )

        else:

            ap_source = (
                "Projected CompanyState fallback — "
                f"AP {projected_ap_days:.0f} days"
            )

            ap_timing_method = (
                "Purchase-cohort AP timing"
            )

    # =============================================================
    # FIXED CASH OUTFLOWS
    # =============================================================

    monthly_fixed_opex = (
        max(
            0.0,
            projected_annual_fixed_opex,
        )
        / 12.0
    )

    monthly_debt_service = (
        max(
            0.0,
            annual_debt_service,
        )
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
            ar_schedule[index]
            if index < len(
                ar_schedule
            )
            else 0.0
        )

        supplier_payments = _as_float(
            supplier_payment_schedule[index]
            if index < len(
                supplier_payment_schedule
            )
            else 0.0
        )

        fixed_opex = (
            monthly_fixed_opex
        )

        debt_service = (
            monthly_debt_service
        )

        # ---------------------------------------------------------
        # IMPORTANT:
        #
        # Inventory itself is NOT a cash payment.
        #
        # Purchases become cash outflow through Supplier Payments.
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
        "baseline_inventory_days"
    ] = baseline_inventory_days

    dataframe.attrs[
        "projected_inventory_days"
    ] = projected_inventory_days

    dataframe.attrs[
        "baseline_ap_days"
    ] = baseline_ap_days

    dataframe.attrs[
        "collection_schedule"
    ] = explicit_collection_schedule

    dataframe.attrs[
        "collection_cash_schedule"
    ] = ar_schedule

    dataframe.attrs[
        "collection_diagnostics"
    ] = ar_diagnostics

    dataframe.attrs[
        "supplier_payment_schedule"
    ] = supplier_payment_schedule

    dataframe.attrs[
        "supplier_payment_diagnostics"
    ] = ap_diagnostics

    dataframe.attrs[
        "monthly_purchases"
    ] = monthly_purchases

    dataframe.attrs[
        "purchasing_decision_detected"
    ] = purchasing_decision is not None

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
        "monthly_sales_used"
    ] = monthly_sales

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

    # =============================================================
    # CURRENT DECISIONS
    # =============================================================

    selected_ar_decision = (
        _selected_ar_decision()
    )

    selected_ap_decision = (
        _selected_ap_decision()
    )

    purchasing_decision = (
        _selected_purchasing_decision()
    )

    selected_ar_days = (
        _decision_ar_days(
            selected_ar_decision
        )
    )

    selected_ap_days = (
        _decision_ap_days(
            selected_ap_decision
        )
    )

    # =============================================================
    # INTRODUCTION
    # =============================================================

    st.info(
        """
        **Cash Management is the common timing layer.**

        Receivables determine when customer cash comes in.

        Purchasing determines what the company buys.

        Supplier terms determine when those purchases are paid.

        Cash Management combines these flows into one monthly
        cash position.
        """
    )

    # =============================================================
    # RECEIVABLES STATUS
    # =============================================================

    st.subheader(
        "Customer Collections"
    )

    if selected_ar_decision is not None:

        collection_schedule = (
            _extract_collection_schedule_from_decision(
                selected_ar_decision
            )
        )

        if collection_schedule is not None:

            st.success(
                "Customer collections are driven by the "
                "Receivables collection profile in the "
                "Current Decision Plan."
            )

        elif selected_ar_days is not None:

            st.warning(
                "A Receivables Decision is selected, but it "
                "does not contain a collection profile. "
                f"Cash Management is using {selected_ar_days:.0f} "
                "AR days as a timing fallback."
            )

    else:

        st.caption(
            "No Receivables Decision is currently selected. "
            "Cash Management is using the projected CompanyState "
            "as the fallback."
        )

    # =============================================================
    # SUPPLIER STATUS
    # =============================================================

    st.subheader(
        "Supplier Payments"
    )

    if selected_ap_decision is not None:

        if selected_ap_days is not None:

            st.success(
                "Supplier cash payments are driven by the "
                f"AP decision: {selected_ap_days:.0f} days."
            )

    else:

        st.caption(
            "No Supplier Decision is currently selected. "
            "Cash Management is using projected AP days."
        )

    # =============================================================
    # PURCHASING STATUS
    # =============================================================

    st.subheader(
        "Purchasing"
    )

    if purchasing_decision is not None:

        st.success(
            "A Purchasing / Inventory Decision is present "
            "in the Current Decision Plan. Supplier payments "
            "are using its purchase schedule."
        )

    else:

        st.caption(
            "Purchasing is currently represented by projected "
            "COGS spread across the six-month timing horizon. "
            "This is a temporary proxy until the Inventory / "
            "Purchasing Decision supplies actual purchase timing."
        )

    # =============================================================
    # KEY CASH METRICS
    # =============================================================

    st.divider()

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

    total_collections = float(
        df["Customer Collections"].sum()
    )

    total_supplier_payments = float(
        df["Supplier Payments"].sum()
    )

    col1, col2, col3, col4 = st.columns(4)

    with col1:

        st.metric(
            "Opening Cash",
            (
                f"€{float(df['Opening Cash'].iloc[0]):,.0f}"
            ),
        )

    with col2:

        st.metric(
            "Customer Collections",
            f"€{total_collections:,.0f}",
        )

    with col3:

        st.metric(
            "Supplier Payments",
            f"€{total_supplier_payments:,.0f}",
        )

    with col4:

        st.metric(
            "Minimum Cash",
            f"€{min_cash:,.0f}",
        )

    st.caption(
        f"Minimum cash occurs in {min_cash_month}. "
        f"Closing cash at the end of the horizon is "
        f"€{final_cash:,.0f}."
    )

    # =============================================================
    # CASH TABLE
    # =============================================================

    st.subheader(
        "Monthly Cash Flow"
    )

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
    # CASH CHART
    # =============================================================

    st.subheader(
        "Cash Position"
    )

    chart_df = df.set_index(
        "Month"
    )[[
        "Closing Cash"
    ]]

    st.line_chart(
        chart_df
    )

    # =============================================================
    # ASSUMPTIONS / DIAGNOSTICS
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
            "Suppliers:",
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
            f"{_as_float(df.attrs.get('baseline_ar_days')):.1f}",
        )

        st.write(
            "Projected AR days:",
            f"{_as_float(df.attrs.get('projected_ar_days')):.1f}",
        )

        st.write(
            "Baseline AP days:",
            f"{_as_float(df.attrs.get('baseline_ap_days')):.1f}",
        )

        st.write(
            "Projected AP days:",
            f"{_as_float(df.attrs.get('projected_ap_days')):.1f}",
        )

        st.write(
            "Baseline inventory days:",
            f"{_as_float(df.attrs.get('baseline_inventory_days')):.1f}",
        )

        st.write(
            "Projected inventory days:",
            f"{_as_float(df.attrs.get('projected_inventory_days')):.1f}",
        )

        st.write(
            "Opening AR:",
            f"€{_as_float(df.attrs.get('opening_ar_balance')):,.0f}",
        )

        st.write(
            "Opening AP:",
            f"€{_as_float(df.attrs.get('opening_ap_balance')):,.0f}",
        )

        monthly_purchases = df.attrs.get(
            "monthly_purchases",
            [],
        )

        if monthly_purchases:

            st.write(
                "Monthly purchasing amounts:"
            )

            purchases_df = pd.DataFrame(
                {
                    "Month": MONTHS,
                    "Purchases": (
                        list(
                            monthly_purchases
                        )[:len(MONTHS)]
                    ),
                }
            )

            purchases_df["Purchases"] = (
                purchases_df["Purchases"]
                .map(
                    lambda value:
                    f"€{value:,.0f}"
                )
            )

            st.dataframe(
                purchases_df,
                use_container_width=True,
                hide_index=True,
            )

        collection_schedule = df.attrs.get(
            "collection_schedule"
        )

        if collection_schedule is not None:

            st.write(
                "Customer collection profile:"
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
                            f"{collection_schedule[0] * 100:.1f}%"
                        ),
                        (
                            f"{collection_schedule[1] * 100:.1f}%"
                        ),
                        (
                            f"{collection_schedule[2] * 100:.1f}%"
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
                "The collection profile is applied separately "
                "to opening AR and to each new monthly sales cohort."
            )

        # ---------------------------------------------------------
        # CUSTOMER COLLECTION RECONCILIATION
        # ---------------------------------------------------------

        diagnostics = df.attrs.get(
            "collection_diagnostics"
        )

        if isinstance(
            diagnostics,
            Mapping,
        ):

            opening_component = (
                diagnostics.get(
                    "opening_ar_collections",
                    [],
                )
            )

            cohort_component = (
                diagnostics.get(
                    "sales_cohort_collections",
                    [],
                )
            )

            if (
                opening_component
                or cohort_component
            ):

                with st.expander(
                    "Customer collection reconciliation",
                    expanded=False,
                ):

                    reconciliation_rows = []

                    for index, month in enumerate(
                        MONTHS
                    ):

                        opening_amount = 0.0

                        if (
                            index
                            < len(
                                opening_component
                            )
                        ):

                            opening_amount = (
                                _as_float(
                                    opening_component[
                                        index
                                    ]
                                )
                            )

                        new_sales_amount = 0.0

                        if (
                            index
                            < len(
                                cohort_component
                            )
                        ):

                            for cohort in (
                                cohort_component
                            ):

                                if (
                                    index
                                    < len(
                                        cohort
                                    )
                                ):

                                    new_sales_amount += (
                                        _as_float(
                                            cohort[index]
                                        )
                                    )

                        total = (
                            opening_amount
                            + new_sales_amount
                        )

                        reconciliation_rows.append(
                            {
                                "Month": month,
                                "Opening AR Collections": (
                                    opening_amount
                                ),
                                "New Sales Collections": (
                                    new_sales_amount
                                ),
                                "Total Customer Collections": (
                                    total
                                ),
                            }
                        )

                    reconciliation_df = pd.DataFrame(
                        reconciliation_rows
                    )

                    for column in (
                        "Opening AR Collections",
                        "New Sales Collections",
                        "Total Customer Collections",
                    ):

                        reconciliation_df[column] = (
                            reconciliation_df[column]
                            .map(
                                lambda value:
                                f"€{value:,.0f}"
                            )
                        )

                    st.dataframe(
                        reconciliation_df,
                        use_container_width=True,
                        hide_index=True,
                    )

        # ---------------------------------------------------------
        # SUPPLIER PAYMENT RECONCILIATION
        # ---------------------------------------------------------

        supplier_diagnostics = df.attrs.get(
            "supplier_payment_diagnostics"
        )

        if isinstance(
            supplier_diagnostics,
            Mapping,
        ):

            supplier_purchases = (
                supplier_diagnostics.get(
                    "monthly_purchases",
                    [],
                )
            )

            supplier_payments = (
                supplier_diagnostics.get(
                    "supplier_payments",
                    [],
                )
            )

            ending_ap = (
                supplier_diagnostics.get(
                    "ending_ap",
                    [],
                )
            )

            if supplier_purchases:

                with st.expander(
                    "Supplier payment reconciliation",
                    expanded=False,
                ):

                    supplier_rows = []

                    for index, month in enumerate(
                        MONTHS
                    ):

                        purchases = (
                            _as_float(
                                supplier_purchases[index]
                                if index
                                < len(
                                    supplier_purchases
                                )
                                else 0.0
                            )
                        )

                        payments = (
                            _as_float(
                                supplier_payments[index]
                                if index
                                < len(
                                    supplier_payments
                                )
                                else 0.0
                            )
                        )

                        ap_balance = (
                            _as_float(
                                ending_ap[index]
                                if index
                                < len(
                                    ending_ap
                                )
                                else 0.0
                            )
                        )

                        supplier_rows.append(
                            {
                                "Month": month,
                                "Purchases": purchases,
                                "Supplier Payments": payments,
                                "Ending AP": ap_balance,
                            }
                        )

                    supplier_df = pd.DataFrame(
                        supplier_rows
                    )

                    for column in (
                        "Purchases",
                        "Supplier Payments",
                        "Ending AP",
                    ):

                        supplier_df[column] = (
                            supplier_df[column]
                            .map(
                                lambda value:
                                f"€{value:,.0f}"
                            )
                        )

                    st.dataframe(
                        supplier_df,
                        use_container_width=True,
                        hide_index=True,
                    )

                    st.caption(
                        "Purchases are the operating requirement. "
                        "Supplier payment terms determine when "
                        "those purchases become cash outflows."
                    )

    # =============================================================
    # EVENTS
    # =============================================================

    with st.expander(
        "Cash events",
        expanded=False,
    ):

        event_rows = []

        for event in result.events:

            event_rows.append(
                {
                    "Month": event.month,
                    "Event": event.label,
                    "Amount": (
                        f"€{event.amount:,.0f}"
                    ),
                    "Type": event.kind,
                }
            )

        if event_rows:

            st.dataframe(
                pd.DataFrame(
                    event_rows
                ),
                use_container_width=True,
                hide_index=True,
            )
