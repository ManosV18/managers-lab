from uuid import uuid4

import plotly.graph_objects as go
import streamlit as st

from core.decision import DecisionFactory
from core.decision_plan import DecisionPlan


# ==========================================
# CANDIDATE KEYS
# ==========================================
WC_INV_CANDIDATE = "wc_inv_candidate"
WC_INV_META = "wc_inv_candidate_meta"


# ==========================================
# PURE CALCULATION ENGINE
# ==========================================
def calculate_inventory_impact(
    current_inventory_days: float,
    target_inventory_days: float,
    annual_cogs: float,
):
    """
    Calculate the economic impact of changing the inventory policy.

    Returns:
        current_inv_val
        target_inv_val
        cash_released
        inventory_turnover
    """

    current_inv_val = (
        current_inventory_days / 365.0
    ) * annual_cogs

    target_inv_val = (
        target_inventory_days / 365.0
    ) * annual_cogs

    cash_released = current_inv_val - target_inv_val

    inventory_turnover = (
        365.0 / target_inventory_days
        if target_inventory_days > 0
        else 0.0
    )

    return (
        current_inv_val,
        target_inv_val,
        cash_released,
        inventory_turnover,
    )


# ==========================================
# CANDIDATE MANAGEMENT
# ==========================================
def set_inventory_candidate(decision, metadata=None):
    st.session_state[WC_INV_CANDIDATE] = decision

    if metadata is not None:
        st.session_state[WC_INV_META] = metadata


def clear_inventory_candidate():
    st.session_state.pop(WC_INV_CANDIDATE, None)
    st.session_state.pop(WC_INV_META, None)


def _get_current_plan() -> DecisionPlan:
    """
    Return the current Decision Plan.

    If no valid plan exists in session state,
    create the default Current Decision Plan.
    """

    plan = st.session_state.get("decision_plan")

    if isinstance(plan, DecisionPlan):
        return plan

    plan = DecisionPlan.create(
        plan_id="main_plan",
        name="Current Decision Plan",
    )

    st.session_state.decision_plan = plan

    return plan


# ==========================================
# BASELINE HELPERS
# ==========================================
def _get_volume(baseline_state):
    """
    Read annual production/sales volume from the
    canonical CompanyState while retaining compatibility
    with older state shapes.
    """

    try:
        return float(baseline_state.volume)
    except AttributeError:
        pass

    try:
        return float(baseline_state.drivers.volume)
    except AttributeError:
        pass

    return 12000.0


def _get_variable_cost(baseline_state):
    """
    Read variable cost per unit from the canonical
    CompanyState while retaining compatibility with
    older state shapes.
    """

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


