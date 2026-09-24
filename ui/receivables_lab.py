from dataclasses import fields, replace
from decimal import Decimal, InvalidOperation, Overflow, getcontext
from uuid import uuid4

import streamlit as st

from core.decision import DecisionFactory
from core.decision_plan import DecisionPlan


# =========================================================
# STATE CONSTANTS & DEFAULTS
# =========================================================

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
) -> dict:
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


def _format_collection_schedule(schedule: dict) -> dict:
    if not isinstance(schedule, dict):
        schedule = DEFAULT_COLLECTION_SCHEDULE

    return {
        "month_0_pct": float(
            schedule.get("month_0_pct", DEFAULT_COLLECTION_SCHEDULE["month_0_pct"])
        ),
        "month_1_pct": float(
            schedule.get("month_1_pct", DEFAULT_COLLECTION_SCHEDULE["month_1_pct"])
        ),
        "month_2_pct": float(
            schedule.get("month_2_pct", DEFAULT_COLLECTION_SCHEDULE["month_2_pct"])
        ),
    }


def _attach_collection_schedule(decision, collection_schedule: dict):
    """
    Attach the cash-timing schedule to the Decision metadata safely.
    """
    metadata = {
        "collection_schedule": _format_collection_schedule(collection_schedule)
    }

    try:
        decision_fields = {field.name for field in fields(decision)}
    except TypeError:
        decision_fields = set()

    for field_name in ("metadata", "meta", "details", "assumptions"):
        if field_name in decision_fields:
            try:
                current = getattr(decision, field_name, None)
                merged = dict(current) if isinstance(current, dict) else {}
                merged.update(metadata)
                return replace(decision, **{field_name: merged})
            except Exception:
                pass

    # Fallback for mutable objects
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

    for field_name in ("metadata", "meta", "details", "assumptions"):
        value = getattr(decision, field_name, None)
        if isinstance(value, dict):
            schedule = value.get("collection_schedule")
            if isinstance(schedule, dict):
                return _format_collection_schedule(schedule)

    return None


# =========================================================
# EARLY PAYMENT DISCOUNT CALCULATOR (VERSION 1 LOGIC)
# =========================================================

