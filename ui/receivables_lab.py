from dataclasses import (
    fields,
    replace,
)
from decimal import (
    Decimal,
    InvalidOperation,
    Overflow,
    getcontext,
)
from uuid import uuid4

import streamlit as st

from core.decision import DecisionFactory
from core.decision_plan import DecisionPlan


# =========================================================
# RECEIVABLES CANDIDATE
# =========================================================

AR_CANDIDATE = "wc_ar_candidate"
AR_META = "wc_ar_candidate_meta"


# =========================================================
# COLLECTION PROFILE
# =========================================================

def _build_collection_profile(
    new_policy_pct,
    new_policy_days,
    old_policy_pct,
    old_policy_days,
):
    """
    Build the simple two-policy collection assumption used by
    Cash Management.

    This is a management-level planning assumption.

    It is NOT customer-level aging and does not attempt to forecast
    individual invoices.

    Example:

        40% of sales -> 10 days
        60% of sales -> 90 days
    """

    new_pct = float(
        new_policy_pct
    )

    old_pct = float(
        old_policy_pct
    )

    total_pct = (
        new_pct
        + old_pct
    )

    if total_pct <= 0:
        return None

    # Normalise percentages so small rounding differences do not
    # distort the cash-timing layer.
    new_pct = (
        new_pct / total_pct
    )

    old_pct = (
        old_pct / total_pct
    )

    return {
        "new_policy_pct": new_pct,
        "new_policy_days": float(
            new_policy_days
        ),
        "old_policy_pct": old_pct,
        "old_policy_days": float(
            old_policy_days
        ),
    }


def _attach_collection_profile(
    decision,
    collection_profile,
):
    """
    Attach collection_profile to the Decision itself.

    DecisionFactory remains responsible for creating the canonical
    AR driver change:

        ar_days

    The collection_profile is additional decision metadata used only
    by the cash-timing layer.

    The function is deliberately defensive because the Decision model
    may expose metadata under a slightly different field name.
    """

    if decision is None:
        return decision

    if collection_profile is None:
        return decision

    # ---------------------------------------------------------
    # Preferred path: immutable dataclass replacement.
    # ---------------------------------------------------------

    try:
        decision_fields = {
            field.name
            for field in fields(
                decision
            )
        }

        for metadata_field in (
            "metadata",
            "meta",
            "details",
            "assumptions",
        ):

            if metadata_field not in decision_fields:
                continue

            existing_metadata = getattr(
                decision,
                metadata_field,
                None,
            )

            if isinstance(
                existing_metadata,
                dict,
            ):
                metadata = dict(
                    existing_metadata
                )

            else:
                metadata = {}

            metadata[
                "collection_profile"
            ] = dict(
                collection_profile
            )

            return replace(
                decision,
                **{
                    metadata_field: metadata
                },
            )

    except (
        TypeError,
        ValueError,
    ):
        pass

    # ---------------------------------------------------------
    # Compatibility path:
    #
    # If the Decision implementation exposes a mutable metadata
    # dictionary but is not a dataclass, use it.
    # ---------------------------------------------------------

    for metadata_field in (
        "metadata",
        "meta",
        "details",
        "assumptions",
    ):

        try:
            existing_metadata = getattr(
                decision,
                metadata_field,
                None,
            )

            if isinstance(
                existing_metadata,
                dict,
            ):

                existing_metadata[
                    "collection_profile"
                ] = dict(
                    collection_profile
                )

                return decision

        except Exception:
            pass

    # ---------------------------------------------------------
    # Final compatibility fallback.
    #
    # Keep the profile in the candidate metadata so the UI can
    # still display it. Cash Management will warn if an older
    # Decision implementation cannot persist it on the Decision.
    # ---------------------------------------------------------

    return decision


