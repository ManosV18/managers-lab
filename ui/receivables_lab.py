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
# COLLECTION SCHEDULE HELPERS
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
    metadata = {
        "collection_schedule": _format_collection_schedule(collection_schedule)
    }

    try:
        decision_fields = {field.name for field in fields(decision)}
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
                current = getattr(decision, field_name, None)
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
        current = getattr(decision, "metadata", None)
        if isinstance(current, dict):
            current.update(metadata)
        else:
            setattr(decision, "metadata", metadata)
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
        value = getattr(decision, field_name, None)
        if isinstance(value, dict):
            schedule = value.get("collection_schedule")
            if isinstance(schedule, dict):
                return _format_collection_schedule(schedule)

    return None


# =========================================================
# DECIMAL HELPERS
# =========================================================

getcontext().prec = 28


def _decimal(value, default="0"):
    try:
        return Decimal(str(value))
    except (InvalidOperation, ValueError, TypeError, Overflow):
        return Decimal(default)


# =========================================================
# EXACT RECEIVABLES CALCULATOR (EXCEL LOGIC MATCH)
# =========================================================


def calculate_discount_npv(
    current_annual_sales,
    extra_annual_sales,
    discount_pct,
    adoption_pct,
    days_currently_paying_clients_take_discount,
    days_currently_paying_clients_not_take_discount,
    new_days_payment_clients_take_disc,
    annual_cogs,
    wacc,
    supplier_days,
):
    """
    Exact mathematical implementation of the Receivables model.
    Inputs:
        discount_pct, adoption_pct, wacc in percentage scale (e.g. 2.0 = 2%, 40.0 = 40%, 20.0 = 20%)
    """
    current_sales = _decimal(current_annual_sales)
    extra_sales = _decimal(extra_annual_sales)
    discount_trial = _decimal(discount_pct) / Decimal("100")
    prc_clients_take_disc = _decimal(adoption_pct) / Decimal("100")

    days_take_disc = _decimal(days_currently_paying_clients_take_discount)
    days_not_take_disc = _decimal(
        days_currently_paying_clients_not_take_discount
    )
    new_days_take_disc = _decimal(new_days_payment_clients_take_disc)

    cogs = _decimal(annual_cogs)
    wacc_val = _decimal(wacc) / Decimal("100")
    supplier_days_val = _decimal(supplier_days)

    if current_sales <= Decimal("0"):
        return None

    # 1. prc_clients_not_take_disc = 1 - prc_clients_take_disc
    prc_clients_not_take_disc = Decimal("1") - prc_clients_take_disc

    # 2. avg_current_collection_days = days_take_disc * prc_take + days_not_take_disc * prc_not_take
    avg_current_collection_days = (
        days_take_disc * prc_clients_take_disc
        + days_not_take_disc * prc_clients_not_take_disc
    )

    # 3. current_receivables = current_sales * avg_current_collection_days / 365
    current_receivables = (
        current_sales * avg_current_collection_days / Decimal("365")
    )

    total_sales = current_sales + extra_sales

    # 4. prcnt_of_total_new_clients_in_new_policy = ((current_sales * prc_clients_take_disc) + extra_sales) / (current_sales + extra_sales)
    if total_sales > Decimal("0"):
        prcnt_of_total_new_clients_in_new_policy = (
            (current_sales * prc_clients_take_disc) + extra_sales
        ) / total_sales
    else:
        prcnt_of_total_new_clients_in_new_policy = Decimal("0")

    # 5. prcnt_not_in_new_policy = 1 - prcnt_of_total_new_clients_in_new_policy
    prcnt_not_in_new_policy = (
        Decimal("1") - prcnt_of_total_new_clients_in_new_policy
    )

    # 6. new_avg_collection_period = prcnt_in_new_policy * new_days_take_disc + prcnt_not_in_new_policy * days_not_take_disc
    new_avg_collection_period = (
        prcnt_of_total_new_clients_in_new_policy * new_days_take_disc
        + prcnt_not_in_new_policy * days_not_take_disc
    )

    # 7. new_receivables = (current_sales + extra_sales) * new_avg_collection_period / 365
    new_receivables = total_sales * new_avg_collection_period / Decimal("365")

    # 8. free_capital = current_receivables - new_receivables
    free_capital = current_receivables - new_receivables

    # 9. profit_from_extra_sales = extra_sales * (1 - (cogs / current_sales))
    profit_from_extra_sales = extra_sales * (
        Decimal("1") - (cogs / current_sales)
    )

    # 10. profit_from_free_capital = free_capital * WACC
    profit_from_free_capital = free_capital * wacc_val

    # 11. discount_cost = (current_sales + extra_sales) * prcnt_of_total_new_clients_in_new_policy * discount_trial
    discount_cost = (
        total_sales
        * prcnt_of_total_new_clients_in_new_policy
        * discount_trial
    )

    # 12. ECONOMIC NPV
    # Formula:
    # (current_sales+extra_sales)*prcnt_of_total_new_clients_in_new_policy*(1-discount_trial)*(1/(1+(WACC/365))^new_days_payment_clients_take_disc)
    # + (current_sales+extra_sales)*(1-prcnt_of_total_new_clients_in_new_policy)*(1/(1+(WACC/365))^days_curently_paying_clients_not_take_discount)
    # - (COGS/current_sales)*(extra_sales/current_sales)*current_sales*(1/(1+(WACC/365))^avg_days_pay_suppliers)
    # - current_sales*(1/(1+(WACC/365))^avg_current_collection_days)

    daily_wacc = Decimal("1") + (wacc_val / Decimal("365"))

    def _dfactor(days):
        return Decimal("1") / (daily_wacc ** _decimal(days))

    term_1 = (
        total_sales
        * prcnt_of_total_new_clients_in_new_policy
        * (Decimal("1") - discount_trial)
        * _dfactor(new_days_take_disc)
    )

    term_2 = (
        total_sales * prcnt_not_in_new_policy * _dfactor(days_not_take_disc)
    )

    term_3 = (
        (cogs / current_sales)
        * (extra_sales / current_sales)
        * current_sales
        * _dfactor(supplier_days_val)
    )

    term_4 = current_sales * _dfactor(avg_current_collection_days)

    economic_npv = term_1 + term_2 - term_3 - term_4

    # 13. MAXIMUM DISCOUNT
    # Formula:
    # 1 - (1+(WACC/365))^(new_days - days_not_take_disc) * (
    #     (1 - (1 / prcnt_in_new_policy))
    #     + (
    #         (1+(WACC/365))^(days_not_take_disc - avg_current_days)
    #         + (COGS/current_sales)*(extra_sales/current_sales)*(1+(WACC/365))^(days_not_take_disc - supplier_days)
    #       ) / (prcnt_in_new_policy * (1 + (extra_sales/current_sales)))
    # )

    if prcnt_of_total_new_clients_in_new_policy > Decimal("0"):
        comp_pow_outer = daily_wacc ** (
            new_days_take_disc - days_not_take_disc
        )
        comp_inner_1 = Decimal("1") - (
            Decimal("1") / prcnt_of_total_new_clients_in_new_policy
        )

        pow_timing_1 = daily_wacc ** (
            days_not_take_disc - avg_current_collection_days
        )
        pow_timing_2 = daily_wacc ** (days_not_take_disc - supplier_days_val)

        numerator_2 = pow_timing_1 + (cogs / current_sales) * (
            extra_sales / current_sales
        ) * pow_timing_2
        denominator_2 = prcnt_of_total_new_clients_in_new_policy * (
            Decimal("1") + (extra_sales / current_sales)
        )

        comp_inner_2 = numerator_2 / denominator_2

        max_discount = Decimal("1") - comp_pow_outer * (
            comp_inner_1 + comp_inner_2
        )
    else:
        max_discount = Decimal("0")

    # 14. OPTIMUM DISCOUNT
    # Formula: (1 - ((1+(WACC/365))^(new_days_take_disc - avg_current_collection_days))) / 2
    optimum_discount = (
        Decimal("1")
        - (
            daily_wacc ** (new_days_take_disc - avg_current_collection_days)
        )
    ) / Decimal("2")

    return {
        "avg_current_collection_days": float(avg_current_collection_days),
        "current_receivables": float(current_receivables),
        "total_new_sales": float(total_sales),
        "pct_total_new_sales_under_policy": float(
            prcnt_of_total_new_clients_in_new_policy
        ),
        "pct_total_new_sales_not_under_policy": float(prcnt_not_in_new_policy),
        "new_avg_collection_period": float(new_avg_collection_period),
        "new_receivables": float(new_receivables),
        "free_capital": float(free_capital),
        "profit_from_extra_sales": float(profit_from_extra_sales),
        "profit_from_free_capital": float(profit_from_free_capital),
        "discount_cost": float(discount_cost),
        "npv": float(economic_npv),
        "max_discount": float(max_discount * Decimal("100")),
        "optimum_discount": float(optimum_discount * Decimal("100")),
    }


