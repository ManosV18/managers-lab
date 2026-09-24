from __future__ import annotations

from dataclasses import asdict, is_dataclass, replace
from decimal import Decimal, InvalidOperation
from typing import Any, Dict, Mapping, Optional, Tuple
from uuid import uuid4

import streamlit as st

from core.decision_factory import DecisionFactory
from core.decision_plan import DecisionPlan


# ============================================================
# RECEIVABLES / AR CANDIDATE
# ============================================================

AR_CANDIDATE = "ar_candidate"

AR_META = {
    "category": "Working Capital",
    "sub_category": "Receivables",
    "source": "Receivables Lab",
}


# ============================================================
# COLLECTION SCHEDULE
#
# IMPORTANT:
# This schedule is a CASH-TIMING assumption.
#
# It is deliberately independent from:
# - NPV
# - maximum discount
# - optimum discount
# - free-capital calculation
# - economic value calculation
#
# The schedule answers:
# "Once we choose the policy, when does the cash arrive?"
#
# The economic model answers:
# "Is the policy economically worth doing?"
# ============================================================

DEFAULT_COLLECTION_SCHEDULE = {
    "month_0_pct": 0.20,
    "month_1_pct": 0.70,
    "month_2_pct": 0.10,
}


# ============================================================
# GENERIC HELPERS
# ============================================================

def _decimal(value: Any, default: str = "0") -> Decimal:
    """
    Safe Decimal conversion.

    The economic formulas below are intentionally kept in their
    original mathematical structure. Decimal is used only to
    reduce avoidable floating-point noise in UI calculations.
    """
    if value is None:
        return Decimal(default)

    if isinstance(value, Decimal):
        return value

    try:
        return Decimal(str(value))
    except (InvalidOperation, ValueError, TypeError):
        return Decimal(default)


