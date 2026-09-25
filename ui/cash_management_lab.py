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

    except (
        TypeError,
        ValueError,
        OverflowError,
    ):
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


def _get_projected_state() -> Any:
    return (
        st.session_state.get("projected_state")
        or st.session_state.get("company_state_projected")
    )


def _get_current_plan() -> Any:
    """
    IMPORTANT V2 CONNECTION

    Receivables Lab and Supplier Lab store the Current
    Decision Plan under:

        st.session_state["decision_plan"]

    Cash Management reads exactly the same object.
    """

    plan = st.session_state.get("decision_plan")

    if isinstance(plan, DecisionPlan):
        return plan

    plan = DecisionPlan.create(
        plan_id="main_plan",
        name="Current Decision Plan",
    )

    st.session_state.decision_plan = plan

    return plan


def _all_decisions(
    plan: Any,
) -> List[Any]:

    if plan is None:
        return []

    decisions = getattr(
        plan,
        "decisions",
        None,
    )

    if decisions is None:
        return []

    if isinstance(decisions, Mapping):
        return list(decisions.values())

    try:
        return list(decisions)
    except Exception:
        return []


def _decision_change(
    decision: Any,
) -> Any:

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

        # -------------------------------------------------
        # V2 decision objects created by DecisionFactory
        # -------------------------------------------------
        #
        # Supplier Lab creates IDs such as:
        #
        #     supplier_ap_a1b2c3d4
        #
        # and stores the actual AP change inside:
        #
        #     decision.changes["ap_days"]
        #
        # Receivables decisions can similarly carry
        # ar_days / collection timing inside .changes.
        #
        # Therefore candidate_key matching is supplemented
        # by the contents of .changes.
        # -------------------------------------------------

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

    decisions = _all_decisions(plan)

    decision = _find_decision(
        decisions,
        WC_AR_CANDIDATE,
    )

    if decision is not None:
        return decision

    return st.session_state.get(
        WC_AR_CANDIDATE
    )