# =========================================================
# CURRENT DECISION PLAN HELPERS
# =========================================================


def _get_current_plan():
    plan = st.session_state.get("decision_plan")
    if isinstance(plan, DecisionPlan):
        return plan

    plan = DecisionPlan.create(
        plan_id="main_plan",
        name="Current Decision Plan",
    )
    st.session_state["decision_plan"] = plan
    return plan


def _find_conflicting_driver(plan, decision):
    target_changes = getattr(decision, "changes", {})
    if not isinstance(target_changes, dict) or "ar_days" not in target_changes:
        return None

    for existing in getattr(plan, "decisions", ()):
        changes = getattr(existing, "changes", {})
        if isinstance(changes, dict) and "ar_days" in changes:
            return existing

    return None


def _add_to_current_plan(decision):
    plan = _get_current_plan()
    conflict = _find_conflicting_driver(plan, decision)

    if conflict is not None:
        st.error(
            "Another Receivables decision already changes the AR policy in the Current Decision Plan."
        )
        return False

    existing_ids = {
        getattr(item, "id", None) for item in getattr(plan, "decisions", ())
    }
    decision_id = getattr(decision, "id", None)

    if decision_id in existing_ids:
        st.info("This decision is already in the Current Decision Plan.")
        return False

    try:
        st.session_state["decision_plan"] = plan.add(decision)
        return True
    except Exception as exc:
        st.error(f"Could not add decision to Current Decision Plan: {exc}")
        return False


