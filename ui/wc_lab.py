from decimal import (
    Decimal,
    InvalidOperation,
    Overflow,
    getcontext,
)
from uuid import uuid4

import streamlit as st
from core.decision import DecisionFactory

# =========================================================
# WORKING CAPITAL CANDIDATE KEYS
# =========================================================

WC_AR_CANDIDATE = "wc_ar_candidate"
WC_INVENTORY_CANDIDATE = "wc_inventory_candidate"
WC_AP_CANDIDATE = "wc_ap_candidate"

WC_AR_META = "wc_ar_candidate_meta"


# =========================================================
# SUPPLIER CREDIT DISCOUNT CALCULATOR
# =========================================================


def calculate_supplier_credit_gain(
    supplier_credit_days: float,
    discount: float,
    cash_prc: float,
    current_sales: float,
    unit_price: float,
    total_unit_cost: float,
    interest_rate_on_debt: float,
):
    """
    Pure calculation for supplier early-payment discount analysis.

    All percentage inputs must be supplied as decimals (0-1).
    Returns:
        discount_gain,
        credit_benefit_lost,
        net_gain
    """

    if unit_price <= 0:
        average_cost_ratio = 0.0
    else:
        average_cost_ratio = total_unit_cost / unit_price

    # 1. Economic benefit from early-payment discount
    discount_gain = (
        current_sales
        * discount
        * cash_prc
    )

    # 2. Economic value of supplier credit given up
    credit_benefit_lost = (
        (current_sales / (365 / supplier_credit_days))
        * average_cost_ratio
        * cash_prc
        * interest_rate_on_debt
    )

    net_gain = discount_gain - credit_benefit_lost

    return (
        discount_gain,
        credit_benefit_lost,
        net_gain,
    )


# =========================================================
# EARLY PAYMENT DISCOUNT CALCULATOR (RECEIVABLES)
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

        if cs <= 0 or pct_take <= 0 or pct_take > 1 or wc < 0:
            return None

        pct_no_take = Decimal("1") - pct_take

        # CURRENT POLICY
        avg_curr_days = (pct_take * d_take_old) + (pct_no_take * d_no_take_old)
        curr_rec = (cs * avg_curr_days) / Decimal("365")

        # NEW POLICY
        total_sales = cs + es
        if total_sales <= 0:
            return None

        prcnt_new_policy = ((cs * pct_take) + es) / total_sales
        prcnt_old_policy = Decimal("1") - prcnt_new_policy

        if prcnt_new_policy <= 0:
            return None

        new_avg_period = (prcnt_new_policy * d_new_policy) + (prcnt_old_policy * d_no_take_old)
        new_rec = (total_sales * new_avg_period) / Decimal("365")
        free_cap = curr_rec - new_rec

        # PROFIT EFFECT
        prof_extra = es * (Decimal("1") - (cg / cs))
        prof_free_cap = free_cap * wc
        dist_cost = total_sales * prcnt_new_policy * dt

        # DISCOUNTED CASH FLOW
        i_float = float(wc / Decimal("365"))
        MAX_EXP = 500.0

        exp_new = min(float(d_new_policy), MAX_EXP)
        exp_no_take = min(float(d_no_take_old), MAX_EXP)
        exp_curr = min(float(avg_curr_days), MAX_EXP)
        exp_supp = min(float(d_supp), MAX_EXP)

        t1_denom = Decimal(str((1.0 + i_float) ** exp_new))
        t2_denom = Decimal(str((1.0 + i_float) ** exp_no_take))
        t3_denom = Decimal(str((1.0 + i_float) ** exp_supp))
        t4_denom = Decimal(str((1.0 + i_float) ** exp_curr))

        term1 = (total_sales * prcnt_new_policy * (Decimal("1") - dt)) / t1_denom
        term2 = (total_sales * prcnt_old_policy) / t2_denom
        term3 = ((cg / cs) * (es / cs) * cs) / t3_denom
        term4 = cs / t4_denom

        inflow = term1 + term2
        outflow = term3 + term4
        npv = inflow - outflow

        # MAXIMUM DISCOUNT
        pow_1 = Decimal(str((1.0 + i_float) ** (exp_new - exp_no_take)))
        pow_2 = Decimal(str((1.0 + i_float) ** (exp_no_take - exp_curr)))
        pow_3 = Decimal(str((1.0 + i_float) ** (exp_no_take - exp_supp)))

        term_inner = (Decimal("1") - (Decimal("1") / prcnt_new_policy)) + (
            pow_2 + (cg / cs) * (es / cs) * pow_3
        ) / (prcnt_new_policy * (Decimal("1") + (es / cs)))

        max_d = Decimal("1") - (pow_1 * term_inner)

        # OPTIMUM DISCOUNT
        pow_opt = Decimal(str((1.0 + i_float) ** (exp_new - exp_curr)))
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
        }

    except (InvalidOperation, Overflow, ZeroDivisionError, ValueError):
        return None


