"""
Managers Lab V2 — Cash Management

Purpose
-------
Monthly cash-timing layer for decisions already made elsewhere.

Canonical V2 flow:
    Locked Baseline
        -> Current Decision Plan
        -> DecisionEvaluator / Runner
        -> Projected CompanyState
        -> Cash Management (cash timing)
        -> Financial Engine / Diagnostics / Control Tower

This module does NOT create a second company model and does NOT replace
the Financial Engine.

Important design rule:
    Decision Labs own the decisions.
    Cash Management translates those decisions into near-term cash
    timing.

Current integration strategy
----------------------------
1. Read the current Decision Plan from session state.
2. Read the projected CompanyState through DecisionEvaluator when available.
3. Pull timing schedules from decision metadata when a Lab already exposes them.
4. Use baseline payment terms only as a fallback until the relevant Lab exposes
   its detailed schedule.
5. Ask the owner only for exceptional cash events the system cannot know.
6. Show a rolling six-month cash consequence window.

The six-month window is deliberately not a six-month detailed budget:
    - Months 1–3: near-term, concrete cash consequences.
    - Months 4–6: consequences of decisions already made.
    - Known commitments beyond month 6 are shown separately rather than forced
      into month 6.

No historical-ratio forecasting is used for receivables or payables when a
decision-specific schedule is available.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
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

# Existing V2 candidate keys seen in the current application.
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
    month_index: int
    amount: float
    label: str
    category: str


@dataclass(frozen=True)
class CashPlanResult:
    opening_cash: float
    rows: Tuple[Dict[str, Any], ...]
    minimum_cash: float
    minimum_cash_month: str
    funding_gap: float
    funding_gap_month: Optional[str]
    recovery_month: Optional[str]
    beyond_horizon_events: Tuple[CashEvent, ...]


# ---------------------------------------------------------------------
# Formatting / safe extraction
# ---------------------------------------------------------------------

def _money(value: float) -> str:
    return f"€{float(value):,.0f}"


def _safe_float(value: Any, default: float = 0.0) -> float:
    try:
        if value is None:
            return default
        return float(value)
    except (TypeError, ValueError):
        return default


def _get_attr(obj: Any, *names: str, default: Any = None) -> Any:
    for name in names:
        if obj is not None and hasattr(obj, name):
            return getattr(obj, name)
    return default


def _decision_changes(decision: Any) -> Mapping[str, Any]:
    changes = getattr(decision, "changes", {})
    return changes if isinstance(changes, Mapping) else {}


def _decision_metadata(decision: Any) -> Mapping[str, Any]:
    """
    Accept metadata stored under common V2 names.

    Different Labs may expose metadata under slightly different keys while
    the integration is being completed. This helper keeps this module
    read-only and tolerant without creating a new architecture.
    """
    for attr in ("metadata", "meta", "details", "assumptions"):
        value = getattr(decision, attr, None)
        if isinstance(value, Mapping):
            return value

    return {}


def _all_decisions() -> List[Any]:
    plan = st.session_state.get("decision_plan")
    decisions = getattr(plan, "decisions", ()) if plan is not None else ()

    if decisions:
        return list(decisions)

    return []


def _find_decision(keys: Sequence[str]) -> Optional[Any]:
    wanted = {key.lower() for key in keys}

    for decision in _all_decisions():
        decision_id = str(getattr(decision, "id", "")).lower()
        category = str(getattr(decision, "category", "")).lower()
        name = str(getattr(decision, "name", "")).lower()

        if decision_id in wanted:
            return decision

        if any(key.lower() in category or key.lower() in name for key in wanted):
            return decision

    # Candidate objects may exist before they are placed in the plan.
    for session_key in keys:
        candidate = st.session_state.get(session_key)
        if candidate is not None:
            return candidate

    return None


# ---------------------------------------------------------------------
# Company / projection
# ---------------------------------------------------------------------

def _get_baseline_state(explicit_baseline: Any = None) -> Any:
    if explicit_baseline is not None:
        return explicit_baseline

    # Keep imports local so the module remains importable in isolation.
    try:
        from core.state_builder import StateBuilder
        from core.baseline_repository import BaselineRepository

        builder = StateBuilder(baseline_repository=BaselineRepository)
        return builder.build_baseline_only()
    except Exception:
        return None


def _get_projected_state(baseline_state: Any) -> Any:
    """
    Use the canonical V2 evaluator when it is available.

    Failure here does not fabricate a projection. The module simply falls
    back to the baseline state and clearly labels the result.
    """
    if baseline_state is None:
        return None

    try:
        from core.decision_evaluator import DecisionEvaluator
        from core.decision_plan import DecisionPlan

        plan = st.session_state.get("decision_plan")
        if plan is None:
            plan = DecisionPlan.create(
                plan_id="empty_plan",
                name="Empty Decision Plan",
            )

        evaluation = DecisionEvaluator.evaluate(
            baseline_state=baseline_state,
            plan=plan,
        )
        return evaluation.projected_state
    except Exception:
        return baseline_state


def _annual_operating_values(state: Any) -> Tuple[float, float]:
    if state is None:
        return 0.0, 0.0

    drivers = getattr(state, "drivers", state)

    price = _safe_float(
        _get_attr(drivers, "price", default=0.0)
    )
    volume = _safe_float(
        _get_attr(drivers, "volume", default=0.0)
    )
    variable_cost = _safe_float(
        _get_attr(
            drivers,
            "variable_cost_per_unit",
            "variable_cost",
            default=0.0,
        )
    )

    return price * volume, variable_cost * volume


def _opening_cash(state: Any) -> float:
    if state is None:
        return 0.0

    drivers = getattr(state, "drivers", state)
    return _safe_float(
        _get_attr(drivers, "opening_cash", default=0.0)
    )


def _working_capital_terms(state: Any) -> Tuple[float, float, float]:
    wc = getattr(state, "working_capital", None)

    return (
        _safe_float(_get_attr(wc, "ar_days", default=0.0)),
        _safe_float(_get_attr(wc, "inventory_days", default=0.0)),
        _safe_float(_get_attr(wc, "ap_days", default=0.0)),
    )


# ---------------------------------------------------------------------
# Timing schedule extraction
# ---------------------------------------------------------------------

def _normalise_schedule(
    schedule: Any,
    horizon: int = 6,
) -> Tuple[List[float], List[CashEvent]]:
    """
    Convert common schedule shapes into six monthly amounts.

    Accepted examples:
        [100, 200, ...]
        {"month_1": 100, "month_2": 200}
        [{"month": 1, "amount": 100}, ...]
        {"events": [{"month": 4, "amount": 1000}]}

    Values beyond month 6 are retained as explicit future commitments.
    """
    values = [0.0] * horizon
    beyond: List[CashEvent] = []

    if schedule is None:
        return values, beyond

    if isinstance(schedule, Mapping):
        if "events" in schedule:
            return _normalise_schedule(schedule["events"], horizon)

        month_values = []
        for key, value in schedule.items():
            key_text = str(key).lower().replace("-", "_").replace(" ", "_")

            month_no = None
            for token in key_text.replace("month", "").split("_"):
                if token.isdigit():
                    month_no = int(token)
                    break

            if month_no is not None:
                month_values.append((month_no, _safe_float(value)))

        if month_values:
            for month_no, amount in month_values:
                if 1 <= month_no <= horizon:
                    values[month_no - 1] += amount
                elif month_no > horizon:
                    beyond.append(
                        CashEvent(
                            month_index=month_no - 1,
                            amount=amount,
                            label="Known future commitment",
                            category="future",
                        )
                    )
            return values, beyond

    if isinstance(schedule, Sequence) and not isinstance(schedule, (str, bytes)):
        for item in schedule:
            if isinstance(item, Mapping):
                month = item.get("month", item.get("month_index"))
                amount = item.get("amount", item.get("value", item.get("cash")))
                if month is None or amount is None:
                    continue

                month_no = _safe_float(month)
                amount_value = _safe_float(amount)

                if 1 <= month_no <= horizon:
                    values[int(month_no) - 1] += amount_value
                elif month_no > horizon:
                    beyond.append(
                        CashEvent(
                            month_index=int(month_no) - 1,
                            amount=amount_value,
                            label=str(item.get("label", "Known future commitment")),
                            category=str(item.get("category", "future")),
                        )
                    )
            else:
                # Plain six-element numeric sequence.
                if len(schedule) <= horizon:
                    for i, value in enumerate(schedule):
                        values[i] += _safe_float(value)
                    break

    return values, beyond


def _extract_schedule_from_decision(
    decision: Any,
    schedule_keys: Sequence[str],
) -> Tuple[List[float], List[CashEvent]]:
    if decision is None:
        return [0.0] * 6, []

    changes = _decision_changes(decision)
    metadata = _decision_metadata(decision)

    for source in (metadata, changes):
        for key in schedule_keys:
            if key in source:
                return _normalise_schedule(source[key])

    return [0.0] * 6, []


def _opening_current_asset_balances(
    state: Any,
    annual_sales: float,
    annual_cogs: float,
) -> Tuple[float, float, float]:
    """
    Derive the opening working-capital balances from the locked CompanyState.

    CompanyState stores the policy in days rather than separate opening AR /
    inventory / AP balances. For the cash-timing layer, the standard 365-day
    relationship is therefore used to establish the opening position.
    """
    ar_days, inventory_days, ap_days = _working_capital_terms(state)

    opening_ar = annual_sales * ar_days / 365.0
    opening_inventory = annual_cogs * inventory_days / 365.0
    opening_ap = annual_cogs * ap_days / 365.0

    return opening_ar, opening_inventory, opening_ap


def _schedule_from_payment_days(
    annual_amount: float,
    payment_days: float,
    opening_balance: float = 0.0,
    horizon: int = 6,
) -> List[float]:
    """
    Build a simple steady-state cash-timing schedule.

    The important difference from the previous fallback is that Month 1 does
    not start with a blank working-capital position. Existing receivables /
    payables are already outstanding at the start of the window and therefore
    have to be collected / paid before the new monthly activity reaches cash.

    Example:
        60-day customer terms -> opening AR is collected over Months 1-2;
        new Months 1-2 sales are collected from Month 3 onward.

        30-day supplier terms -> opening AP is paid in Month 1; new monthly
        purchases begin hitting cash from Month 2 onward.

    This remains a fallback. A Decision Lab schedule always takes precedence.
    """
    values = [0.0] * horizon

    if annual_amount <= 0:
        return values

    monthly_amount = annual_amount / 12.0
    lag_days = max(0.0, payment_days)

    if lag_days <= 0:
        for month in range(horizon):
            values[month] += monthly_amount
        return values

    lag_months = max(1, int(round(lag_days / 30.0)))

    # Existing balance is already owed at the start of Month 1. Spread it
    # over the same approximate payment window instead of pretending it does
    # not exist.
    opening_slice = opening_balance / lag_months
    for month in range(min(lag_months, horizon)):
        values[month] += opening_slice

    # New monthly activity reaches cash after the payment lag.
    for source_month in range(horizon):
        target_month = source_month + lag_months
        if target_month < horizon:
            values[target_month] += monthly_amount

    return values


# ---------------------------------------------------------------------
# Inventory events
# ---------------------------------------------------------------------

def _inventory_event_schedule(
    annual_cogs: float,
    inventory_decision: Any,
    horizon: int = 6,
) -> Tuple[List[float], List[CashEvent], str]:
    """
    Prefer explicit inventory order events.

    If the Inventory Lab has only supplied an inventory-days policy, do not
    pretend that the policy itself tells us when a large order is paid.
    Instead, return zero scheduled purchase events and tell the UI that the
    detailed event schedule is still pending integration.
    """
    if inventory_decision is None:
        return [0.0] * horizon, [], "No inventory decision selected."

    schedule, beyond = _extract_schedule_from_decision(
        inventory_decision,
        (
            "purchase_schedule",
            "order_schedule",
            "inventory_purchase_schedule",
            "cash_purchase_schedule",
            "payment_schedule",
            "inventory_events",
            "order_events",
        ),
    )

    if any(schedule) or beyond:
        return schedule, beyond, "Inventory Lab schedule"

    metadata = _decision_metadata(inventory_decision)
    changes = _decision_changes(inventory_decision)

    target_days = None
    for source in (metadata, changes):
        for key in ("inventory_days", "target_inventory_days"):
            if key in source:
                target_days = _safe_float(source[key], default=0.0)
                break
        if target_days is not None:
            break

    if target_days is not None:
        return (
            [0.0] * horizon,
            [],
            "Inventory policy selected; purchase timing requires the Inventory Lab event schedule.",
        )

    return [0.0] * horizon, [], "No inventory cash event available."


# ---------------------------------------------------------------------
# Main cash-plan calculation
# ---------------------------------------------------------------------

def build_cash_plan(
    baseline_state: Any,
    projected_state: Any,
    horizon: int = 6,
    exceptional_events: Optional[Sequence[CashEvent]] = None,
) -> CashPlanResult:
    annual_sales, annual_cogs = _annual_operating_values(projected_state)
    opening_cash = _opening_cash(baseline_state)

    # CompanyState stores working-capital policy as days. For the six-month
    # cash window we first establish the opening AR / inventory / AP position
    # and then roll the new monthly activity forward from that position.
    opening_ar, _opening_inventory, opening_ap = _opening_current_asset_balances(
        baseline_state,
        annual_sales,
        annual_cogs,
    )

    ar_days, inventory_days, ap_days = _working_capital_terms(projected_state)

    # Customer collections:
    # Prefer a decision-specific collection schedule.
    ar_decision = _find_decision(AR_CANDIDATE_KEYS)

    collections, collection_beyond = _extract_schedule_from_decision(
        ar_decision,
        (
            "collection_schedule",
            "collections_schedule",
            "cash_collection_schedule",
            "customer_collection_schedule",
            "receivables_schedule",
        ),
    )

    collection_source = "Receivables / Credit Policy Lab"
    if not any(collections) and not collection_beyond:
        collections = _schedule_from_payment_days(
            annual_sales,
            ar_days,
            opening_balance=opening_ar,
            horizon=horizon,
        )
        collection_source = "Baseline terms fallback"

    # Supplier payments:
    ap_decision = _find_decision(AP_CANDIDATE_KEYS)

    supplier_payments, supplier_beyond = _extract_schedule_from_decision(
        ap_decision,
        (
            "payment_schedule",
            "supplier_payment_schedule",
            "payables_schedule",
            "cash_payment_schedule",
        ),
    )

    payment_source = "Suppliers & Payables Lab"
    if not any(supplier_payments) and not supplier_beyond:
        supplier_payments = _schedule_from_payment_days(
            annual_cogs,
            ap_days,
            opening_balance=opening_ap,
            horizon=horizon,
        )
        payment_source = "Baseline terms fallback"

    # Inventory:
    inventory_decision = _find_decision(INVENTORY_CANDIDATE_KEYS)
    inventory_payments, inventory_beyond, inventory_source = (
        _inventory_event_schedule(
            annual_cogs,
            inventory_decision,
            horizon=horizon,
        )
    )

    # Operating expenses are derived from the projected annual operating model,
    # not entered twelve times.
    fixed_opex = _safe_float(
        _get_attr(
            getattr(projected_state, "drivers", projected_state),
            "fixed_opex",
            default=0.0,
        )
    )
    monthly_opex = fixed_opex / 12.0

    # Known debt service is a baseline/projected obligation, spread only as a
    # regular monthly run-rate. One-off debt events can later be supplied as
    # explicit events.
    capital = getattr(projected_state, "capital_structure", None)
    annual_debt_service = _safe_float(
        _get_attr(capital, "annual_debt_service", default=0.0)
    )
    monthly_debt_service = annual_debt_service / 12.0

    exceptional = list(exceptional_events or [])

    rows: List[Dict[str, Any]] = []
    cash = opening_cash

    for i in range(horizon):
        exceptional_in = sum(
            event.amount
            for event in exceptional
            if event.month_index == i and event.amount >= 0
        )
        exceptional_out = sum(
            abs(event.amount)
            for event in exceptional
            if event.month_index == i and event.amount < 0
        )

        net_cash_flow = (
            collections[i]
            - supplier_payments[i]
            - inventory_payments[i]
            - monthly_opex
            - monthly_debt_service
            + exceptional_in
            - exceptional_out
        )

        opening = cash
        cash += net_cash_flow

        rows.append(
            {
                "Month": MONTHS[i],
                "Opening Cash": opening,
                "Customer Collections": collections[i],
                "Supplier Payments": supplier_payments[i],
                "Inventory Purchases": inventory_payments[i],
                "Operating Expenses": monthly_opex,
                "Debt Service": monthly_debt_service,
                "Exceptional Inflows": exceptional_in,
                "Exceptional Outflows": exceptional_out,
                "Net Cash Flow": net_cash_flow,
                "Closing Cash": cash,
            }
        )

    closing_values = [row["Closing Cash"] for row in rows]
    minimum_cash = min(closing_values) if closing_values else opening_cash
    minimum_index = (
        closing_values.index(minimum_cash)
        if closing_values
        else 0
    )

    funding_gap = max(0.0, -minimum_cash)
    funding_gap_month = (
        MONTHS[minimum_index]
        if funding_gap > 0
        else None
    )

    recovery_month = None
    if funding_gap > 0:
        for i, value in enumerate(closing_values):
            if i > minimum_index and value >= 0:
                recovery_month = MONTHS[i]
                break

    beyond_horizon = (
        collection_beyond
        + supplier_beyond
        + inventory_beyond
    )

    return CashPlanResult(
        opening_cash=opening_cash,
        rows=tuple(rows),
        minimum_cash=minimum_cash,
        minimum_cash_month=MONTHS[minimum_index] if rows else MONTHS[0],
        funding_gap=funding_gap,
        funding_gap_month=funding_gap_month,
        recovery_month=recovery_month,
        beyond_horizon_events=tuple(beyond_horizon),
    )


# ---------------------------------------------------------------------
# UI
# ---------------------------------------------------------------------

def _render_event_input() -> List[CashEvent]:
    st.subheader("Anything the system cannot know?")
    st.caption(
        "Add only exceptional cash events that are not already produced by "
        "another Decision Lab."
    )

    events: List[CashEvent] = []

    enabled = st.checkbox(
        "Add an exceptional event",
        key="cash_management_exceptional_event_enabled",
    )

    if not enabled:
        return events

    c1, c2, c3 = st.columns(3)

    with c1:
        month = st.selectbox(
            "Month",
            options=list(range(1, 7)),
            format_func=lambda x: MONTHS[x - 1],
            key="cash_management_exceptional_month",
        )

    with c2:
        amount = st.number_input(
            "Amount (€)",
            value=0.0,
            step=1000.0,
            format="%.0f",
            key="cash_management_exceptional_amount",
        )

    with c3:
        direction = st.selectbox(
            "Cash direction",
            options=["Outflow", "Inflow"],
            key="cash_management_exceptional_direction",
        )

    label = st.text_input(
        "What is it?",
        value="Exceptional event",
        key="cash_management_exceptional_label",
    )

    signed_amount = (
        abs(amount)
        if direction == "Inflow"
        else -abs(amount)
    )

    if amount != 0:
        events.append(
            CashEvent(
                month_index=month - 1,
                amount=signed_amount,
                label=label or "Exceptional event",
                category="exceptional",
            )
        )

    return events


def render_cash_management_lab(
    baseline_state: Any = None,
) -> None:
    st.title("💧 Cash Management")
    st.caption(
        "See when cash comes in, when it goes out, and where pressure appears."
    )

    baseline = _get_baseline_state(baseline_state)

    if baseline is None:
        st.warning("Please set and confirm the Locked Baseline first.")
        return

    projected = _get_projected_state(baseline)

    plan = st.session_state.get("decision_plan")
    decisions = getattr(plan, "decisions", ()) if plan is not None else ()

    st.info(
        "This is a cash-timing layer — not another company forecast. "
        "Customer collections, supplier payments and inventory events should "
        "come from the relevant Decision Labs."
    )

    if decisions:
        st.caption(
            f"Current Decision Plan: **{getattr(plan, 'name', 'Current Decision Plan')}** "
            f"({len(decisions)} decision(s))"
        )
    else:
        st.caption("No decisions are currently selected. Showing baseline cash timing.")

    exceptional_events = _render_event_input()

    # =========================================================
    # TEMPORARY DEBUG CHECK
    # =========================================================
    st.write("DEBUG projected ar_days:", _working_capital_terms(projected)[0])
    st.write("DEBUG baseline ar_days:", _working_capital_terms(baseline)[0])
    # =========================================================

    result = build_cash_plan(
        baseline_state=baseline,
        projected_state=projected,
        horizon=6,
        exceptional_events=exceptional_events,
    )

    st.divider()
    st.subheader("Cash Consequences — Next 6 Months")

    k1, k2, k3, k4 = st.columns(4)

    k1.metric("Opening Cash", _money(result.opening_cash))
    k2.metric("Minimum Cash", _money(result.minimum_cash))
    k3.metric(
        "Funding Gap",
        _money(result.funding_gap),
    )
    recovery_display = (
        result.recovery_month
        if result.recovery_month is not None
        else ("Beyond 6 months" if result.funding_gap > 0 else "Not required")
    )
    k4.metric("Recovery", recovery_display)

    if result.funding_gap > 0:
        st.error(
            f"Cash falls below zero in **{result.funding_gap_month}**. "
            f"Maximum projected gap: **{_money(result.funding_gap)}**."
        )
    else:
        st.success(
            f"Projected minimum cash is **{_money(result.minimum_cash)}** "
            f"in **{result.minimum_cash_month}**."
        )

    df = pd.DataFrame(list(result.rows))

    display = df.copy()
    money_columns = [
        "Opening Cash",
        "Customer Collections",
        "Supplier Payments",
        "Inventory Purchases",
        "Operating Expenses",
        "Debt Service",
        "Exceptional Inflows",
        "Exceptional Outflows",
        "Net Cash Flow",
        "Closing Cash",
    ]

    for column in money_columns:
        display[column] = display[column].map(_money)

    st.dataframe(
        display,
        use_container_width=True,
        hide_index=True,
    )

    st.divider()
    st.subheader("Where the timing comes from")

    source_rows = [
        {
            "Cash item": "Customer collections",
            "Source": "Receivables / Credit Policy Lab",
            "Status": (
                "Decision schedule"
                if _find_decision(AR_CANDIDATE_KEYS) is not None
                else "Baseline terms fallback"
            ),
        },
        {
            "Cash item": "Supplier payments",
            "Source": "Suppliers & Payables Lab",
            "Status": (
                "Decision schedule"
                if _find_decision(AP_CANDIDATE_KEYS) is not None
                else "Baseline terms fallback"
            ),
        },
        {
            "Cash item": "Inventory purchases",
            "Source": "Inventory Lab",
            "Status": (
                "Decision schedule"
                if any(row["Inventory Purchases"] != 0 for row in result.rows)
                else "Included in supplier-payment timing unless an event schedule exists"
            ),
        },
        {
            "Cash item": "Operating expenses",
            "Source": "Projected CompanyState",
            "Status": "Monthly run-rate",
        },
        {
            "Cash item": "Debt service",
            "Source": "Projected CompanyState",
            "Status": "Monthly run-rate",
        },
        {
            "Cash item": "Exceptional events",
            "Source": "Owner input",
            "Status": "Only when system cannot know",
        },
    ]

    st.dataframe(
        source_rows,
        use_container_width=True,
        hide_index=True,
    )

    if result.beyond_horizon_events:
        st.divider()
        st.subheader("Known commitments beyond Month 6")
        st.caption(
            "These are not forced into Month 6. They remain visible as future commitments."
        )

        future_rows = [
            {
                "Timing": f"Month {event.month_index + 1}",
                "Amount": _money(event.amount),
                "Category": event.category,
                "Description": event.label,
            }
            for event in result.beyond_horizon_events
        ]

        st.dataframe(
            future_rows,
            use_container_width=True,
            hide_index=True,
        )

    st.divider()
    st.caption(
        "V2 principle: Decisions change the company. Diagnostics explain the company. "
        "This layer maps the cash timing of the current decision plan; it does not "
        "create a second independent company model."
    )
