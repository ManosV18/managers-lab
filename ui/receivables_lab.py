from dataclasses import fields, replace
from decimal import Decimal, InvalidOperation, Overflow, getcontext
from uuid import uuid4

import streamlit as st

from core.decision import DecisionFactory
from core.decision_plan import DecisionPlan

AR_CANDIDATE = "wc_ar_candidate"
AR_META = "wc_ar_candidate_meta"

DEFAULT_COLLECTION_SCHEDULE = {
"month_0_pct": 0.20,
"month_1_pct": 0.70,
"month_2_pct": 0.10,
}

# =========================================================

# COLLECTION SCHEDULE

# =========================================================

def _normalise_collection_schedule(
month_0_pct: float,
month_1_pct: float,
month_2_pct: float,
):
values = [
max(0.0, float(month_0_pct)),
max(0.0, float(month_1_pct)),
max(0.0, float(month_2_pct)),
]

```
total = sum(values)

if total <= 0:
    values = [
        DEFAULT_COLLECTION_SCHEDULE["month_0_pct"],
        DEFAULT_COLLECTION_SCHEDULE["month_1_pct"],
        DEFAULT_COLLECTION_SCHEDULE["month_2_pct"],
    ]
    total = sum(values)

return {
    "month_0_pct": values[0] / total,
    "month_1_pct": values[1] / total,
    "month_2_pct": values[2] / total,
}
```

def _format_collection_schedule(schedule):
if not isinstance(schedule, dict):
schedule = DEFAULT_COLLECTION_SCHEDULE

```
return {
    "month_0_pct": float(
        schedule.get(
            "month_0_pct",
            DEFAULT_COLLECTION_SCHEDULE["month_0_pct"],
        )
    ),
    "month_1_pct": float(
        schedule.get(
            "month_1_pct",
            DEFAULT_COLLECTION_SCHEDULE["month_1_pct"],
        )
    ),
    "month_2_pct": float(
        schedule.get(
            "month_2_pct",
            DEFAULT_COLLECTION_SCHEDULE["month_2_pct"],
        )
    ),
}
```

def _attach_collection_schedule(decision, collection_schedule):
"""
Attach the cash-timing schedule to the Decision metadata.

```
Important:
collection_schedule is NOT placed in decision.changes.
decision.changes contains canonical CompanyState driver changes only.
"""

metadata = {
    "collection_schedule": _format_collection_schedule(
        collection_schedule
    )
}

try:
    decision_fields = {
        field.name
        for field in fields(decision)
    }
except TypeError:
    decision_fields = set()

for field_name in (
    "metadata",
    "meta",
    "details",
    "assumptions",
):
    if field_name in decision_fields:
        try:
            current = getattr(
                decision,
                field_name,
                None,
            )

            if isinstance(current, dict):
                merged = dict(current)
                merged.update(metadata)
            else:
                merged = metadata

            return replace(
                decision,
                **{field_name: merged},
            )
        except Exception:
            pass

# Fallback for mutable decision objects.
try:
    current = getattr(
        decision,
        "metadata",
        None,
    )

    if isinstance(current, dict):
        current.update(metadata)
    else:
        setattr(
            decision,
            "metadata",
            metadata,
        )

except Exception:
    pass

return decision
```

def _decision_collection_schedule(decision):
if decision is None:
return None

```
for field_name in (
    "metadata",
    "meta",
    "details",
    "assumptions",
):
    value = getattr(
        decision,
        field_name,
        None,
    )

    if isinstance(value, dict):
        schedule = value.get(
            "collection_schedule"
        )

        if isinstance(schedule, dict):
            return _format_collection_schedule(
                schedule
            )

