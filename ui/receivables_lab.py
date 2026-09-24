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


def _format_collection_schedule(schedule):
    if not isinstance(schedule, dict):
        schedule = DEFAULT_COLLECTION_SCHEDULE

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


def _attach_collection_schedule(decision, collection_schedule):
    """
    Attach the cash-timing schedule to the Decision metadata.

    IMPORTANT:
    collection_schedule is NOT placed in decision.changes.

    decision.changes contains canonical CompanyState driver
    changes only.

    The schedule is a separate cash-timing assumption.
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


def _decision_collection_schedule(decision):
    if decision is None:
        return None

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
# RECEIVABLES / DISCOUNT ANALYSIS
# =========================================================

def calculate_discount_npv(
    current_annual_sales,
    extra_annual_sales,
    discount_pct,
    adoption_pct,
    current_discount_days,
    current_non_discount_days,
    new_collection_days,
    annual_cogs,
    wacc,
    supplier_days,
):
    """
    ORIGINAL RECEIVABLES / DISCOUNT ECONOMIC MODEL.

    IMPORTANT:
    The formulas in this function are deliberately kept separate
    from the collection schedule.

    The collection schedule is ONLY a cash-timing assumption and
    does not participate in the NPV calculation.

    Core model:

        current_collection_days =
            current_discount_days * adoption
            + current_non_discount_days * (1 - adoption)

        current_receivables =
            current_sales * current_collection_days / 365

        pct_new_policy =
            (
                current_sales * adoption
                + extra_sales
            ) / (current_sales + extra_sales)

        new_avg_collection_period =
            pct_new_policy * new_collection_days
            + (1 - pct_new_policy)
              * current_non_discount_days

        new_receivables =
            (
                (current_sales + extra_sales)
                * new_avg_collection_period
                / 365
            )

        free_capital =
            current_receivables - new_receivables

        extra_sales_profit =
            extra_sales
            * (1 - COGS / current_sales)

        free_capital_profit =
            free_capital * WACC

        discount_cost =
            (current_sales + extra_sales)
            * pct_new_policy
            * discount

        NPV =
            discounted cash inflows
            - discounted incremental COGS
            - discounted current-sales receivables value

    These formulas intentionally match the original model supplied
    for the Receivables Lab.
    """

    sales = _decimal(
        current_annual_sales
    )

    extra_sales = _decimal(
        extra_annual_sales
    )

    discount = (
        _decimal(discount_pct)
        / Decimal("100")
    )

    adoption = (
        _decimal(adoption_pct)
        / Decimal("100")
    )

    current_discount_days = _decimal(
        current_discount_days
    )

    current_non_discount_days = _decimal(
        current_non_discount_days
    )

    new_days = _decimal(
        new_collection_days
    )

    cogs = _decimal(
        annual_cogs
    )

    discount_rate = _decimal(
        wacc
    )

    supplier_days_value = _decimal(
        supplier_days
    )

    # =====================================================
    # CURRENT COLLECTION PERIOD
    # =====================================================
    #
    # EXACT ORIGINAL FORMULA:
    #
    # current discount clients * adoption
    # +
    # current non-discount clients * (1 - adoption)
    #
    # Example:
    # 60 * 40% + 120 * 60% = 96
    #

    avg_current_collection_days = (
        current_discount_days * adoption
        + current_non_discount_days
        * (Decimal("1") - adoption)
    )

    # =====================================================
    # CURRENT RECEIVABLES
    # =====================================================
    #
    # EXACT ORIGINAL FORMULA:
    #
    # current_sales
    # * avg_current_collection_days
    # / 365
    #

    current_receivables = (
        sales
        * avg_current_collection_days
        / Decimal("365")
    )

    # =====================================================
    # NEW POLICY SHARE
    # =====================================================
    #
    # EXACT ORIGINAL FORMULA:
    #
    # ((current_sales * adoption) + extra_sales)
    # /
    # (current_sales + extra_sales)
    #
    # Example:
    # ((1000 * 40%) + 250) / 1250
    # = 650 / 1250
    # = 52%
    #

    denominator_sales = (
        sales + extra_sales
    )

    if denominator_sales > 0:
        pct_new_policy = (
            (
                sales * adoption
                + extra_sales
            )
            / denominator_sales
        )
    else:
        pct_new_policy = Decimal("0")

    pct_not_new_policy = (
        Decimal("1")
        - pct_new_policy
    )

    # =====================================================
    # NEW AVERAGE COLLECTION PERIOD
    # =====================================================
    #
    # EXACT ORIGINAL FORMULA:
    #
    # pct_new_policy * new_days
    # +
    # (1 - pct_new_policy)
    # * current_non_discount_days
    #
    # Example:
    # 52% * 10 + 48% * 120
    # = 63.2
    #

    new_avg_collection_period = (
        pct_new_policy * new_days
        + pct_not_new_policy
        * current_non_discount_days
    )

    # =====================================================
    # NEW RECEIVABLES
    # =====================================================
    #
    # EXACT ORIGINAL FORMULA:
    #
    # ((current_sales + extra_sales)
    #  * new_avg_collection_period)
    # / 365
    #

    new_receivables = (
        denominator_sales
        * new_avg_collection_period
        / Decimal("365")
    )

    # =====================================================
    # FREE CAPITAL
    # =====================================================

    free_capital = (
        current_receivables
        - new_receivables
    )

    # =====================================================
    # EXTRA SALES PROFIT
    # =====================================================
    #
    # EXACT ORIGINAL FORMULA:
    #
    # extra_sales
    # * (1 - COGS / current_sales)
    #
    #

    if sales > 0:
        variable_cost_rate = (
            cogs / sales
        )
    else:
        variable_cost_rate = Decimal("0")

    profit_from_extra_sales = (
        extra_sales
        * (
            Decimal("1")
            - variable_cost_rate
        )
    )

    # =====================================================
    # FREE CAPITAL PROFIT
    # =====================================================
    #
    # EXACT ORIGINAL FORMULA:
    #
    # free_capital * WACC
    #

    profit_from_free_capital = (
        free_capital
        * discount_rate
    )

    # =====================================================
    # DISCOUNT COST
    # =====================================================
    #
    # EXACT ORIGINAL FORMULA:
    #
    # (current_sales + extra_sales)
    # * pct_new_policy
    # * discount_trial
    #

    discount_cost = (
        denominator_sales
        * pct_new_policy
        * discount
    )

    # =====================================================
    # NPV
    # =====================================================
    #
    # EXACT ORIGINAL FORMULA:
    #
    # (current_sales + extra_sales)
    # * pct_new_policy
    # * (1 - discount)
    # * [1 / (1 + WACC/365)^new_days]
    #
    # +
    #
    # (current_sales + extra_sales)
    # * (1 - pct_new_policy)
    # * [1 / (1 + WACC/365)^non_discount_days]
    #
    # -
    #
    # (COGS/current_sales)
    # * (extra_sales/current_sales)
    # * current_sales
    # * [1 / (1 + WACC/365)^supplier_days]
    #
    # -
    #
    # current_sales
    # * [1 / (1 + WACC/365)^avg_current_collection_days]
    #
    # =====================================================

    daily_discount_factor = (
        Decimal("1")
        + (
            discount_rate
            / Decimal("365")
        )
    )

    pv_discount_clients = (
        denominator_sales
        * pct_new_policy
        * (
            Decimal("1")
            - discount
        )
        / (
            daily_discount_factor
            ** new_days
        )
    )

    pv_non_discount_clients = (
        denominator_sales
        * pct_not_new_policy
        / (
            daily_discount_factor
            ** current_non_discount_days
        )
    )

    if sales > 0:
        pv_extra_sales_cogs = (
            (cogs / sales)
            * (extra_sales / sales)
            * sales
            / (
                daily_discount_factor
                ** supplier_days_value
            )
        )
    else:
        pv_extra_sales_cogs = Decimal("0")

    pv_current_sales = (
        sales
        / (
            daily_discount_factor
            ** avg_current_collection_days
        )
    )

    npv = (
        pv_discount_clients
        + pv_non_discount_clients
        - pv_extra_sales_cogs
        - pv_current_sales
    )

    # =====================================================
    # MAXIMUM DISCOUNT
    # =====================================================
    #
    # EXACT ORIGINAL FORMULA:
    #
    # 1 -
    # (1 + WACC/365)
    # ^(new_days - non_discount_days)
    #
    # *
    # (
    #   (
    #       1 - (1 / pct_new_policy)
    #   )
    #   +
    #   (
    #       (
    #           (1 + WACC/365)
    #           ^(non_discount_days - avg_current_days)
    #       )
    #       +
    #       (
    #           COGS/current_sales
    #       )
    #       *
    #       (
    #           extra_sales/current_sales
    #       )
    #       *
    #       (
    #           1 + WACC/365
    #       )
    #       ^(non_discount_days - supplier_days)
    #   )
    #   /
    #   (
    #       pct_new_policy
    #       *
    #       (1 + extra_sales/current_sales)
    #   )
    # )
    #

    if (
        sales > 0
        and pct_new_policy > 0
    ):
        max_discount = (
            Decimal("1")
            - (
                daily_discount_factor
                ** (
                    new_days
                    - current_non_discount_days
                )
            )
            * (
                (
                    Decimal("1")
                    - (
                        Decimal("1")
                        / pct_new_policy
                    )
                )
                + (
                    (
                        daily_discount_factor
                        ** (
                            current_non_discount_days
                            - avg_current_collection_days
                        )
                    )
                    + (
                        cogs / sales
                    )
                    * (
                        extra_sales / sales
                    )
                    * (
                        daily_discount_factor
                        ** (
                            current_non_discount_days
                            - supplier_days_value
                        )
                    )
                )
                / (
                    pct_new_policy
                    * (
                        Decimal("1")
                        + (
                            extra_sales / sales
                        )
                    )
                )
            )
        )
    else:
        max_discount = Decimal("0")

    # =====================================================
    # OPTIMUM DISCOUNT
    # =====================================================
    #
    # EXACT ORIGINAL FORMULA:
    #
    # (
    #   1 -
    #   (1 + WACC/365)
    #   ^(new_days - avg_current_days)
    # )
    # / 2
    #

    optimum_discount = (
        Decimal("1")
        - (
            daily_discount_factor
            ** (
                new_days
                - avg_current_collection_days
            )
        )
    ) / Decimal("2")

    # =====================================================
    # RETURN
    # =====================================================

    return {
        "avg_current_collection_days": float(
            avg_current_collection_days
        ),
        "current_receivables": float(
            current_receivables
        ),
        "pct_new_policy": float(
            pct_new_policy * Decimal("100")
        ),
        "pct_not_new_policy": float(
            pct_not_new_policy * Decimal("100")
        ),
        "new_avg_collection_period": float(
            new_avg_collection_period
        ),
        "new_receivables": float(
            new_receivables
        ),
        "free_capital": float(
            free_capital
        ),
        "profit_from_extra_sales": float(
            profit_from_extra_sales
        ),
        "profit_from_free_capital": float(
            profit_from_free_capital
        ),
        "discount_cost": float(
            discount_cost
        ),
        "npv": float(
            npv
        ),
        "max_discount": float(
            max_discount
        ),
        "optimum_discount": float(
            optimum_discount
        ),
        "supplier_days": float(
            supplier_days_value
        ),
        "current_discount_days": float(
            current_discount_days
        ),
        "current_non_discount_days": float(
            current_non_discount_days
        ),
        "new_collection_days": float(
            new_days
        ),
    }


# =========================================================
# CURRENT DECISION PLAN
# =========================================================

def _get_current_plan():
    plan = st.session_state.get(
        "decision_plan"
    )

    if isinstance(plan, DecisionPlan):
        return plan

    plan = DecisionPlan.create(
        plan_id="main_plan",
        name="Current Decision Plan",
    )

    st.session_state[
        "decision_plan"
    ] = plan

    return plan


def _find_conflicting_driver(
    plan,
    decision,
):
    """
    Detect another decision already changing ar_days.
    """

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


def _add_to_current_plan(
    decision,
):
    plan = _get_current_plan()

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
        st.session_state[
            "decision_plan"
        ] = plan.add(
            decision
        )

        return True

    except Exception as exc:
        st.error(
            f"Could not add decision to Current Decision Plan: {exc}"
        )

        return False


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

    st.session_state[
        AR_META
    ] = metadata or {}


def clear_ar_candidate():
    st.session_state.pop(
        AR_CANDIDATE,
        None,
    )

    st.session_state.pop(
        AR_META,
        None,
    )


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

    return (
        float(drivers.price)
        * float(drivers.volume)
    )


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
        * _get_variable_cost(
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

        The economic Receivables calculation and the monthly
        cash collection schedule are separate.

        **Economic value** determines whether the policy makes
        financial sense.

        **Collection timing** determines when cash actually
        enters the monthly cash-flow layer.
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
    # COLLECTION SCHEDULE
    # =====================================================

    st.subheader(
        "1. Collection Schedule"
    )

    st.caption(
        "This is the cash-timing assumption only. "
        "It does not enter the Receivables NPV calculation."
    )

    st.markdown(
        """
        The schedule answers:

        **When will the money actually arrive?**

        It is independent from the economic test of the
        receivables policy.
        """
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
            f"Entered pattern totals "
            f"{schedule_total:.1f}%. "
            "The system will normalise it to 100%."
        )

    st.info(
        "The collection schedule is used only by the "
        "monthly cash-timing layer. It does not replace "
        "AR days and does not change the NPV."
    )

    # =====================================================
    # EARLY PAYMENT DISCOUNT
    # =====================================================

    st.divider()

    st.subheader(
        "2. Early-Payment Discount Analysis"
    )

    st.caption(
        "This is the economic test of the policy. "
        "The formulas below are independent of the collection schedule."
    )

    # -----------------------------------------------------
    # SALES / DISCOUNT
    # -----------------------------------------------------

    d1, d2, d3 = st.columns(3)

    with d1:
        extra_sales = st.number_input(
            "Additional Annual Sales (€)",
            min_value=0.0,
            value=250.0,
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
            "Customers Taking Discount (%)",
            min_value=0.0,
            max_value=100.0,
            value=40.0,
            step=5.0,
            key="receivables_adoption_pct",
        )

    # -----------------------------------------------------
    # PAYMENT DAYS
    # -----------------------------------------------------

    e1, e2, e3 = st.columns(3)

    with e1:
        current_discount_days = st.number_input(
            "Current Payment Days — Discount Clients",
            min_value=0.0,
            max_value=365.0,
            value=60.0,
            step=1.0,
            key="receivables_current_discount_days",
        )

    with e2:
        current_non_discount_days = st.number_input(
            "Current Payment Days — Non-Discount Clients",
            min_value=0.0,
            max_value=365.0,
            value=120.0,
            step=1.0,
            key="receivables_current_non_discount_days",
        )

    with e3:
        new_collection_days = st.number_input(
            "New Payment Days — Discount Clients",
            min_value=0.0,
            max_value=365.0,
            value=10.0,
            step=1.0,
            key="receivables_new_discount_days",
        )

    # -----------------------------------------------------
    # COST OF CAPITAL / SUPPLIERS
    # -----------------------------------------------------

    f1, f2, f3 = st.columns(3)

    with f1:
        wacc = st.number_input(
            "WACC (%)",
            min_value=0.0,
            max_value=100.0,
            value=20.0,
            step=0.5,
            key="receivables_wacc",
        )

    with f2:
        supplier_days = st.number_input(
            "Average Days to Pay Suppliers",
            min_value=0.0,
            max_value=365.0,
            value=30.0,
            step=1.0,
            key="receivables_supplier_days",
        )

    with f3:
        st.metric(
            "Annual COGS",
            f"€{annual_cogs:,.0f}",
        )

    # =====================================================
    # ANALYZE
    # =====================================================

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
            current_discount_days=current_discount_days,
            current_non_discount_days=(
                current_non_discount_days
            ),
            new_collection_days=new_collection_days,
            annual_cogs=annual_cogs,
            wacc=wacc / 100.0,
            supplier_days=supplier_days,
        )

        st.session_state[
            "receivables_discount_result"
        ] = result

    result = st.session_state.get(
        "receivables_discount_result"
    )

    if result is not None:

        # =================================================
        # RESULT
        # =================================================

        st.divider()

        st.subheader(
            "Discount Policy Result"
        )

        r1, r2, r3, r4 = st.columns(4)

        r1.metric(
            "Current Collection",
            f"{result['avg_current_collection_days']:.1f} days",
        )

        r2.metric(
            "New Avg. Collection",
            f"{result['new_avg_collection_period']:.1f} days",
        )

        r3.metric(
            "Free Capital",
            f"€{result['free_capital']:,.2f}",
        )

        r4.metric(
            "Economic NPV",
            f"€{result['npv']:,.2f}",
        )

        # -------------------------------------------------
        # SECOND ROW
        # -------------------------------------------------

        r5, r6, r7, r8 = st.columns(4)

        r5.metric(
            "Current Receivables",
            f"€{result['current_receivables']:,.2f}",
        )

        r6.metric(
            "New Receivables",
            f"€{result['new_receivables']:,.2f}",
        )

        r7.metric(
            "Discount Cost",
            f"€{result['discount_cost']:,.2f}",
        )

        r8.metric(
            "New Policy Share",
            f"{result['pct_new_policy']:.1f}%",
        )

        # -------------------------------------------------
        # ECONOMIC COMPONENTS
        # -------------------------------------------------

        st.markdown(
            "### Economic Components"
        )

        ec1, ec2, ec3 = st.columns(3)

        ec1.metric(
            "Extra-Sales Profit",
            f"€{result['profit_from_extra_sales']:,.2f}",
        )

        ec2.metric(
            "Free-Capital Profit",
            f"€{result['profit_from_free_capital']:,.2f}",
        )

        ec3.metric(
            "Discount Cost",
            f"€{result['discount_cost']:,.2f}",
        )

        # -------------------------------------------------
        # DISCOUNT BOUNDARIES
        # -------------------------------------------------

        st.markdown(
            "### Discount Economics"
        )

        dc1, dc2 = st.columns(2)

        dc1.metric(
            "Maximum Discount",
            f"{result['max_discount'] * 100:.2f}%",
        )

        dc2.metric(
            "Optimum Discount",
            f"{result['optimum_discount'] * 100:.2f}%",
        )

        if result["npv"] > 0:
            st.success(
                "Under these assumptions, the tested policy "
                "has positive economic value."
            )
        elif result["npv"] < 0:
            st.warning(
                "Under these assumptions, the tested policy "
                "has negative economic value."
            )
        else:
            st.info(
                "The calculated economic effect is approximately neutral."
            )

        # =================================================
        # COLLECTION SCHEDULE FOR CASH MODEL
        # =================================================

        st.divider()

        st.markdown(
            "### 3. Collection Timing for the Cash Model"
        )

        st.caption(
            "This schedule is completely separate from the NPV calculation. "
            "It tells the monthly cash-flow layer when collections occur."
        )

        st.info(
            "For example, 20% / 70% / 10% means that €100 of sales "
            "generated today produces €20 cash in the current month, "
            "€70 next month and €10 in month +2."
        )

        if st.button(
            "Use Current Collection Schedule",
            key="receivables_use_discount_schedule",
            use_container_width=True,
        ):
            try:
                decision = DecisionFactory.ar_days_change(
                    decision_id=f"ar_{uuid4().hex[:8]}",
                    target_ar_days=float(
                        result[
                            "new_avg_collection_period"
                        ]
                    ),
                )
            except TypeError:
                decision = DecisionFactory.ar_days_change(
                    f"ar_{uuid4().hex[:8]}",
                    float(
                        result[
                            "new_avg_collection_period"
                        ]
                    ),
                )

            decision = _attach_collection_schedule(
                decision,
                collection_schedule,
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
                        collection_schedule
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
                    "pct_new_policy": float(
                        result["pct_new_policy"]
                    ),
                },
            )

            st.success(
                "Discount-based Receivables policy is ready "
                "as a candidate."
            )

            st.rerun()

    # =====================================================
    # ACTIVE CANDIDATE
    # =====================================================

    st.divider()

    st.subheader(
        "4. Active Receivables Decision Candidate"
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
                f"€{float(metadata['npv']):,.2f}"
            )

        if "free_capital" in metadata:
            st.write(
                f"**Estimated Free Capital:** "
                f"€{float(metadata['free_capital']):,.2f}"
            )

        if "max_discount" in metadata:
            st.write(
                f"**Maximum Discount:** "
                f"{float(metadata['max_discount']) * 100:.2f}%"
            )

        if "optimum_discount" in metadata:
            st.write(
                f"**Optimum Discount:** "
                f"{float(metadata['optimum_discount']) * 100:.2f}%"
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
                        "Receivables decision added to "
                        "Current Decision Plan."
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
        **Receivables economic model**

        Discount policy → economic calculation → NPV /
        maximum discount / optimum discount.

        **AR days**

        The resulting collection policy changes the canonical
        `ar_days` driver in `CompanyState`.

        **Collection schedule**

        The 20% / 70% / 10% pattern is stored separately as
        a cash-timing assumption.

        It is used by the monthly cash-flow layer and does
        **not** participate in the Receivables NPV calculation.

        Therefore:

        **Economic value ≠ cash timing.**

        The economic calculation determines whether the policy
        creates value.

        The collection schedule determines when that value is
        reflected in actual monthly cash.
        """
    )
