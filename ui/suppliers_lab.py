from decimal import Decimal, getcontext
from uuid import uuid4

import streamlit as st
from core.decision import DecisionFactory

# ==========================================
# CANDIDATE KEYS (SUPPLIERS / AP SPECIFIC)
# ==========================================
WC_AP_CANDIDATE = "wc_ap_candidate"
WC_AP_META = "wc_ap_candidate_meta"


# ==========================================
# PURE CALCULATION ENGINE
# ==========================================
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
        discount_gain, credit_benefit_lost, net_gain
    """
    if unit_price <= 0:
        average_cost_ratio = 0.0
    else:
        average_cost_ratio = total_unit_cost / unit_price

    # 1. Economic benefit from early-payment discount
    discount_gain = current_sales * discount * cash_prc

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


# ==========================================
# CANDIDATE MANAGEMENT HELPERS
# ==========================================
def set_ap_candidate(decision, metadata=None):
    st.session_state[WC_AP_CANDIDATE] = decision
    if metadata is not None:
        st.session_state[WC_AP_META] = metadata


def clear_ap_candidate():
    st.session_state.pop(WC_AP_CANDIDATE, None)
    st.session_state.pop(WC_AP_META, None)


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


# ==========================================
# MAIN RENDER FUNCTION
# ==========================================
def render_suppliers_lab(baseline_state):
    st.title("🚚 Suppliers & Payables Lab")

    st.markdown(
        """
        Evaluate Accounts Payable (AP) policies and supplier credit terms against the baseline.
        
        This Lab generates **Supplier Decisions** without mutating `CompanyState` directly. 
        Decisions are passed to the **Decision Plan** for execution engine evaluation.
        """
    )

    # BASELINE METRICS EXTRACTION
    wc = baseline_state.working_capital
    current_ap_days = float(wc.ap_days)

    st.subheader("Current Supplier Credit State")
    col1, col2, col3 = st.columns(3)
    col1.metric("Current AP Days", f"{current_ap_days:.1f}")
    col2.metric("Working Capital Mode", "Baseline Locked")
    col3.metric("Pending AP Candidate", "Yes" if WC_AP_CANDIDATE in st.session_state else "None")

    st.divider()

    # SECTION 1: SUPPLIER CREDIT ANALYSIS TOOL
    st.markdown("### 💳 Early Payment Discount Analysis")
    st.caption(
        "Evaluate whether paying suppliers early to claim a discount "
        "creates more value than keeping interest-free credit."
    )

    with st.expander("💡 Strategic Framework", expanded=False):
        st.markdown(
            """
            **The core trade-off:**
            
            * **Discount Benefit:** Financial saving realized by paying suppliers earlier than standard terms.
            * **Value of Supplier Credit Given Up:** Opportunity cost of losing the interest-free cash financing buffer.
            
            If **Discount Benefit > Value of Supplier Credit Given Up**, taking the discount increases overall profitability.
            """
        )

    col_a, col_b = st.columns(2)

    with col_a:
        supplier_credit_days = st.number_input(
            "Supplier Credit Period (Days)",
            min_value=1,
            max_value=365,
            value=max(1, int(current_ap_days)),
            step=1,
            key="supp_credit_days",
        )

        discount_pct = st.number_input(
            "Early Payment Discount (%)",
            min_value=0.0,
            max_value=100.0,
            value=2.0,
            step=0.1,
            key="supp_discount_pct",
        )

        cash_prc_pct = st.slider(
            "% of Purchases Eligible for Discount",
            min_value=0,
            max_value=100,
            value=50,
            step=5,
            key="supp_discount_eligibility",
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
            key="supp_spend",
        )

        interest_rate_pct = st.number_input(
            "Cost of Cash / WACC (%)",
            min_value=0.0,
            max_value=100.0,
            value=15.0,
            step=0.1,
            key="supp_interest_rate",
        )

    early_payment_days = st.number_input(
        "Target Early Payment Days",
        min_value=0,
        max_value=int(supplier_credit_days),
        value=min(10, int(supplier_credit_days)),
        step=1,
        key="supp_early_payment_days",
    )

    # EXECUTE CALCULATIONS
    discount = discount_pct / 100.0
    cash_prc = cash_prc_pct / 100.0
    interest_rate_on_debt = interest_rate_pct / 100.0

    unit_price = float(getattr(baseline_state, "price", 150.0))
    total_unit_cost = variable_cost

    discount_gain, credit_cost, net_gain = calculate_supplier_credit_gain(
        supplier_credit_days=float(supplier_credit_days),
        discount=discount,
        cash_prc=cash_prc,
        current_sales=float(current_supplier_spend),
        unit_price=unit_price,
        total_unit_cost=total_unit_cost,
        interest_rate_on_debt=interest_rate_on_debt,
    )

    effective_ap_days = (
        cash_prc * float(early_payment_days)
        + (1.0 - cash_prc) * float(supplier_credit_days)
    )

    # RESULTS DISPLAY
    st.divider()
    st.subheader("🏁 Trade-off Evaluation")

    c1, c2, c3 = st.columns(3)
    c1.metric("Discount Benefit", f"€ {discount_gain:,.0f}")
    c2.metric("Value of Supplier Credit Given Up", f"-€ {credit_cost:,.0f}")
    c3.metric(
        "Net Economic Benefit",
        f"€ {net_gain:,.0f}",
        delta="Creates Value" if net_gain >= 0 else "Destroys Value",
        delta_color="normal" if net_gain >= 0 else "inverse",
    )

    st.info(
        f"""
        **Baseline AP Days:** {current_ap_days:.1f} days | 
        **Effective Policy Target AP Days:** {effective_ap_days:.1f} days
        """
    )

    if net_gain > 0:
        st.success(
            f"Taking the discount produces a **net gain of €{net_gain:,.0f}**. "
            "It is economically advantageous to adopt this policy."
        )
        
        if st.button(
            "Use This Supplier Payment Policy",
            key="supp_create_candidate",
            use_container_width=True,
        ):
            decision = DecisionFactory.ap_days_change(
                decision_id=f"supplier_ap_{uuid4().hex[:8]}",
                target_ap_days=effective_ap_days,
            )

            set_ap_candidate(
                decision=decision,
                metadata={
                    "source": "suppliers_lab",
                    "method": "Early Payment Discount Analysis",
                    "ap_days": effective_ap_days,
                    "net_gain": net_gain,
                },
            )

            st.success(
                "Supplier payment policy is ready as an AP candidate."
            )
            st.rerun()
    else:
        st.info(
            "No AP decision recommended. "
            "Keeping supplier credit creates more economic value under these assumptions."
        )

    # SECTION 2: CANDIDATE INSPECTION & DISPATCH
    st.divider()
    st.subheader("🧩 Active Payables Decision Candidate")

    ap_candidate = st.session_state.get(WC_AP_CANDIDATE)
    if ap_candidate is not None:
        ap_meta = st.session_state.get(WC_AP_META, {})
        ap_val = ap_candidate.changes.get("ap_days")

        st.success(f"**Selected Policy Target:** {ap_val:.1f} AP Days")
        if "net_gain" in ap_meta:
            st.write(f"Projected Net Value Created: **€{ap_meta['net_gain']:,.0f}**")

        btn_col1, btn_col2 = st.columns(2)
        if btn_col1.button("➕ Push Candidate to Decision Plan", key="supp_push_to_plan", use_container_width=True):
            add_decision_to_plan(ap_candidate)
            st.success("AP Decision added to Decision Plan!")

        if btn_col2.button("Clear Candidate", key="supp_clear_candidate", use_container_width=True):
            clear_ap_candidate()
            st.rerun()
    else:
        st.info("No active Payables decision candidate selected.")