# ==========================================
# MAIN INVENTORY LAB
# ==========================================
def show_inventory_lab(baseline_state):

    st.title("📦 Inventory Lab")

    st.markdown(
        """
        Evaluate inventory holding policies and their
        working-capital impact against the locked baseline.

        This Lab creates an **Inventory Decision**.
        It does not change `CompanyState` directly.

        The decision is passed to the **Current Decision Plan**
        and evaluated together with the other business decisions.
        """
    )

    # ==========================================
    # BASELINE DATA
    # ==========================================

    wc = baseline_state.working_capital

    current_inventory_days = float(
        wc.inventory_days
    )

    volume = _get_volume(baseline_state)
    variable_cost = _get_variable_cost(baseline_state)

    annual_cogs = volume * variable_cost

    # ==========================================
    # CURRENT STATE
    # ==========================================

    st.subheader("Current Inventory Holding State")

    col1, col2, col3 = st.columns(3)

    col1.metric(
        "Current Inventory Days",
        f"{current_inventory_days:.1f}",
    )

    col2.metric(
        "Annual COGS",
        f"€ {annual_cogs:,.0f}",
    )

    col3.metric(
        "Pending Inventory Candidate",
        "Yes"
        if WC_INV_CANDIDATE in st.session_state
        else "None",
    )

    st.divider()

    # ==========================================
    # INVENTORY POLICY
    # ==========================================

    st.markdown("### 📊 Target Inventory Policy")

    st.caption(
        "Choose the inventory holding period the business "
        "wants to operate with."
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

    # ==========================================
    # CALCULATE IMPACT
    # ==========================================

    (
        current_inv_val,
        target_inv_val,
        cash_released,
        inventory_turnover,
    ) = calculate_inventory_impact(
        current_inventory_days=current_inventory_days,
        target_inventory_days=float(
            target_inventory_days
        ),
        annual_cogs=annual_cogs,
    )

    # ==========================================
    # ECONOMIC RESULT
    # ==========================================

    st.divider()

    st.subheader("🏁 Working Capital Impact")

    c1, c2, c3 = st.columns(3)

    c1.metric(
        "Current Inventory Value",
        f"€ {current_inv_val:,.0f}",
    )

    c2.metric(
        "Target Inventory Value",
        f"€ {target_inv_val:,.0f}",
    )

    c3.metric(
        "Inventory Turnover",
        f"{inventory_turnover:.1f}x",
    )

    # ==========================================
    # CASH IMPACT MESSAGE
    # ==========================================

    if cash_released > 0:

        st.success(
            f"""
            Reducing inventory from
            **{current_inventory_days:.1f} days**
            to **{target_inventory_days} days**
            releases approximately
            **€{cash_released:,.0f}**
            of working capital.
            """
        )

    elif cash_released < 0:

        st.warning(
            f"""
            Increasing inventory from
            **{current_inventory_days:.1f} days**
            to **{target_inventory_days} days**
            requires approximately
            **€{abs(cash_released):,.0f}**
            of additional working capital.
            """
        )

    else:

        st.info(
            "The target inventory policy matches "
            "the current baseline."
        )

    # ==========================================
    # CAPITAL ALLOCATION
    # ==========================================

    st.divider()

    st.subheader("📈 Inventory Capital")

    col_a, col_b = st.columns(2)

    with col_a:

        st.metric(
            "Cash Released / Required",
            f"€ {cash_released:,.0f}",
            delta=(
                f"€ {cash_released:,.0f}"
                if cash_released != 0
                else None
            ),
        )

    with col_b:

        st.metric(
            "Target Inventory / Annual COGS",
            (
                f"{(target_inv_val / annual_cogs):.1%}"
                if annual_cogs > 0
                else "0.0%"
            ),
        )

    # ==========================================
    # SIMPLE CAPITAL ALLOCATION CHART
    # ==========================================

    productive_base = max(
        0.0,
        annual_cogs - target_inv_val,
    )

    fig = go.Figure(
        data=[
            go.Pie(
                labels=[
                    "Annual COGS not tied in inventory",
                    "Inventory",
                ],
                values=[
                    productive_base,
                    target_inv_val,
                ],
                hole=0.55,
            )
        ]
    )

    fig.update_layout(
        title="Inventory Capital Allocation",
        height=320,
        margin=dict(
            l=20,
            r=20,
            t=40,
            b=20,
        ),
    )

    st.plotly_chart(
        fig,
        use_container_width=True,
    )

    # ==========================================
    # DECISION CREATION
    # ==========================================

    st.divider()

    if st.button(
        "Use This Inventory Holding Policy",
        key="inventory_create_candidate",
        use_container_width=True,
    ):

        try:

            decision = DecisionFactory.inventory_days_change(
                decision_id=(
                    f"inventory_{uuid4().hex[:8]}"
                ),
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
                    current_inv_val
                ),
                "target_inventory_value": (
                    target_inv_val
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

    # ==========================================
    # ACTIVE CANDIDATE
    # ==========================================

    st.divider()

    st.subheader(
        "🧩 Active Inventory Decision Candidate"
    )

    inv_candidate = st.session_state.get(
        WC_INV_CANDIDATE
    )

    if inv_candidate is not None:

        inv_meta = st.session_state.get(
            WC_INV_META,
            {},
        )

        # --------------------------------------
        # SAFE DECISION VALUE EXTRACTION
        # --------------------------------------

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
            inv_val = float(
                raw_inv_val
            )
        except (
            TypeError,
            ValueError,
        ):
            inv_val = 0.0

        # --------------------------------------
        # CANDIDATE DISPLAY
        # --------------------------------------

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

        # --------------------------------------
        # DISPATCH
        # --------------------------------------

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