def _selected_ap_decision() -> Any:

    plan = _get_current_plan()

    decisions = _all_decisions(plan)

    decision = _find_decision(
        decisions,
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

def _get_drivers(
    state: Any,
) -> Any:

    return _get_attr(
        state,
        ("drivers",),
        state,
    )


def _get_working_capital(
    state: Any,
) -> Any:

    return _get_attr(
        state,
        (
            "working_capital",
            "working_capital_policy",
        ),
        None,
    )


def _get_capital_structure(
    state: Any,
) -> Any:

    return _get_attr(
        state,
        ("capital_structure",),
        None,
    )


def _annual_revenue(
    state: Any,
) -> float:

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

    if (
        volume is not None
        and price is not None
    ):
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


def _annual_cogs(
    state: Any,
) -> float:

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

    if (
        volume is not None
        and variable_cost is not None
    ):
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


def _annual_fixed_opex(
    state: Any,
) -> float:

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


def _opening_cash(
    state: Any,
) -> float:

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


def _annual_debt_service(
    state: Any,
) -> float:

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


def _baseline_ar_days(
    state: Any,
) -> float:

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


def _baseline_ap_days(
    state: Any,
) -> float:

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
# BASELINE OPENING AP
# =========================================================

def _opening_ap(
    state: Any,
) -> float:
    """
    Opening Accounts Payable implied by the baseline
    purchasing requirement and baseline AP days.

    This mirrors the supplier logic:

        Opening AP
        = annual purchases × AP days / 365

    The current V2 CompanyState does not carry a separate
    opening AP euro balance, so it is inferred from the
    baseline operating model.
    """

    annual_cogs = _annual_cogs(state)

    baseline_ap_days = _baseline_ap_days(state)

    return max(
        0.0,
        annual_cogs
        * baseline_ap_days
        / 365.0,
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

    # -----------------------------------------------------
    # Direct decision attributes / keys
    # -----------------------------------------------------

    value = _get_attr(
        decision,
        names,
        None,
    )

    if value is not None:
        return value

    # -----------------------------------------------------
    # V2 DecisionFactory .changes
    # -----------------------------------------------------

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

    # -----------------------------------------------------
    # Decision change
    # -----------------------------------------------------

    change = _decision_change(decision)

    value = _get_attr(
        change,
        names,
        None,
    )

    if value is not None:
        return value

    # -----------------------------------------------------
    # Nested containers
    # -----------------------------------------------------

    containers = (
        _get_attr(
            decision,
            ("payload",),
            None,
        ),
        _get_attr(
            decision,
            ("parameters",),
            None,
        ),
        _get_attr(
            decision,
            ("params",),
            None,
        ),
        _get_attr(
            decision,
            ("metadata",),
            None,
        ),
        _get_attr(
            change,
            ("payload",),
            None,
        ),
        _get_attr(
            change,
            ("parameters",),
            None,
        ),
        _get_attr(
            change,
            ("params",),
            None,
        ),
        _get_attr(
            change,
            ("metadata",),
            None,
        ),
    )

    for container in containers:

        if not isinstance(
            container,
            Mapping,
        ):
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
    """
    Extract the Receivables collection schedule.

    Supported forms:

        month_0_pct
        month_1_pct
        month_2_pct

    or:

        month_0
        month_1
        month_2

    or nested inside:

        collection_schedule
        collection_profile
        collection_distribution
        collection_timing
        schedule

    The function also searches payload / parameters /
    params / metadata and V2 .changes.
    """

    if source is None:
        return None

    candidates: List[Any] = [
        source
    ]

    # V2 DecisionFactory stores decision parameters
    # inside .changes.
    changes = _get_attr(
        source,
        ("changes",),
        None,
    )

    if changes is not None:
        candidates.append(changes)

    change = _decision_change(
        source
    )

    if change is not None:
        candidates.append(change)

    original_candidates = list(
        candidates
    )

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
                candidates.append(
                    container
                )

    # -----------------------------------------------------
    # Structured profile
    # -----------------------------------------------------

    structured_names = (
        "collection_schedule",
        "collection_profile",
        "collection_distribution",
        "collection_timing",
        "schedule",
    )

    for obj in candidates:

        if not isinstance(
            obj,
            Mapping,
        ):
            continue

        for name in structured_names:

            nested = obj.get(name)

            if isinstance(
                nested,
                Mapping,
            ):

                result = (
                    _extract_collection_profile(
                        nested
                    )
                )

                if result:
                    return result

    # -----------------------------------------------------
    # Flat profile
    # -----------------------------------------------------

    result: Dict[int, float] = {}

    for month_index in range(0, 6):

        possible_keys = (
            f"month_{month_index}_pct",
            f"month_{month_index}",
            f"month{month_index}_pct",
            f"month{month_index}",
        )

        found = None

        for obj in candidates:

            if isinstance(
                obj,
                Mapping,
            ):

                for key in possible_keys:

                    if key in obj:

                        found = obj[key]
                        break

            if found is not None:
                break

            for key in possible_keys:

                value = _get_attr(
                    obj,
                    (key,),
                    None,
                )

                if value is not None:

                    found = value
                    break

            if found is not None:
                break

        if found is not None:

            result[
                month_index
            ] = _normalise_pct(
                found
            )

    if not result:
        return None

    result = {
        index: value
        for index, value in result.items()
        if value >= 0
    }

    if not result:
        return None

    total = sum(
        result.values()
    )

    if total <= 0:
        return None

    # Normalise rounding differences.
    result = {
        index: value / total
        for index, value in result.items()
    }

    return result


def _get_collection_profile(
    decision: Any,
) -> Optional[Dict[int, float]]:
    """
    Read collection timing from:

    1. Current Decision Plan
    2. AR candidate
    3. AR candidate metadata

    This means the Cash Management Lab does not require
    the decision to be locked before it can simulate it.
    """

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
# MONTHLY TIMING
# =========================================================

def _monthly_delay_allocation(
    days: float,
) -> Dict[int, float]:
    """
    Timing convention:

        0 days  -> same month
        30 days -> next month
        45 days -> 50% next month + 50% month +2
        60 days -> month +2
        90 days -> month +3

    Uses 30-day months intentionally.
    """

    days = max(
        0.0,
        _to_float(days),
    )

    months = days / 30.0

    lower = int(months)

    fraction = (
        months - lower
    )

    if fraction <= 0:
        return {
            lower: 1.0
        }

    return {
        lower: 1.0 - fraction,
        lower + 1: fraction,
    }


# =========================================================
# COLLECTION BY PROFILE
# =========================================================

def _collections_from_profile(
    monthly_sales: Sequence[float],
    profile: Mapping[int, float],
    opening_ar: float = 0.0,
) -> List[float]:
    """
    Cohort-based collection model.

    Example 20 / 70 / 10:

        Month 1:
            20% of Month 1 sales
            + 20% of opening AR

        Month 2:
            70% of Month 1 sales
            + 20% of Month 2 sales
            + 70% of opening AR

        Month 3:
            10% of Month 1 sales
            + 70% of Month 2 sales
            + 20% of Month 3 sales
            + 10% of opening AR
    """

    horizon = len(
        monthly_sales
    )

    receipts = [
        0.0
        for _ in range(horizon)
    ]

    # -----------------------------------------------------
    # OPENING AR
    # -----------------------------------------------------

    for delay, percentage in profile.items():

        target_month = int(
            delay
        )

        if (
            0 <= target_month
            < horizon
        ):

            receipts[
                target_month
            ] += (
                opening_ar
                * percentage
            )

    # -----------------------------------------------------
    # MONTHLY SALES COHORTS
    # -----------------------------------------------------

    for cohort_month, sales in enumerate(
        monthly_sales
    ):

        for delay, percentage in profile.items():

            target_month = (
                cohort_month
                + int(delay)
            )

            if (
                0 <= target_month
                < horizon
            ):

                receipts[
                    target_month
                ] += (
                    sales
                    * percentage
                )

    return receipts


# =========================================================
# RECEIPTS
# =========================================================

def _build_receipts(
    baseline_state: Any,
    ar_decision: Any,
    monthly_sales: Sequence[float],
) -> List[float]:

    profile = _get_collection_profile(
        ar_decision
    )

    annual_revenue = _annual_revenue(
        baseline_state
    )

    # Opening receivables belong to the baseline.
    # The new AR decision does not rewrite the opening balance.
    opening_ar = (
        annual_revenue
        * _baseline_ar_days(
            baseline_state
        )
        / 365.0
    )

    # -----------------------------------------------------
    # EXPLICIT RECEIVABLES COLLECTION PROFILE
    # -----------------------------------------------------

    if profile:

        return _collections_from_profile(
            monthly_sales=monthly_sales,
            profile=profile,
            opening_ar=opening_ar,
        )

    # -----------------------------------------------------
    # FALLBACK: AR DAYS
    # -----------------------------------------------------

    ar_days = _decision_ar_days(
        baseline_state,
        ar_decision,
    )

    allocation = _monthly_delay_allocation(
        ar_days
    )

    receipts = [
        0.0
        for _ in monthly_sales
    ]

    # Opening AR
    for delay, percentage in allocation.items():

        target_month = int(
            delay
        )

        if (
            0 <= target_month
            < len(receipts)
        ):

            receipts[
                target_month
            ] += (
                opening_ar
                * percentage
            )

    # New sales cohorts
    for cohort_month, sales in enumerate(
        monthly_sales
    ):

        for delay, percentage in allocation.items():

            target_month = (
                cohort_month
                + int(delay)
            )

            if (
                0 <= target_month
                < len(receipts)
            ):

                receipts[
                    target_month
                ] += (
                    sales
                    * percentage
                )

    return receipts


# =========================================================
# SUPPLIER PAYMENTS
# =========================================================

def _build_supplier_payments(
    baseline_state: Any,
    ap_decision: Any,
    monthly_purchases: Sequence[float],
) -> List[float]:
    """
    Build supplier cash payments from:

        1. Opening AP
        2. New monthly purchase cohorts
        3. Selected AP payment terms

    Opening AP is paid in Month 1, matching the Supplier Lab.

    New purchases are paid according to the selected AP days.

    This keeps Cash Management as the timing layer rather than
    creating a second supplier model.
    """

    ap_days = _decision_ap_days(
        baseline_state,
        ap_decision,
    )

    allocation = _monthly_delay_allocation(
        ap_days
    )

    payments = [
        0.0
        for _ in monthly_purchases
    ]

    # -----------------------------------------------------
    # OPENING AP
    # -----------------------------------------------------
    #
    # Opening AP is an existing obligation from the baseline.
    # It is paid during Month 1.
    # -----------------------------------------------------

    opening_ap = _opening_ap(
        baseline_state
    )

    if payments:
        payments[0] += opening_ap

    # -----------------------------------------------------
    # NEW PURCHASE COHORTS
    # -----------------------------------------------------

    for cohort_month, purchases in enumerate(
        monthly_purchases
    ):

        for delay, percentage in allocation.items():

            target_month = (
                cohort_month
                + int(delay)
            )

            if (
                0 <= target_month
                < len(payments)
            ):

                payments[
                    target_month
                ] += (
                    purchases
                    * percentage
                )

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
) -> Dict[str, List[float]]:

    annual_revenue = _annual_revenue(
        baseline_state
    )

    annual_cogs = _annual_cogs(
        baseline_state
    )

    # -----------------------------------------------------
    # MONTHLY SALES
    # -----------------------------------------------------

    monthly_sales = [
        annual_revenue / 12.0
        for _ in MONTHS
    ]

    # -----------------------------------------------------
    # MONTHLY PURCHASE PROXY
    #
    # Until a formal purchasing decision exists,
    # purchases are represented by monthly COGS.
    # -----------------------------------------------------

    monthly_purchases = [
        annual_cogs / 12.0
        for _ in MONTHS
    ]

    # -----------------------------------------------------
    # RECEIPTS
    # -----------------------------------------------------

    receipts = _build_receipts(
        baseline_state=baseline_state,
        ar_decision=ar_decision,
        monthly_sales=monthly_sales,
    )

    # -----------------------------------------------------
    # SUPPLIER PAYMENTS
    # -----------------------------------------------------

    supplier_payments = (
        _build_supplier_payments(
            baseline_state=baseline_state,
            ap_decision=ap_decision,
            monthly_purchases=monthly_purchases,
        )
    )

    # -----------------------------------------------------
    # OPERATING EXPENSES
    # -----------------------------------------------------

    operating_expenses = [
        monthly_opex
        for _ in MONTHS
    ]

    # -----------------------------------------------------
    # DEBT
    # -----------------------------------------------------

    debt_payments = [
        monthly_debt
        for _ in MONTHS
    ]

    # -----------------------------------------------------
    # CASH
    # -----------------------------------------------------

    net_cash_flow = []

    ending_cash = []

    cash = _opening_cash(
        baseline_state
    )

    for month_index in range(
        len(MONTHS)
    ):

        net = (
            receipts[month_index]
            - supplier_payments[
                month_index
            ]
            - operating_expenses[
                month_index
            ]
            - debt_payments[
                month_index
            ]
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
# UI
# =========================================================

def render_cash_management_lab(
    baseline_state: Any = None,
) -> None:

    if baseline_state is None:
        baseline_state = _get_baseline_state()

    if baseline_state is None:

        st.warning(
            "Baseline company state is not available."
        )

        return

    # =====================================================
    # READ CURRENT DECISIONS
    # =====================================================

    ar_decision = _selected_ar_decision()

    ap_decision = _selected_ap_decision()

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
                default_monthly_opex
            ),
            step=1000.0,
            format="%.0f",
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
                default_monthly_debt
            ),
            step=1000.0,
            format="%.0f",
        )

    minimum_cash = st.number_input(
        "Minimum cash reserve to maintain",
        min_value=0.0,
        value=0.0,
        step=5000.0,
        format="%.0f",
        help=(
            "Cash level you want to keep available at all times."
        ),
    )

    # =====================================================
    # CURRENT POLICIES
    # =====================================================

    current_ar_days = _decision_ar_days(
        baseline_state,
        ar_decision,
    )

    current_ap_days = _decision_ap_days(
        baseline_state,
        ap_decision,
    )

    collection_profile = (
        _get_collection_profile(
            ar_decision
        )
    )

    # -----------------------------------------------------
    # SHOW RECEIVABLES TIMING
    # -----------------------------------------------------

    if collection_profile:

        profile_text = " / ".join(
            f"Month {int(delay) + 1}: {percentage:.0%}"
            for delay, percentage
            in sorted(
                collection_profile.items()
            )
        )

        st.success(
            f"Collection timing from Receivables Decision: "
            f"{profile_text}"
        )

    else:

        st.caption(
            "Collection timing: "
            f"approximately {current_ar_days:.0f} days"
        )

    # -----------------------------------------------------
    # SHOW S