def _float(value: Any, default: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _get_attr(
    obj: Any,
    name: str,
    default: Any = None,
) -> Any:
    if obj is None:
        return default

    if isinstance(obj, Mapping):
        return obj.get(name, default)

    return getattr(obj, name, default)


def _normalise_collection_schedule(
    schedule: Optional[Mapping[str, Any]],
) -> Dict[str, float]:
    """
    Normalise the collection schedule to a 100% distribution.

    This function has NO connection to the NPV model.
    """
    source = dict(
        schedule
        or DEFAULT_COLLECTION_SCHEDULE
    )

    month_0 = max(
        0.0,
        _float(
            source.get("month_0_pct", 0.0)
        ),
    )

    month_1 = max(
        0.0,
        _float(
            source.get("month_1_pct", 0.0)
        ),
    )

    month_2 = max(
        0.0,
        _float(
            source.get("month_2_pct", 0.0)
        ),
    )

    total = (
        month_0
        + month_1
        + month_2
    )

    if total <= 0:
        return dict(
            DEFAULT_COLLECTION_SCHEDULE
        )

    return {
        "month_0_pct": month_0 / total,
        "month_1_pct": month_1 / total,
        "month_2_pct": month_2 / total,
    }


def _format_collection_schedule(
    schedule: Mapping[str, Any],
) -> str:
    normalised = _normalise_collection_schedule(
        schedule
    )

    return (
        f"Month 0: "
        f"{normalised['month_0_pct'] * 100:.0f}%  |  "
        f"Month 1: "
        f"{normalised['month_1_pct'] * 100:.0f}%  |  "
        f"Month 2: "
        f"{normalised['month_2_pct'] * 100:.0f}%"
    )


def _attach_collection_schedule(
    decision: Any,
    schedule: Mapping[str, Any],
) -> Any:
    """
    Store the collection schedule on the decision metadata
    without putting it into the economic NPV calculation.
    """
    normalised = _normalise_collection_schedule(
        schedule
    )

    try:
        metadata = dict(
            getattr(
                decision,
                "metadata",
                {},
            )
            or {}
        )

        metadata[
            "collection_schedule"
        ] = normalised

        if hasattr(
            decision,
            "metadata",
        ):
            try:
                return replace(
                    decision,
                    metadata=metadata,
                )
            except Exception:
                pass

    except Exception:
        pass

    return decision


def _decision_collection_schedule(
    decision: Any,
) -> Dict[str, float]:
    if decision is None:
        return dict(
            DEFAULT_COLLECTION_SCHEDULE
        )

    metadata = _get_attr(
        decision,
        "metadata",
        {},
    )

    if isinstance(metadata, Mapping):
        schedule = metadata.get(
            "collection_schedule"
        )

        if isinstance(
            schedule,
            Mapping,
        ):
            return _normalise_collection_schedule(
                schedule
            )

    return dict(
        DEFAULT_COLLECTION_SCHEDULE
    )


# ============================================================
# BASELINE HELPERS
# ============================================================

def _drivers(baseline_state: Any) -> Any:
    return _get_attr(
        baseline_state,
        "drivers",
        baseline_state,
    )


def _capital_structure(
    baseline_state: Any,
) -> Any:
    return _get_attr(
        baseline_state,
        "capital_structure",
        None,
    )


def _annual_sales(
    baseline_state: Any,
) -> float:
    """
    CompanyState revenue.

    Revenue = volume * price
    """
    drivers = _drivers(
        baseline_state
    )

    price = _float(
        _get_attr(
            drivers,
            "price",
            0.0,
        )
    )

    volume = _float(
        _get_attr(
            drivers,
            "volume",
            0.0,
        )
    )

    return price * volume


def _annual_cogs(
    baseline_state: Any,
) -> float:
    """
    CompanyState COGS.

    COGS = volume * variable_cost_per_unit
    """
    drivers = _drivers(
        baseline_state
    )

    volume = _float(
        _get_attr(
            drivers,
            "volume",
            0.0,
        )
    )

    variable_cost = _float(
        _get_attr(
            drivers,
            "variable_cost_per_unit",
            0.0,
        )
    )

    return volume * variable_cost


def _baseline_ar_days(
    baseline_state: Any,
) -> float:
    working_capital = _get_attr(
        baseline_state,
        "working_capital",
        None,
    )

    return _float(
        _get_attr(
            working_capital,
            "ar_days",
            0.0,
        )
    )


def _baseline_wacc(
    baseline_state: Any,
) -> float:
    capital = _capital_structure(
        baseline_state
    )

    return _float(
        _get_attr(
            capital,
            "wacc",
            0.0,
        )
    )


def _baseline_ap_days(
    baseline_state: Any,
) -> float:
    working_capital = _get_attr(
        baseline_state,
        "working_capital",
        None,
    )

    return _float(
        _get_attr(
            working_capital,
            "ap_days",
            0.0,
        )
    )


# ============================================================
# LEGACY RECEIVABLES ECONOMIC MODEL
# ============================================================
#
# IMPORTANT:
#
# These are the original economic formulas.
#
# The collection schedule does NOT participate here.
#
# The model deliberately distinguishes:
#
#   ECONOMIC POLICY MODEL
#       ↓
#   NPV / discount economics
#
# from:
#
#   CASH TIMING MODEL
#       ↓
#   monthly collection schedule
#
# ============================================================

def calculate_discount_npv(
    current_sales: float,
    extra_sales: float,
    discount_trial: float,
    prc_clients_take_disc: float,
    days_curently_paying_clients_take_discount: float,
    days_curently_paying_clients_not_take_discount: float,
    new_days_payment_clients_take_disc: float,
    cogs: float,
    wacc: float,
    avg_days_pay_suppliers: float,
) -> Dict[str, float]:
    """
    Canonical Receivables economic calculation.

    The formulas here intentionally preserve the legacy model.

    Returns:
        current_collection_days
        current_receivables
        prcnt_of_total_new_clients_in_new_policy
        new_avg_collection_period
        new_receivables
        free_capital
        extra_sales_profit
        free_capital_profit
        discount_cost
        economic_npv
        maximum_discount
        optimum_discount
    """

    # --------------------------------------------------------
    # Current collection period
    # --------------------------------------------------------

    avg_current_collection_days = (
        days_curently_paying_clients_take_discount
        * prc_clients_take_disc
        + days_curently_paying_clients_not_take_discount
        * (
            1
            - prc_clients_take_disc
        )
    )

    # --------------------------------------------------------
    # Current receivables
    # --------------------------------------------------------

    current_receivables = (
        current_sales
        * avg_current_collection_days
        / 365.0
    )

    # --------------------------------------------------------
    # Percentage of total new clients / sales under
    # the new policy
    #
    # EXACT LEGACY FORMULA
    # --------------------------------------------------------

    prcnt_of_total_new_clients_in_new_policy = (
        (
            current_sales
            * prc_clients_take_disc
        )
        + extra_sales
    ) / (
        current_sales
        + extra_sales
    )

    # --------------------------------------------------------
    # Complementary percentage
    # --------------------------------------------------------

    prcnt_of_total_new_clients_not_in_new_policy = (
        1
        - prcnt_of_total_new_clients_in_new_policy
    )

    # --------------------------------------------------------
    # New average collection period
    #
    # EXACT LEGACY FORMULA
    # --------------------------------------------------------

    new_avg_collection_period = (
        prcnt_of_total_new_clients_in_new_policy
        * new_days_payment_clients_take_disc
        + prcnt_of_total_new_clients_not_in_new_policy
        * days_curently_paying_clients_not_take_discount
    )

    # --------------------------------------------------------
    # New receivables
    # --------------------------------------------------------

    new_receivables = (
        (
            current_sales
            + extra_sales
        )
        * new_avg_collection_period
        / 365.0
    )

    # --------------------------------------------------------
    # Free capital
    # --------------------------------------------------------

    free_capital = (
        current_receivables
        - new_receivables
    )

    # --------------------------------------------------------
    # Extra-sales profit
    #
    # EXACT LEGACY FORMULA
    # --------------------------------------------------------

    extra_sales_profit = (
        extra_sales
        * (
            1
            - (
                cogs
                / current_sales
            )
        )
    )

    # --------------------------------------------------------
    # Free-capital profit
    #
    # EXACT LEGACY FORMULA
    # --------------------------------------------------------

    free_capital_profit = (
        free_capital
        * wacc
    )

    # --------------------------------------------------------
    # Discount cost
    #
    # EXACT LEGACY FORMULA
    # --------------------------------------------------------

    discount_cost = (
        (
            current_sales
            + extra_sales
        )
        * prcnt_of_total_new_clients_in_new_policy
        * discount_trial
    )

    # --------------------------------------------------------
    # ECONOMIC NPV
    #
    # EXACT LEGACY FORMULA
    #
    # Do NOT replace this with:
    #
    #   extra profit
    #   + free capital profit
    #   - discount cost
    #
    # That is NOT the legacy NPV calculation.
    # --------------------------------------------------------

    daily_discount_factor = (
        1
        + (
            wacc
            / 365.0
        )
    )

    economic_npv = (
        (
            current_sales
            + extra_sales
        )
        * prcnt_of_total_new_clients_in_new_policy
        * (
            1
            - discount_trial
        )
        * (
            1
            / (
                daily_discount_factor
                ** new_days_payment_clients_take_disc
            )
        )
        +
        (
            current_sales
            + extra_sales
        )
        * (
            1
            - prcnt_of_total_new_clients_in_new_policy
        )
        * (
            1
            / (
                daily_discount_factor
                ** days_curently_paying_clients_not_take_discount
            )
        )
        -
        (
            cogs
            / current_sales
        )
        * (
            extra_sales
            / current_sales
        )
        * current_sales
        * (
            1
            / (
                daily_discount_factor
                ** avg_days_pay_suppliers
            )
        )
        -
        current_sales
        * (
            1
            / (
                daily_discount_factor
                ** avg_current_collection_days
            )
        )
    )

    # --------------------------------------------------------
    # MAXIMUM DISCOUNT
    #
    # EXACT LEGACY FORMULA
    # --------------------------------------------------------

    maximum_discount = (
        1
        -
        (
            daily_discount_factor
            ** (
                new_days_payment_clients_take_disc
                -
                days_curently_paying_clients_not_take_discount
            )
        )
        *
        (
            (
                1
                -
                (
                    1
                    /
                    prcnt_of_total_new_clients_in_new_policy
                )
            )
            +
            (
                (
                    daily_discount_factor
                    ** (
                        days_curently_paying_clients_not_take_discount
                        -
                        avg_current_collection_days
                    )
                )
                +
                (
                    cogs
                    / current_sales
                )
                * (
                    extra_sales
                    / current_sales
                )
                * (
                    daily_discount_factor
                    ** (
                        days_curently_paying_clients_not_take_discount
                        -
                        avg_days_pay_suppliers
                    )
                )
            )
            /
            (
                prcnt_of_total_new_clients_in_new_policy
                * (
                    1
                    + (
                        extra_sales
                        / current_sales
                    )
                )
            )
        )
    )

    # --------------------------------------------------------
    # OPTIMUM DISCOUNT
    #
    # EXACT LEGACY FORMULA
    # --------------------------------------------------------

    optimum_discount = (
        1
        -
        (
            daily_discount_factor
            ** (
                new_days_payment_clients_take_disc
                -
                avg_current_collection_days
            )
        )
    ) / 2.0

    return {
        "current_collection_days":
            avg_current_collection_days,

        "current_receivables":
            current_receivables,

        "prcnt_of_total_new_clients_in_new_policy":
            prcnt_of_total_new_clients_in_new_policy,

        "prcnt_of_total_new_clients_not_in_new_policy":
            prcnt_of_total_new_clients_not_in_new_policy,

        "new_avg_collection_period":
            new_avg_collection_period,

        "new_receivables":
            new_receivables,

        "free_capital":
            free_capital,

        "extra_sales_profit":
            extra_sales_profit,

        "free_capital_profit":
            free_capital_profit,

        "discount_cost":
            discount_cost,

        "economic_npv":
            economic_npv,

        "maximum_discount":
            maximum_discount,

        "optimum_discount":
            optimum_discount,
    }


# ============================================================
# DECISION PLAN HELPERS
# ============================================================

def _get_current_plan() -> Optional[DecisionPlan]:
    plan = st.session_state.get(
        "decision_plan"
    )

    if isinstance(
        plan,
        DecisionPlan,
    ):
        return plan

    return None


def _find_conflicting_driver(
    plan: Optional[DecisionPlan],
    driver_name: str,
) -> Optional[Any]:

    if plan is None:
        return None

    for decision in getattr(
        plan,
        "decisions",
        [],
    ):
        changes = getattr(
            decision,
            "changes",
            {},
        )

        if driver_name in changes:
            return decision

    return None


def _add_to_current_plan(
    decision: Any,
) -> None:
    """
    Add the Receivables decision as the AR decision candidate.

    The collection schedule remains metadata and does not become
    a CompanyState driver.
    """

    plan = _get_current_plan()

    if plan is None:
        plan = DecisionPlan.create(
            plan_id="main_plan",
            name="Current Decision Plan",
        )

    decisions = list(
        getattr(
            plan,
            "decisions",
            [],
        )
        or []
    )

    # Remove an existing decision that changes ar_days.
    filtered = []

    for existing in decisions:
        changes = getattr(
            existing,
            "changes",
            {},
        )

        if "ar_days" not in changes:
            filtered.append(
                existing
            )

    filtered.append(
        decision
    )

    try:
        st.session_state.decision_plan = (
            replace(
                plan,
                decisions=tuple(filtered),
            )
        )
        return

    except Exception:
        pass

    try:
        st.session_state.decision_plan = (
            DecisionPlan.create(
                plan_id="main_plan",
                name="Current Decision Plan",
                decisions=filtered,
            )
        )
        return

    except Exception:
        pass

    # Last-resort fallback for older DecisionPlan implementations.
    try:
        plan.decisions = filtered
        st.session_state.decision_plan = plan
    except Exception:
        st.session_state.decision_plan = plan


# ============================================================
# DECISION CREATION
# ============================================================

def _build_ar_decision(
    projected_ar_days: float,
    economic_result: Mapping[str, Any],
    collection_schedule: Mapping[str, Any],
) -> Any:
    """
    Create the AR Decision.

    Only the policy driver is written to the Decision.

    Collection schedule is stored separately as metadata.
    """

    changes = {
        "ar_days": float(
            projected_ar_days
        )
    }

    metadata = dict(
        AR_META
    )

    metadata.update(
        {
            "economic_model":
                "legacy_receivables_model",

            "economic_result":
                dict(economic_result),

            "collection_schedule":
                _normalise_collection_schedule(
                    collection_schedule
                ),
        }
    )

    try:
        decision = DecisionFactory.create(
            decision_id=f"ar_{uuid4().hex[:10]}",
            name="Receivables Policy",
            category="Working Capital",
            description=(
                "Receivables policy created "
                "from the Receivables Lab."
            ),
            changes=changes,
            metadata=metadata,
        )

        return decision

    except TypeError:
        pass

    except Exception:
        pass

    # Compatibility fallback for DecisionFactory variants.
    try:
        decision = DecisionFactory.create(
            name="Receivables Policy",
            category="Working Capital",
            description=(
                "Receivables policy created "
                "from the Receivables Lab."
            ),
            changes=changes,
            metadata=metadata,
        )

        return decision

    except Exception:
        pass

    # Final compatibility path.
    from core.decision import Decision

    try:
        return Decision(
            id=f"ar_{uuid4().hex[:10]}",
            name="Receivables Policy",
            category="Working Capital",
            description=(
                "Receivables policy created "
                "from the Receivables Lab."
            ),
            changes=changes,
            metadata=metadata,
        )

    except TypeError:
        return Decision(
            id=f"ar_{uuid4().hex[:10]}",
            name="Receivables Policy",
            category="Working Capital",
            description=(
                "Receivables policy created "
                "from the Receivables Lab."
            ),
            changes=changes,
        )


# ============================================================
# MAIN UI
# ============================================================

def render_receivables_lab(
    baseline_state: Any,
) -> None:

    st.title(
        "💶 Receivables Lab"
    )

    st.caption(
        "Test the economics of customer-payment policies "
        "before putting a receivables decision into the "
        "Current Decision Plan."
    )

    # ========================================================
    # BASELINE REFERENCE
    # ========================================================

    baseline_sales = _annual_sales(
        baseline_state
    )

    baseline_cogs = _annual_cogs(
        baseline_state
    )

    baseline_ar_days = _baseline_ar_days(
        baseline_state
    )

    baseline_wacc = _baseline_wacc(
        baseline_state
    )

    baseline_ap_days = _baseline_ap_days(
        baseline_state
    )

    st.subheader(
        "1. Current Business Reference"
    )

    c1, c2, c3, c4 = st.columns(4)

    c1.metric(
        "Baseline Annual Sales",
        f"€{baseline_sales:,.0f}",
    )

    c2.metric(
        "Baseline Annual COGS",
        f"€{baseline_cogs:,.0f}",
    )

    c3.metric(
        "Baseline AR Days",
        f"{baseline_ar_days:.0f}",
    )

    c4.metric(
        "Baseline Supplier Days",
        f"{baseline_ap_days:.0f}",
    )

    # ========================================================
    # ECONOMIC MODEL INPUTS
    # ========================================================

    st.divider()

    st.subheader(
        "2. Receivables Economic Decision"
    )

    st.write(
        "This section answers one question:"
    )

    st.info(
        "Is it economically worth giving customers a "
        "discount so that we get paid earlier?"
    )

    st.caption(
        "These calculations use the Receivables economic model. "
        "They are independent of the monthly collection schedule."
    )

    # --------------------------------------------------------
    # Sales
    # --------------------------------------------------------

    i1, i2, i3 = st.columns(3)

    with i1:
        current_sales = st.number_input(
            "Current Annual Sales",
            min_value=0.0001,
            value=float(
                baseline_sales
                if baseline_sales > 0
                else 1000.0
            ),
            step=100.0,
            key="receivables_current_sales",
        )

    with i2:
        extra_sales = st.number_input(
            "Extra Annual Sales",
            min_value=0.0,
            value=250.0,
            step=50.0,
            key="receivables_extra_sales",
        )

    with i3:
        cogs = st.number_input(
            "Annual COGS",
            min_value=0.0001,
            value=float(
                baseline_cogs
                if baseline_cogs > 0
                else 800.0
            ),
            step=100.0,
            key="receivables_cogs",
        )

    # --------------------------------------------------------
    # Discount policy
    # --------------------------------------------------------

    st.markdown(
        "#### Early-Payment Discount Policy"
    )

    p1, p2, p3 = st.columns(3)

    with p1:
        discount_trial_pct = st.number_input(
            "Trial Discount (%)",
            min_value=0.0,
            max_value=100.0,
            value=2.0,
            step=0.25,
            key="receivables_discount_trial",
        )

    with p2:
        prc_clients_take_disc_pct = st.number_input(
            "Current Clients Taking Discount (%)",
            min_value=0.0,
            max_value=100.0,
            value=40.0,
            step=5.0,
            key="receivables_prc_clients_take_disc",
        )

    with p3:
        new_days_payment_clients_take_disc = st.number_input(
            "New Payment Days — Discount Clients",
            min_value=0.0,
            value=10.0,
            step=5.0,
            key="receivables_new_days_payment_clients_take_disc",
        )

    # --------------------------------------------------------
    # Current payment behaviour
    # --------------------------------------------------------

    st.markdown(
        "#### Current Customer Payment Behaviour"
    )

    p4, p5, p6 = st.columns(3)

    with p4:
        days_curently_paying_clients_take_discount = (
            st.number_input(
                "Current Discount Clients — Days",
                min_value=0.0,
                value=60.0,
                step=5.0,
                key=(
                    "receivables_days_current_discount_clients"
                ),
            )
        )

    with p5:
        days_curently_paying_clients_not_take_discount = (
            st.number_input(
                "Current Non-Discount Clients — Days",
                min_value=0.0,
                value=120.0,
                step=5.0,
                key=(
                    "receivables_days_current_non_discount_clients"
                ),
            )
        )

    with p6:
        avg_days_pay_suppliers = st.number_input(
            "Average Supplier Payment Days",
            min_value=0.0,
            value=float(
                baseline_ap_days
                if baseline_ap_days > 0
                else 30.0
            ),
            step=5.0,
            key="receivables_avg_days_pay_suppliers",
        )

    # --------------------------------------------------------
    # WACC
    # --------------------------------------------------------

    wacc_pct = st.number_input(
        "WACC (%)",
        min_value=0.0,
        max_value=100.0,
        value=float(
            baseline_wacc * 100.0
            if baseline_wacc > 0
            else 20.0
        ),
        step=1.0,
        key="receivables_wacc",
    )

    # Convert percentage inputs to decimals.
    discount_trial = (
        discount_trial_pct / 100.0
    )

    prc_clients_take_disc = (
        prc_clients_take_disc_pct
        / 100.0
    )

    wacc = (
        wacc_pct
        / 100.0
    )

    # ========================================================
    # ECONOMIC CALCULATION
    # ========================================================

    economic_result = calculate_discount_npv(
        current_sales=current_sales,
        extra_sales=extra_sales,
        discount_trial=discount_trial,
        prc_clients_take_disc=(
            prc_clients_take_disc
        ),
        days_curently_paying_clients_take_discount=(
            days_curently_paying_clients_take_discount
        ),
        days_curently_paying_clients_not_take_discount=(
            days_curently_paying_clients_not_take_discount
        ),
        new_days_payment_clients_take_disc=(
            new_days_payment_clients_take_disc
        ),
        cogs=cogs,
        wacc=wacc,
        avg_days_pay_suppliers=(
            avg_days_pay_suppliers
        ),
    )

    # ========================================================
    # ECONOMIC RESULTS
    # ========================================================

    st.divider()

    st.subheader(
        "3. Economic Result"
    )

    r1, r2, r3, r4 = st.columns(4)

    r1.metric(
        "Current Collection",
        (
            f"{economic_result['current_collection_days']:.1f} days"
        ),
    )

    r2.metric(
        "New Avg Collection",
        (
            f"{economic_result['new_avg_collection_period']:.1f} days"
        ),
    )

    r3.metric(
        "Free Capital",
        (
            f"€{economic_result['free_capital']:,.2f}"
        ),
    )

    r4.metric(
        "Economic NPV",
        (
            f"€{economic_result['economic_npv']:,.2f}"
        ),
    )

    # ========================================================
    # ECONOMIC DETAIL
    # ========================================================

    st.markdown(
        "#### Economic Detail"
    )

    d1, d2, d3 = st.columns(3)

    d1.metric(
        "Current Receivables",
        (
            f"€{economic_result['current_receivables']:,.2f}"
        ),
    )

    d2.metric(
        "New Receivables",
        (
            f"€{economic_result['new_receivables']:,.2f}"
        ),
    )

    d3.metric(
        "New Policy Share",
        (
            f"{economic_result['prcnt_of_total_new_clients_in_new_policy'] * 100:.2f}%"
        ),
    )

    d4, d5, d6 = st.columns(3)

    d4.metric(
        "Extra-Sales Profit",
        (
            f"€{economic_result['extra_sales_profit']:,.2f}"
        ),
    )

    d5.metric(
        "Free-Capital Profit",
        (
            f"€{economic_result['free_capital_profit']:,.2f}"
        ),
    )

    d6.metric(
        "Discount Cost",
        (
            f"€{economic_result['discount_cost']:,.2f}"
        ),
    )

    # ========================================================
    # DISCOUNT THRESHOLDS
    # ========================================================

    st.markdown(
        "#### Discount Thresholds"
    )

    t1, t2 = st.columns(2)

    t1.metric(
        "Maximum Discount",
        (
            f"{economic_result['maximum_discount'] * 100:.2f}%"
        ),
    )

    t2.metric(
        "Optimum Discount",
        (
            f"{economic_result['optimum_discount'] * 100:.2f}%"
        ),
    )

    st.caption(
        "Maximum Discount and Optimum Discount are calculated "
        "from the original Receivables formulas. They are not "
        "derived from the monthly collection schedule."
    )

    # ========================================================
    # ECONOMIC INTERPRETATION
    # ========================================================

    if economic_result["economic_npv"] > 0:
        st.success(
            "The economic NPV is positive under these assumptions."
        )
    elif economic_result["economic_npv"] < 0:
        st.warning(
            "The economic NPV is negative under these assumptions."
        )
    else:
        st.info(
            "The economic NPV is approximately zero under these assumptions."
        )

    # ========================================================
    # COLLECTION SCHEDULE
    # ========================================================
    #
    # COMPLETELY SEPARATE FROM THE ECONOMIC MODEL.
    #
    # This answers:
    #
    # "Once we choose the policy, when does the cash arrive?"
    #
    # It does NOT alter:
    # - NPV
    # - maximum discount
    # - optimum discount
    # - free capital
    # ========================================================

    st.divider()

    st.subheader(
        "4. Monthly Collection Schedule"
    )

    st.write(
        "This is the practical cash-timing assumption after "
        "the receivables policy has been chosen."
    )

    st.caption(
        "The schedule is independent from the NPV calculation. "
        "Changing it does not change the economic value above."
    )

    existing_decision = st.session_state.get(
        AR_CANDIDATE
    )

    existing_schedule = (
        _decision_collection_schedule(
            existing_decision
        )
    )

    s1, s2, s3 = st.columns(3)

    with s1:
        month_0_pct = st.number_input(
            "Month 0 Collection (%)",
            min_value=0.0,
            max_value=100.0,
            value=(
                existing_schedule[
                    "month_0_pct"
                ]
                * 100.0
            ),
            step=5.0,
            key="receivables_collection_month_0",
        )

    with s2:
        month_1_pct = st.number_input(
            "Month 1 Collection (%)",
            min_value=0.0,
            max_value=100.0,
            value=(
                existing_schedule[
                    "month_1_pct"
                ]
                * 100.0
            ),
            step=5.0,
            key="receivables_collection_month_1",
        )

    with s3:
        month_2_pct = st.number_input(
            "Month 2 Collection (%)",
            min_value=0.0,
            max_value=100.0,
            value=(
                existing_schedule[
                    "month_2_pct"
                ]
                * 100.0
            ),
            step=5.0,
            key="receivables_collection_month_2",
        )

    collection_schedule = (
        _normalise_collection_schedule(
            {
                "month_0_pct":
                    month_0_pct / 100.0,

                "month_1_pct":
                    month_1_pct / 100.0,

                "month_2_pct":
                    month_2_pct / 100.0,
            }
        )
    )

    schedule_total = (
        collection_schedule["month_0_pct"]
        + collection_schedule["month_1_pct"]
        + collection_schedule["month_2_pct"]
    )

    st.metric(
        "Collection Distribution",
        _format_collection_schedule(
            collection_schedule
        ),
    )

    st.caption(
        f"Total distribution: "
        f"{schedule_total * 100:.1f}%"
    )

    # ========================================================
    # DECISION TARGET
    # ========================================================

    st.divider()

    st.subheader(
        "5. Receivables Policy Decision"
    )

    projected_ar_days = st.number_input(
        "Target AR Days for CompanyState",
        min_value=0.0,
        value=float(
            economic_result[
                "new_avg_collection_period"
            ]
        ),
        step=1.0,
        key="receivables_target_ar_days",
    )

    st.caption(
        "This is the AR policy that will be written to the "
        "Current Decision Plan. The monthly collection schedule "
        "remains separate."
    )

    # ========================================================
    # CONFLICT CHECK
    # ========================================================

    current_plan = _get_current_plan()

    conflicting_decision = (
        _find_conflicting_driver(
            current_plan,
            "ar_days",
        )
    )

    if conflicting_decision is not None:
        st.warning(
            "The Current Decision Plan already contains "
            "another decision changing AR days. Saving this "
            "Receivables Policy will replace that AR decision."
        )

    # ========================================================
    # SAVE DECISION
    # ========================================================

    if st.button(
        "💾 Use This Receivables Policy",
        type="primary",
        use_container_width=True,
        key="receivables_use_policy",
    ):

        decision = _build_ar_decision(
            projected_ar_days=projected_ar_days,
            economic_result=economic_result,
            collection_schedule=collection_schedule,
        )

        # Store candidate separately.
        st.session_state[
            AR_CANDIDATE
        ] = decision

        # Add the policy decision to the Current Decision Plan.
        _add_to_current_plan(
            decision
        )

        st.success(
            "Receivables Policy added to the Current Decision Plan."
        )

        st.info(
            "The AR-days policy is now part of the decision "
            "layer. The collection schedule remains a separate "
            "cash-timing assumption."
        )

    # ========================================================
    # CURRENT CANDIDATE
    # ========================================================

    candidate = st.session_state.get(
        AR_CANDIDATE
    )

    if candidate is not None:

        st.divider()

        st.subheader(
            "Current Receivables Candidate"
        )

        candidate_changes = _get_attr(
            candidate,
            "changes",
            {},
        )

        candidate_metadata = _get_attr(
            candidate,
            "metadata",
            {},
        )

        c1, c2, c3 = st.columns(3)

        c1.metric(
            "Target AR Days",
            (
                f"{_float(candidate_changes.get('ar_days', 0.0)):.1f}"
            ),
        )

        c2.metric(
            "Economic NPV",
            (
                f"€{_float(candidate_metadata.get('economic_result', {}).get('economic_npv', 0.0)):,.2f}"
            ),
        )

        c3.metric(
            "Collection Schedule",
            _format_collection_schedule(
                _decision_collection_schedule(
                    candidate
                )
            ),
        )

        st.caption(
            "The candidate contains both the receivables policy "
            "and the separate collection schedule. Only AR days "
            "acts as the CompanyState policy driver."
        )
