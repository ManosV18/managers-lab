from decimal import Decimal, InvalidOperation
from uuid import uuid4

import streamlit as st

from core.decision import DecisionFactory
from core.decision_plan import DecisionPlan


# =========================================================
# CANDIDATE KEYS
# =========================================================

WC_AP_CANDIDATE = "wc_ap_candidate"
WC_AP_META = "wc_ap_candidate_meta"


# =========================================================
# NUMERIC HELPERS
# =========================================================

def _safe_float(value, default=0.0):
    try:
        if value is None:
            return float(default)

        result = float(value)

        if result != result:
            return float(default)

        return result

    except (TypeError, ValueError, OverflowError):
        return float(default)


def _money(value):
    return f"€{float(value):,.0f}"


def _pct(value):
    return f"{float(value):.1f}%"


# =========================================================
# BASELINE EXTRACTION
# =========================================================

def _get_operational_drivers(baseline_state):
    """
    V2 canonical CompanyState:
        baseline_state.drivers

    A small fallback is retained for compatibility with older
    state objects, but the canonical path is drivers.
    """

    drivers = getattr(baseline_state, "drivers", None)

    if drivers is not None:
        return drivers

    return baseline_state


def _get_working_capital(baseline_state):
    wc = getattr(baseline_state, "working_capital", None)

    if wc is None:
        raise AttributeError(
            "CompanyState is missing working_capital."
        )

    return wc


def _get_price(drivers):
    return _safe_float(
        getattr(drivers, "price", 0.0),
        0.0,
    )


def _get_volume(drivers):
    return _safe_float(
        getattr(drivers, "volume", 0.0),
        0.0,
    )


def _get_variable_cost(drivers):
    return _safe_float(
        getattr(drivers, "variable_cost_per_unit", 0.0),
        0.0,
    )


def _get_annual_cogs(baseline_state):
    """
    Annual COGS = annual volume × variable cost per unit.

    This is the starting point for supplier purchases.

    If inventory policy is unchanged, annual purchases are
    approximately equal to annual COGS.
    """

    drivers = _get_operational_drivers(baseline_state)

    volume = _get_volume(drivers)
    variable_cost = _get_variable_cost(drivers)

    return max(0.0, volume * variable_cost)


def _get_inventory_days(baseline_state):
    wc = _get_working_capital(baseline_state)

    return max(
        0.0,
        _safe_float(
            getattr(wc, "inventory_days", 0.0),
            0.0,
        ),
    )


def _get_ap_days(baseline_state):
    wc = _get_working_capital(baseline_state)

    return max(
        0.0,
        _safe_float(
            getattr(wc, "ap_days", 0.0),
            0.0,
        ),
    )


# =========================================================
# PURCHASES MODEL
# =========================================================

def calculate_supplier_purchases(
    annual_cogs,
    opening_inventory_days,
    closing_inventory_days=None,
):
    """
    Convert operating COGS into annual purchases.

    Inventory determines purchases:

        Purchases
        = COGS
        + Closing Inventory
        - Opening Inventory

    The current CompanyState does not contain an explicit
    opening-inventory euro balance. Therefore inventory value
    is inferred from annual COGS / 365.

    If closing inventory days are not supplied, the baseline
    inventory policy is maintained.
    """

    annual_cogs = max(0.0, float(annual_cogs))
    opening_inventory_days = max(
        0.0,
        float(opening_inventory_days),
    )

    if closing_inventory_days is None:
        closing_inventory_days = opening_inventory_days

    closing_inventory_days = max(
        0.0,
        float(closing_inventory_days),
    )

    opening_inventory = (
        annual_cogs
        * opening_inventory_days
        / 365.0
    )

    closing_inventory = (
        annual_cogs
        * closing_inventory_days
        / 365.0
    )

    purchases = (
        annual_cogs
        + closing_inventory
        - opening_inventory
    )

    return {
        "annual_cogs": annual_cogs,
        "opening_inventory": opening_inventory,
        "closing_inventory": closing_inventory,
        "annual_purchases": max(0.0, purchases),
    }


# =========================================================
# PAYMENT TIMING ENGINE
# =========================================================

