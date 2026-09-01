from uuid import uuid4

import plotly.graph_objects as go
import streamlit as st

from core.decision import DecisionFactory


# ==========================================
# CANDIDATE KEYS (INVENTORY SPECIFIC)
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
    fixed_assets: float,
    depreciation: float,
):
    """
    Pure calculation for inventory policy changes.
    
    Returns:
        current_inv_val, target_inv_val, cash_released, inv_turnover, capital_drag
    """
    current_inv_val = (current_inventory_days / 365.0) * annual_cogs
    target_inv_val = (target_inventory_days / 365.0) * annual_cogs
    cash_released = current_inv_val - target_inv_val
    inv_turnover = (365.0 / target_inventory_days) if target_inventory_days > 0 else 0.0

    asset_utilization_ratio = (target_inv_val / fixed_assets) if fixed_assets > 0 else 0.0
    capital_drag = asset_utilization_ratio * depreciation

    return (
        current_inv_val,
        target_inv_val,
        cash_released,
        inv_turnover,
        capital_drag,
    )


# ==========================================
# CANDIDATE MANAGEMENT HELPERS
# ==========================================
def set_inventory_candidate(decision, metadata=None):
    st.session_state[WC_INV_CANDIDATE] = decision
    if metadata is not None:
        st.session_state[WC_INV_META] = metadata


def clear_inventory_candidate():
    st.session_state.pop(WC_INV_CANDIDATE, None)
    st.session_state.pop(WC_INV_META, None)


def add_decision_to_collection(decision):
    """
    Add a Decision to the central Decision Manager collection.

    Decision Manager reads st.session_state.decisions
    and is responsible for building the DecisionPlan.
    """

    if not hasattr(decision, "id"):
        st.error("Invalid Decision object.")
        return False

    if not isinstance(
        st.session_state.get("decisions"),
        list,
    ):
        st.session_state.decisions = []

    existing_ids = {
        getattr(d, "id", None)
        for d in st.session_state.decisions
    }

    if decision.id not in existing_ids:
        st.session_state.decisions.append(
            decision
        )

    return True


# ==========================================
# BASELINE HELPERS
# ==========================================
def _get_volume(baseline_state):
    try:
        return float(baseline_state.volume)
    except AttributeError:
        return 12000.0


def _get_variable_cost(baseline_state):
    try:
        return float(baseline_state.unit_economics.variable_cost)
    except AttributeError:
        return float(getattr(baseline_state, "variable_cost", 100.0))


def _get_fixed_assets(baseline_state):
    try:
        return float(baseline_state.fixed_assets)
    except AttributeError:
        return float(getattr(baseline_state, "fixed_assets", 800000.0))


def _get_depreciation(baseline_state):
    try:
        return float(baseline_state.depreciation)
    except AttributeError:
        return float(getattr(baseline_state, "depreciation", 50000.0))