def calculate_discount_npv(
    current_sales,
    extra_sales,
    discount_trial,
    prc_clients_take_disc,
    days_currently_paying_clients_take_discount,
    days_currently_paying_clients_not_take_discount,
    new_days_payment_clients_take_disc,
    cogs,
    wacc,
    avg_days_pay_suppliers,
) -> dict:
    """
    Evaluate whether an early-payment discount creates economic value using 
    exact discounted cash flow (DCF/NPV) formulas. All rates expected in decimals (0.0 - 1.0).
    """
    getcontext().prec = 50

    try:
        cs = Decimal(str(current_sales))
        es = Decimal(str(extra_sales))
        dt = Decimal(str(discount_trial))
        pct_take = Decimal(str(prc_clients_take_disc))

        d_take_old = Decimal(str(days_currently_paying_clients_take_discount))
        d_no_take_old = Decimal(str(days_currently_paying_clients_not_take_discount))
        d_new_policy = Decimal(str(new_days_payment_clients_take_disc))

        cg = Decimal(str(cogs))
        wc = Decimal(str(wacc))
        d_supp = Decimal(str(avg_days_pay_suppliers))

        if cs <= 0 or pct_take <= 0 or pct_take > 1 or wc < 0 or dt < 0 or dt > 1:
            return None

        pct_no_take = Decimal("1") - pct_take

        # Current Policy
        avg_curr_days = pct_take * d_take_old + pct_no_take * d_no_take_old
        curr_rec = (cs * avg_curr_days) / Decimal("365")

        # New Policy
        total_sales = cs + es
        if total_sales <= 0:
            return None

        prcnt_new_policy = ((cs * pct_take) + es) / total_sales
        prcnt_old_policy = Decimal("1") - prcnt_new_policy

        if prcnt_new_policy <= 0:
            return None

        new_avg_period = (
            prcnt_new_policy * d_new_policy + prcnt_old_policy * d_no_take_old
        )
        new_rec = (total_sales * new_avg_period) / Decimal("365")

        free_cap = curr_rec - new_rec

        # Profit Effect
        gross_margin_ratio = Decimal("1") - (cg / cs)
        prof_extra = es * gross_margin_ratio
        prof_free_cap = free_cap * wc
        dist_cost = total_sales * prcnt_new_policy * dt

        # Discounted Cash Flow (NPV Calculations)
        i_float = float(wc / Decimal("365"))
        MAX_EXP = 500.0

        exp_new = min(float(d_new_policy), MAX_EXP)
        exp_no_take = min(float(d_no_take_old), MAX_EXP)
        exp_curr = min(float(avg_curr_days), MAX_EXP)
        exp_supp = min(float(d_supp), MAX_EXP)

        base = 1.0 + i_float

        t1_denom = Decimal(str(base ** exp_new))
        t2_denom = Decimal(str(base ** exp_no_take))
        t3_denom = Decimal(str(base ** exp_supp))
        t4_denom = Decimal(str(base ** exp_curr))

        term1 = (total_sales * prcnt_new_policy * (Decimal("1") - dt)) / t1_denom
        term2 = (total_sales * prcnt_old_policy) / t2_denom
        term3 = ((cg / cs) * (es / cs) * cs) / t3_denom
        term4 = cs / t4_denom

        inflow = term1 + term2
        outflow = term3 + term4
        npv = inflow - outflow

        # Maximum & Optimum Discounts
        pow_1 = Decimal(str(base ** (exp_new - exp_no_take)))
        pow_2 = Decimal(str(base ** (exp_no_take - exp_curr)))
        pow_3 = Decimal(str(base ** (exp_no_take - exp_supp)))

        term_inner = (
            Decimal("1")
            - (Decimal("1") / prcnt_new_policy)
            + (pow_2 + (cg / cs) * (es / cs) * pow_3)
            / (prcnt_new_policy * (Decimal("1") + (es / cs)))
        )

        max_d = Decimal("1") - pow_1 * term_inner

        pow_opt = Decimal(str(base ** (exp_new - exp_curr)))
        opt_d = (Decimal("1") - pow_opt) / Decimal("2")

        return {
            "avg_current_collection_days": float(avg_curr_days),
            "current_receivables": float(curr_rec),
            "new_avg_collection_period": float(new_avg_period),
            "new_receivables": float(new_rec),
            "free_capital": float(free_cap),
            "profit_from_extra_sales": float(prof_extra),
            "profit_from_free_capital": float(prof_free_cap),
            "discount_cost": float(dist_cost),
            "npv": float(npv),
            "max_discount": float(max_d * 100),
            "optimum_discount": float(opt_d * 100),
            "pct_new_policy": float(prcnt_new_policy * 100),
            "supplier_days": float(d_supp),
        }

    except (InvalidOperation, Overflow, ZeroDivisionError, ValueError):
        return None


# =========================================================
# STATE & PLAN MANAGEMENT
# =========================================================

def _get_current_plan() -> DecisionPlan:
    plan = st.session_state.get("decision_plan")
    if isinstance(plan, DecisionPlan):
        return plan

    plan = DecisionPlan.create(plan_id="main_plan", name="Current Decision Plan")
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


def _add_to_current_plan(decision) -> bool:
    plan = _get_current_plan()
    conflict = _find_conflicting_driver(plan, decision)

    if conflict is not None:
        st.error("Another Receivables decision already changes AR policy in this Plan.")
        return False

    existing_ids = {getattr(item, "id", None) for item in getattr(plan, "decisions", ())}
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


def set_ar_candidate(decision, metadata=None):
    st.session_state[AR_CANDIDATE] = decision
    st.session_state[AR_META] = metadata or {}


def clear_ar_candidate():
    st.session_state.pop(AR_CANDIDATE, None)
    st.session_state.pop(AR_META, None)


def get_ar_candidate():
    return st.session_state.get(AR_CANDIDATE)


# =========================================================
# BASELINE HELPERS
# =========================================================

def _get_revenue(baseline_state) -> float:
    try:
        return float(baseline_state.income_statement.revenue)
    except AttributeError:
        price = float(getattr(baseline_state.drivers, "price", getattr(baseline_state, "price", 150.0)))
        volume = float(getattr(baseline_state.drivers, "volume", getattr(baseline_state, "volume", 12000.0)))
        return price * volume


