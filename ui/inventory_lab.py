from uuid import uuid4

import streamlit as st

from core.decision import DecisionFactory
from core.decision_plan import DecisionPlan


# =========================================================
# INVENTORY CANDIDATE
# =========================================================

WC_INV_CANDIDATE = "wc_inv_candidate"
WC_INV_META = "wc_inv_candidate_meta"


# =========================================================
# CALCULATIONS
# =========================================================

def calculate_inventory_impact(
    current_inventory_days: float,
    target_inventory_days: float,
    annual_cogs: float,
):
    """
    Calculate the working-capital impact of changing
    the inventory holding period.

    Inventory is expressed as days of annual COGS.
    """

    current_inventory_value = (
        current_inventory_days / 365.0
    ) * annual_cogs

    target_inventory_value = (
        target_inventory_days / 365.0
    ) * annual_cogs

    cash_released = (
        current_inventory_value
        - target_inventory_value
    )

    inventory_turnover = (
        365.0 / target_inventory_days
        if target_inventory_days > 0
        else 0.0
    )

    return (
        current_inventory_value,
        target_inventory_value,
        cash_released,
        inventory_turnover,
    )


# =========================================================
# SESSION STATE
# =========================================================

def set_inventory_candidate(decision, metadata=None):
    st.session_state[WC_INV_CANDIDATE] = decision

    if metadata is not None:
        st.session_state[WC_INV_META] = metadata


def clear_inventory_candidate():
    st.session_state.pop(WC_INV_CANDIDATE, None)
    st.session_state.pop(WC_INV_META, None)


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
# BASELINE HELPERS
# =========================================================

def _get_volume(baseline_state):
    try:
        return float(baseline_state.drivers.volume)
    except AttributeError:
        pass

    try:
        return float(baseline_state.volume)
    except AttributeError:
        pass

    return 12000.0


def _get_variable_cost(baseline_state):
    try:
        return float(
            baseline_state.drivers.variable_cost_per_unit
        )
    except AttributeError:
        pass

    try:
        return float(
            baseline_state.unit_economics.variable_cost
        )
    except AttributeError:
        pass

    try:
        return float(baseline_state.variable_cost)
    except AttributeError:
        pass

    return 100.0


# =========================================================
# INVENTORY LAB
# =========================================================