# ==========================================
# MAIN RENDER FUNCTION
# ==========================================
def show_inventory_lab(baseline_state):
    st.title("📦 Inventory Lab")

    st.markdown(
        """
        Evaluate Inventory holding policies and working capital optimization against the baseline.
        
        This Lab generates **Inventory Decisions** without mutating `CompanyState` directly. 
        Decisions are passed to the **Decision Plan** for execution engine evaluation.
        """
    )

    # BASELINE METRICS EXTRACTION
    wc = baseline_state.working_capital
    current_inventory_days = float(wc.inventory_days)

    volume = _get_volume(baseline_state)
    variable_cost = _get_variable_cost(baseline_state)
    fixed_assets = _get_fixed_assets(baseline_state)
    depreciation = _get_depreciation(baseline_state)

    annual_cogs = volume * variable_cost

    st.subheader("Current Inventory Holding State")
    col1, col2, col3 = st.columns(3)
    col1.metric("Current Inventory Days", f"{current_inventory_days:.1f}")
    col2.metric("Working Capital Mode", "Baseline Locked")
    col3.metric("Pending Inventory Candidate", "Yes" if WC_INV_CANDIDATE in st.session_state else "None")

    st.divider()

    # SECTION 1: INVENTORY POLICY ANALYSIS TOOL
    st.markdown("### 📊 Target Inventory Policy Analysis")
    st.caption("Decide how many days of inventory the business should hold.")

    target_inventory_days = st.slider(
        "Target Inventory Holding Time (Days)",
        min_value=1,
        max_value=365,
        value=max(1, int(round(current_inventory_days))),
        step=1,
        key="inventory_target_days",
    )

    # EXECUTE CALCULATIONS
    (
        current_inv_val,
        target_inv_val,
        cash_released,
        inv_turnover,
        capital_drag,
    ) = calculate_inventory_impact(
        current_inventory_days=current_inventory_days,
        target_inventory_days=float(target_inventory_days),
        annual_cogs=annual_cogs,
        fixed_assets=fixed_assets,
        depreciation=depreciation,
    )

    # RESULTS DISPLAY
    st.divider()
    st.subheader("🏁 Trade-off Evaluation")

    c1, c2, c3 = st.columns(3)
    c1.metric("Target Inventory Value", f"€ {target_inv_val:,.0f}")
    c2.metric(
        "Cash Released",
        f"€ {cash_released:,.0f}",
        delta=f"€ {cash_released:,.0f}" if cash_released != 0 else None,
    )
    c3.metric("Inventory Turnover", f"{inv_turnover:.1f}x")

    if cash_released > 0:
        st.success(
            f"💰 Reducing inventory from **{current_inventory_days:.1f} days** "
            f"to **{target_inventory_days} days** releases approximately **€{cash_released:,.0f}** of cash."
        )
    elif cash_released < 0:
        st.warning(
            f"⚠️ Increasing inventory from **{current_inventory_days:.1f} days** "
            f"to **{target_inventory_days} days** requires approximately **€{abs(cash_released):,.0f}** of extra cash."
        )
    else:
        st.info("The target inventory policy matches the current baseline.")

    # CAPITAL ALLOCATION CHART
    st.divider()
    st.subheader("📈 Capital Allocation & Drag")

    col_a, col_b = st.columns(2)
    with col_a:
        asset_utilization = (target_inv_val / fixed_assets) if fixed_assets > 0 else 0.0
        st.progress(min(max(asset_utilization, 0.0), 1.0))
        st.caption(
            f"Approximately **{asset_utilization:.1%}** of fixed-asset capital "
            "is tied up in inventory."
        )

    with col_b:
        st.metric(
            "Estimated Annual Capital Drag",
            f"€ {capital_drag:,.0f}",
            help="Illustrative estimate based on inventory value relative to fixed assets and depreciation.",
        )

    productive_capital = max(0.0, fixed_assets - target_inv_val)
    fig = go.Figure(
        data=[
            go.Pie(
                labels=["Productive Capital", "Inventory Cash"],
                values=[productive_capital, target_inv_val],
                hole=0.55,
            )
        ]
    )
    fig.update_layout(title="Capital Allocation", height=320, margin=dict(l=20, r=20, t=40, b=20))
    st.plotly_chart(fig, use_container_width=True)

    if st.button(
        "Use This Inventory Holding Policy",
        key="inventory_create_candidate",
        use_container_width=True,
    ):
        try:
            decision = DecisionFactory.inventory_days_change(
                decision_id=f"inventory_{uuid4().hex[:8]}",
                target_inventory_days=float(target_inventory_days),
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
                "inventory_days": float(target_inventory_days),
                "baseline_inventory_days": current_inventory_days,
                "inventory_value": target_inv_val,
                "cash_released": cash_released,
                "inventory_turnover": inv_turnover,
            },
        )

        st.success("Inventory policy is ready as an Inventory candidate.")
        st.rerun()

    # SECTION 2: CANDIDATE INSPECTION & DISPATCH
    st.divider()
    st.subheader("🧩 Active Inventory Decision Candidate")

    inv_candidate = st.session_state.get(WC_INV_CANDIDATE)
    if inv_candidate is not None:
        inv_meta = st.session_state.get(WC_INV_META, {})

        # Safe extraction of Inventory Value from changes dictionary
        raw_inv_val = 0.0
        if hasattr(inv_candidate, "changes") and isinstance(inv_candidate.changes, dict):
            raw_inv_val = inv_candidate.changes.get(
                "inventory_days", inv_candidate.changes.get("target_inventory_days", 0)
            )
        inv_val = float(raw_inv_val) if raw_inv_val is not None else 0.0

        st.success(f"**Selected Policy Target:** {inv_val:.1f} Inventory Days")
        if "cash_released" in inv_meta:
            st.write(f"Projected Cash Impact: **€{float(inv_meta['cash_released']):,.0f}**")

        btn_col1, btn_col2 = st.columns(2)
        if btn_col1.button(
            "➕ Add Inventory Decision",
            key="inv_add_decision",
            use_container_width=True,
        ):
            success = add_decision_to_collection(
                inv_candidate
            )

            if success:
                st.success(
                    f"Inventory Decision added: "
                    f"{inv_candidate.name}"
                )
                clear_inventory_candidate()
                st.rerun()
            else:
                st.error(
                    "Failed to add Inventory Decision."
                )

        if btn_col2.button("Clear Candidate", key="inv_clear_candidate", use_container_width=True):
            clear_inventory_candidate()
            st.rerun()
    else:
        st.info("No active Inventory decision candidate selected.")