# =========================================================
# CANDIDATE STATE HELPERS
# =========================================================


def set_ar_candidate(decision, metadata=None):
    st.session_state[AR_CANDIDATE] = decision
    st.session_state[AR_META] = metadata or {}


def clear_ar_candidate():
    st.session_state.pop(AR_CANDIDATE, None)
    st.session_state.pop(AR_META, None)


def get_ar_candidate():
    return st.session_state.get(AR_CANDIDATE)


# =========================================================
# BASELINE EXTRACTION HELPERS
# =========================================================


def _get_revenue(baseline_state):
    drivers = getattr(baseline_state, "drivers", baseline_state)
    price = float(getattr(drivers, "price", 150.0))
    volume = float(getattr(drivers, "volume", 12000.0))
    return price * volume


def _get_annual_cogs(baseline_state):
    drivers = getattr(baseline_state, "drivers", baseline_state)
    volume = float(getattr(drivers, "volume", 12000.0))
    vc = float(getattr(drivers, "variable_cost_per_unit", 100.0))
    return volume * vc


# =========================================================
# MAIN UI
# =========================================================


def render_receivables_lab(baseline_state):
    st.title("💶 Receivables Lab")

    wc = getattr(baseline_state, "working_capital", None)
    current_ar_days = float(getattr(wc, "ar_days", 96.0)) if wc else 96.0
    current_ap_days = float(getattr(wc, "ap_days", 30.0)) if wc else 30.0

    cap = getattr(baseline_state, "capital_structure", None)
    current_wacc = float(getattr(cap, "wacc", 0.20)) if cap else 0.20

    annual_sales = _get_revenue(baseline_state)
    annual_cogs = _get_annual_cogs(baseline_state)

    st.markdown(
        """
    Evaluate customer credit and collection policies without changing the locked baseline.

    The decision changes the central **AR days** driver.
    The collection schedule is used only by the monthly cash-timing layer.
    """
    )

    # =====================================================
    # 1. CURRENT STATE
    # =====================================================

    st.subheader("Current Receivables Position")

    c1, c2, c3 = st.columns(3)
    c1.metric("Current AR Days", f"{current_ar_days:.1f}")
    c2.metric("Annual Sales", f"€{annual_sales:,.0f}")

    current_receivables = annual_sales * current_ar_days / 365.0
    c3.metric("Estimated Receivables", f"€{current_receivables:,.0f}")

    st.divider()

    # =====================================================
    # 2. MANUAL COLLECTION POLICY
    # =====================================================

    st.subheader("1. Set a Collection Policy")
    st.caption(
        "The 20% / 70% / 10% pattern is only the default. You can change it to reflect how your customers actually pay."
    )

    target_ar_days = st.number_input(
        "Target Collection Time (days)",
        min_value=0.0,
        max_value=365.0,
        value=float(current_ar_days),
        step=1.0,
        key="receivables_target_ar_days",
    )

    st.markdown("**Collection timing**")

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

    collection_schedule = _normalise_collection_schedule(
        month_0, month_1, month_2
    )

    schedule_total = month_0 + month_1 + month_2
    if abs(schedule_total - 100.0) > 0.01:
        st.caption(
            f"Entered pattern totals {schedule_total:.1f}%. The system will normalise it to 100%."
        )

    st.info(
        "This collection schedule is a cash-timing assumption. It does not replace AR days in CompanyState."
    )

    if st.button(
        "Use This Collection Policy",
        key="receivables_use_manual_policy",
        use_container_width=True,
    ):
        try:
            decision = DecisionFactory.ar_days_change(
                decision_id=f"ar_{uuid4().hex[:8]}",
                target_ar_days=float(target_ar_days),
            )
        except TypeError:
            decision = DecisionFactory.ar_days_change(
                f"ar_{uuid4().hex[:8]}", float(target_ar_days)
            )

        decision = _attach_collection_schedule(decision, collection_schedule)

        set_ar_candidate(
            decision,
            metadata={
                "source": "receivables_lab",
                "method": "Collection Policy",
                "ar_days": float(target_ar_days),
                "baseline_ar_days": float(current_ar_days),
                "collection_schedule": collection_schedule,
            },
        )

        st.success("Collection policy is ready as a Receivables candidate.")
        st.rerun()

    # =====================================================
    # 3. EARLY PAYMENT DISCOUNT ANALYSIS
    # =====================================================

    st.divider()

    st.subheader("2. Early-Payment Discount Analysis")
    st.caption(
        "Test whether faster customer payment justifies the cost of an early-payment discount."
    )

    d1, d2, d3 = st.columns(3)
    with d1:
        extra_sales = st.number_input(
            "Additional Annual Sales (€)",
            min_value=0.0,
            value=250.0 if annual_sales == 1000.0 else float(annual_sales * 0.25),
            step=100.0,
            key="receivables_extra_sales",
        )
    with d2:
        discount_pct = st.number_input(
            "Discount Offered (%)",
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
            value=40.0,
            step=5.0,
            key="receivables_adoption_pct",
        )

    e1, e2, e3 = st.columns(3)
    with e1:
        days_take_discount = st.number_input(
            "Current Days (Taking Discount)",
            min_value=0.0,
            max_value=365.0,
            value=60.0,
            step=1.0,
            key="receivables_days_take_discount",
        )
    with e2:
        days_not_take_discount = st.number_input(
            "Current Days (Not Taking Discount)",
            min_value=0.0,
            max_value=365.0,
            value=120.0,
            step=1.0,
            key="receivables_days_not_take_discount",
        )
    with e3:
        new_days_discount = st.number_input(
            "New Payment Days (With Discount)",
            min_value=0.0,
            max_value=365.0,
            value=10.0,
            step=1.0,
            key="receivables_new_days_discount",
        )

    f1, f2, f3 = st.columns(3)
    with f1:
        supplier_days = st.number_input(
            "Supplier Payment Days",
            min_value=0.0,
            max_value=365.0,
            value=float(current_ap_days),
            step=1.0,
            key="receivables_supplier_days",
        )
    with f2:
        wacc = st.number_input(
            "WACC (%)",
            min_value=0.0,
            max_value=100.0,
            value=float(current_wacc * 100.0 if current_wacc <= 1.0 else current_wacc),
            step=0.5,
            key="receivables_wacc",
        )
    with f3:
        st.metric("Annual COGS", f"€{annual_cogs:,.0f}")

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
            days_currently_paying_clients_take_discount=days_take_discount,
            days_currently_paying_clients_not_take_discount=days_not_take_discount,
            new_days_payment_clients_take_disc=new_days_discount,
            annual_cogs=annual_cogs,
            wacc=wacc,
            supplier_days=supplier_days,
        )

        st.session_state["receivables_discount_result"] = result

    result = st.session_state.get("receivables_discount_result")

    if result is not None:
        st.divider()
        st.subheader("Discount Policy Result")

        r1, r2, r3, r4 = st.columns(4)
        r1.metric(
            "New Avg. Collection",
            f"{result['new_avg_collection_period']:.1f} days",
        )
        r2.metric(
            "Receivables Released",
            f"€{result['free_capital']:,.2f}",
        )
        r3.metric(
            "Discount Cost",
            f"€{result['discount_cost']:,.2f}",
        )
        r4.metric(
            "Economic NPV",
            f"€{result['npv']:,.2f}",
        )

        if result["npv"] > 0:
            st.success(
                "Under these assumptions, the policy produces a positive economic contribution."
            )
        elif result["npv"] < 0:
            st.warning(
                "Under these assumptions, the cost of the policy exceeds its calculated economic benefit."
            )
        else:
            st.info("The calculated economic effect is approximately neutral.")

        st.markdown("### Economic Detail")

        x1, x2, x3, x4 = st.columns(4)
        x1.metric(
            "Total New Sales",
            f"€{result['total_new_sales']:,.2f}",
        )
        x2.metric(
            "Sales Under New Policy",
            f"{result['pct_total_new_sales_under_policy']:.1%}",
        )
        x3.metric(
            "Profit from Extra Sales",
            f"€{result['profit_from_extra_sales']:,.2f}",
        )
        x4.metric(
            "Capital Benefit",
            f"€{result['profit_from_free_capital']:,.2f}",
        )

        y1, y2 = st.columns(2)
        with y1:
            st.metric(
                "Maximum Discount",
                f"{result['max_discount']:.2f}%",
            )
        with y2:
            st.metric(
                "Indicative Optimum Discount",
                f"{result['optimum_discount']:.2f}%",
            )

        st.markdown("### Collection timing for the cash model")
        st.caption(
            "This schedule determines when the monthly cash-flow layer recognises customer collections."
        )

        q1, q2, q3 = st.columns(3)
        with q1:
            discount_month_0 = st.number_input(
                "Same Month (%)",
                min_value=0.0,
                max_value=100.0,
                value=20.0,
                step=5.0,
                key="receivables_discount_month_0_pct",
            )
        with q2:
            discount_month_1 = st.number_input(
                "Next Month (%)",
                min_value=0.0,
                max_value=100.0,
                value=70.0,
                step=5.0,
                key="receivables_discount_month_1_pct",
            )
        with q3:
            discount_month_2 = st.number_input(
                "Month +2 (%)",
                min_value=0.0,
                max_value=100.0,
                value=10.0,
                step=5.0,
                key="receivables_discount_month_2_pct",
            )

        discount_collection_schedule = _normalise_collection_schedule(
            discount_month_0, discount_month_1, discount_month_2
        )

        if st.button(
            "Use This Collection Policy",
            key="receivables_use_discount_policy",
            use_container_width=True,
        ):
            try:
                decision = DecisionFactory.ar_days_change(
                    decision_id=f"ar_{uuid4().hex[:8]}",
                    target_ar_days=float(result["new_avg_collection_period"]),
                )
            except TypeError:
                decision = DecisionFactory.ar_days_change(
                    f"ar_{uuid4().hex[:8]}",
                    float(result["new_avg_collection_period"]),
                )

            decision = _attach_collection_schedule(
                decision, discount_collection_schedule
            )

            set_ar_candidate(
                decision,
                metadata={
                    "source": "receivables_lab",
                    "method": "Early Payment Discount",
                    "ar_days": float(result["new_avg_collection_period"]),
                    "baseline_ar_days": float(current_ar_days),
                    "collection_schedule": discount_collection_schedule,
                    "npv": float(result["npv"]),
                    "free_capital": float(result["free_capital"]),
                    "discount_cost": float(result["discount_cost"]),
                    "max_discount": float(result["max_discount"]),
                    "optimum_discount": float(result["optimum_discount"]),
                    "pct_total_new_sales_under_policy": float(
                        result["pct_total_new_sales_under_policy"]
                    ),
                },
            )

            st.success(
                "Discount-based collection policy is ready as a Receivables candidate."
            )
            st.rerun()

    # =====================================================
    # 4. ACTIVE CANDIDATE
    # =====================================================

    st.divider()
    st.subheader("3. Active Receivables Decision Candidate")

    candidate = get_ar_candidate()

    if candidate is None:
        st.info("No active Receivables decision candidate.")
    else:
        metadata = st.session_state.get(AR_META, {})
        changes = getattr(candidate, "changes", {})

        candidate_ar_days = None
        if isinstance(changes, dict):
            candidate_ar_days = changes.get("ar_days")
        if candidate_ar_days is None:
            candidate_ar_days = metadata.get("ar_days")

        schedule = (
            _decision_collection_schedule(candidate)
            or metadata.get("collection_schedule")
            or DEFAULT_COLLECTION_SCHEDULE
        )

        st.success(f"**Target AR Days:** {float(candidate_ar_days):.1f}")

        method = metadata.get("method")
        if method:
            st.write(f"**Method:** {method}")

        st.write(
            "**Cash Collection Schedule:** "
            f"{schedule['month_0_pct']:.0%} same month / "
            f"{schedule['month_1_pct']:.0%} next month / "
            f"{schedule['month_2_pct']:.0%} month +2"
        )

        if "npv" in metadata:
            st.write(
                f"**Calculated Economic NPV:** €{float(metadata['npv']):,.2f}"
            )
        if "free_capital" in metadata:
            st.write(
                f"**Estimated Cash Released:** €{float(metadata['free_capital']):,.2f}"
            )
        if "max_discount" in metadata:
            st.write(f"**Maximum Discount:** {float(metadata['max_discount']):.2f}%")
        if "optimum_discount" in metadata:
            st.write(
                f"**Indicative Optimum Discount:** {float(metadata['optimum_discount']):.2f}%"
            )

        b1, b2 = st.columns(2)
        with b1:
            if st.button(
                "➕ Add to Current Decision Plan",
                key="receivables_add_to_plan",
                use_container_width=True,
            ):
                if _add_to_current_plan(candidate):
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
    # V2 LOGIC CAPTION
    # =====================================================

    st.divider()
    st.subheader("How this connects to Managers Lab V2")
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