def build_monthly_payment_schedule(
    annual_purchases,
    opening_ap,
    ap_days,
    monthly_purchase_profile=None,
):
    """
    Build a 12-month supplier cash-payment schedule.

    Purchases are the driver.

    AP days determine when each purchase is paid.

    We approximate a month as 30 days.

    Examples:
        30 days -> 100% paid next month
        45 days -> 50% next month + 50% following month
        60 days -> 100% paid two months later

    Opening AP is paid in Month 1.

    Returns a list of 12 dictionaries.
    """

    annual_purchases = max(
        0.0,
        float(annual_purchases),
    )

    opening_ap = max(
        0.0,
        float(opening_ap),
    )

    ap_days = max(
        0.0,
        float(ap_days),
    )

    if monthly_purchase_profile is None:
        monthly_purchase_profile = [
            1.0 / 12.0
            for _ in range(12)
        ]

    if len(monthly_purchase_profile) != 12:
        raise ValueError(
            "monthly_purchase_profile must contain 12 values."
        )

    purchases = [
        annual_purchases * float(weight)
        for weight in monthly_purchase_profile
    ]

    schedule = [
        {
            "month": month + 1,
            "purchases": purchases[month],
            "cash_paid": 0.0,
            "ending_ap": 0.0,
        }
        for month in range(12)
    ]

    # Existing AP is paid during Month 1.
    schedule[0]["cash_paid"] += opening_ap

    # -----------------------------------------------------
    # Allocate each month's purchases to future payments.
    # -----------------------------------------------------

    lag = ap_days / 30.0

    whole_months = int(lag)
    fractional_month = lag - whole_months

    for purchase_month in range(12):
        purchase_amount = purchases[purchase_month]

        if purchase_amount <= 0:
            continue

        # No credit:
        if ap_days <= 0:
            payment_month = purchase_month

            if payment_month < 12:
                schedule[payment_month]["cash_paid"] += (
                    purchase_amount
                )

            continue

        first_payment_month = (
            purchase_month + whole_months
        )

        if fractional_month <= 0.000001:
            if first_payment_month < 12:
                schedule[first_payment_month]["cash_paid"] += (
                    purchase_amount
                )

        else:
            first_share = 1.0 - fractional_month
            second_share = fractional_month

            if first_payment_month < 12:
                schedule[first_payment_month]["cash_paid"] += (
                    purchase_amount * first_share
                )

            second_payment_month = first_payment_month + 1

            if second_payment_month < 12:
                schedule[second_payment_month]["cash_paid"] += (
                    purchase_amount * second_share
                )

    # -----------------------------------------------------
    # Ending AP = cumulative purchases - cumulative cash paid
    # -----------------------------------------------------

    cumulative_purchases = opening_ap
    cumulative_cash_paid = 0.0

    for row in schedule:
        cumulative_purchases += row["purchases"]
        cumulative_cash_paid += row["cash_paid"]

        row["ending_ap"] = max(
            0.0,
            cumulative_purchases
            - cumulative_cash_paid,
        )

    return schedule


# =========================================================
# EARLY PAYMENT DISCOUNT ENGINE
# =========================================================

def calculate_early_payment_discount(
    annual_purchases,
    supplier_credit_days,
    early_payment_days,
    discount,
    eligible_percentage,
    financing_rate,
):
    """
    Economic analysis of paying suppliers early.

    Discount benefit:
        purchases × discount × eligible %

    Financing cost:
        value of supplier credit surrendered × financing rate

    The relevant credit surrendered is the number of days
    between normal supplier payment and early payment.
    """

    annual_purchases = max(
        0.0,
        float(annual_purchases),
    )

    supplier_credit_days = max(
        0.0,
        float(supplier_credit_days),
    )

    early_payment_days = max(
        0.0,
        float(early_payment_days),
    )

    discount = max(
        0.0,
        float(discount),
    )

    eligible_percentage = max(
        0.0,
        min(1.0, float(eligible_percentage)),
    )

    financing_rate = max(
        0.0,
        float(financing_rate),
    )

    payment_acceleration_days = max(
        0.0,
        supplier_credit_days
        - early_payment_days,
    )

    eligible_purchases = (
        annual_purchases
        * eligible_percentage
    )

    discount_gain = (
        eligible_purchases
        * discount
    )

    financing_cost = (
        eligible_purchases
        * payment_acceleration_days
        / 365.0
        * financing_rate
    )

    net_gain = (
        discount_gain
        - financing_cost
    )

    return {
        "eligible_purchases": eligible_purchases,
        "payment_acceleration_days": payment_acceleration_days,
        "discount_gain": discount_gain,
        "financing_cost": financing_cost,
        "net_gain": net_gain,
    }