# =========================================================
# CANDIDATE MANAGEMENT
# =========================================================


def set_wc_candidate(decision, candidate_key, metadata=None):
    st.session_state[candidate_key] = decision
    if metadata is not None and candidate_key == WC_AR_CANDIDATE:
        st.session_state[WC_AR_META] = metadata


def clear_wc_candidate(candidate_key):
    st.session_state.pop(candidate_key, None)
    if candidate_key == WC_AR_CANDIDATE:
        st.session_state.pop(WC_AR_META, None)


def get_wc_candidates():
    candidates = {}
    ar = st.session_state.get(WC_AR_CANDIDATE)
    inventory = st.session_state.get(WC_INVENTORY_CANDIDATE)
    ap = st.session_state.get(WC_AP_CANDIDATE)

    if ar is not None:
        candidates["ar"] = ar
    if inventory is not None:
        candidates["inventory"] = inventory
    if ap is not None:
        candidates["ap"] = ap

    return candidates


def add_decision_to_plan(decision):
    """Safely adds a decision candidate to the DecisionPlan instance in session state."""
    if "decision_plan" not in st.session_state or st.session_state["decision_plan"] is None:
        st.warning("No active Decision Plan found in session state.")
        return

    plan = st.session_state["decision_plan"]

    if hasattr(plan, "add_decision"):
        plan.add_decision(decision)
    elif hasattr(plan, "add"):
        plan.add(decision)
    elif hasattr(plan, "decisions") and isinstance(plan.decisions, list):
        existing_ids = [d.id for d in plan.decisions]
        if decision.id not in existing_ids:
            plan.decisions.append(decision)
    elif isinstance(plan, list):
        existing_ids = [d.id for d in plan]
        if decision.id not in existing_ids:
            plan.append(decision)


# =========================================================
# WORKING CAPITAL LAB
# =========================================================


