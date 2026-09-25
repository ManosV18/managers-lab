from __future__ import annotations

from typing import Any, Dict, List, Mapping, Optional, Sequence, Tuple

import pandas as pd
import streamlit as st


# =========================================================
# CONSTANTS
# =========================================================

MONTHS = [f"Month {i}" for i in range(1, 7)]

WC_AR_CANDIDATE = "wc_ar_candidate"
WC_AP_CANDIDATE = "wc_ap_candidate"


# =========================================================
# GENERIC HELPERS
# =========================================================

def _get_attr(obj: Any, *names: str, default: Any = None) -> Any:
    """Read the first available attribute/key from an object or mapping."""
    if obj is None:
        return default

    for name in names:
        if isinstance(obj, Mapping) and name in obj:
            return obj[name]

        try:
            value = getattr(obj, name)
        except Exception:
            value = None

        if value is not None:
            return value

    return default


def _to_float(value: Any, default: float = 0.0) -> float:
    try:
        if value is None:
            return default
        return float(value)
    except (TypeError, ValueError):
        return default


def _money(value: float) -> str:
    return f"€{value:,.0f}"


# =========================================================
# STATE HELPERS
# =========================================================

def _get_baseline_state() -> Any:
    """
    Try to retrieve the canonical baseline CompanyState from the
    existing Managers Lab V2 repositories/session state.
    """
    # First try common session-state locations.
    for key in (
        "baseline_state",
        "locked_baseline_state",
        "company_state",
    ):
        value = st.session_state.get(key)
        if value is not None:
            return value

    # Then try the canonical repository used by V2.
    try:
        from core.baseline import BaselineRepository

        repo = BaselineRepository()
        for method_name in ("get_baseline", "load", "current"):
            method = getattr(repo, method_name, None)
            if callable(method):
                try:
                    value = method()
                    if value is not None:
                        return value
                except Exception:
                    pass
    except Exception:
        pass

    return None


def _get_projected_state() -> Any:
    """
    Retrieve projected CompanyState if another V2 component has already
    created one. Otherwise return None.
    """
    for key in (
        "projected_state",
        "current_projected_state",
    ):
        value = st.session_state.get(key)
        if value is not None:
            return value

    return None


def _get_current_plan() -> Any:
    """
    Read the Current Decision Plan without creating a second architecture.
    """
    try:
        from core.decision_plan import DecisionPlan

        # Existing V2 convention.
        return DecisionPlan.create(
            plan_id="main_plan",
            name="Current Decision Plan",
        )
    except Exception:
        return None


def _all_decisions(plan: Any) -> List[Any]:
    if plan is None:
        return []

    for attr in (
        "decisions",
        "items",
        "active_decisions",
    ):
        value = _get_attr(plan, attr, default=None)

        if value is None:
            continue

        if isinstance(value, Mapping):
            return list(value.values())

        if isinstance(value, Sequence) and not isinstance(
            value, (str, bytes)
        ):
            return list(value)

    return []


def _decision_change(decision: Any) -> str:
    return str(
        _get_attr(
            decision,
            "change",
            "change_type",
            "type",
            "decision_type",
            default="",
        )
        or ""
    ).lower()


def _find_decision(
    plan: Any,
    keywords: Sequence[str],
) -> Optional[Any]:
    decisions = _all_decisions(plan)

    for decision in decisions:
        change = _decision_change(decision)

        if any(keyword.lower() in change for keyword in keywords):
            return decision

    return None


def _selected_ar_decision(plan: Any) -> Optional[Any]:
    return _find_decision(
        plan,
        (
            "ar_days",
            "receivable",
            "collection",
            "customer_credit",
        ),
    )


def _selected_ap_decision(plan: Any) -> Optional[Any]:
    return _find_decision(
        plan,
        (
            "ap_days",
            "payable",
            "supplier_credit",
        ),
    )


# =========================================================
# COMPANY ECONOMICS
# =========================================================

def _get_drivers(state: Any) -> Any:
    return _get_attr(state, "drivers", default=None)


def _get_working_capital(state: Any) -> Any:
    return _get_attr(state, "working_capital", default=None)


def _get_capital_structure(state: Any) -> Any:
    return _get_attr(state, "capital_structure", default=None)


def _annual_revenue(state: Any) -> float:
    drivers = _get_drivers(state)

    direct_revenue = _get_attr(
        drivers,
        "annual_revenue",
        default=None,
    )

    if direct_revenue is not None:
        return _to_float(direct_revenue)

    price = _to_float(
        _get_attr(
            drivers,
            "price",
            default=_get_attr(state, "price", default=0),
        )
    )

    volume = _to_float(
        _get_attr(
            drivers,
            "volume",
            default=_get_attr(state, "volume", default=0),
        )
    )

    return price * volume


