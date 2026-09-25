from __future__ import annotations

from typing import Any, Dict, Iterable, List, Mapping, Optional, Sequence, Tuple

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

def _get_attr(obj: Any, names: Sequence[str], default: Any = None) -> Any:
    """
    Read the first available attribute/key from an object or mapping.
    """
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


def _to_float(value: Any, default: float = 0.0) -> float:
    try:
        if value is None:
            return default

        if isinstance(value, str):
            value = value.replace(",", "").replace("€", "").strip()

        return float(value)
    except (TypeError, ValueError, OverflowError):
        return default


def _money(value: Any) -> str:
    return f"€{_to_float(value):,.0f}"


def _normalise_pct(value: Any) -> float:
    """
    Convert either:
        0.20 -> 0.20
        20   -> 0.20
    """
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
    Current Decision Plan — V2 architecture.
    """
    plan = st.session_state.get("decision_plan")

    if plan is not None:
        return plan

    try:
        plan = DecisionPlan.create(
            plan_id="main_plan",
            name="Current Decision Plan",
        )
    except Exception:
        try:
            plan = DecisionPlan(
                plan_id="main_plan",
                name="Current Decision Plan",
            )
        except Exception:
            plan = None

    if plan is not None:
        st.session_state["decision_plan"] = plan

    return plan


def _all_decisions(plan: Any) -> List[Any]:
    if plan is None:
        return []

    for name in (
        "decisions",
        "items",
        "decision_items",
        "active_decisions",
    ):
        value = _get_attr(plan, (name,), None)

        if value is None:
            continue

        if isinstance(value, Mapping):
            return list(value.values())

        try:
            return list(value)
        except Exception:
            pass

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

    return None


def _selected_ar_decision() -> Any:
    plan = _get_current_plan()
    decisions = _all_decisions(plan)

    decision = _find_decision(decisions, WC_AR_CANDIDATE)

    if decision is not None:
        return decision

    # Candidate is kept as a fallback because the Receivables Lab
    # may have stored the detailed collection profile there.
    return st.session_state.get(WC_AR_CANDIDATE)


def _selected_ap_decision() -> Any:
    plan = _get_current_plan()
    decisions = _all_decisions(plan)

    decision = _find_decision(decisions, WC_AP_CANDIDATE)

    if decision is not None:
        return decision

    return st.session_state.get(WC_AP_CANDIDATE)


# =========================================================
# COMPANY ECONOMICS
# =========================================================

def _get_drivers(state: Any) -> Any:
    return _get_attr(state, ("drivers",), state)


def _get_working_capital(state: Any) -> Any:
    return _get_attr(
        state,
        ("working_capital", "working_capital_policy"),
        None,
    )


def _get_capital_structure(state: Any) -> Any:
    return _get_attr(state, ("capital_structure",), None)


def _annual_revenue(state: Any) -> float:
    drivers = _get_drivers(state)

    volume = _get_attr(
        drivers,
        ("volume", "annual_volume"),
        None,
    )

    price = _get_attr(
        drivers,
        ("price", "unit_price"),
        None,
    )

    if volume is not None and price is not None:
        return _to_float(volume) * _to_float(price)

    return _to_float(
        _get_attr(
            drivers,
            ("revenue", "annual_revenue"),
            0.0,
        )
    )


def _annual_cogs(state: Any) -> float:
    drivers = _get_drivers(state)

    volume = _get_attr(
        drivers,
        ("volume", "annual_volume"),
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
        return _to_float(volume) * _to_float(variable_cost)

    return _to_float(
        _get_attr(
            drivers,
            ("cogs", "annual_cogs", "cost_of_goods_sold"),
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
# DECISION VALUES
# =========================================================

def _decision_value(
    decision: Any,
    names: Sequence[str],
    default: Any = None,
) -> Any:
    if decision is None:
        return default

    # Direct attributes / keys
    value = _get_attr(decision, names, None)

    if value is not None:
        return value

    # Change object
    change = _decision_change(decision)

    value = _get_attr(change, names, None)

    if value is not None:
        return value

    # Common nested payload containers
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

        value = _get_attr(container, names, None)

        if value is not None:
            return value

    return default


def _decision_ar_days(
    baseline_state: Any,
    decision: Any,
) -> float:
    baseline = _baseline_ar_days(baseline_state)

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

    return _to_float(value, baseline)


def _decision_ap_days(
    baseline_state: Any,
    decision: Any,
) -> float:
    baseline = _baseline_ap_days(baseline_state)

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

    return _to_float(value, baseline)


# =========================================================
# COLLECTION PROFILE
# =========================================================

def _extract_collection_profile(source: Any) -> Optional[Dict[int, float]]:
    """
    Extract an explicit collection profile from a decision/candidate.

    Supported examples:

        {
            "month_0_pct": 20,
            "month_1_pct": 70,
            "month_2_pct": 10,
        }

    or:

        {
            "month_0": 0.20,
            "month_1": 0.70,
            "month_2": 0.10,
        }

    or nested:

        {
            "collection_schedule": {
                "month_0_pct": 20,
                ...
            }
        }
    """

    if source is None:
        return None

    # -----------------------------------------------------
    # 1. Look for an already structured schedule/profile
    # -----------------------------------------------------

    structured_names = (
        "collection_schedule",
        "collection_profile",
        "collection_distribution",
        "collection_timing",
        "schedule",
    )

    candidates: List[Any] = [source]

    change = _decision_change(source)

    if change is not None:
        candidates.append(change)

    for obj in list(candidates):
        for container_name in (
            "payload",
            "parameters",
            "params",
            "metadata",
        ):
            container = _get_attr(obj, (container_name,), None)

            if container is not None:
                candidates.append(container)

    for obj in candidates:
        if not isinstance(obj, Mapping):
            continue

        for name in structured_names:
            nested = obj.get(name)

            if isinstance(nested, Mapping):
                result = _extract_collection_profile(nested)

                if result:
                    return result

    # -----------------------------------------------------
    # 2. Flat keys
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
            if isinstance(obj, Mapping):
                for key in possible_keys:
                    if key in obj:
                        found = obj[key]
                        break

            if found is not None:
                break

            for key in possible_keys:
                value = _get_attr(obj, (key,), None)

                if value is not None:
                    found = value
                    break

            if found is not None:
                break

        if found is not None:
            result[month_index] = _normalise_pct(found)

    if not result:
        return None

    # Remove zero/negative noise only after extraction.
    result = {
        index: value
        for index, value in result.items()
        if value >= 0
    }

    if not result:
        return None

    total = sum(result.values())

    if total <= 0:
        return None

    # If the profile is slightly below/above 100 because of rounding,
    # normalise it. This does not change its shape.
    result = {
        index: value / total
        for index, value in result.items()
    }

    return result


def _get_collection_profile(decision: Any) -> Optional[Dict[int, float]]:
    """
    First inspect the selected decision.

    If the decision does not expose the detailed collection schedule,
    inspect the original Receivables Lab candidate stored in session_state.

    This is the key fix for the Month-4-only receipts problem.
    """

    profile = _extract_collection_profile(decision)

    if profile:
        return profile

    candidate = st.session_state.get(WC_AR_CANDIDATE)

    profile = _extract_collection_profile(candidate)

    if profile:
        return profile

    return None


# =========================================================
# MONTHLY TIMING
# =========================================================

def _monthly_delay_allocation(days: float) -> Dict[int, float]:
    """
    Simple owner-manager timing convention:

        0 days  -> same month
        30 days -> next month
        45 days -> 50% next month + 50% month +2
        60 days -> month +2
        90 days -> month +3

    Uses 30-day months intentionally.
    """

    days = max(0.0, _to_float(days))

    months = days / 30.0

    lower = int(months)
    fraction = months - lower

    if fraction <= 0:
        return {lower: 1.0}

    return {
        lower: 1.0 - fraction,
        lower + 1: fraction,
    }


def _allocate_cohort(
    amount: float,
    delay_allocation: Mapping[int, float],
    month_index: int,
    horizon: int = 6,
) -> List[float]:
    result = [0.0] * horizon

    for delay, percentage in delay_allocation.items():
        target_month = month_index + int(delay)

        if 0 <= target_month < horizon:
            result[target_month] += amount * percentage

    return result


# =========================================================
# RECEIPTS
# =========================================================

def _collections_from_profile(
    monthly_sales: Sequence[float],
    profile: Mapping[int, float],
    opening_ar: float = 0.0,
) -> List[float]:
    """
    Cohort-based collection model.

    Each month's sales cohort is allocated independently according
    to the selected collection profile.

    Example:
        20% / 70% / 10%

    Month 1:
        20% of Month 1 sales

    Month 2:
        70% of Month 1 sales
        +20% of Month 2 sales

    Month 3:
        10% of Month 1 sales
        +70% of Month 2 sales
        +20% of Month 3 sales
    """

    horizon = len(monthly_sales)

    receipts = [0.0] * horizon

    # -----------------------------------------------------
    # Opening receivables
    # -----------------------------------------------------
    #
    # We use the same explicit collection profile for the
    # opening AR balance. This gives the cash model an actual
    # starting collection stream instead of waiting for the
    # selected AR days to create a month-4 lump.
    #
    # If the profile is 20/70/10, opening AR contributes:
    # 20% in Month 1, 70% in Month 2, 10% in Month 3.
    #
    for delay, percentage in profile.items():
        target_month = int(delay)

        if 0 <= target_month < horizon:
            receipts[target_month] += opening_ar * percentage

    # -----------------------------------------------------
    # New sales cohorts
    # -----------------------------------------------------

    for cohort_month, sales in enumerate(monthly_sales):
        for delay, percentage in profile.items():
            target_month = cohort_month + int(delay)

            if 0 <= target_month < horizon:
                receipts[target_month] += sales * percentage

    return receipts


def _build_receipts(
    baseline_state: Any,
    ar_decision: Any,
    monthly_sales: Sequence[float],
) -> List[float]:

    profile = _get_collection_profile(ar_decision)

    annual_revenue = _annual_revenue(baseline_state)

    # IMPORTANT:
    # Opening AR belongs to the locked/baseline company position.
    # A new collection policy should not rewrite the opening
    # receivables balance.
    opening_ar = annual_revenue * _baseline_ar_days(baseline_state) / 365.0

    if profile:
        return _collections_from_profile(
            monthly_sales=monthly_sales,
            profile=profile,
            opening_ar=opening_ar,
        )

    # -----------------------------------------------------
    # Fallback: AR days
    # -----------------------------------------------------

    ar_days = _decision_ar_days(
        baseline_state,
        ar_decision,
    )

    allocation = _monthly_delay_allocation(ar_days)

    receipts = [0.0] * len(monthly_sales)

    # Opening AR under days-based fallback.
    opening_allocation = allocation

    for delay, percentage in opening_allocation.items():
        target_month = int(delay)

        if 0 <= target_month < len(receipts):
            receipts[target_month] += opening_ar * percentage

    # New sales cohorts.
    for cohort_month, sales in enumerate(monthly_sales):
        for delay, percentage in allocation.items():
            target_month = cohort_month + int(delay)

            if 0 <= target_month < len(receipts):
                receipts[target_month] += sales * percentage

    return receipts


# =========================================================
# SUPPLIER PAYMENTS
# =========================================================

def _build_supplier_payments(
    baseline_state: Any,
    ap_decision: Any,
    monthly_purchases: Sequence[float],
) -> List[float]:

    ap_days = _decision_ap_days(
        baseline_state,
        ap_decision,
    )

    allocation = _monthly_delay_allocation(ap_days)

    payments = [0.0] * len(monthly_purchases)

    for cohort_month, purchases in enumerate(monthly_purchases):
        for delay, percentage in allocation.items():
            target_month = cohort_month + int(delay)

            if 0 <= target_month < len(payments):
                payments[target_month] += purchases * percentage

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

    annual_revenue = _annual_revenue(baseline_state)
    annual_cogs = _annual_cogs(baseline_state)

    monthly_sales = [
        annual_revenue / 12.0
        for _ in MONTHS
    ]

    # Until a formal purchasing decision exists, projected
    # purchases are represented by monthly COGS.
    monthly_purchases = [
        annual_cogs / 12.0
        for _ in MONTHS
    ]

    receipts = _build_receipts(
        baseline_state=baseline_state,
        ar_decision=ar_decision,
        monthly_sales=monthly_sales,
    )

    supplier_payments = _build_supplier_payments(
        baseline_state=baseline_state,
        ap_decision=ap_decision,
        monthly_purchases=monthly_purchases,
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

    cash = _opening_cash(baseline_state)

    for month_index in range(len(MONTHS)):

        net = (
            receipts[month_index]
            - supplier_payments[month_index]
            - operating_expenses[month_index]
            - debt_payments[month_index]
        )

        cash += net

        net_cash_flow.append(net)
        ending_cash.append(cash)

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

def render_cash_management_lab(baseline_state: Any = None) -> None:

    if baseline_state is None:
        baseline_state = _get_baseline_state()

    if baseline_state is None:
        st.warning("Baseline company state is not available.")
        return

    ar_decision = _selected_ar_decision()
    ap_decision = _selected_ap_decision()

    st.subheader("Cash Management")

    st.caption(
        "This is the timing layer that turns your Receivables, "
        "Supplier and operating decisions into a monthly cash view."
    )

    # =====================================================
    # ASSUMPTIONS
    # =====================================================

    st.markdown("### Cash assumptions")

    col1, col2 = st.columns(2)

    default_monthly_opex = _annual_fixed_opex(baseline_state) / 12.0
    default_monthly_debt = _annual_debt_service(baseline_state) / 12.0

    with col1:
        monthly_opex = st.number_input(
            "Average monthly operating expenses",
            min_value=0.0,
            value=float(default_monthly_opex),
            step=1000.0,
            format="%.0f",
            help=(
                "Average monthly operating expenses excluding "
                "supplier payments and loan payments."
            ),
        )

    with col2:
        monthly_debt = st.number_input(
            "Monthly loan installments & interest",
            min_value=0.0,
            value=float(default_monthly_debt),
            step=1000.0,
            format="%.0f",
        )

    minimum_cash = st.number_input(
        "Minimum cash reserve to maintain",
        min_value=0.0,
        value=0.0,
        step=5000.0,
        format="%.0f",
        help="Cash level you want to keep available at all times.",
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

    collection_profile = _get_collection_profile(ar_decision)

    if collection_profile:
        profile_text = " / ".join(
            f"{int(delay)}m: {percentage:.0%}"
            for delay, percentage
            in sorted(collection_profile.items())
        )

        st.caption(
            f"Collection timing: {profile_text}"
        )
    else:
        st.caption(
            f"Collection timing: approximately {current_ar_days:.0f} days"
        )

    st.caption(
        f"Supplier payment timing: approximately {current_ap_days:.0f} days"
    )

    # =====================================================
    # BUILD CASH PLAN
    # =====================================================

    plan = _build_cash_plan(
        baseline_state=baseline_state,
        ar_decision=ar_decision,
        ap_decision=ap_decision,
        monthly_opex=monthly_opex,
        monthly_debt=monthly_debt,
    )

    receipts = plan["receipts"]
    supplier_payments = plan["supplier_payments"]
    operating_expenses = plan["operating_expenses"]
    debt_payments = plan["debt_payments"]
    net_cash_flow = plan["net_cash_flow"]
    ending_cash = plan["ending_cash"]

    # =====================================================
    # SIX-MONTH OUTLOOK
    # =====================================================

    st.markdown("### Six-month cash outlook")

    opening_cash = _opening_cash(baseline_state)

    st.caption(
        f"Opening cash: {_money(opening_cash)}"
    )

    table = pd.DataFrame(
        {
            "Receipts": receipts,
            "Supplier payments": supplier_payments,
            "Operating expenses": operating_expenses,
            "Loan payments & interest": debt_payments,
            "Net cash flow": net_cash_flow,
            "Ending cash balance": ending_cash,
        },
        index=MONTHS,
    ).T

    st.dataframe(
        table.style.format(
            lambda value: _money(value)
        ),
        use_container_width=True,
    )

    # =====================================================
    # CASH POSITION
    # =====================================================

    minimum_projected_cash = min(ending_cash)

    minimum_index = ending_cash.index(
        minimum_projected_cash
    )

    minimum_month = MONTHS[minimum_index]

    funding_required = max(
        0.0,
        minimum_cash - minimum_projected_cash,
    )

    surplus_above_minimum = max(
        0.0,
        minimum_projected_cash - minimum_cash,
    )

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(
            "Lowest projected cash",
            _money(minimum_projected_cash),
        )

    with col2:
        st.metric(
            "Lowest point",
            minimum_month,
        )

    with col3:
        st.metric(
            "Funding required",
            _money(funding_required),
        )

    # =====================================================
    # INTERPRETATION
    # =====================================================

    st.markdown("### What does this mean?")

    if funding_required > 0:

        st.warning(
            f"The business falls below the minimum cash reserve in "
            f"{minimum_month}. The projected shortfall is "
            f"{_money(funding_required)}."
        )

        st.write(
            "The issue is timing: the business may be generating sales "
            "and profit, but cash is leaving the business before the "
            "corresponding customer receipts arrive."
        )

    else:

        st.success(
            f"The six-month cash plan stays above the minimum cash "
            f"reserve. The lowest projected balance is "
            f"{_money(minimum_projected_cash)} in {minimum_month}."
        )

        if surplus_above_minimum > 0:
            st.write(
                f"At its lowest point, the business retains "
                f"{_money(surplus_above_minimum)} above the minimum "
                f"cash reserve."
            )
        else:
            st.write(
                "The projected cash balance reaches the minimum "
                "reserve but does not fall below it."
            )


# =========================================================
# OPTIONAL COMPATIBILITY ALIAS
# =========================================================

def show_cash_management_lab(baseline_state: Any = None) -> None:
    render_cash_management_lab(baseline_state)
