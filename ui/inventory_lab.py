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
            int(round(curren