def _annual_cogs(state: Any) -> float:
    drivers = _get_drivers(state)

    direct_cogs = _get_attr(
        drivers,
        "annual_cogs",
        "cogs",
        default=None,
    )

    if direct_cogs is not None:
        return _to_float(direct_cogs)

    variable_cost = _to_float(
        _get_attr(
            drivers,
            "variable_cost_per_unit",
            default=_get_attr(
                state,
                "variable_cost_per_unit",
                default=0,
            ),
        )
    )

    volume = _to_float(
        _get_attr(
            drivers,
            "volume",
            default=_get_attr(state, "volume", default=0),
        )
    )

    return variable_cost * volume


def _annual_fixed_opex(state: Any) -> float:
    drivers = _get_drivers(state)

    value = _get_attr(
        drivers,
        "fixed_opex",
        default=_get_attr(
            state,
            "fixed_opex",
            default=0,
        ),
    )

    return _to_float(value)


def _opening_cash(state: Any) -> float:
    drivers = _get_drivers(state)

    value = _get_attr(
        drivers,
        "opening_cash",
        default=_get_attr(
            state,
            "opening_cash",
            default=0,
        ),
    )

    return _to_float(value)


def _annual_debt_service(state: Any) -> float:
    capital = _get_capital_structure(state)

    value = _get_attr(
        capital,
        "annual_debt_service",
        default=_get_attr(
            state,
            "annual_debt_service",
            default=0,
        ),
    )

    return _to_float(value)


def _baseline_ar_days(state: Any) -> float:
    wc = _get_working_capital(state)

    return _to_float(
        _get_attr(
            wc,
            "ar_days",
            default=_get_attr(
                state,
                "ar_days",
                default=0,
            ),
        )
    )