def _decision_collection_profile(
    decision,
):
    """
    Read collection_profile back from a Decision.

    Useful for validating that the profile actually travelled with
    the Decision before it is added to Current Decision Plan.
    """

    if decision is None:
        return None

    for metadata_field in (
        "metadata",
        "meta",
        "details",
        "assumptions",
    ):

        metadata = getattr(
            decision,
            metadata_field,
            None,
        )

        if not isinstance(
            metadata,
            dict,
        ):
            continue

        profile = metadata.get(
            "collection_profile"
        )

        if isinstance(
            profile,
            dict,
        ):
            return profile

    return None


# =========================================================
# EARLY PAYMENT DISCOUNT CALCULATOR
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
):
    """
    Evaluate whether an early-payment discount creates economic value.

    All percentage inputs are supplied as decimals (0-1).

    Returns a dictionary containing:
        - current weighted collection days
        - new weighted collection days
        - current receivables
        - new receivables
        - cash released
        - profit from extra sales
        - profit from released cash
        - discount cost
        - NPV
        - maximum discount
        - optimum discount
        - percentage of sales under new policy
    """

    getcontext().prec = 50

    try:
        cs = Decimal(
            str(current_sales)
        )

        es = Decimal(
            str(extra_sales)
        )

        dt = Decimal(
            str(discount_trial)
        )

        pct_take = Decimal(
            str(prc_clients_take_disc)
        )

        d_take_old = Decimal(
            str(
                days_currently_paying_clients_take_discount
            )
        )

        d_no_take_old = Decimal(
            str(
                days_currently_paying_clients_not_take_discount
            )
        )

        d_new_policy = Decimal(
            str(
                new_days_payment_clients_take_disc
            )
        )

        cg = Decimal(
            str(cogs)
        )

        wc = Decimal(
            str(wacc)
        )

        d_supp = Decimal(
            str(avg_days_pay_suppliers)
        )

        # -----------------------------------------------------
        # VALIDATION
        # -----------------------------------------------------

        if (
            cs <= 0
            or pct_take <= 0
            or pct_take > 1
            or wc < 0
        ):
            return None

        if (
            dt < 0
            or dt > 1
        ):
            return None

        pct_no_take = (
            Decimal("1")
            - pct_take
        )

        # -----------------------------------------------------
        # CURRENT POLICY
        # -----------------------------------------------------

        avg_curr_days = (
            pct_take
            * d_take_old
            + pct_no_take
            * d_no_take_old
        )

        curr_rec = (
            cs
            * avg_curr_days
        ) / Decimal("365")

        # -----------------------------------------------------
        # NEW POLICY
        # -----------------------------------------------------

        total_sales = (
            cs + es
        )

        if total_sales <= 0:
            return None

        prcnt_new_policy = (
            (
                cs
                * pct_take
            )
            + es
        ) / total_sales

        prcnt_old_policy = (
            Decimal("1")
            - prcnt_new_policy
        )

        if prcnt_new_policy <= 0:
            return None

        new_avg_period = (
            prcnt_new_policy
            * d_new_policy
            + prcnt_old_policy
            * d_no_take_old
        )

        new_rec = (
            total_sales
            * new_avg_period
        ) / Decimal("365")

        free_cap = (
            curr_rec
            - new_rec
        )

        # -----------------------------------------------------
        # PROFIT EFFECT
        # -----------------------------------------------------

        gross_margin_ratio = (
            Decimal("1")
            - (
                cg / cs
            )
        )

        prof_extra = (
            es
            * gross_margin_ratio
        )

        prof_free_cap = (
            free_cap
            * wc
        )

        dist_cost = (
            total_sales
            * prcnt_new_policy
            * dt
        )

        # -----------------------------------------------------
        # DISCOUNTED CASH FLOW
        # -----------------------------------------------------

        i_float = float(
            wc / Decimal("365")
        )

        MAX_EXP = 500.0

        exp_new = min(
            float(
                d_new_policy
            ),
            MAX_EXP,
        )

        exp_no_take = min(
            float(
                d_no_take_old
            ),
            MAX_EXP,
        )

        exp_curr = min(
            float(
                avg_curr_days
            ),
            MAX_EXP,
        )

        exp_supp = min(
            float(
                d_supp
            ),
            MAX_EXP,
        )

        base = (
            1.0
            + i_float
        )

        t1_denom = Decimal(
            str(
                base ** exp_new
            )
        )

        t2_denom = Decimal(
            str(
                base ** exp_no_take
            )
        )

        t3_denom = Decimal(
            str(
                base ** exp_supp
            )
        )

        t4_denom = Decimal(
            str(
                base ** exp_curr
            )
        )

        term1 = (
            total_sales
            * prcnt_new_policy
            * (
                Decimal("1")
                - dt
            )
        ) / t1_denom

        term2 = (
            total_sales
            * prcnt_old_policy
        ) / t2_denom

        term3 = (
            (cg / cs)
            * (es / cs)
            * cs
        ) / t3_denom

        term4 = (
            cs
            / t4_denom
        )

        inflow = (
            term1
            + term2
        )

        outflow = (
            term3
            + term4
        )

        npv = (
            inflow
            - outflow
        )

        # -----------------------------------------------------
        # MAXIMUM DISCOUNT
        # -----------------------------------------------------

        pow_1 = Decimal(
            str(
                base
                ** (
                    exp_new
                    - exp_no_take
                )
            )
        )

        pow_2 = Decimal(
            str(
                base
                ** (
                    exp_no_take
                    - exp_curr
                )
            )
        )

        pow_3 = Decimal(
            str(
                base
                ** (
                    exp_no_take
                    - exp_supp
                )
            )
        )

        term_inner = (
            Decimal("1")
            - (
                Decimal("1")
                / prcnt_new_policy
            )
            + (
                pow_2
                + (
                    cg / cs
                )
                * (
                    es / cs
                )
                * pow_3
            )
            / (
                prcnt_new_policy
                * (
                    Decimal("1")
                    + (
                        es / cs
                    )
                )
            )
        )

        max_d = (
            Decimal("1")
            - pow_1
            * term_inner
        )

        # -----------------------------------------------------
        # OPTIMUM DISCOUNT
        # -----------------------------------------------------

        pow_opt = Decimal(
            str(
                base
                ** (
                    exp_new
                    - exp_curr
                )
            )
        )

        opt_d = (
            Decimal("1")
            - pow_opt
        ) / Decimal("2")

        return {
            "avg_current_collection_days": float(
                avg_curr_days
            ),
            "current_receivables": float(
                curr_rec
            ),
            "new_avg_collection_period": float(
                new_avg_period
            ),
            "new_receivables": float(
                new_rec
            ),
            "free_capital": float(
                free_cap
            ),
            "profit_from_extra_sales": float(
                prof_extra
            ),
            "profit_from_free_capital": float(
                prof_free_cap
            ),
            "discount_cost": float(
                dist_cost
            ),
            "npv": float(
                npv
            ),
            "max_discount": float(
                max_d * 100
            ),
            "optimum_discount": float(
                opt_d * 100
            ),
            "pct_new_policy": float(
                prcnt_new_policy * 100
            ),
        }

    except (
        InvalidOperation,
        Overflow,
        ZeroDivisionError,
        ValueError,
    ):
        return None