return None
```

# =========================================================

# DECIMAL HELPERS

# =========================================================

getcontext().prec = 28

def _decimal(value, default="0"):
try:
return Decimal(str(value))
except (
InvalidOperation,
ValueError,
TypeError,
Overflow,
):
return Decimal(default)

# =========================================================

# RECEIVABLES / EARLY PAYMENT DISCOUNT ANALYSIS

# =========================================================

def calculate_discount_npv(
current_annual_sales,
extra_annual_sales,
discount_pct,
adoption_pct,
current_collection_days,
new_collection_days,
annual_cogs,
wacc,
supplier_days,
non_discount_days,
):
"""
Evaluate an early-payment discount policy.

```
This follows the original Receivables model logic.

Important distinction:

1. adoption_pct describes the percentage of CURRENT customers
   who take the discount.

2. When extra sales are introduced, the percentage of TOTAL
   NEW sales under the new policy is recalculated:

       (
           current_sales * adoption
           + extra_sales
       )
       /
       (
           current_sales + extra_sales
       )

   This is the key distinction between the original model
   and the previous simplified implementation.

3. The economic NPV is calculated using discounted cash flows,
   not simply:

       extra_sales_profit
       + released_capital * WACC
       - discount_cost

4. Supplier payment days affect the timing of the COGS cash
   outflow for the incremental sales.

5. Collection schedule is intentionally NOT part of this
   calculation. It belongs to the monthly cash-timing layer.
