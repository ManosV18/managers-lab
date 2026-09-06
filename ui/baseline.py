from datetime import datetime

import streamlit as st

from core.baseline_repository import BaselineRepository
from core.models import (
    CapitalStructure,
    CompanyState,
    OperationalDrivers,
    WorkingCapitalPolicy,
)


# =========================================================
# IMPORT → BASELINE BRIDGE
# =========================================================

def _sync_imported_data_to_baseline():
    """
    Synchronize imported company data into the canonical
    baseline session-state keys used by this UI.
    """

    s = st.session_state

    imported_to_baseline = {
        # -----------------------------------------------------
        # OPERATING DRIVERS
        # -----------------------------------------------------
        "price": "baseline_price",
        "variable_cost": "baseline_variable_cost",
        "volume": "baseline_volume",
        "fixed_cost": "baseline_fixed_opex",
        "fixed_opex": "baseline_fixed_opex",
        "fixed_assets": "baseline_fixed_assets",
        "depreciation": "baseline_depreciation",
        "target_profit_goal": "baseline_target_profit_goal",
        "opening_cash": "baseline_opening_cash",

        # -----------------------------------------------------
        # CAPITAL STRUCTURE
        # -----------------------------------------------------
        "wacc": "baseline_wacc",
        "total_debt": "baseline_total_debt",
        "equity": "baseline_equity",
        "cost_of_debt": "baseline_cost_of_debt",
        "annual_cash_interest_paid": "baseline_annual_cash_interest_paid",
        "annual_interest_only": "baseline_annual_cash_interest_paid",
        "annual_debt_service": "baseline_annual_debt_service",
        "principal_payments": "baseline_principal_payments",
        "tax_rate": "baseline_tax_rate",

        # -----------------------------------------------------
        # WORKING CAPITAL
        # -----------------------------------------------------
        "ar_days": "baseline_ar_days",
        "inv_days": "baseline_inventory_days",
        "inventory_days": "baseline_inventory_days",
        "ap_days": "baseline_ap_days",

        # -----------------------------------------------------
        # REPORTED FINANCIAL RESULTS
        # -----------------------------------------------------
        "profit_before_tax": "baseline_profit_before_tax",
        "ebt": "baseline_profit_before_tax",
        "tax": "baseline_tax",
        "net_profit": "baseline_net_profit",
    }

    for imported_key, baseline_key in imported_to_baseline.items():

        if imported_key not in s:
            continue

        try:
            s[baseline_key] = float(
                s[imported_key]
            )
        except (TypeError, ValueError):
            pass

    # ---------------------------------------------------------
    # IMPORTED LABEL
    # ---------------------------------------------------------

    if s.get("scenario_name"):
        s["baseline_label"] = str(
            s["scenario_name"]
        )


# =========================================================
# HELPER
# =========================================================

def _get_float(key, default):
    """
    Safely retrieve a numeric baseline value.
    """

    try:
        return float(
            st.session_state.get(
                key,
                default,
            )
        )
    except (TypeError, ValueError):
        return float(default)


# =========================================================
# MAIN BASELINE VIEW
# =========================================================

