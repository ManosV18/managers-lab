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
    Receivables economic calculation.

    The calculation logic is based on the original V1 model.

    Percentage inputs are supplied as decimals (0-1).

    Returns:
        - current weighted collection days
        - current receivables
        - new weighted collection days
        - new receivables
        - free capital
        - profit from extra sales
        - profit from released capital
        - discount cost
        - NPV
        - maximum discount
        - optimum discount
        - percentage under new policy
    """

    getcontext().prec = 50

    try:
        cs = Decimal(str(current_sales))
        es = Decimal(str(extra_sales))
        dt = Decimal(str(discount_trial))
        pct_take = Decimal(str(prc_clients_take_disc))

        d_take_old = Decimal(
            str(days_currently_paying_clients_take_discount)
        )

        d_no_take_old = Decimal(
            str(days_currently_paying_clients_not_take_discount)
        )

        d_new_policy = Decimal(
            str(new_days_payment_clients_take_disc)
        )

        cg = Decimal(str(cogs))
        wc = Decimal(str(wacc))
        d_supp = Decimal(str(avg_days_pay_suppliers))

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

        if es < 0:
            return None

        if dt < 0 or dt > 1:
            return None

        if cg < 0:
            return None

        if (
            d_take_old < 0
            or d_no_take_old < 0
            or d_new_policy < 0
            or d_supp < 0
        ):
            return None

        pct_no_take = (
            Decimal("1") - pct_take
        )

        # =====================================================
        # CURRENT POLICY
        # =====================================================

        avg_curr_days = (
            pct_take * d_take_old
            + pct_no_take * d_no_take_old
        )

        curr_rec = (
            cs * avg_curr_days
        ) / Decimal("365")

        # =====================================================
        # NEW POLICY
        # =====================================================

        total_sales = (
            cs + es
        )

        if total_sales <= 0:
            return None

        prcnt_new_policy = (
            (cs * pct_take) + es
        ) / total_sales

        prcnt_old_policy = (
            Decimal("1")
            - prcnt_new_policy
        )

        if prcnt_new_policy <= 0:
            return None

        new_avg_period = (
            prcnt_new_policy * d_new_policy
            + prcnt_old_policy * d_no_take_old
        )

        new_rec = (
            total_sales * new_avg_period
        ) / Decimal("365")

        free_cap = (
            curr_rec - new_rec
        )

        # =====================================================
        # PROFIT EFFECT
        # =====================================================

        gross_margin_ratio = (
            Decimal("1")
            - (cg / cs)
        )

        prof_extra = (
            es * gross_margin_ratio
        )

        prof_free_cap = (
            free_cap * wc
        )

        dist_cost = (
            total_sales
            * prcnt_new_policy
            * dt
        )

        # =====================================================
        # DISCOUNTED CASH FLOW
        # =====================================================

        i_float = float(
            wc / Decimal("365")
        )

        MAX_EXP = 500.0

        exp_new = min(
            float(d_new_policy),
            MAX_EXP,
        )

        exp_no_take = min(
            float(d_no_take_old),
            MAX_EXP,
        )

        exp_curr = min(
            float(avg_curr_days),
            MAX_EXP,
        )

        exp_supp = min(
            float(d_supp),
            MAX_EXP,
        )

        base = (
            1.0 + i_float
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
            * (Decimal("1") - dt)
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
            cs / t4_denom
        )

        inflow = (
            term1 + term2
        )

        outflow = (
            term3 + term4
        )

        npv = (
            inflow - outflow
        )

        # =====================================================
        # MAXIMUM DISCOUNT
        # =====================================================

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
                    (cg / cs)
                    * (es / cs)
                    * pow_3
                )
            )
            / (
                prcnt_new_policy
                * (
                    Decimal("1")
                    + (es / cs)
                )
            )
        )

        max_d = (
            Decimal("1")
            - pow_1 * term_inner
        )

        # =====================================================
        # OPTIMUM DISCOUNT
        # =====================================================

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

    DecisionPlan is immutable, therefore every add operation
    returns a new plan which must be stored back in session state.
    """

    plan = st.session_state.get(
        "decision_plan"
    )

    if isinstance(plan, DecisionPlan):
        return plan

    plan = DecisionPlan.create(
        plan_id="main_plan",
        name="Current Decision Plan",
    )

    st.session_state.decision_plan = plan

    return plan


def _find_conflicting_driver(
    plan,
    decision,
):
    """
    Check whether another decision already changes ar_days.
    """

    decision_changes = getattr(
        decision,
        "changes",
        {},
    )

    if "ar_days" not in decision_changes:
        return None

    for existing_decision in plan.decisions:

        existing_changes = getattr(
            existing_decision,
            "changes",
            {},
        )

        if "ar_days" in existing_changes:
            return existing_decision

    return None