def _baseline_ap_days(state: Any) -> float:
    wc = _get_working_capital(state)

    return _to_float(
        _get_attr(
            wc,
            "ap_days",
            default=_get_attr(
                state,
                "ap_days",
                default=0,
            ),
        )
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

    for name in names:
        value = _get_attr(decision, name, default=None)

        if value is not None:
            return value

    # Some decision implementations store values in payload/parameters.
    payload = _get_attr(
        decision,
        "payload",
        "parameters",
        "params",
        "metadata",
        default=None,
    )

    if isinstance(payload, Mapping):
        for name in names:
            if name in payload:
                return payload[name]

    return default


def _decision_ar_days(
    baseline_state: Any,
    plan: Any,
) -> float:
    decision = _selected_ar_decision(plan)

    value = _decision_value(
        decision,
        (
            "target_ar_days",
            "ar_days",
            "new_ar_days",
        ),
        default=None,
    )

    if value is None:
        candidate = st.session_state.get(WC_AR_CANDIDATE)

        value = _decision_value(
            candidate,
            (
                "target_ar_days",
                "ar_days",
                "new_ar_days",
            ),
            default=None,
        )

    if value is None:
        return _baseline_ar_days(baseline_state)

    return _to_float(value, _baseline_ar_days(baseline_state))


def _decision_ap_days(
    baseline_state: Any,
    plan: Any,
) -> float:
    decision = _selected_ap_decision(plan)

    value = _decision_value(
        decision,
        (
            "target_ap_days",
            "ap_days",
            "new_ap_days",
        ),
        default=None,
    )

    if value is None:
        candidate = st.session_state.get(WC_AP_CANDIDATE)

        value = _decision_value(
            candidate,
            (
                "target_ap_days",
                "ap_days",
                "new_ap_days",
            ),
            default=None,
        )

    if value is None:
        return _baseline_ap_days(baseline_state)

    return _to_float(value, _baseline_ap_days(baseline_state))


# =========================================================
# MONTHLY TIMING
# =========================================================

def _monthly_delay_allocation(days: float) -> List[Tuple[int, float]]:
    """
    Simple owner-manager monthly convention.

    0 days  -> same month
    30 days -> next month
    45 days -> 50% next month + 50% month +2
    60 days -> month +2
    90 days -> month +3

    This intentionally avoids calendar-day precision.
    """

    days = max(0.0, float(days))

    if days <= 0:
        return [(0, 1.0)]

    # Each 30-day block represents one month.
    month_delay = days / 30.0

    whole = int(month_delay)
    fraction = month_delay - whole

    if fraction <= 0:
        return [(whole, 1.0)]

    return [
        (whole, 1.0 - fraction),
        (whole + 1, fraction),
    ]


def _allocate_cohort(
    monthly_values: Sequence[float],
    delay_days: float,
    horizon: int = 6,
) -> List[float]:
    """
    Allocate each monthly cohort according to the selected payment delay.

    Amounts falling beyond the six-month horizon are simply not shown.
    """

    result = [0.0] * horizon
    allocation = _monthly_delay_allocation(delay_days)

    for cohort_month, amount in enumerate(monthly_values):
        for delay_months, percentage in allocation:
            target_month = cohort_month + delay_months

            if 0 <= target_month < horizon:
                result[target_month] += amount * percentage

    return result


# =========================================================
# RECEIPTS
# =========================================================

def _get_collection_profile(
    decision: Any,
) -> Optional[Dict[int, float]]:
    """
    Receivables Lab can provide an explicit collection profile.

    Example:
        Month 0 = 20%
        Month 1 = 70%
        Month 2 = 10%

    If no explicit profile exists, Cash Management falls back to
    the selected AR days.
    """

    if decision is None:
        return None

    profile = _decision_value(
        decision,
        (
            "collection_schedule",
            "collection_profile",
            "collection_distribution",
            "schedule",
        ),
        default=None,
    )

    if not isinstance(profile, Mapping):
        return None

    result: Dict[int, float] = {}

    for key, value in profile.items():
        try:
            if isinstance(key, str):
                cleaned = (
                    key.lower()
                    .replace("month_", "")
                    .replace("month", "")
                    .strip()
                )
                offset = int(cleaned)
            else:
                offset = int(key)

            result[offset] = _to_float(value)

        except (TypeError, ValueError):
            continue

    if not result:
        return None

    total = sum(result.values())

    if total <= 0:
        return None

    # Normalize percentages if supplied as 20/70/10 instead of
    # 0.20/0.70/0.10.
    if total > 1.000001:
        result = {
            key: value / 100.0
            for key, value in result.items()
        }

    return result


def _collections_from_profile(
    monthly_sales: Sequence[float],
    profile: Mapping[int, float],
    horizon: int = 6,
) -> List[float]:
    result = [0.0] * horizon

    for cohort_month, sales in enumerate(monthly_sales):
        for offset, percentage in profile.items():
            target_month = cohort_month + int(offset)

            if 0 <= target_month < horizon:
                result[target_month] += sales * percentage

    return result


def _build_receipts(
    baseline_state: Any,
    projected_state: Any,
    plan: Any,
    horizon: int = 6,
) -> List[float]:
    """
    Receipts consist of:

    1. opening receivables collected according to the selected
       collection policy / AR days;
    2. collections from the six new monthly sales cohorts.

    No separate AR reconciliation table is exposed to the user.
    """

    state = projected_state or baseline_state

    annual_revenue = _annual_revenue(state)
    monthly_sales = [annual_revenue / 12.0] * horizon

    ar_decision = _selected_ar_decision(plan)

    profile = _get_collection_profile(ar_decision)

    if profile is not None:
        new_sales_receipts = _collections_from_profile(
            monthly_sales,
            profile,
            horizon,
        )
    else:
        ar_days = _decision_ar_days(
            baseline_state,
            plan,
        )

        new_sales_receipts = _allocate_cohort(
            monthly_sales,
            ar_days,
            horizon,
        )

    # Opening AR.
    #
    # Approximation:
    # opening AR = annual revenue * AR days / 365.
    #
    # This is the same working-capital convention used by the
    # financial engine. Only the timing is expanded here.
    opening_ar = (
        annual_revenue
        * _decision_ar_days(baseline_state, plan)
        / 365.0
    )

    opening_ar_receipts = [0.0] * horizon

    if profile is not None:
        # For an explicit collection profile we use the profile
        # starting from Month 1.
        for offset, percentage in profile.items():
            target_month = int(offset)

            if 0 <= target_month < horizon:
                opening_ar_receipts[target_month] += (
                    opening_ar * percentage
                )
    else:
        allocation = _monthly_delay_allocation(
            _decision_ar_days(
                baseline_state,
                plan,
            )
        )

        for offset, percentage in allocation:
            if 0 <= offset < horizon:
                opening_ar_receipts[offset] += (
                    opening_ar * percentage
                )

    return [
        new_sales_receipts[i] + opening_ar_receipts[i]
        for i in range(horizon)
    ]


# =========================================================
# SUPPLIER PAYMENTS
# =========================================================

def _build_supplier_payments(
    baseline_state: Any,
    projected_state: Any,
    plan: Any,
    horizon: int = 6,
) -> List[float]:
    """
    Monthly purchasing proxy = projected annual COGS / 12.

    No purchasing schedule is required unless a separate decision
    explicitly changes purchasing. The Supplier Lab controls the
    payment timing through AP days.
    """

    state = projected_state or baseline_state

    annual_cogs = _annual_cogs(state)
    monthly_purchases = [annual_cogs / 12.0] * horizon

    ap_days = _decision_ap_days(
        baseline_state,
        plan,
    )

    # Opening AP:
    # approximate opening supplier balance using annual COGS and
    # selected AP days, consistent with the working-capital formula.
    opening_ap = annual_cogs * ap_days / 365.0

    result = _allocate_cohort(
        monthly_purchases,
        ap_days,
        horizon,
    )

    opening_ap_payments = [0.0] * horizon

    for offset, percentage in _monthly_delay_allocation(ap_days):
        if 0 <= offset < horizon:
            opening_ap_payments[offset] += (
                opening_ap * percentage
            )

    return [
        result[i] + opening_ap_payments[i]
        for i in range(horizon)
    ]


# =========================================================
# CASH PLAN
# =========================================================

def _build_cash_plan(
    opening_cash: float,
    receipts: Sequence[float],
    supplier_payments: Sequence[float],
    operating_expenses: Sequence[float],
    debt_payments: Sequence[float],
) -> Dict[str, List[float]]:
    net_cash_flow: List[float] = []
    ending_cash: List[float] = []

    cash = float(opening_cash)

    for i in range(len(receipts)):
        net = (
            receipts[i]
            - supplier_payments[i]
            - operating_expenses[i]
            - debt_payments[i]
        )

        cash += net

        net_cash_flow.append(net)
        ending_cash.append(cash)

    return {
        "receipts": list(receipts),
        "supplier_payments": list(supplier_payments),
        "operating_expenses": list(operating_expenses),
        "debt_payments": list(debt_payments),
        "net_cash_flow": net_cash_flow,
        "ending_cash": ending_cash,
    }


# =========================================================
# MAIN UI
# =========================================================

def render_cash_management_lab(
    baseline_state: Any = None,
) -> None:
    """
    Managers Lab V2 — Cash Management.

    Purpose:
        Show the owner-manager the six-month cash position in one
        simple table.

    The underlying timing logic remains connected to:
        Receivables Lab
        Supplier Lab
        Current Decision Plan

    The UI intentionally does NOT expose:
        - collection reconciliation tables
        - supplier reconciliation tables
        - purchasing tables
        - cash-event tables
        - AR/AP diagnostic tables
        - inventory schedules
        - detailed accounting reports
    """

    st.subheader("Cash Management")

    if baseline_state is None:
        baseline_state = _get_baseline_state()

    if baseline_state is None:
        st.warning(
            "Δεν υπάρχει διαθέσιμο CompanyState για να δημιουργηθεί "
            "η πρόβλεψη ταμείου."
        )
        return

    projected_state = _get_projected_state()
    state_for_defaults = projected_state or baseline_state

    plan = _get_current_plan()

    # -----------------------------------------------------
    # BASIC DEFAULTS
    # -----------------------------------------------------

    opening_cash = _opening_cash(baseline_state)

    annual_fixed_opex = _annual_fixed_opex(state_for_defaults)
    default_monthly_opex = annual_fixed_opex / 12.0

    annual_debt_service = _annual_debt_service(
        state_for_defaults
    )
    default_monthly_debt = annual_debt_service / 12.0

    # -----------------------------------------------------
    # SIMPLE USER INPUTS
    # -----------------------------------------------------

    st.markdown("### Cash assumptions")

    col1, col2 = st.columns(2)

    with col1:
        monthly_opex = st.number_input(
            "Μέσο μηνιαίο λειτουργικό κόστος",
            min_value=0.0,
            value=float(default_monthly_opex),
            step=1000.0,
            help=(
                "Αφήστε το ποσό όπως είναι για να χρησιμοποιηθεί "
                "ο μέσος όρος των λειτουργικών εξόδων της εταιρείας. "
                "Αλλάξτε το μόνο αν θέλετε διαφορετικό μηνιαίο ποσό."
            ),
        )

    with col2:
        monthly_debt = st.number_input(
            "Μηνιαίες δόσεις δανείων & τόκοι",
            min_value=0.0,
            value=float(default_monthly_debt),
            step=1000.0,
            help=(
                "Ένα συνολικό ποσό για όλα τα δάνεια μαζί — "
                "κεφάλαιο και τόκοι."
            ),
        )

    minimum_cash = st.number_input(
        "Ελάχιστα διαθέσιμα που θέλω να κρατάω στο ταμείο",
        min_value=0.0,
        value=0.0,
        step=1000.0,
        help=(
            "Το ελάχιστο ποσό μετρητών που θέλετε να παραμένει "
            "διαθέσιμο στο τέλος κάθε μήνα."
        ),
    )

    # -----------------------------------------------------
    # BUILD MONTHLY CASH FLOWS
    # -----------------------------------------------------

    receipts = _build_receipts(
        baseline_state=baseline_state,
        projected_state=projected_state,
        plan=plan,
        horizon=6,
    )

    supplier_payments = _build_supplier_payments(
        baseline_state=baseline_state,
        projected_state=projected_state,
        plan=plan,
        horizon=6,
    )

    operating_expenses = [
        float(monthly_opex)
        for _ in range(6)
    ]

    debt_payments = [
        float(monthly_debt)
        for _ in range(6)
    ]

    cash_plan = _build_cash_plan(
        opening_cash=opening_cash,
        receipts=receipts,
        supplier_payments=supplier_payments,
        operating_expenses=operating_expenses,
        debt_payments=debt_payments,
    )

    ending_cash = cash_plan["ending_cash"]
    net_cash_flow = cash_plan["net_cash_flow"]

    minimum_projected_cash = min(ending_cash)

    minimum_month_index = ending_cash.index(
        minimum_projected_cash
    )

    minimum_month = MONTHS[minimum_month_index]

    funding_required = max(
        0.0,
        minimum_cash - minimum_projected_cash,
    )

    surplus_above_minimum = max(
        0.0,
        minimum_projected_cash - minimum_cash,
    )

    # -----------------------------------------------------
    # KEY RESULT
    # -----------------------------------------------------

    st.markdown("### Six-month cash outlook")

    st.caption(
        f"Opening cash: {_money(opening_cash)}"
    )

    # -----------------------------------------------------
    # ONE TABLE
    # -----------------------------------------------------

    table = pd.DataFrame(
        {
            "Εισπράξεις": cash_plan["receipts"],
            "Πληρωμές προμηθευτών": cash_plan[
                "supplier_payments"
            ],
            "Λειτουργικά έξοδα": cash_plan[
                "operating_expenses"
            ],
            "Δόσεις δανείων & τόκοι": cash_plan[
                "debt_payments"
            ],
            "Καθαρή ταμειακή ροή": cash_plan[
                "net_cash_flow"
            ],
            "Διαθέσιμα τέλους μήνα": cash_plan[
                "ending_cash"
            ],
        },
        index=MONTHS,
    ).T

    formatted_table = table.map(
        lambda value: _money(float(value))
    )

    st.dataframe(
        formatted_table,
        use_container_width=True,
        height=300,
    )

    # -----------------------------------------------------
    # RESULT
    # -----------------------------------------------------

    st.markdown("### What does this mean?")

    result_col1, result_col2, result_col3 = st.columns(3)

    with result_col1:
        st.metric(
            "Χαμηλότερο ταμείο",
            _money(minimum_projected_cash),
            minimum_month,
        )

    with result_col2:
        st.metric(
            "Πάνω από το ελάχιστο",
            _money(surplus_above_minimum),
        )

    with result_col3:
        st.metric(
            "Χρηματοδότηση που χρειάζεται",
            _money(funding_required),
        )

    # -----------------------------------------------------
    # OWNER-MANAGER INTERPRETATION
    # -----------------------------------------------------

    if funding_required > 0:
        st.error(
            f"Χρειάζεται επιπλέον χρηματοδότηση "
            f"{_money(funding_required)} ώστε το ταμείο να "
            f"μην πέσει κάτω από {_money(minimum_cash)}. "
            f"Το χαμηλότερο σημείο εμφανίζεται στον "
            f"{minimum_month}."
        )

    else:
        st.success(
            f"Δεν προκύπτει χρηματοδοτικό κενό. "
            f"Το χαμηλότερο ταμείο είναι "
            f"{_money(minimum_projected_cash)}, δηλαδή "
            f"{_money(surplus_above_minimum)} πάνω από το "
            f"ελάχιστο που θέλετε να κρατάτε."
        )

    # -----------------------------------------------------
    # SMALL ASSUMPTION LINE
    # -----------------------------------------------------

    ar_days = _decision_ar_days(
        baseline_state,
        plan,
    )

    ap_days = _decision_ap_days(
        baseline_state,
        plan,
    )

    st.caption(
        f"Η πρόβλεψη χρησιμοποιεί τις τρέχουσες αποφάσεις "
        f"Receivables / Suppliers: εισπράξεις με βάση "
        f"{ar_days:.0f} ημέρες και πληρωμές προμηθευτών με βάση "
        f"{ap_days:.0f} ημέρες."
    )