# =========================================================
# CURRENT DECISION PLAN
# =========================================================

def _get_current_plan():
    """
    Return the active Current Decision Plan.

    DecisionPlan is immutable, so every add operation returns
    a new plan that must be stored back in session state.
    """

    plan = st.session_state.get(
        "decision_plan"
    )

    if isinstance(
        plan,
        DecisionPlan,
    ):
        return plan

    plan = DecisionPlan.create(
        plan_id="main_plan",
        name="Current Decision Plan",
    )

    st.session_state.decision_plan = (
        plan
    )

    return plan


def _find_conflicting_driver(
    plan,
    decision,
):
    """
    Detect whether another decision in the current plan
    already changes the same CompanyState driver.

    Receivables decisions change:
        ar_days
    """

    decision_changes = getattr(
        decision,
        "changes",
        {},
    )

    if "ar_days" not in decision_changes:
        return None

    for existing_decision in (
        plan.decisions
    ):

        existing_changes = getattr(
            existing_decision,
            "changes",
            {},
        )

        if "ar_days" in existing_changes:
            return existing_decision

    return None


def _add_to_current_plan(
    decision,
):
    """
    Add a Receivables Decision directly to Current Decision Plan.

    This is the direct path:

        Receivables Lab
            ↓
        Current Decision Plan

    The decision is NOT executed here.
    Execution/evaluation remains centralized.
    """

    current_plan = (
        _get_current_plan()
    )

    # -----------------------------------------------------
    # DUPLICATE CHECK
    # -----------------------------------------------------

    if current_plan.contains(
        decision.id
    ):

        st.warning(
            "This decision is already in the Current Decision Plan."
        )

        return False

    # -----------------------------------------------------
    # DRIVER CONFLICT CHECK
    # -----------------------------------------------------

    conflict = (
        _find_conflicting_driver(
            current_plan,
            decision,
        )
    )

    if conflict is not None:

        st.error(
            "The Current Decision Plan already contains "
            "a decision that changes Collection Time. "
            "Remove or replace that decision before adding this one."
        )

        return False

    # -----------------------------------------------------
    # IMMUTABLE PLAN UPDATE
    # -----------------------------------------------------

    updated_plan = (
        current_plan.add(
            decision
        )
    )

    st.session_state.decision_plan = (
        updated_plan
    )

    return True