def render_baseline_setup():
    """
    Canonical Baseline Company Snapshot.

    Import Data
        ↓
    Baseline Snapshot
        ↓
    CompanyState
        ↓
    BaselineRepository
    """

    # =========================================================
    # IMPORT → BASELINE
    # =========================================================

    _sync_imported_data_to_baseline()

    s = st.session_state

    # =========================================================
    # INTERNAL BASELINE METADATA
    # =========================================================

    label = str(
        s.get(
            "baseline_label",
            "Baseline Company",
        )
    )

    version = int(
        s.get(
            "baseline_version",
            1,
        )
    )

    # =========================================================
    # PAGE HEADER
    # =========================================================

    st.title("🏢 Baseline Company Snapshot")

    st.caption(
        "Review the current position and confirm the baseline "
        "when ready."
    )

    # =========================================================
    # IMPORT STATUS
    # =========================================================

    if s.get("import_source"):

        st.success(
            f"📥 Imported data loaded from: "
            f"**{s['import_source']}**"
        )

        st.caption(
            "The imported values have been transferred into "
            "the Baseline Snapshot. Review them before locking."
        )

    # =========================================================
    # OPERATING DRIVERS
    # =========================================================

    st.subheader("⚙️ Operating Drivers")

    col1, col2, col3 = st.columns(3)

    with col1:

        price = st.number_input(
            "Unit Price (€)",
            min_value=0.0,
            value=_get_float(
                "baseline_price",
                150.0,
            ),
            step=1.0,
            key="baseline_price",
        )

        volume = st.number_input(
            "Annual Volume",
            min_value=0.0,
            value=_get_float(
                "baseline_volume",
                12000.0,
            ),
            step=500.0,
            key="baseline_volume",
        )

    with col2:

        variable_cost_per_unit = st.number_input(
            "Variable Cost / Unit (€)",
            min_value=0.0,
            value=_get_float(
                "baseline_variable_cost",
                100.0,
            ),
            step=1.0,
            key="baseline_variable_cost",
        )

        fixed_opex = st.number_input(
            "Fixed Operating Costs (€)",
            min_value=0.0,
            value=_get_float(
                "baseline_fixed_opex",
                450000.0,
            ),
            step=10000.0,
            key="baseline_fixed_opex",
        )

    with col3:

        fixed_assets = st.number_input(
            "Fixed Assets (€)",
            min_value=0.0,
            value=_get_float(
                "baseline_fixed_assets",
                800000.0,
            ),
            step=10000.0,
            key="baseline_fixed_assets",
        )

        depreciation = st.number_input(
            "Depreciation (€)",
            min_value=0.0,
            value=_get_float(
                "baseline_depreciation",
                50000.0,
            ),
            step=5000.0,
            key="baseline_depreciation",
        )

    # =========================================================
    # ADDITIONAL OPERATING DATA
    # =========================================================

    col1, col2 = st.columns(2)

    with col1:

        target_profit_goal = st.number_input(
            "Target Profit Goal (€)",
            min_value=0.0,
            value=_get_float(
                "baseline_target_profit_goal",
                200000.0,
            ),
            step=10000.0,
            key="baseline_target_profit_goal",
        )

    with col2:

        opening_cash = st.number_input(
            "Opening Cash (€)",
            min_value=0.0,
            value=_get_float(
                "baseline_opening_cash",
                150000.0,
            ),
            step=10000.0,
            key="baseline_opening_cash",
        )

    # =========================================================
    # REPORTED FINANCIAL RESULTS
    # =========================================================

    st.divider()

    st.subheader("📊 Reported Financial Results")

    st.caption(
        "Enter the company's reported figures. "
        "Managers Lab does not calculate the Baseline."
    )

    col1, col2, col3 = st.columns(3)

    with col1:

        profit_before_tax = st.number_input(
            "Profit Before Tax (EBT) (€)",
            min_value=0.0,
            value=_get_float(
                "baseline_profit_before_tax",
                150000.0,
            ),
            step=10000.0,
            key="baseline_profit_before_tax",
        )

    with col2:

        tax = st.number_input(
            "Tax (€)",
            min_value=0.0,
            value=_get_float(
                "baseline_tax",
                33000.0,
            ),
            step=5000.0,
            key="baseline_tax",
        )

    with col3:

        net_profit = st.number_input(
            "Net Profit (€)",
            min_value=0.0,
            value=_get_float(
                "baseline_net_profit",
                117000.0,
            ),
            step=10000.0,
            key="baseline_net_profit",
        )

    # =========================================================
    # CAPITAL STRUCTURE
    # =========================================================

    st.divider()

    st.subheader("🏦 Capital Structure")

    col1, col2, col3, col4 = st.columns(4)

    with col1:

        wacc = st.number_input(
            "Baseline WACC (%)",
            min_value=0.0,
            max_value=100.0,
            value=_get_float(
                "baseline_wacc",
                8.0,
            ),
            step=0.1,
            key="baseline_wacc",
        )

    with col2:

        total_debt = st.number_input(
            "Total Debt (€)",
            min_value=0.0,
            value=_get_float(
                "baseline_total_debt",
                500000.0,
            ),
            step=25000.0,
            key="baseline_total_debt",
        )

    with col3:

        equity = st.number_input(
            "Equity (€)",
            min_value=0.0,
            value=_get_float(
                "baseline_equity",
                500000.0,
            ),
            step=25000.0,
            key="baseline_equity",
        )

    with col4:

        cost_of_debt = st.number_input(
            "Cost of Debt (%)",
            min_value=0.0,
            max_value=100.0,
            value=_get_float(
                "baseline_cost_of_debt",
                6.0,
            ),
            step=0.1,
            key="baseline_cost_of_debt",
        )

    # =========================================================
    # DEBT / TAX
    # =========================================================

    col1, col2, col3, col4 = st.columns(4)

    with col1:

        annual_cash_interest_paid = st.number_input(
            "Annual Cash Interest Paid (€)",
            min_value=0.0,
            value=_get_float(
                "baseline_annual_cash_interest_paid",
                25000.0,
            ),
            step=5000.0,
            key="baseline_annual_cash_interest_paid",
        )

    with col2:

        annual_debt_service = st.number_input(
            "Annual Debt Service (€)",
            min_value=0.0,
            value=_get_float(
                "baseline_annual_debt_service",
                70000.0,
            ),
            step=5000.0,
            key="baseline_annual_debt_service",
        )

    with col3:

        principal_payments = st.number_input(
            "Annual Principal Payments (€)",
            min_value=0.0,
            value=_get_float(
                "baseline_principal_payments",
                45000.0,
            ),
            step=5000.0,
            key="baseline_principal_payments",
        )

    with col4:

        tax_rate = st.number_input(
            "Corporate Tax Rate (%)",
            min_value=0.0,
            max_value=100.0,
            value=_get_float(
                "baseline_tax_rate",
                22.0,
            ),
            step=0.5,
            key="baseline_tax_rate",
        )

    # =========================================================
    # WORKING CAPITAL
    # =========================================================

    st.divider()

    st.subheader("💧 Working Capital Policy")

    col1, col2, col3 = st.columns(3)

    with col1:

        ar_days = st.number_input(
            "Accounts Receivable Days",
            min_value=0.0,
            value=_get_float(
                "baseline_ar_days",
                90.0,
            ),
            step=1.0,
            key="baseline_ar_days",
        )

    with col2:

        inventory_days = st.number_input(
            "Inventory Days",
            min_value=0.0,
            value=_get_float(
                "baseline_inventory_days",
                75.0,
            ),
            step=1.0,
            key="baseline_inventory_days",
        )

    with col3:

        ap_days = st.number_input(
            "Accounts Payable Days",
            min_value=0.0,
            value=_get_float(
                "baseline_ap_days",
                45.0,
            ),
            step=1.0,
            key="baseline_ap_days",
        )

    # =========================================================
    # LOCK BASELINE
    # =========================================================

    st.divider()

    st.subheader("🔐 Lock Baseline")

    st.caption(
        "Locking the baseline creates the immutable "
        "CompanyState used by all downstream modules."
    )

    if not st.button(
        "🔒 Lock Baseline",
        type="primary",
        use_container_width=True,
        key="lock_baseline",
    ):
        return

    # =========================================================
    # VALIDATION
    # =========================================================

    if not label.strip():
        st.error("Baseline label cannot be empty.")
        return

    if price <= 0:
        st.error("Unit Price must be greater than zero.")
        return

    if volume <= 0:
        st.error("Annual Volume must be greater than zero.")
        return

    if variable_cost_per_unit < 0:
        st.error("Variable Cost cannot be negative.")
        return

    if fixed_opex < 0:
        st.error("Fixed Operating Costs cannot be negative.")
        return

    if fixed_assets < 0:
        st.error("Fixed Assets cannot be negative.")
        return

    if depreciation < 0:
        st.error("Depreciation cannot be negative.")
        return

    if wacc < 0:
        st.error("WACC cannot be negative.")
        return

    if cost_of_debt < 0:
        st.error("Cost of Debt cannot be negative.")
        return

    if total_debt < 0:
        st.error("Total Debt cannot be negative.")
        return

    if equity < 0:
        st.error("Equity cannot be negative.")
        return

    # =========================================================
    # CREATE OPERATIONAL DRIVERS
    # =========================================================

    drivers = OperationalDrivers(
        price=float(price),
        volume=float(volume),
        variable_cost_per_unit=float(variable_cost_per_unit),
        fixed_opex=float(fixed_opex),
        fixed_assets=float(fixed_assets),
        depreciation=float(depreciation),
        target_profit_goal=float(target_profit_goal),
        opening_cash=float(opening_cash),
    )

    # =========================================================
    # CREATE CAPITAL STRUCTURE
    # =========================================================

    capital_structure = CapitalStructure(
        wacc=float(wacc) / 100.0,
        total_debt=float(total_debt),
        equity=float(equity),
        cost_of_debt=float(cost_of_debt) / 100.0,
        annual_cash_interest_paid=float(annual_cash_interest_paid),
        annual_debt_service=float(annual_debt_service),
        principal_payments=float(principal_payments),
        tax_rate=float(tax_rate) / 100.0,
    )

    # =========================================================
    # CREATE WORKING CAPITAL POLICY
    # =========================================================

    working_capital = WorkingCapitalPolicy(
        ar_days=float(ar_days),
        inventory_days=float(inventory_days),
        ap_days=float(ap_days),
    )

    # =========================================================
    # CREATE IMMUTABLE COMPANY STATE
    # =========================================================

    baseline = CompanyState(
        version=int(version),
        created_at=datetime.utcnow().isoformat(timespec="seconds"),
        label=label.strip(),
        drivers=drivers,
        capital_structure=capital_structure,
        working_capital=working_capital,

        # REPORTED BASELINE FINANCIALS (NO CALCULATIONS)
        profit_before_tax=float(profit_before_tax),
        tax=float(tax),
        net_profit=float(net_profit),
    )

    # =========================================================
    # SAVE CANONICAL BASELINE
    # =========================================================

    BaselineRepository.save(baseline)

    # =========================================================
    # SESSION STATE
    # =========================================================

    st.session_state["baseline_locked"] = True
    st.session_state["baseline_state"] = baseline

    # =========================================================
    # RESET DECISION STATE
    # =========================================================

    st.session_state["decisions"] = []
    st.session_state.pop("selected_decision", None)
    st.session_state.pop("decision_plan", None)
    st.session_state.pop("wacc_locked", None)
    st.session_state.pop("wacc_result", None)

    # =========================================================
    # SUCCESS
    # =========================================================

    st.success(
        f"🔒 Baseline '{baseline.label}' "
        f"(Version {baseline.version}) "
        f"locked successfully."
    )

    # =========================================================
    # ACTIVE BASELINE
    # =========================================================

    st.divider()

    st.subheader("📌 Active Baseline")

    current = BaselineRepository.get()

    if current is not None:

        st.success(
            f"🔒 Active Baseline: "
            f"{current.label} | "
            f"Version {current.version}"
        )

        st.caption(f"Created: {current.created_at}")

        c1, c2, c3 = st.columns(3)

        with c1:
            st.metric(
                "Price",
                f"€ {current.drivers.price:,.2f}",
            )

        with c2:
            st.metric(
                "Volume",
                f"{current.drivers.volume:,.0f}",
            )

        with c3:
            st.metric(
                "AR Days",
                f"{current.working_capital.ar_days:,.1f}",
            )

        c4, c5, c6 = st.columns(3)

        with c4:
            st.metric(
                "Variable Cost",
                f"€ {current.drivers.variable_cost_per_unit:,.2f}",
            )

        with c5:
            st.metric(
                "Fixed OPEX",
                f"€ {current.drivers.fixed_opex:,.0f}",
            )

        with c6:
            st.metric(
                "Total Debt",
                f"€ {current.capital_structure.total_debt:,.0f}",
            )