def _get_annual_cogs(baseline_state) -> float:
    try:
        volume = float(getattr(baseline_state.drivers, "volume", getattr(baseline_state, "volume", 12000.0)))
        vc = float(getattr(baseline_state.drivers, "variable_cost_per_unit", getattr(baseline_state, "variable_cost", 100.0)))
        return volume * vc
    except AttributeError:
        return 12000.0 * 100.0


# =========================================================
# MAIN UI RENDER
# =========================================================

def render_receivables_lab(baseline_state):
    st.title("💶 Receivables Lab")

    wc = baseline_state.working_capital
    current_ar_days = float(wc.ar_days)
    annual_sales = _get_revenue(baseline_state)
    annual_cogs = _get_annual_cogs(baseline_state)

    st.markdown(
        "Evaluate customer credit and collection policies without changing the locked baseline."
    )

    # 1. Current State
    st.subheader("Current Receivables Position")
    c1, c2, c3 = st.columns(3)
    c1.metric("Current AR Days", f"{current_ar_days:.1f}")
    c2.metric("Annual Sales", f"€{annual_sales:,.0f}")
    current_receivables = annual_sales * current_ar_days / 365.0
    c3.metric("Estimated Receivables", f"€{current_receivables:,.0f}")

    st.divider()

    # 2. Collection Policy
    st.subheader("1. Set a Collection Policy")
    target_ar_days = st.number_input(
        "Target Collection Time (days)",
        min_value=0.0,
        max_value=365.0,
        value=current_ar_days,
        step=1.0,
        key="receivables_target_ar_days",
    )

    s1, s2, s3 = st.columns(3)
    month_0 = s1.number_input("Same Month (%)", 0.0, 100.0, 20.0, 5.0, key="rec_m0")
    month_1 = s2.number_input("Next Month (%)", 0.0, 100.0, 70.0, 5.0, key="rec_m1")
    month_2 = s3.number_input("Month +2 (%)", 0.0, 100.0, 10.0, 5.0, key="rec_m2")

    collection_schedule = _normalise_collection_schedule(month_0, month_1, month_2)

    if st.button("Use This Collection Policy", key="rec_use_manual_policy", use_container_width=True):
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
                "baseline_ar_days": current_ar_days,
                "collection_schedule": collection_schedule,
            },
        )
        st.success("Collection policy set as active candidate.")
        st.rerun()

    st.divider()

    # 3. Discount Analysis
    st.subheader("2. Offer Early Payment Discount")
    d1, d2, d3 = st.columns(3)
    extra_sales = d1.number_input("Additional Sales (€)", 0.0, value=0.0, step=10000.0, key="rec_ext_sales")
    discount_pct = d2.number_input("Discount (%)", 0.0, 100.0, 2.0, 0.1, key="rec_disc_pct")
    adoption_pct = d3.number_input("Expected Adoption (%)", 0.0, 100.0, 40.0, 1.0, key="rec_adopt_pct")

    e1, e2, e3 = st.columns(3)
    discount_days = e1.number_input("New Payment Days (Discount)", 1.0, 365.0, 10.0, 1.0, key="rec_disc_days")
    non_discount_days = e2.number_input("Payment Days (No Discount)", 1.0, 365.0, max(1.0, current_ar_days * 1.5), 1.0, key="rec_nondisc_days")
    supplier_days = e3.number_input("Supplier Payment Days", 1.0, 365.0, float(getattr(wc, "ap_days", 30.0)), 1.0, key="rec_sup_days")

    f1, f2 = st.columns(2)
    wacc_pct = f1.number_input("Cost of Capital / WACC (%)", 0.0, 100.0, 15.0, 0.5, key="rec_wacc")
    f2.metric("Annual COGS", f"€{annual_cogs:,.0f}")

    if st.button("Analyze Discount Policy", key="rec_analyze_discount", use_container_width=True):
        st.session_state["receivables_discount_result"] = calculate_discount_npv(
            current_sales=annual_sales,
            extra_sales=extra_sales,
            discount_trial=discount_pct / 100.0,
            prc_clients_take_disc=adoption_pct / 100.0,
            days_currently_paying_clients_take_discount=current_ar_days,
            days_currently_paying_clients_not_take_discount=non_discount_days,
            new_days_payment_clients_take_disc=discount_days,
            cogs=annual_cogs,
            wacc=wacc_pct / 100.0,
            avg_days_pay_suppliers=supplier_days,
        )

    result = st.session_state.get("receivables_discount_result")
    if result is not None:
        st.divider()
        st.subheader("🏁 Collection Policy Result")

        r1, r2, r3, r4 = st.columns(4)
        npv_val = result["npv"]
        r1.metric("Economic Value (NPV)", f"€{npv_val:,.0f}", delta="Creates Value" if npv_val > 0 else "Destroys Value")
        r2.metric("New Collection Time", f"{result['new_avg_collection_period']:.1f} days")
        r3.metric("Cash Released", f"€{result['free_capital']:,.0f}")
        r4.metric("Discount Cost", f"€{result['discount_cost']:,.0f}")

        q1, q2, q3 = st.columns(3)
        disc_m0 = q1.number_input("Same Month (%)", 0.0, 100.0, 20.0, 5.0, key="disc_m0")
        disc_m1 = q2.number_input("Next Month (%)", 0.0, 100.0, 70.0, 5.0, key="disc_m1")
        disc_m2 = q3.number_input("Month +2 (%)", 0.0, 100.0, 10.0, 5.0, key="disc_m2")

        disc_schedule = _normalise_collection_schedule(disc_m0, disc_m1, disc_m2)

        if st.button("Use Discount Policy", key="rec_use_discount_policy", use_container_width=True):
            try:
                decision = DecisionFactory.ar_days_change(
                    decision_id=f"ar_{uuid4().hex[:8]}",
                    target_ar_days=float(result["new_avg_collection_period"]),
                )
            except TypeError:
                decision = DecisionFactory.ar_days_change(
                    f"ar_{uuid4().hex[:8]}", float(result["new_avg_collection_period"])
                )

            decision = _attach_collection_schedule(decision, disc_schedule)
            set_ar_candidate(
                decision,
                metadata={
                    "source": "receivables_lab",
                    "method": "Early Payment Discount",
                    "ar_days": float(result["new_avg_collection_period"]),
                    "baseline_ar_days": current_ar_days,
                    "collection_schedule": disc_schedule,
                    "npv": float(result["npv"]),
                    "free_capital": float(result["free_capital"]),
                },
            )
            st.success("Discount Policy candidate active.")
            st.rerun()

    # 4. Active Candidate Management
    st.divider()
    st.subheader("🧩 Active Receivables Decision Candidate")
    candidate = get_ar_candidate()

    if candidate is None:
        st.info("No collection policy has been selected yet.")
    else:
        metadata = st.session_state.get(AR_META, {})
        changes = getattr(candidate, "changes", {})
        cand_ar_days = (
            changes.get("ar_days")
            if isinstance(changes, dict)
            else metadata.get("ar_days")
        )
        schedule = (
            _decision_collection_schedule(candidate)
            or metadata.get("collection_schedule")
            or DEFAULT_COLLECTION_SCHEDULE
        )

        st.success(f"**Method:** {metadata.get('method', 'Collection Policy')} | **Target AR Days:** {float(cand_ar_days):.1f}")
        st.write(
            f"**Cash Collection Schedule:** {schedule['month_0_pct']:.0%} / {schedule['month_1_pct']:.0%} / {schedule['month_2_pct']:.0%}"
        )
        if "npv" in metadata:
            st.write(f"**Economic Value (NPV):** €{metadata['npv']:,.0f}")

        b1, b2 = st.columns(2)
        with b1:
            if st.button("➕ Add to Current Decision Plan", key="add_plan_btn", use_container_width=True):
                if _add_to_current_plan(candidate):
                    st.success("Added to Plan!")
                    clear_ar_candidate()
                    st.rerun()

        with b2:
            if st.button("Clear Candidate", key="clear_cand_btn", use_container_width=True):
                clear_ar_candidate()
                st.rerun()