def render_wc_lab(baseline_state):
    st.title("💧 Working Capital Lab")

    st.markdown(
        """
        Test Working Capital policies against the locked baseline.

        Each business decision can produce **one candidate**. You can inspect candidates here and **send them directly to the Decision Plan** for execution in `decision_view.py`.
        """
    )

    # BASELINE
    wc = baseline_state.working_capital
    current_ar_days = float(wc.ar_days)
    current_inventory_days = float(wc.inventory_days)
    current_ap_days = float(wc.ap_days)

    st.subheader("Current Working Capital Policy")
    col1, col2, col3 = st.columns(3)
    col1.metric("AR Days", f"{current_ar_days:.1f}")
    col2.metric("Inventory Days", f"{current_inventory_days:.1f}")
    col3.metric("AP Days", f"{current_ap_days:.1f}")

    st.divider()

    # TABS
    tab1, tab2, tab3 = st.tabs(["Receivables", "Inventory", "Payables"])

    # RECEIVABLES
    with tab1:
        st.subheader("Accounts Receivable")
        st.caption("Define the AR policy. Only one AR candidate can exist at a time.")

        st.markdown("### Manual Collection Policy")
        ar_target = st.number_input(
            "Target AR Days",
            min_value=0.0,
            value=current_ar_days,
            step=1.0,
            key="wc_ar_target",
        )

        if st.button("Use Manual Collection Policy", key="wc_use_manual_ar", use_container_width=True):
            decision = DecisionFactory.ar_days_change(
                decision_id=f"wc_ar_manual_{uuid4().hex[:8]}",
                target_ar_days=ar_target,
            )
            set_wc_candidate(
                decision=decision,
                candidate_key=WC_AR_CANDIDATE,
                metadata={
                    "source": "manual",
                    "method": "Manual Collection Policy",
                    "ar_days": float(ar_target),
                },
            )
            st.success("Manual AR policy set as active AR candidate.")
            st.rerun()

        st.divider()

        # EARLY PAYMENT DISCOUNT
        st.markdown("### 💳 Early Payment Discount")
        st.caption("Evaluate whether faster customer payment creates value after the discount cost.")

        with st.expander("💡 What does this tool evaluate?", expanded=False):
            st.markdown(
                """
                The question is not simply: **"How much discount should I offer?"**
                
                The business question is: **"Does collecting cash sooner create more value than the margin I sacrifice?"**

                The tool calculates the resulting weighted collection period and the NPV of the policy.
                """
            )

        # SYSTEM DEFAULTS
        try:
            revenue = float(baseline_state.income_statement.revenue)
        except AttributeError:
            p = float(getattr(baseline_state, "price", 150.0))
            v = float(getattr(baseline_state, "volume", 12000.0))
            revenue = p * v

        try:
            variable_cost = float(baseline_state.unit_economics.variable_cost)
        except AttributeError:
            variable_cost = float(getattr(baseline_state, "variable_cost", 100.0))

        try:
            volume = float(baseline_state.volume)
        except AttributeError:
            volume = 12000.0

        cogs_default = variable_cost * volume

        # DISCOUNT INPUTS
        col_a, col_b = st.columns(2)

        with col_a:
            current_sales = st.number_input(
                "Current Sales (€)",
                min_value=0.0,
                value=float(revenue),
                step=1000.0,
                key="wc_discount_current_sales",
            )
            extra_sales = st.number_input(
                "Expected Additional Sales (€)",
                min_value=0.0,
                value=float(revenue * 0.10),
                step=1000.0,
                key="wc_discount_extra_sales",
            )
            discount_trial = (
                st.number_input(
                    "Discount Offered (%)",
                    min_value=0.0,
                    max_value=100.0,
                    value=2.0,
                    step=0.1,
                    key="wc_discount_rate",
                )
                / 100
            )
            adoption = (
                st.number_input(
                    "Expected Customer Adoption (%)",
                    min_value=0.0,
                    max_value=100.0,
                    value=40.0,
                    step=1.0,
                    key="wc_discount_adoption",
                )
                / 100
            )
            current_discount_days = st.number_input(
                "Current Days — Customers Taking Discount",
                min_value=1,
                max_value=365,
                value=int(current_ar_days),
                key="wc_discount_current_days",
            )

        with col_b:
            new_payment_days = st.number_input(
                "Target Payment Days After Discount",
                min_value=1,
                max_value=365,
                value=10,
                step=1,
                key="wc_discount_new_days",
            )
            cogs_value = st.number_input(
                "COGS (€)",
                min_value=0.0,
                value=float(cogs_default),
                step=1000.0,
                key="wc_discount_cogs",
            )
            wacc_value = (
                st.number_input(
                    "WACC (%)",
                    min_value=0.0,
                    max_value=100.0,
                    value=15.0,
                    step=0.1,
                    key="wc_discount_wacc",
                )
                / 100
            )
            supplier_days = st.number_input(
                "Supplier Days",
                min_value=1,
                max_value=365,
                value=int(current_ap_days),
                key="wc_discount_supplier_days",
            )
            non_discount_days = st.number_input(
                "Collection Days — Customers Not Taking Discount",
                min_value=1,
                max_value=365,
                value=int(current_ar_days * 1.5),
                key="wc_discount_non_discount_days",
            )

        if st.button("Analyze Early Payment Discount", key="wc_analyze_discount", use_container_width=True):
            result = calculate_discount_npv(
                current_sales,
                extra_sales,
                discount_trial,
                adoption,
                current_discount_days,
                non_discount_days,
                new_payment_days,
                cogs_value,
                wacc_value,
                supplier_days,
            )

            if result is None:
                st.error("Calculation error. Please check your inputs.")
            else:
                st.session_state["wc_discount_result"] = result

        result = st.session_state.get("wc_discount_result")

        if result is not None:
            st.divider()
            st.subheader("🏁 Discount Policy Result")

            c1, c2, c3 = st.columns(3)
            c1.metric(
                "Decision NPV",
                f"€ {result['npv']:,.0f}",
                delta="Creates Value" if result["npv"] > 0 else "Destroys Value",
            )
            c2.metric("New Weighted AR Days", f"{result['new_avg_collection_period']:.1f}")
            c3.metric("Cash Released", f"€ {result['free_capital']:,.0f}")

            st.info(
                f"""
                Current weighted collection period: **{result['avg_current_collection_days']:.1f} days**  
                New weighted collection period: **{result['new_avg_collection_period']:.1f} days**
                """
            )

            if st.button("Use This Discount Policy", key="wc_use_discount_policy", use_container_width=True):
                effective_ar_days = float(result["new_avg_collection_period"])
                decision = DecisionFactory.ar_days_change(
                    decision_id=f"wc_discount_ar_{uuid4().hex[:8]}",
                    target_ar_days=effective_ar_days,
                )
                set_wc_candidate(
                    decision=decision,
                    candidate_key=WC_AR_CANDIDATE,
                    metadata={
                        "source": "tool",
                        "method": "Early Payment Discount",
                        "ar_days": effective_ar_days,
                        "npv": result["npv"],
                        "cash_released": result["free_capital"],
                        "discount": discount_trial * 100,
                        "adoption": adoption * 100,
                    },
                )
                st.success("Early Payment Discount set as active AR candidate.")
                st.rerun()

    # INVENTORY
    with tab2:
        st.subheader("Inventory Policy")
        st.caption("Only one Inventory candidate can exist.")

        inventory_target = st.number_input(
            "Target Inventory Days",
            min_value=0.0,
            value=current_inventory_days,
            step=1.0,
            key="wc_inventory_target",
        )

        if st.button("Use Inventory Policy", key="wc_use_inventory", use_container_width=True):
            decision = DecisionFactory.inventory_days_change(
                decision_id=f"wc_inventory_{uuid4().hex[:8]}",
                target_inventory_days=inventory_target,
            )
            set_wc_candidate(
                decision=decision,
                candidate_key=WC_INVENTORY_CANDIDATE,
                metadata={
                    "source": "manual",
                    "method": "Manual Inventory Policy",
                    "inventory_days": float(inventory_target),
                },
            )
            st.success("Inventory policy set as active Inventory candidate.")
            st.rerun()

    # PAYABLES
    with tab3:
        st.subheader("Accounts Payable Policy")
        st.caption(
            "Evaluate whether paying suppliers early for a discount "
            "creates more value than preserving supplier credit."
        )

        # 1. CURRENT POLICY
        st.markdown("### Current Supplier Payment Policy")
        col1, col2, col3 = st.columns(3)
        col1.metric(
            "Current AP Days",
            f"{current_ap_days:.1f}",
        )

        # 2. SUPPLIER CREDIT INPUTS
        st.markdown("### Supplier Credit Decision")

        with st.expander("💡 What does this tool evaluate?", expanded=False):
            st.markdown(
                """
                The business question is:

                **"Does paying suppliers early to obtain a discount create
                more economic value than keeping the supplier's interest-free credit?"**

                The analysis compares:

                **Early Payment Discount Benefit**

                versus

                **Economic Value of Supplier Credit Given Up**
                """
            )

        col_a, col_b = st.columns(2)

        with col_a:
            supplier_credit_days = st.number_input(
                "Supplier Credit Period (Days)",
                min_value=1,
                max_value=365,
                value=int(current_ap_days),
                step=1,
                key="wc_supplier_credit_days",
            )

            discount_pct = st.number_input(
                "Early Payment Discount (%)",
                min_value=0.0,
                max_value=100.0,
                value=2.0,
                step=0.1,
                key="wc_supplier_discount_pct",
            )

            cash_prc_pct = st.slider(
                "% of Purchases Eligible for Discount",
                min_value=0,
                max_value=100,
                value=50,
                step=5,
                key="wc_supplier_discount_eligibility",
            )

        with col_b:
            try:
                variable_cost = float(baseline_state.unit_economics.variable_cost)
            except AttributeError:
                variable_cost = float(getattr(baseline_state, "variable_cost", 100.0))

            try:
                volume = float(baseline_state.volume)
            except AttributeError:
                volume = 12000.0

            supplier_spend_default = variable_cost * volume

            current_supplier_spend = st.number_input(
                "Annual Supplier Spend (€)",
                min_value=0.0,
                value=float(supplier_spend_default),
                step=1000.0,
                key="wc_supplier_spend",
            )

            interest_rate_pct = st.number_input(
                "Cost of Cash (%)",
                min_value=0.0,
                max_value=100.0,
                value=15.0,
                step=0.1,
                key="wc_supplier_interest_rate",
            )

        # 3. EARLY PAYMENT TERMS
        early_payment_days = st.number_input(
            "Early Payment Days",
            min_value=0,
            max_value=int(supplier_credit_days),
            value=min(10, int(supplier_credit_days)),
            step=1,
            key="wc_supplier_early_payment_days",
        )

        # 4. ECONOMIC CALCULATION
        discount = discount_pct / 100.0
        cash_prc = cash_prc_pct / 100.0
        interest_rate_on_debt = interest_rate_pct / 100.0

        unit_price = float(getattr(baseline_state, "price", 150.0))
        total_unit_cost = variable_cost

        (
            discount_gain,
            credit_cost,
            net_gain,
        ) = calculate_supplier_credit_gain(
            supplier_credit_days=float(supplier_credit_days),
            discount=discount,
            cash_prc=cash_prc,
            current_sales=float(current_supplier_spend),
            unit_price=unit_price,
            total_unit_cost=total_unit_cost,
            interest_rate_on_debt=interest_rate_on_debt,
        )

        # 5. EFFECTIVE AP DAYS
        effective_ap_days = (
            cash_prc * float(early_payment_days)
            + (1.0 - cash_prc) * float(supplier_credit_days)
        )

        # 6. RESULTS
        st.divider()
        st.subheader("🏁 Supplier Credit Result")

        c1, c2, c3 = st.columns(3)

        c1.metric(
            "Discount Benefit",
            f"€ {discount_gain:,.0f}",
        )

        c2.metric(
            "Cost of Using Cash Early",
            f"-€ {credit_cost:,.0f}",
        )

        c3.metric(
            "Net Economic Benefit",
            f"€ {net_gain:,.0f}",
            delta=(
                "Creates Value"
                if net_gain >= 0
                else "Destroys Value"
            ),
            delta_color="normal" if net_gain >= 0 else "inverse",
        )

        st.info(
            f"""
            **Current AP Days:** {current_ap_days:.1f} days

            **Supplier Credit Period:** {supplier_credit_days} days

            **Early Payment:** {early_payment_days} days

            **Discount Eligible Purchases:** {cash_prc_pct:.0f}%

            **Effective AP Policy:** {effective_ap_days:.1f} days
            """
        )

        # 7. STRATEGIC ASSESSMENT
        if net_gain > 0:
            st.success(
                f"""
                ### Early Payment Creates Economic Value

                Under the current assumptions, taking the supplier discount
                creates an estimated **net economic benefit of
                €{net_gain:,.0f}**.

                The value of the discount exceeds the estimated economic
                cost of giving up supplier credit.
                """
            )
        else:
            st.warning(
                f"""
                ### Preserving Supplier Credit Creates More Value

                Under the current assumptions, paying suppliers early does
                not compensate for the value of the supplier credit.

                Estimated economic disadvantage:
                **€{abs(net_gain):,.0f}**
                """
            )

        # 8. CREATE AP CANDIDATE
        if net_gain > 0:
            if st.button(
                "Use This Supplier Credit Policy",
                key="wc_use_supplier_discount",
                use_container_width=True,
            ):
                decision = DecisionFactory.ap_days_change(
                    decision_id=f"wc_supplier_discount_{uuid4().hex[:8]}",
                    target_ap_days=effective_ap_days,
                )

                set_wc_candidate(
                    decision=decision,
                    candidate_key=WC_AP_CANDIDATE,
                    metadata={
                        "source": "tool",
                        "method": "Early Payment Discount",
                        "ap_days": effective_ap_days,
                        "supplier_credit_days": supplier_credit_days,
                        "early_payment_days": early_payment_days,
                        "discount": discount_pct,
                        "discount_eligibility": cash_prc_pct,
                        "discount_gain": discount_gain,
                        "credit_cost": credit_cost,
                        "net_gain": net_gain,
                    },
                )

                st.success(
                    "Early Payment Discount set as active Payables candidate."
                )

                st.rerun()

        else:
            st.info(
                "No AP candidate created because preserving supplier "
                "credit currently creates greater economic value."
            )

    # -----------------------------------------------------
    # DISPLAY CANDIDATES & PUSH TO DECISION PLAN
    # -----------------------------------------------------
    st.divider()
    st.subheader("🧩 Working Capital Candidates")

    # AR Candidate
    ar_candidate = st.session_state.get(WC_AR_CANDIDATE)
    if ar_candidate is not None:
        st.markdown("### Receivables Candidate")
        ar_meta = st.session_state.get(WC_AR_META, {})
        method = ar_meta.get("method", ar_candidate.name)
        ar_value = ar_candidate.changes.get("ar_days")

        st.success(f"**{method}**")
        if ar_value is not None:
            st.write(f"Target AR Days → **{float(ar_value):.1f}**")
        if "npv" in ar_meta:
            st.write(f"Decision NPV → **€{ar_meta['npv']:,.0f}**")
        if "cash_released" in ar_meta:
            st.write(f"Cash Released → **€{ar_meta['cash_released']:,.0f}**")

        btn_col1, btn_col2 = st.columns(2)
        if btn_col1.button("➕ Add AR Candidate to Decision Plan", key="wc_add_ar_to_plan", use_container_width=True):
            add_decision_to_plan(ar_candidate)
            st.success("Added AR Decision to Decision Plan!")

        if btn_col2.button("Clear AR Candidate", key="wc_clear_ar_candidate", use_container_width=True):
            clear_wc_candidate(WC_AR_CANDIDATE)
            st.rerun()
    else:
        st.info("No AR candidate selected.")

    # Inventory Candidate
    inventory_candidate = st.session_state.get(WC_INVENTORY_CANDIDATE)
    if inventory_candidate is not None:
        st.markdown("### Inventory Candidate")
        st.success("**Inventory Policy**")
        inv_val = inventory_candidate.changes.get("inventory_days")
        if inv_val is not None:
            st.write(f"Target Inventory Days → **{float(inv_val):.1f}**")

        btn_col1, btn_col2 = st.columns(2)
        if btn_col1.button("➕ Add Inventory Candidate to Decision Plan", key="wc_add_inv_to_plan", use_container_width=True):
            add_decision_to_plan(inventory_candidate)
            st.success("Added Inventory Decision to Decision Plan!")

        if btn_col2.button("Clear Inventory Candidate", key="wc_clear_inventory_candidate", use_container_width=True):
            clear_wc_candidate(WC_INVENTORY_CANDIDATE)
            st.rerun()
    else:
        st.info("No Inventory candidate selected.")

    # AP Candidate
    ap_candidate = st.session_state.get(WC_AP_CANDIDATE)
    if ap_candidate is not None:
        st.markdown("### Payables Candidate")
        st.success("**Supplier Payment Policy**")
        ap_val = ap_candidate.changes.get("ap_days")
        if ap_val is not None:
            st.write(f"Target AP Days → **{float(ap_val):.1f}**")

        btn_col1, btn_col2 = st.columns(2)
        if btn_col1.button("➕ Add Payables Candidate to Decision Plan", key="wc_add_ap_to_plan", use_container_width=True):
            add_decision_to_plan(ap_candidate)
            st.success("Added Payables Decision to Decision Plan!")

        if btn_col2.button("Clear Payables Candidate", key="wc_clear_ap_candidate", use_container_width=True):
            clear_wc_candidate(WC_AP_CANDIDATE)
            st.rerun()
    else:
        st.info("No Payables candidate selected.")

    # LOGIC
    st.divider()
    st.subheader("Working Capital Core Logic")
    st.info(
        """
        **AR Days ↓** → Receivables ↓ → Cash Released ↑  
        **Inventory Days ↓** → Inventory Investment ↓ → Cash Released ↑  
        **AP Days ↑** → Supplier Financing ↑ → Cash Preserved ↑
        """
    )