"""

sales = _decimal(current_annual_sales)
extra_sales = _decimal(extra_annual_sales)

discount = (
    _decimal(discount_pct)
    / Decimal("100")
)

adoption = (
    _decimal(adoption_pct)
    / Decimal("100")
)

current_days = _decimal(
    current_collection_days
)

new_days = _decimal(
    new_collection_days
)

cogs = _decimal(annual_cogs)

discount_rate = _decimal(wacc)

supplier_days_value = _decimal(
    supplier_days
)

non_discount_days_value = _decimal(
    non_discount_days
)

# -----------------------------------------------------
# CURRENT BUSINESS
# -----------------------------------------------------

# Current average collection period.
#
# This is the original model's weighted average:
#
# current discount-taking customers
# + current non-discount customers

avg_current_collection_days = (
    current_days * adoption
    + non_discount_days_value
    * (Decimal("1") - adoption)
)

# Current receivables.

if sales > 0:
    current_receivables = (
        sales
        * avg_current_collection_days
        / Decimal("365")
    )
else:
    current_receivables = Decimal("0")

# -----------------------------------------------------
# NEW BUSINESS MIX
# -----------------------------------------------------

total_new_sales = (
    sales + extra_sales
)

if total_new_sales > 0:
    pct_total_new_sales_under_policy = (
        (
            sales * adoption
        )
        + extra_sales
    ) / total_new_sales
else:
    pct_total_new_sales_under_policy = Decimal(
        "0"
    )

pct_total_new_sales_not_under_policy = (
    Decimal("1")
    - pct_total_new_sales_under_policy
)

# -----------------------------------------------------
# NEW AVERAGE COLLECTION PERIOD
# -----------------------------------------------------

new_avg_collection_period = (
    pct_total_new_sales_under_policy
    * new_days
    +
    pct_total_new_sales_not_under_policy
    * non_discount_days_value
)

# -----------------------------------------------------
# NEW RECEIVABLES
# -----------------------------------------------------

if total_new_sales > 0:
    new_receivables = (
        total_new_sales
        * new_avg_collection_period
        / Decimal("365")
    )
else:
    new_receivables = Decimal("0")

# -----------------------------------------------------
# CAPITAL RELEASED
# -----------------------------------------------------

free_capital = (
    current_receivables
    - new_receivables
)

# -----------------------------------------------------
# VARIABLE COST RATE
# -----------------------------------------------------

if sales > 0:
    variable_cost_rate = (
        cogs / sales
    )
else:
    variable_cost_rate = Decimal("0")

# -----------------------------------------------------
# PROFIT FROM EXTRA SALES
# -----------------------------------------------------

profit_margin_on_extra_sales = (
    Decimal("1")
    - variable_cost_rate
)

profit_from_extra_sales = (
    extra_sales
    * profit_margin_on_extra_sales
)

# -----------------------------------------------------
# PROFIT FROM RELEASED CAPITAL
#
# Kept as a separate diagnostic output because this was
# part of the original model's decomposition.
# -----------------------------------------------------

profit_from_free_capital = (
    free_capital
    * discount_rate
)

# -----------------------------------------------------
# DISCOUNT COST
# -----------------------------------------------------

discount_cost = (
    total_new_sales
    * pct_total_new_sales_under_policy
    * discount
)

# -----------------------------------------------------
# DISCOUNT FACTOR HELPER
#
# Original model:
#
# 1 / (1 + WACC / 365)^days
# -----------------------------------------------------

daily_discount_factor = (
    Decimal("1")
    + discount_rate / Decimal("365")
)

def _discount_factor(days):
    return (
        Decimal("1")
        /
        (
            daily_discount_factor
            ** days
        )
    )

# -----------------------------------------------------
# ECONOMIC NPV
#
# This reproduces the original model:
#
#   total new sales under policy
#   × (1 - discount)
#   × discount factor at new payment days
#
# + total new sales not under policy
#   × discount factor at normal payment days
#
# - incremental COGS
#   × supplier payment discount factor
#
# - current sales
#   × current collection discount factor
#
# -----------------------------------------------------

discounted_sales_under_policy = (
    total_new_sales
    * pct_total_new_sales_under_policy
    * (Decimal("1") - discount)
    * _discount_factor(
        new_days
    )
)

discounted_sales_not_under_policy = (
    total_new_sales
    * pct_total_new_sales_not_under_policy
    * _discount_factor(
        non_discount_days_value
    )
)

incremental_cogs = (
    variable_cost_rate
    * extra_sales
)

discounted_incremental_cogs = (
    incremental_cogs
    * _discount_factor(
        supplier_days_value
    )
)

discounted_current_sales = (
    sales
    * _discount_factor(
        avg_current_collection_days
    )
)

npv = (
    discounted_sales_under_policy
    + discounted_sales_not_under_policy
    - discounted_incremental_cogs
    - discounted_current_sales
)

# -----------------------------------------------------
# MAXIMUM DISCOUNT
#
# Original model formula.
# -----------------------------------------------------

if (
    pct_total_new_sales_under_policy > 0
    and total_new_sales > 0
):
    numerator_component = (
        Decimal("1")
        - (
            Decimal("1")
            / pct_total_new_sales_under_policy
        )
    )

    timing_component = (
        (
            daily_discount_factor
            ** (
                non_discount_days_value
                - avg_current_collection_days
            )
        )
        +
        variable_cost_rate
        * (
            extra_sales / sales
            if sales > 0
            else Decimal("0")
        )
        *
        (
            daily_discount_factor
            ** (
                non_discount_days_value
                - supplier_days_value
            )
        )
    )

    denominator = (
        pct_total_new_sales_under_policy
        *
        (
            Decimal("1")
            + (
                extra_sales / sales
                if sales > 0
                else Decimal("0")
            )
        )
    )

    if denominator > 0:
        max_discount = (
            Decimal("1")
            -
            (
                daily_discount_factor
                ** (
                    new_days
                    - non_discount_days_value
                )
            )
            *
            (
                numerator_component
                +
                (
                    timing_component
                    / denominator
                )
            )
        )
    else:
        max_discount = Decimal("0")
else:
    max_discount = Decimal("0")

# Keep the result economically bounded.

maximum_discount_reported = max(
    Decimal("0"),
    min(
        max_discount,
        Decimal("1"),
    ),
)

# -----------------------------------------------------
# OPTIMUM DISCOUNT
#
# Original model:
#
# 1 -
# (1 + WACC / 365)^(new_days - current_avg_days)
# -----------------------------------------------------

optimum_discount = (
    Decimal("1")
    -
    (
        daily_discount_factor
        ** (
            new_days
            - avg_current_collection_days
        )
    )
) / Decimal("2")

optimum_discount = max(
    Decimal("0"),
    min(
        optimum_discount,
        Decimal("1"),
    ),
)

return {
    # Current position
    "avg_current_collection_days": float(
        avg_current_collection_days
    ),
    "current_receivables": float(
        current_receivables
    ),

    # New business mix
    "total_new_sales": float(
        total_new_sales
    ),
    "pct_total_new_sales_under_policy": float(
        pct_total_new_sales_under_policy
    ),
    "pct_total_new_sales_not_under_policy": float(
        pct_total_new_sales_not_under_policy
    ),

    # New collection position
    "new_avg_collection_period": float(
        new_avg_collection_period
    ),
    "new_receivables": float(
        new_receivables
    ),
    "free_capital": float(
        free_capital
    ),

    # Economic decomposition
    "profit_from_extra_sales": float(
        profit_from_extra_sales
    ),
    "profit_from_free_capital": float(
        profit_from_free_capital
    ),
    "discount_cost": float(
        discount_cost
    ),

    # Discounted economic result
    "npv": float(
        npv
    ),

    # Thresholds
    "max_discount": float(
        maximum_discount_reported
    ),
    "optimum_discount": float(
        optimum_discount
    ),

    # Supporting values
    "variable_cost_rate": float(
        variable_cost_rate
    ),
    "incremental_cogs": float(
        incremental_cogs
    ),
    "supplier_days": float(
        supplier_days_value
    ),
}
```

# =========================================================

# CURRENT DECISION PLAN

# =========================================================

def _get_current_plan():
plan = st.session_state.get(
"decision_plan"
)

```
if isinstance(plan, DecisionPlan):
    return plan

plan = DecisionPlan.create(
    plan_id="main_plan",
    name="Current Decision Plan",
)

st.session_state["decision_plan"] = plan

return plan
```

def _find_conflicting_driver(
plan,
decision,
):
"""
Detect another decision already changing ar_days.
"""

```
target_changes = getattr(
    decision,
    "changes",
    {},
)

if not isinstance(
    target_changes,
    dict,
):
    return None

if "ar_days" not in target_changes:
    return None

for existing in getattr(
    plan,
    "decisions",
    (),
):
    changes = getattr(
        existing,
        "changes",
        {},
    )

    if (
        isinstance(changes, dict)
        and "ar_days" in changes
    ):
        return existing

return None
```

def _add_to_current_plan(
decision,
):
plan = _get_current_plan()

```
conflict = _find_conflicting_driver(
    plan,
    decision,
)

if conflict is not None:
    st.error(
        "Another Receivables decision already changes "
        "the AR policy in the Current Decision Plan."
    )
    return False

existing_ids = {
    getattr(
        item,
        "id",
        None,
    )
    for item in getattr(
        plan,
        "decisions",
        (),
    )
}

decision_id = getattr(
    decision,
    "id",
    None,
)

if decision_id in existing_ids:
    st.info(
        "This decision is already in the Current Decision Plan."
    )
    return False

try:
    st.session_state["decision_plan"] = plan.add(
        decision
    )
    return True

except Exception as exc:
    st.error(
        f"Could not add decision to Current Decision Plan: {exc}"
    )
    return False
```

# =========================================================

# CANDIDATE STATE

# =========================================================

def set_ar_candidate(
decision,
metadata=None,
):
st.session_state[
AR_CANDIDATE
] = decision

```
st.session_state[
    AR_META
] = metadata or {}
```

def clear_ar_candidate():
st.session_state.pop(
AR_CANDIDATE,
None,
)

```
st.session_state.pop(
    AR_META,
    None,
)
```

def get_ar_candidate():
return st.session_state.get(
AR_CANDIDATE
)

# =========================================================

# BASELINE HELPERS

# =========================================================

def _get_revenue(
baseline_state,
):
drivers = baseline_state.drivers

```
return (
    float(drivers.price)
    * float(drivers.volume)
)
```

def _get_volume(
baseline_state,
):
return float(
baseline_state.drivers.volume
)

def _get_variable_cost(
baseline_state,
):
return float(
baseline_state
.drivers
.variable_cost_per_unit
)

def _get_annual_cogs(
baseline_state,
):
return (
_get_volume(
baseline_state
)
*
_get_variable_cost(
baseline_state
)
)

# =========================================================

# MAIN UI

# =========================================================

def render_receivables_lab(
baseline_state,
):
st.title(
"💶 Receivables Lab"
)

```
wc = baseline_state.working_capital

current_ar_days = float(
    wc.ar_days
)

annual_sales = _get_revenue(
    baseline_state
)

annual_cogs = _get_annual_cogs(
    baseline_state
)

st.markdown(
    """
    Evaluate customer credit and collection policies
    without changing the locked baseline.

    The decision changes the central **AR days** driver.
    The collection schedule is used only by the monthly
    cash-timing layer.
    """
)

# =====================================================
# CURRENT STATE
# =====================================================

st.subheader(
    "Current Receivables Position"
)

c1, c2, c3 = st.columns(3)

c1.metric(
    "Current AR Days",
    f"{current_ar_days:.1f}",
)

c2.metric(
    "Annual Sales",
    f"€{annual_sales:,.0f}",
)

# Current AR position uses the baseline AR days.
current_receivables = (
    annual_sales
    * current_ar_days
    / 365.0
)

c3.metric(
    "Estimated Receivables",
    f"€{current_receivables:,.0f}",
)

st.divider()

# =====================================================
# MANUAL COLLECTION POLICY
# =====================================================

st.subheader(
    "1. Set a Collection Policy"
)

st.caption(
    "The 20% / 70% / 10% pattern is only the default. "
    "You can change it to reflect how your customers actually pay."
)

target_ar_days = st.number_input(
    "Target Collection Time (days)",
    min_value=0.0,
    max_value=365.0,
    value=float(
        current_ar_days
    ),
    step=1.0,
    key="receivables_target_ar_days",
)

st.markdown(
    "**Collection timing**"
)

s1, s2, s3 = st.columns(3)

with s1:
    month_0 = st.number_input(
        "Same Month (%)",
        min_value=0.0,
        max_value=100.0,
        value=20.0,
        step=5.0,
        key="receivables_month_0_pct",
    )

with s2:
    month_1 = st.number_input(
        "Next Month (%)",
        min_value=0.0,
        max_value=100.0,
        value=70.0,
        step=5.0,
        key="receivables_month_1_pct",
    )

with s3:
    month_2 = st.number_input(
        "Month +2 (%)",
        min_value=0.0,
        max_value=100.0,
        value=10.0,
        step=5.0,
        key="receivables_month_2_pct",
    )

collection_schedule = (
    _normalise_collection_schedule(
        month_0,
        month_1,
        month_2,
    )
)

schedule_total = (
    month_0
    + month_1
    + month_2
)

if abs(
    schedule_total - 100.0
) > 0.01:
    st.caption(
        f"Entered pattern totals {schedule_total:.1f}%. "
        "The system will normalise it to 100%."
    )

st.info(
    "This collection schedule is a cash-timing assumption. "
    "It does not replace AR days in CompanyState."
)

if st.button(
    "Use This Collection Policy",
    key="receivables_use_manual_policy",
    use_container_width=True,
):
    try:
        decision = (
            DecisionFactory.ar_days_change(
                decision_id=(
                    f"ar_{uuid4().hex[:8]}"
                ),
                target_ar_days=float(
                    target_ar_days
                ),
            )
        )
    except TypeError:
        decision = (
            DecisionFactory.ar_days_change(
                f"ar_{uuid4().hex[:8]}",
                float(
                    target_ar_days
                ),
            )
        )

    decision = _attach_collection_schedule(
        decision,
        collection_schedule,
    )

    set_ar_candidate(
        decision,
        metadata={
            "source": "receivables_lab",
            "method": "Collection Policy",
            "ar_days": float(
                target_ar_days
            ),
            "baseline_ar_days": float(
                current_ar_days
            ),
            "collection_schedule": (
                collection_schedule
            ),
        },
    )

    st.success(
        "Collection policy is ready as a Receivables candidate."
    )

    st.rerun()

# =====================================================
# EARLY PAYMENT DISCOUNT
# =====================================================

st.divider()

st.subheader(
    "2. Early-Payment Discount Analysis"
)

st.caption(
    "Test whether faster customer payment justifies the cost "
    "of an early-payment discount."
)

d1, d2, d3 = st.columns(3)

with d1:
    extra_sales = st.number_input(
        "Additional Annual Sales (€)",
        min_value=0.0,
        value=0.0,
        step=10000.0,
        key="receivables_extra_sales",
    )

with d2:
    discount_pct = st.number_input(
        "Discount (%)",
        min_value=0.0,
        max_value=100.0,
        value=2.0,
        step=0.5,
        key="receivables_discount_pct",
    )

with d3:
    adoption_pct = st.number_input(
        "Customers Using Discount (%)",
        min_value=0.0,
        max_value=100.0,
        value=50.0,
        step=5.0,
        key="receivables_adoption_pct",
    )

e1, e2, e3 = st.columns(3)

with e1:
    discount_days = st.number_input(
        "Payment Days with Discount",
        min_value=0.0,
        max_value=365.0,
        value=15.0,
        step=1.0,
        key="receivables_discount_days",
    )

with e2:
    non_discount_days = st.number_input(
        "Payment Days without Discount",
        min_value=0.0,
        max_value=365.0,
        value=float(
            current_ar_days
        ),
        step=1.0,
        key="receivables_non_discount_days",
    )

with e3:
    supplier_days = st.number_input(
        "Supplier Payment Days",
        min_value=0.0,
        max_value=365.0,
        value=float(
            baseline_state
            .working_capital
            .ap_days
        ),
        step=1.0,
        key="receivables_supplier_days",
    )

f1, f2 = st.columns(2)

with f1:
    wacc = st.number_input(
        "WACC (%)",
        min_value=0.0,
        max_value=100.0,
        value=float(
            baseline_state
            .capital_structure
            .wacc
        ) * 100.0,
        step=0.5,
        key="receivables_wacc",
    )

with f2:
    st.metric(
        "Annual COGS",
        f"€{annual_cogs:,.0f}",
    )

if st.button(
    "Analyze Discount Policy",
    key="receivables_analyze_discount",
    use_container_width=True,
):
    result = calculate_discount_npv(
        current_annual_sales=annual_sales,
        extra_annual_sales=extra_sales,
        discount_pct=discount_pct,
        adoption_pct=adoption_pct,
        current_collection_days=current_ar_days,
        new_collection_days=discount_days,
        annual_cogs=annual_cogs,
        wacc=wacc / 100.0,
        supplier_days=supplier_days,
        non_discount_days=non_discount_days,
    )

    st.session_state[
        "receivables_discount_result"
    ] = result

result = st.session_state.get(
    "receivables_discount_result"
)

if result is not None:
    st.divider()

    st.subheader(
        "Discount Policy Result"
    )

    r1, r2, r3, r4 = st.columns(4)

    r1.metric(
        "New Avg. Collection",
        f"{result['new_avg_collection_period']:.1f} days",
    )

    r2.metric(
        "Receivables Released",
        f"€{result['free_capital']:,.0f}",
    )

    r3.metric(
        "Discount Cost",
        f"€{result['discount_cost']:,.0f}",
    )

    r4.metric(
        "Economic NPV",
        f"€{result['npv']:,.0f}",
    )

    if result["npv"] > 0:
        st.success(
            "Under these assumptions, the policy produces a "
            "positive economic contribution."
        )
    elif result["npv"] < 0:
        st.warning(
            "Under these assumptions, the cost of the policy "
            "exceeds its calculated economic benefit."
        )
    else:
        st.info(
            "The calculated economic effect is approximately neutral."
        )

    # -------------------------------------------------
    # SUPPORTING ECONOMIC OUTPUTS
    # -------------------------------------------------

    st.markdown(
        "### Economic Detail"
    )

    x1, x2, x3, x4 = st.columns(4)

    x1.metric(
        "New Sales",
        f"€{result['total_new_sales']:,.0f}",
    )

    x2.metric(
        "Sales Under New Policy",
        f"{result['pct_total_new_sales_under_policy']:.0%}",
    )

    x3.metric(
        "Profit from Extra Sales",
        f"€{result['profit_from_extra_sales']:,.0f}",
    )

    x4.metric(
        "Capital Benefit",
        f"€{result['profit_from_free_capital']:,.0f}",
    )

    y1, y2 = st.columns(2)

    with y1:
        st.metric(
            "Maximum Discount",
            f"{result['max_discount']:.2%}",
        )

    with y2:
        st.metric(
            "Indicative Optimum Discount",
            f"{result['optimum_discount']:.2%}",
        )

    st.caption(
        "The maximum and optimum discount calculations follow "
        "the original Receivables model. They are separate from "
        "the monthly cash collection schedule."
    )

    # -------------------------------------------------
    # COLLECTION TIMING
    # -------------------------------------------------

    st.markdown(
        "### Collection timing for the cash model"
    )

    st.caption(
        "This schedule determines when the monthly cash-flow layer "
        "recognises customer collections."
    )

    q1, q2, q3 = st.columns(3)

    with q1:
        discount_month_0 = st.number_input(
            "Same Month (%)",
            min_value=0.0,
            max_value=100.0,
            value=20.0,
            step=5.0,
            key=(
                "receivables_discount_month_0_pct"
            ),
        )

    with q2:
        discount_month_1 = st.number_input(
            "Next Month (%)",
            min_value=0.0,
            max_value=100.0,
            value=70.0,
            step=5.0,
            key=(
                "receivables_discount_month_1_pct"
            ),
        )

    with q3:
        discount_month_2 = st.number_input(
            "Month +2 (%)",
            min_value=0.0,
            max_value=100.0,
            value=10.0,
            step=5.0,
            key=(
                "receivables_discount_month_2_pct"
            ),
        )

    discount_collection_schedule = (
        _normalise_collection_schedule(
            discount_month_0,
            discount_month_1,
            discount_month_2,
        )
    )

    discount_schedule_total = (
        discount_month_0
        + discount_month_1
        + discount_month_2
    )

    if abs(
        discount_schedule_total - 100.0
    ) > 0.01:
        st.caption(
            f"Entered pattern totals "
            f"{discount_schedule_total:.1f}%. "
            "The system will normalise it to 100%."
        )

    if st.button(
        "Use This Collection Policy",
        key="receivables_use_discount_policy",
        use_container_width=True,
    ):
        try:
            decision = (
                DecisionFactory.ar_days_change(
                    decision_id=(
                        f"ar_{uuid4().hex[:8]}"
                    ),
                    target_ar_days=float(
                        result[
                            "new_avg_collection_period"
                        ]
                    ),
                )
            )
        except TypeError:
            decision = (
                DecisionFactory.ar_days_change(
                    f"ar_{uuid4().hex[:8]}",
                    float(
                        result[
                            "new_avg_collection_period"
                        ]
                    ),
                )
            )

        decision = _attach_collection_schedule(
            decision,
            discount_collection_schedule,
        )

        set_ar_candidate(
            decision,
            metadata={
                "source": "receivables_lab",
                "method": "Early Payment Discount",
                "ar_days": float(
                    result[
                        "new_avg_collection_period"
                    ]
                ),
                "baseline_ar_days": float(
                    current_ar_days
                ),
                "collection_schedule": (
                    discount_collection_schedule
                ),
                "npv": float(
                    result["npv"]
                ),
                "free_capital": float(
                    result["free_capital"]
                ),
                "discount_cost": float(
                    result["discount_cost"]
                ),
                "max_discount": float(
                    result["max_discount"]
                ),
                "optimum_discount": float(
                    result["optimum_discount"]
                ),
                "pct_total_new_sales_under_policy": float(
                    result[
                        "pct_total_new_sales_under_policy"
                    ]
                ),
            },
        )

        st.success(
            "Discount-based collection policy is ready as a Receivables candidate."
        )

        st.rerun()

# =====================================================
# ACTIVE CANDIDATE
# =====================================================

st.divider()

st.subheader(
    "3. Active Receivables Decision Candidate"
)

candidate = get_ar_candidate()

if candidate is None:
    st.info(
        "No active Receivables decision candidate."
    )

else:
    metadata = st.session_state.get(
        AR_META,
        {},
    )

    changes = getattr(
        candidate,
        "changes",
        {},
    )

    candidate_ar_days = None

    if isinstance(
        changes,
        dict,
    ):
        candidate_ar_days = changes.get(
            "ar_days"
        )

    if candidate_ar_days is None:
        candidate_ar_days = metadata.get(
            "ar_days"
        )

    schedule = (
        _decision_collection_schedule(
            candidate
        )
        or metadata.get(
            "collection_schedule"
        )
        or DEFAULT_COLLECTION_SCHEDULE
    )

    st.success(
        f"**Target AR Days:** "
        f"{float(candidate_ar_days):.1f}"
    )

    method = metadata.get(
        "method"
    )

    if method:
        st.write(
            f"**Method:** {method}"
        )

    st.write(
        "**Cash Collection Schedule:** "
        f"{schedule['month_0_pct']:.0%} same month / "
        f"{schedule['month_1_pct']:.0%} next month / "
        f"{schedule['month_2_pct']:.0%} month +2"
    )

    if "npv" in metadata:
        st.write(
            f"**Calculated Economic NPV:** "
            f"€{float(metadata['npv']):,.0f}"
        )

    if "free_capital" in metadata:
        st.write(
            f"**Estimated Cash Released:** "
            f"€{float(metadata['free_capital']):,.0f}"
        )

    if "max_discount" in metadata:
        st.write(
            f"**Maximum Discount:** "
            f"{float(metadata['max_discount']):.2%}"
        )

    if "optimum_discount" in metadata:
        st.write(
            f"**Indicative Optimum Discount:** "
            f"{float(metadata['optimum_discount']):.2%}"
        )

    b1, b2 = st.columns(2)

    with b1:
        if st.button(
            "➕ Add to Current Decision Plan",
            key="receivables_add_to_plan",
            use_container_width=True,
        ):
            if _add_to_current_plan(
                candidate
            ):
                st.success(
                    "Receivables decision added to Current Decision Plan."
                )

                clear_ar_candidate()

                st.rerun()

    with b2:
        if st.button(
            "Clear Candidate",
            key="receivables_clear_candidate",
            use_container_width=True,
        ):
            clear_ar_candidate()

            st.rerun()

# =====================================================
# V2 LOGIC
# =====================================================

st.divider()

st.subheader(
    "How this connects to Managers Lab V2"
)

st.markdown(
    """
    **AR days** → canonical working-capital driver in `CompanyState`.

    **Collection schedule** → monthly cash-timing assumption used by
    Managing Current Assets / Cash Management.

    The schedule does **not** create another receivables model and does
    not replace the Financial Engine's AR-days calculation.

    **Early-payment discount analysis** → economic decision analysis
    performed from the locked baseline inputs. It does not modify the
    baseline directly.

    **Current Decision Plan** → receives only the canonical AR-days
    decision. The collection schedule remains decision metadata for the
    monthly cash-timing layer.
    """
)