# =========================================================
# CANDIDATE MANAGEMENT
# =========================================================

def set_ar_candidate(
    decision,
    metadata=None,
):
    st.session_state[
        AR_CANDIDATE
    ] = decision

    if metadata is not None:

        st.session_state[
            AR_META
        ] = metadata


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
    try:
        return float(
            baseline_state
            .income_statement
            .revenue
        )

    except AttributeError:

        price = float(
            getattr(
                baseline_state,
                "price",
                150.0,
            )
        )

        volume = float(
            getattr(
                baseline_state,
                "volume",
                12000.0,
            )
        )

        return (
            price
            * volume
        )


def _get_variable_cost(
    baseline_state,
):
    try:
        return float(
            baseline_state
            .unit_economics
            .variable_cost
        )

    except AttributeError:

        return float(
            getattr(
                baseline_state,
                "variable_cost",
                100.0,
            )
        )


def _get_volume(
    baseline_state,
):
    try:
        return float(
            baseline_state.volume
        )

    except AttributeError:
        return 12000.0


# =========================================================
# RECEIVABLES LAB
# =========================================================

def render_receivables_lab(
    baseline_state,
):
    """
    Receivables Decision Lab.

    Business question:
        "When should my customers pay me?"

    Produces an AR Decision candidate and sends it
    directly to the Current Decision Plan.

    The Decision contains two distinct layers:

        ar_days
            → central CompanyState / Financial Engine

        collection_profile
            → Cash Management timing layer

    The collection_profile is a management assumption,
    not customer-level aging analysis.
    """

    st.title(
        "💶 Receivables Lab"
    )

    st.markdown(
        """
        Decide how quickly customers should pay you.

        The lab compares your current collection policy with
        alternative payment policies and can create an **AR Decision**
        for the central Decision Plan.
        """
    )

    # =====================================================
    # CURRENT POLICY
    # =====================================================

    wc = baseline_state.working_capital

    current_ar_days = float(
        wc.ar_days
    )

    st.subheader(
        "When do you currently collect?"
    )

    st.metric(
        "Current Collection Time",
        f"{current_ar_days:.1f} days",
    )

    revenue = _get_revenue(
        baseline_state
    )

    variable_cost = _get_variable_cost(
        baseline_state
    )

    volume = _get_volume(
        baseline_state
    )

    cogs_default = (
        variable_cost
        * volume
    )

    # =====================================================
    # SIMPLE MANUAL POLICY
    # =====================================================

    st.divider()

    st.subheader(
        "1. Set a Collection Target"
    )

    st.caption(
        "If you already know the collection target, "
        "you can set it directly."
    )

    ar_target = st.number_input(
        "Target Collection Time (days)",
        min_value=0.0,
        value=current_ar_days,
        step=1.0,
        key="receivables_ar_target",
    )

    if st.button(
        "Use This Collection Policy",
        key="receivables_use_manual",
        use_container_width=True,
    ):

        decision = (
            DecisionFactory.ar_days_change(
                decision_id=(
                    "receivables_manual_"
                    f"{uuid4().hex[:8]}"
                ),
                target_ar_days=ar_target,
            )
        )

        collection_profile = (
            _build_collection_profile(
                new_policy_pct=1.0,
                new_policy_days=ar_target,
                old_policy_pct=0.0,
                old_policy_days=current_ar_days,
            )
        )

        decision = (
            _attach_collection_profile(
                decision,
                collection_profile,
            )
        )

        set_ar_candidate(
            decision=decision,
            metadata={
                "source": "manual",
                "method": (
                    "Manual Collection Policy"
                ),
                "ar_days": float(
                    ar_target
                ),
                "collection_profile": (
                    collection_profile
                ),
            },
        )

        st.success(
            "Collection policy is ready as an AR candidate."
        )

        st.rerun()

    # =====================================================
    # EARLY PAYMENT DISCOUNT
    # =====================================================

    st.divider()

    st.subheader(
        "2. Offer Customers a Discount for Paying Earlier"
    )

    st.caption(
        "Use this when the question is: "
        "\"Is it worth giving customers a discount to get the cash sooner?\""
    )

    with st.expander(
        "💡 What is this decision about?",
        expanded=False,
    ):

        st.markdown(
            """
            You are trading **margin** for **faster cash collection**.

            The lab estimates whether the faster cash collection
            compensates for the discount you give customers.

            It also considers possible additional sales.

            For Cash Management, the resulting policy remains simple:

            **one percentage follows the new payment policy and the
            remaining percentage follows the old policy.**

            This is a management planning assumption, not an
            invoice-level customer aging analysis.
            """
        )

    col_a, col_b = st.columns(2)

    # -----------------------------------------------------
    # LEFT
    # -----------------------------------------------------

    with col_a:

        current_sales = st.number_input(
            "Current Annual Sales (€)",
            min_value=0.0,
            value=float(
                revenue
            ),
            step=1000.0,
            key="receivables_current_sales",
        )

        extra_sales = st.number_input(
            "Expected Additional Sales (€)",
            min_value=0.0,
            value=float(
                revenue * 0.10
            ),
            step=1000.0,
            key="receivables_extra_sales",
        )

        discount_trial = (
            st.number_input(
                "Discount Offered (%)",
                min_value=0.0,
                max_value=100.0,
                value=2.0,
                step=0.1,
                key="receivables_discount_rate",
            )
            / 100.0
        )

        adoption = (
            st.number_input(
                "Expected Customer Adoption (%)",
                min_value=0.0,
                max_value=100.0,
                value=40.0,
                step=1.0,
                key="receivables_adoption",
            )
            / 100.0
        )

        current_discount_days = (
            st.number_input(
                "Current Payment Days — Customers Taking Discount",
                min_value=1,
                max_value=365,
                value=max(
                    1,
                    int(
                        current_ar_days
                    ),
                ),
                key="receivables_current_discount_days",
            )
        )

    # -----------------------------------------------------
    # RIGHT
    # -----------------------------------------------------

    with col_b:

        new_payment_days = st.number_input(
            "New Payment Days for Customers Taking Discount",
            min_value=1,
            max_value=365,
            value=10,
            step=1,
            key="receivables_new_payment_days",
        )

        cogs_value = st.number_input(
            "Annual COGS (€)",
            min_value=0.0,
            value=float(
                cogs_default
            ),
            step=1000.0,
            key="receivables_cogs",
        )

        wacc_value = (
            st.number_input(
                "Cost of Capital (%)",
                min_value=0.0,
                max_value=100.0,
                value=15.0,
                step=0.1,
                key="receivables_wacc",
            )
            / 100.0
        )

        supplier_days = st.number_input(
            "Supplier Payment Days",
            min_value=1,
            max_value=365,
            value=max(
                1,
                int(
                    wc.ap_days
                ),
            ),
            key="receivables_supplier_days",
        )

        non_discount_days = (
            st.number_input(
                "Payment Days — Customers Not Taking Discount",
                min_value=1,
                max_value=365,
                value=max(
                    1,
                    int(
                        current_ar_days * 1.5
                    ),
                ),
                key="receivables_non_discount_days",
            )
        )

    # =====================================================
    # ANALYZE
    # =====================================================

    if st.button(
        "Analyze Early Payment Policy",
        key="receivables_analyze_discount",
        use_container_width=True,
    ):

        result = calculate_discount_npv(
            current_sales=current_sales,
            extra_sales=extra_sales,
            discount_trial=discount_trial,
            prc_clients_take_disc=adoption,
            days_currently_paying_clients_take_discount=(
                current_discount_days
            ),
            days_currently_paying_clients_not_take_discount=(
                non_discount_days
            ),
            new_days_payment_clients_take_disc=(
                new_payment_days
            ),
            cogs=cogs_value,
            wacc=wacc_value,
            avg_days_pay_suppliers=supplier_days,
        )

        if result is None:

            st.error(
                "The calculation could not be completed. "
                "Please check the assumptions."
            )

        else:

            # Keep the actual customer adoption separately from
            # the NPV model's pct_new_policy calculation.
            #
            # Cash Management needs the simple business assumption:
            #
            #     adoption -> new policy
            #     1-adoption -> old policy
            #
            # This avoids accidentally treating additional sales as
            # a separate customer-aging category.
            collection_profile = (
                _build_collection_profile(
                    new_policy_pct=adoption,
                    new_policy_days=new_payment_days,
                    old_policy_pct=(
                        1.0 - adoption
                    ),
                    old_policy_days=non_discount_days,
                )
            )

            result[
                "collection_profile"
            ] = collection_profile

            result[
                "customer_adoption_pct"
            ] = (
                adoption * 100.0
            )

            st.session_state[
                "receivables_discount_result"
            ] = result

    # =====================================================
    # RESULT
    # =====================================================

    result = st.session_state.get(
        "receivables_discount_result"
    )

    if result is not None:

        st.divider()

        st.subheader(
            "🏁 Collection Policy Result"
        )

        c1, c2, c3 = st.columns(3)

        npv = result[
            "npv"
        ]

        c1.metric(
            "Economic Value",
            f"€ {npv:,.0f}",
            delta=(
                "Creates Value"
                if npv > 0
                else "Destroys Value"
            ),
        )

        c2.metric(
            "New Collection Time",
            f"{result['new_avg_collection_period']:.1f} days",
        )

        c3.metric(
            "Cash Released",
            f"€ {result['free_capital']:,.0f}",
        )

        st.info(
            f"""
            **Current collection time:** 
            {result['avg_current_collection_days']:.1f} days

            **New collection time:** 
            {result['new_avg_collection_period']:.1f} days

            **Cash released:** 
            €{result['free_capital']:,.0f}

            **Discount cost:** 
            €{result['discount_cost']:,.0f}

            **Additional profit from sales:** 
            €{result['profit_from_extra_sales']:,.0f}
            """
        )

        collection_profile = result.get(
            "collection_profile"
        )

        if collection_profile is not None:

            st.caption(
                "Cash timing assumption:"
            )

            st.write(
                f"**{collection_profile['new_policy_pct'] * 100:.0f}%** "
                f"of sales at approximately "
                f"**{collection_profile['new_policy_days']:.0f} days**; "
                f"the remaining "
                f"**{collection_profile['old_policy_pct'] * 100:.0f}%** "
                f"at approximately "
                f"**{collection_profile['old_policy_days']:.0f} days**."
            )

        # -------------------------------------------------
        # CREATE CANDIDATE
        # -------------------------------------------------

        if st.button(
            "Use This Collection Policy",
            key="receivables_use_discount",
            use_container_width=True,
        ):

            effective_ar_days = float(
                result[
                    "new_avg_collection_period"
                ]
            )

            decision = (
                DecisionFactory.ar_days_change(
                    decision_id=(
                        "receivables_discount_"
                        f"{uuid4().hex[:8]}"
                    ),
                    target_ar_days=(
                        effective_ar_days
                    ),
                )
            )

            # IMPORTANT:
            #
            # For the cash-timing layer we use actual customer adoption,
            # not result["pct_new_policy"], because the latter also
            # incorporates extra sales into the NPV model's weighting.
            #
            # Business assumption:
            #
            #     adoption % -> new payment policy
            #     remaining % -> old payment policy
            #
            decision = (
                _attach_collection_profile(
                    decision,
                    collection_profile,
                )
            )

            set_ar_candidate(
                decision=decision,
                metadata={
                    "source": "tool",
                    "method": (
                        "Early Payment Discount"
                    ),
                    "ar_days": (
                        effective_ar_days
                    ),
                    "npv": npv,
                    "cash_released": result[
                        "free_capital"
                    ],
                    "discount": (
                        discount_trial * 100
                    ),
                    "adoption": (
                        adoption * 100
                    ),
                    "collection_profile": (
                        collection_profile
                    ),
                },
            )

            st.success(
                "Collection policy is ready as an AR candidate."
            )

            st.rerun()

    # =====================================================
    # ACTIVE CANDIDATE
    # =====================================================

    st.divider()

    st.subheader(
        "🧩 Receivables Decision"
    )

    ar_candidate = get_ar_candidate()

    if ar_candidate is None:

        st.info(
            "No collection policy has been selected yet."
        )

    else:

        ar_meta = st.session_state.get(
            AR_META,
            {},
        )

        method = ar_meta.get(
            "method",
            getattr(
                ar_candidate,
                "name",
                "Collection Policy",
            ),
        )

        changes = getattr(
            ar_candidate,
            "changes",
            {},
        )

        ar_value = (
            changes.get(
                "ar_days"
            )
            if isinstance(
                changes,
                dict,
            )
            else None
        )

        st.success(
            f"**{method}**"
        )

        if ar_value is not None:

            st.write(
                "Target Collection Time → "
                f"**{float(ar_value):.1f} days**"
            )

        if "collection_profile" in ar_meta:

            profile = (
                ar_meta[
                    "collection_profile"
                ]
            )

            st.write(
                "Cash Timing Policy → "
                f"**{profile['new_policy_pct'] * 100:.0f}% "
                f"at {profile['new_policy_days']:.0f} days** "
                f"+ **{profile['old_policy_pct'] * 100:.0f}% "
                f"at {profile['old_policy_days']:.0f} days**"
            )

        if "npv" in ar_meta:

            st.write(
                "Economic Value → "
                f"**€{ar_meta['npv']:,.0f}**"
            )

        if "cash_released" in ar_meta:

            st.write(
                "Cash Released → "
                f"**€{ar_meta['cash_released']:,.0f}**"
            )

        btn_col1, btn_col2 = (
            st.columns(2)
        )

        if btn_col1.button(
            "➕ Add to Decision Plan",
            key="receivables_add_to_plan",
            use_container_width=True,
        ):

            success = (
                _add_to_current_plan(
                    ar_candidate
                )
            )

            if success:

                st.success(
                    "Receivables Decision added directly to Current Decision Plan."
                )

        if btn_col2.button(
            "Clear Decision",
            key="receivables_clear_candidate",
            use_container_width=True,
        ):

            clear_ar_candidate()

            st.rerun()

    # =====================================================
    # BUSINESS LOGIC
    # =====================================================

    st.divider()

    st.subheader(
        "What changes in the company?"
    )

    st.info(
        """
        **Customers pay sooner**
        → Receivables fall
        → Cash is released
        → Liquidity improves

        The selected policy becomes an **AR Decision**.

        The Decision carries both:

        **Collection Time**
        → used by the central financial model

        **Collection Policy**
        → used by Cash Management to estimate when sales
        turn into cash over the next six months.

        The collection policy is a management planning assumption.
        It does not attempt to reconstruct individual customer aging.
        """
    )