def show_inventory_lab(baseline_state):

    st.title("📦 Inventory Lab")

    st.markdown(
        """
        Evaluate the size of the inventory the business wants
        to carry and its working-capital impact.

        This is a **policy-level decision**, not an inventory
        management system. The objective is to estimate the
        financial effect of changing the overall inventory level.
        """
    )

    wc = baseline_state.working_capital

    current_inventory_days = float(
        wc.inventory_days
    )

    volume = _get_volume(baseline_state)
    variable_cost = _get_variable_cost(baseline_state)

    annual_cogs = volume * variable_cost

    # =====================================================
    # CURRENT STATE
    # =====================================================

    st.subheader("Current Inventory Position")

    (
        current_inventory_value,
        _,
        _,
        current_turnover,
    ) = calculate_inventory_impact(
        current_inventory_days=current_inventory_days,
        target_inventory_days=current_inventory_days,
        annual_cogs=annual_cogs,
    )

    col1, col2, col3 = st.columns(3)

    col1.metric(
        "Current Inventory Days",
        f"{current_inventory_days:.1f}",
    )

    col2.metric(
        "Current Inventory Value",
        f"€ {current_inventory_value:,.0f}",
    )

    col3.metric(
        "Current Inventory Turnover",
        f"{current_turnover:.1f}x",
    )

    st.caption(
        f"Annual COGS: € {annual_cogs:,.0f}"
    )

    st.divider()

    # =====================================================
    # TARGET POLICY
    # =====================================================

    st.subheader("🎯 Target Inventory Policy")

    st.caption(
        "Choose approximately how many days of inventory "
        "the business wants to carry."
    )

    target_inventory_days = st.slider(
        "Target Inventory Holding Time (Days)",
        min_value=1,
        max_value=365,
        value=max(
            1,
            int(round(current_inventory_days)),
        ),
        step=1,
        key="inventory_target_days",
    )

    (
        current_inventory_value,
        target_inventory_value,
        cash_released,
        inventory_turnover,
    ) = calculate_inventory_impact(
        current_inventory_days=current_inventory_days,
        target_inventory_days=float(
            target_inventory_days
        ),
        annual_cogs=annual_cogs,
    )

    # =====================================================
    # RESULT
    # =====================================================

    st.divider()

    st.subheader("🏁 Working Capital Impact")

    c1, c2, c3, c4 = st.columns(4)

    c1.metric(
        "Current Inventory",
        f"€ {current_inventory_value:,.0f}",
    )

    c2.metric(
        "Target Inventory",
        f"€ {target_inventory_value:,.0f}",
    )

    c3.metric(
        "Inventory Turnover",
        f"{inventory_turnover:.1f}x",
    )

    c4.metric(
        "Cash Impact",
        f"€ {abs(cash_released):,.0f}",
        delta=(
            "Released"
            if cash_released >= 0
            else "Additional cash required"
        ),
        delta_color=(
            "normal"
            if cash_released >= 0
            else "inverse"
        ),
    )

    # =====================================================
    # INTERPRETATION
    # =====================================================

    if cash_released > 0:

        st.success(
            f"""
            Reducing inventory from
            **{current_inventory_days:.1f} days**
            to **{target_inventory_days:.1f} days**
            would release approximately
            **€{cash_released:,.0f}**
            of working capital.
            """
        )

    elif cash_released < 0:

        st.warning(
            f"""
            Increasing inventory from
            **{current_inventory_days:.1f} days**
            to **{target_inventory_days:.1f} days**
            would require approximately
            **€{abs(cash_released):,.0f}**
            of additional working capital.
            """
        )

    else:

        st.info(
            "The target inventory level matches "
            "the current baseline."
        )

    st.divider()

    # =====================================================
    # DECISION
    # =====================================================

    if st.button(
        "Use This Inventory Policy",
        key="inventory_create_candidate",
        use_container_width=True,
    ):

        try:

            decision = DecisionFactory.inventory_days_change(
                decision_id=f"inventory_{uuid4().hex[:8]}",
                target_inventory_days=float(
                    target_inventory_days
                ),
            )

        except TypeError:

            decision = DecisionFactory.inventory_days_change(
                f"inventory_{uuid4().hex[:8]}",
                float(target_inventory_days),
            )

        set_inventory_candidate(
            decision=decision,
            metadata={
                "source": "inventory_lab",
                "method": "Inventory Holding Policy",
                "inventory_days": float(
                    target_inventory_days
                ),
                "baseline_inventory_days": (
                    current_inventory_days
                ),
                "current_inventory_value": (
                    current_inventory_value
                ),
                "target_inventory_value": (
                    target_inventory_value
                ),
                "cash_released": cash_released,
                "inventory_turnover": (
                    inventory_turnover
                ),
            },
        )

        st.success(
            "Inventory policy is ready as an Inventory candidate."
        )

        st.rerun()

    # =====================================================
    # ACTIVE CANDIDATE
    # =====================================================

    st.divider()

    st.subheader("🧩 Active Inventory Decision Candidate")

    inv_candidate = st.session_state.get(
        WC_INV_CANDIDATE
    )

    if inv_candidate is not None:

        inv_meta = st.session_state.get(
            WC_INV_META,
            {},
        )

        raw_inv_val = 0.0

        if (
            hasattr(inv_candidate, "changes")
            and isinstance(
                inv_candidate.changes,
                dict,
            )
        ):

            raw_inv_val = inv_candidate.changes.get(
                "inventory_days",
                inv_candidate.changes.get(
                    "target_inventory_days",
                    0,
                ),
            )

        try:
            inv_val = float(raw_inv_val)
        except (TypeError, ValueError):
            inv_val = 0.0

        st.success(
            f"**Selected Policy Target:** "
            f"{inv_val:.1f} Inventory Days"
        )

        if "cash_released" in inv_meta:

            cash_impact = float(
                inv_meta["cash_released"]
            )

            if cash_impact >= 0:

                st.write(
                    "Projected Working Capital Released: "
                    f"**€{cash_impact:,.0f}**"
                )

            else:

                st.write(
                    "Additional Working Capital Required: "
                    f"**€{abs(cash_impact):,.0f}**"
                )

        btn_col1, btn_col2 = st.columns(2)

        if btn_col1.button(
            "➕ Add Inventory Decision",
            key="inv_add_decision",
            use_container_width=True,
        ):

            current_plan = _get_current_plan()

            updated_plan = current_plan.add(
                inv_candidate
            )

            st.session_state.decision_plan = (
                updated_plan
            )

            st.success(
                f"Inventory Decision added: "
                f"{inv_candidate.name}"
            )

            clear_inventory_candidate()

            st.rerun()

        if btn_col2.button(
            "Clear Candidate",
            key="inv_clear_candidate",
            use_container_width=True,
        ):

            clear_inventory_candidate()

            st.rerun()

    else:

        st.info(
            "No active Inventory decision candidate selected."
        )