# =========================================================
# CANDIDATE MANAGEMENT
# =========================================================

def set_ap_candidate(decision, metadata=None):
    st.session_state[WC_AP_CANDIDATE] = decision

    if metadata is not None:
        st.session_state[WC_AP_META] = metadata


def clear_ap_candidate():
    st.session_state.pop(WC_AP_CANDIDATE, None)
    st.session_state.pop(WC_AP_META, None)


def _get_current_plan() -> DecisionPlan:
    plan = st.session_state.get("decision_plan")

    if isinstance(plan, DecisionPlan):
        return plan

    plan = DecisionPlan.create(
        plan_id="main_plan",
        name="Current Decision Plan",
    )

    st.session_state.decision_plan = plan

    return plan


# =========================================================
# MAIN RENDER
# =========================================================

def render_suppliers_lab(baseline_state):

    st.title("🚚 Suppliers & Payables Lab")

    st.markdown(
        """
        **Inventory determines what you need to buy.**
        
        **Payment terms determine when you pay for it.**
        
        This Lab therefore starts from the operating purchasing
        requirement and evaluates supplier payment timing separately.
        """
    )

    # =====================================================
    # BASELINE
    # =====================================================

    wc = _get_working_capital(baseline_state)

    current_ap_days = _get_ap_days(baseline_state)
    inventory_days = _get_inventory_days(baseline_state)
    annual_cogs = _get_annual_cogs(baseline_state)

    purchase_model = calculate_supplier_purchases(
        annual_cogs=annual_cogs,
        opening_inventory_days=inventory_days,
        closing_inventory_days=inventory_days,
    )

    annual_purchases = purchase_model["annual_purchases"]

    current_ap = (
        annual_purchases
        * current_ap_days
        / 365.0
    )

    # =====================================================
    # CURRENT SUPPLIER STATE
    # =====================================================

    st.subheader("Current Supplier Credit State")

    col1, col2, col3, col4 = st.columns(4)

    col1.metric(
        "Inventory Days",
        f"{inventory_days:.1f}",
    )

    col2.metric(
        "Current AP Days",
        f"{current_ap_days:.1f}",
    )

    col3.metric(
        "Annual Purchases",
        _money(annual_purchases),
    )

    col4.metric(
        "Current AP",
        _money(current_ap),
    )

    st.caption(
        "Purchases are derived from the operating model. "
        "They are not entered manually in the Supplier Lab."
    )

    st.divider()

    # =====================================================
    # SECTION 1 — PAYMENT TERMS
    # =====================================================

    st.markdown("### 💳 Supplier Payment Terms")

    st.caption(
        "Evaluate what happens if supplier payment terms change. "
        "The purchase requirement stays unchanged; only the timing "
        "of supplier cash payments changes."
    )

    col_a, col_b = st.columns(2)

    with col_a:

        proposed_ap_days = st.number_input(
            "Target Supplier Payment Terms (Days)",
            min_value=0,
            max_value=365,
            value=max(
                0,
                int(round(current_ap_days)),
            ),
            step=1,
            key="supp_target_ap_days",
        )

    with col_b:

        financing_rate_pct = st.number_input(
            "Cost of Cash / Financing Rate (%)",
            min_value=0.0,
            max_value=100.0,
            value=15.0,
            step=0.1,
            key="supp_financing_rate",
        )

    proposed_ap_days = float(proposed_ap_days)

    proposed_ap = (
        annual_purchases
        * proposed_ap_days
        / 365.0
    )

    cash_released = proposed_ap - current_ap

    # =====================================================
    # PAYMENT SCHEDULES
    # =====================================================

    current_schedule = build_monthly_payment_schedule(
        annual_purchases=annual_purchases,
        opening_ap=current_ap,
        ap_days=current_ap_days,
    )

    proposed_schedule = build_monthly_payment_schedule(
        annual_purchases=annual_purchases,
        opening_ap=current_ap,
        ap_days=proposed_ap_days,
    )

    current_year_cash = sum(
        row["cash_paid"]
        for row in current_schedule
    )

    proposed_year_cash = sum(
        row["cash_paid"]
        for row in proposed_schedule
    )

    first_year_cash_difference = (
        proposed_year_cash
        - current_year_cash
    )

    # =====================================================
    # RESULT
    # =====================================================

    st.divider()

    st.subheader("🏁 Payment Terms Impact")

    r1, r2, r3, r4 = st.columns(4)

    r1.metric(
        "Current AP",
        _money(current_ap),
    )

    r2.metric(
        "Target AP",
        _money(proposed_ap),
    )

    r3.metric(
        "Change in AP",
        _money(cash_released),
        delta=(
            "Cash Released"
            if cash_released >= 0
            else "Cash Absorbed"
        ),
    )

    r4.metric(
        "Annual Purchases",
        _money(annual_purchases),
    )

    if proposed_ap_days > current_ap_days:

        st.success(
            f"""
            Extending supplier terms from
            **{current_ap_days:.1f} to {proposed_ap_days:.1f} days**
            increases Accounts Payable by approximately
            **{_money(cash_released)}**.

            This is cash financing provided by suppliers rather than
            additional borrowing.
            """
        )

    elif proposed_ap_days < current_ap_days:

        st.warning(
            f"""
            Shortening supplier terms from
            **{current_ap_days:.1f} to {proposed_ap_days:.1f} days**
            reduces Accounts Payable by approximately
            **{_money(abs(cash_released))}**.

            This means cash leaves the company earlier.
            """
        )

    else:

        st.info(
            "The proposed supplier payment terms are unchanged."
        )

    # =====================================================
    # CASH TIMING TABLE
    # =====================================================

    st.markdown("### 📅 Supplier Cash Timing")

    timing_rows = []

    for current_row, proposed_row in zip(
        current_schedule,
        proposed_schedule,
    ):

        timing_rows.append(
            {
                "Month": f"Month {current_row['month']}",
                "Purchases": current_row["purchases"],
                "Current Cash Paid": current_row["cash_paid"],
                "Target Cash Paid": proposed_row["cash_paid"],
                "Cash Timing Change": (
                    proposed_row["cash_paid"]
                    - current_row["cash_paid"]
                ),
                "Target Ending AP": proposed_row["ending_ap"],
            }
        )

    st.dataframe(
        timing_rows,
        use_container_width=True,
        hide_index=True,
        column_config={
            "Purchases": st.column_config.NumberColumn(
                "Purchases",
                format="€%,.0f",
            ),
            "Current Cash Paid": st.column_config.NumberColumn(
                "Current Cash Paid",
                format="€%,.0f",
            ),
            "Target Cash Paid": st.column_config.NumberColumn(
                "Target Cash Paid",
                format="€%,.0f",
            ),
            "Cash Timing Change": st.column_config.NumberColumn(
                "Cash Timing Change",
                format="€%,.0f",
            ),
            "Target Ending AP": st.column_config.NumberColumn(
                "Target Ending AP",
                format="€%,.0f",
            ),
        },
    )

    # =====================================================
    # SECTION 2 — EARLY PAYMENT DISCOUNT
    # =====================================================

    st.divider()

    st.markdown("### 💰 Early Payment Discount Analysis")

    st.caption(
        "This is a separate supplier decision: pay earlier to obtain "
        "a discount. The question is whether the discount compensates "
        "for giving up supplier financing earlier."
    )

    col_c, col_d = st.columns(2)

    with col_c:

        discount_pct = st.number_input(
            "Early Payment Discount (%)",
            min_value=0.0,
            max_value=100.0,
            value=2.0,
            step=0.1,
            key="supp_discount_pct",
        )

        eligible_pct = st.slider(
            "% of Purchases Eligible for Discount",
            min_value=0,
            max_value=100,
            value=50,
            step=5,
            key="supp_discount_eligibility",
        )

    with col_d:

        early_payment_days = st.number_input(
            "Early Payment Days",
            min_value=0,
            max_value=365,
            value=min(
                10,
                max(
                    0,
                    int(round(current_ap_days)),
                ),
            ),
            step=1,
            key="supp_early_payment_days",
        )

        st.metric(
            "Normal Supplier Terms",
            f"{current_ap_days:.1f} days",
        )

    discount_result = calculate_early_payment_discount(
        annual_purchases=annual_purchases,
        supplier_credit_days=current_ap_days,
        early_payment_days=float(early_payment_days),
        discount=float(discount_pct) / 100.0,
        eligible_percentage=float(eligible_pct) / 100.0,
        financing_rate=float(financing_rate_pct) / 100.0,
    )

    discount_gain = discount_result["discount_gain"]
    financing_cost = discount_result["financing_cost"]
    discount_net_gain = discount_result["net_gain"]

    st.divider()

    st.subheader("Early Payment Trade-off")

    d1, d2, d3 = st.columns(3)

    d1.metric(
        "Discount Benefit",
        _money(discount_gain),
    )

    d2.metric(
        "Supplier Credit Given Up",
        f"-{_money(financing_cost)}",
    )

    d3.metric(
        "Net Economic Benefit",
        _money(discount_net_gain),
        delta=(
            "Creates Value"
            if discount_net_gain >= 0
            else "Destroys Value"
        ),
        delta_color=(
            "normal"
            if discount_net_gain >= 0
            else "inverse"
        ),
    )

    st.caption(
        f"""
        Eligible purchases: {_money(discount_result['eligible_purchases'])}
        · Credit surrendered:
        {discount_result['payment_acceleration_days']:.1f} days
        """
    )

    if discount_net_gain > 0:

        st.success(
            f"""
            Under these assumptions, the early-payment discount creates
            approximately **{_money(discount_net_gain)}** of net economic
            value.
            """
        )

    elif discount_net_gain < 0:

        st.info(
            f"""
            Under these assumptions, retaining supplier credit has higher
            economic value. The estimated opportunity cost of paying early
            exceeds the discount benefit by approximately
            **{_money(abs(discount_net_gain))}**.
            """
        )

    else:

        st.info(
            "The estimated discount benefit and financing cost are equal."
        )

    # =====================================================
    # DECISION CREATION
    # =====================================================

    st.divider()

    st.subheader("🧩 Supplier Decision Candidate")

    st.caption(
        "Choose whether to create an AP decision from the payment-terms "
        "analysis. The decision will be sent to the Current Decision Plan."
    )

    candidate_exists = (
        WC_AP_CANDIDATE in st.session_state
    )

    col_e, col_f = st.columns(2)

    with col_e:

        if st.button(
            "➕ Use Target Supplier Terms",
            key="supp_create_candidate",
            use_container_width=True,
        ):

            decision = DecisionFactory.ap_days_change(
                decision_id=f"supplier_ap_{uuid4().hex[:8]}",
                target_ap_days=proposed_ap_days,
            )

            set_ap_candidate(
                decision=decision,
                metadata={
                    "source": "suppliers_lab",
                    "method": "Supplier Payment Terms Analysis",
                    "current_ap_days": current_ap_days,
                    "target_ap_days": proposed_ap_days,
                    "annual_purchases": annual_purchases,
                    "current_ap": current_ap,
                    "target_ap": proposed_ap,
                    "cash_released": cash_released,
                    "inventory_days": inventory_days,
                },
            )

            st.success(
                "Supplier payment policy is ready as an AP candidate."
            )

            st.rerun()

    with col_f:

        if st.button(
            "Clear Candidate",
            key="supp_clear_candidate",
            use_container_width=True,
            disabled=not candidate_exists,
        ):

            clear_ap_candidate()
            st.rerun()

    # =====================================================
    # ACTIVE CANDIDATE
    # =====================================================

    ap_candidate = st.session_state.get(
        WC_AP_CANDIDATE
    )

    if ap_candidate is not None:

        st.divider()

        st.markdown("### Active Payables Decision")

        ap_meta = st.session_state.get(
            WC_AP_META,
            {},
        )

        ap_val = ap_candidate.changes.get(
            "ap_days"
        )

        c1, c2, c3 = st.columns(3)

        c1.metric(
            "Target AP Days",
            f"{float(ap_val):.1f}",
        )

        c2.metric(
            "Annual Purchases",
            _money(
                ap_meta.get(
                    "annual_purchases",
                    annual_purchases,
                )
            ),
        )

        c3.metric(
            "Cash Released",
            _money(
                ap_meta.get(
                    "cash_released",
                    0.0,
                )
            ),
        )

        st.info(
            f"""
            **Current:** {current_ap_days:.1f} days  
            **Target:** {float(ap_val):.1f} days  
            **Decision:** AP payment-term change
            """
        )

        if st.button(
            "➕ Push Candidate to Current Decision Plan",
            key="supp_push_to_plan",
            use_container_width=True,
        ):

            current_plan = _get_current_plan()

            updated_plan = current_plan.add(
                ap_candidate
            )

            st.session_state.decision_plan = (
                updated_plan
            )

            st.success(
                f"AP Decision added to Decision Plan: "
                f"{ap_candidate.name}"
            )

            clear_ap_candidate()

            st.rerun()