def _add_to_current_plan(decision):
    """
    Add the decision to Current Decision Plan.

    The decision is not executed here.

    Execution/evaluation remains centralized in the V2 architecture.
    """

    current_plan = _get_current_plan()

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

    conflict = _find_conflicting_driver(
        current_plan,
        decision,
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

    updated_plan = current_plan.add(
        decision
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
# V2 BASELINE HELPERS
# =========================================================

def _get_revenue(
    baseline_state,
):
    """
    Annual company sales from central CompanyState.

    V2:
        revenue = price * volume
    """

    drivers = baseline_state.drivers

    return (
        float(drivers.price)
        * float(drivers.volume)
    )


def _get_cogs(
    baseline_state,
):
    """
    Annual company COGS from central CompanyState.

    V2:
        COGS = variable_cost_per_unit * volume
    """

    drivers = baseline_state.drivers

    return (
        float(
            drivers.variable_cost_per_unit
        )
        * float(
            drivers.volume
        )
    )


def _get_wacc(
    baseline_state,
):
    """
    WACC from central CompanyState.
    """

    return float(
        baseline_state
        .capital_structure
        .wacc
    )


def _get_ar_days(
    baseline_state,
):
    """
    Current AR days from central CompanyState.
    """

    return float(
        baseline_state
        .working_capital
        .ar_days
    )


def _get_ap_days(
    baseline_state,
):
    """
    Current AP days from central CompanyState.
    """

    return float(
        baseline_state
        .working_capital
        .ap_days
    )


# =========================================================
# RECEIVABLES LAB
# =========================================================

def render_receivables_lab(
    baseline_state,
):
    """
    Receivables Decision Lab — Managers Lab V2.

    Company financial data comes from the central CompanyState.

    The original V1 economic calculation is preserved.

    Decision inputs remain editable because they describe the
    proposed commercial policy rather than the company's locked
    baseline.

    Flow:

        Locked Baseline
              ↓
        Receivables Lab
              ↓
        AR Decision
              ↓
        Current Decision Plan
              ↓
        Central evaluation / projected CompanyState
    """

    st.title(
        "💶 Receivables Lab"
    )

    st.markdown(
        """
        Decide how quickly customers should pay you.

        The company financial data is taken automatically from
        the current **Baseline**. You only change the commercial
        policy you are testing.
        """
    )

    # =====================================================
    # COMPANY BASELINE
    # =====================================================

    revenue = _get_revenue(
        baseline_state
    )

    cogs_default = _get_cogs(
        baseline_state
    )

    wacc_default = _get_wacc(
        baseline_state
    )

    current_ar_days = _get_ar_days(
        baseline_state
    )

    supplier_days_default = _get_ap_days(
        baseline_state
    )

    st.subheader(
        "Company Baseline"
    )

    b1, b2, b3, b4, b5 = st.columns(5)

    b1.metric(
        "Annual Sales",
        f"€{revenue:,.0f}",
    )

    b2.metric(
        "Annual COGS",
        f"€{cogs_default:,.0f}",
    )

    b3.metric(
        "Current AR Days",
        f"{current_ar_days:.1f}",
    )

    b4.metric(
        "Supplier Days",
        f"{supplier_days_default:.1f}",
    )

    b5.metric(
        "WACC",
        f"{wacc_default * 100:.2f}%",
    )

    st.caption(
        "These are company baseline values. "
        "They are read from the central CompanyState and "
        "cannot be changed inside this Lab."
    )

    # =====================================================
    # SIMPLE MANUAL POLICY
    # =====================================================

    st.divider()

    st.subheader(
        "1. Set a Collection Target"
    )

    st.caption(
        "Use this when you already know the collection target "
        "you want the company to adopt."
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
        "Test whether faster collection creates enough economic "
        "value to justify the discount."
    )

    with st.expander(
        "💡 What is this decision about?",
        expanded=False,
    ):
        st.markdown(
            """
            You are trading **margin** for **faster cash collection**.

            The model compares the current collection pattern with
            the proposed policy and calculates:

            - receivables before and after the change,
            - cash released,
            - profit from additional sales,
            - profit from released capital,
            - discount cost,
            - NPV,
            - maximum discount,
            - optimum discount.
            """
        )

    col_a, col_b = st.columns(2)

    # =====================================================
    # POLICY INPUTS — LEFT
    # =====================================================

    with col_a:

        extra_sales = st.number_input(
            "Expected Additional Sales (€)",
            min_value=0.0,
            value=0.0,
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
                "Customers Taking Discount (%)",
                min_value=0.0,
                max_value=100.0,
                value=40.0,
                step=1.0,
                key="receivables_adoption",
            )
            / 100.0
        )

        current_discount_days = st.number_input(
            "Current Payment Days — Customers Taking Discount",
            min_value=0,
            max_value=365,
            value=max(
                0,
                int(
                    round(
                        current_ar_days
                    )
                ),
            ),
            step=1,
            key="receivables_current_discount_days",
        )

    # =====================================================
    # POLICY INPUTS — RIGHT
    # =====================================================

    with col_b:

        non_discount_days = st.number_input(
            "Current Payment Days — Customers Not Taking Discount",
            min_value=0,
            max_value=365,
            value=max(
                0,
                int(
                    round(
                        current_ar_days
                    )
                ),
            ),
            step=1,
            key="receivables_non_discount_days",
        )

        new_payment_days = st.number_input(
            "New Payment Days for Customers Taking Discount",
            min_value=0,
            max_value=365,
            value=10,
            step=1,
            key="receivables_new_payment_days",
        )

    st.caption(
        f"Baseline AR days: {current_ar_days:.1f} days  |  "
        f"Baseline supplier payment days: "
        f"{supplier_days_default:.1f} days  |  "
        f"Baseline WACC: {wacc_default * 100:.2f}%"
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
            current_sales=revenue,
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
            cogs=cogs_default,
            wacc=wacc_default,
            avg_days_pay_suppliers=(
                supplier_days_default
            ),
        )

        if result is None:

            st.error(
                "The calculation could not be completed. "
                "Please check the policy assumptions."
            )

        else:

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
            f"€{npv:,.0f}",
            delta=(
                "Creates Value"
                if npv > 0
                else "Destroys Value"
            ),
        )

        c2.metric(
            "New Collection Time",
            (
                f"{result['new_avg_collection_period']:.1f}"
                " days"
            ),
        )

        c3.metric(
            "Cash Released",
            (
                f"€{result['free_capital']:,.0f}"
            ),
        )

        # -------------------------------------------------
        # DETAILED RESULT
        # -------------------------------------------------

        r1, r2 = st.columns(2)

        with r1:

            st.metric(
                "Current Receivables",
                (
                    f"€"
                    f"{result['current_receivables']:,.0f}"
                ),
            )

            st.metric(
                "New Receivables",
                (
                    f"€"
                    f"{result['new_receivables']:,.0f}"
                ),
            )

            st.metric(
                "Discount Cost",
                (
                    f"€"
                    f"{result['discount_cost']:,.0f}"
                ),
            )

            st.metric(
                "Additional Profit",
                (
                    f"€"
                    f"{result['profit_from_extra_sales']:,.0f}"
                ),
            )

        with r2:

            st.metric(
                "Profit from Released Capital",
                (
                    f"€"
                    f"{result['profit_from_free_capital']:,.0f}"
                ),
            )

            st.metric(
                "Maximum Discount",
                (
                    f"{result['max_discount']:.2f}%"
                ),
            )

            st.metric(
                "Optimum Discount",
                (
                    f"{result['optimum_discount']:.2f}%"
                ),
            )

            st.metric(
                "Customers Under New Policy",
                (
                    f"{result['pct_new_policy']:.2f}%"
                ),
            )

        
        # =================================================
        # CREATE AR DECISION CANDIDATE
        # =================================================

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
                    "cash_released": (
                        result[
                            "free_capital"
                        ]
                    ),
                    "discount": (
                        discount_trial * 100
                    ),
                    "adoption": (
                        adoption * 100
                    ),
                    "baseline_sales": revenue,
                    "baseline_cogs": (
                        cogs_default
                    ),
                    "baseline_wacc": (
                        wacc_default
                    ),
                    "baseline_ar_days": (
                        current_ar_days
                    ),
                    "baseline_ap_days": (
                        supplier_days_default
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

        ar_value = (
            ar_candidate
            .changes
            .get("ar_days")
        )

        st.success(
            f"**{method}**"
        )

        if ar_value is not None:

            st.write(
                "Target Collection Time → "
                f"**{float(ar_value):.1f} days**"
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

        btn_col1, btn_col2 = st.columns(2)

        # -------------------------------------------------
        # ADD TO CURRENT DECISION PLAN
        # -------------------------------------------------

        if btn_col1.button(
            "➕ Add to Decision Plan",
            key="receivables_add_to_plan",
            use_container_width=True,
        ):

            success = _add_to_current_plan(
                ar_candidate
            )

            if success:

                st.success(
                    "Receivables Decision added directly "
                    "to Current Decision Plan."
                )

        # -------------------------------------------------
        # CLEAR
        # -------------------------------------------------

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

        The central V2 system then determines its effect on
        the company's projected financial state.
        """
    )
