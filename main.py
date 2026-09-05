import sys
from pathlib import Path

# =========================================================
# APPLICATION ROOT
# =========================================================

root_dir = Path(__file__).resolve().parent

if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))


# =========================================================
# STREAMLIT CONFIGURATION
# =========================================================

import streamlit as st

st.set_page_config(
    page_title="Managers Lab",
    page_icon="🧠",
    layout="wide",
)


# =========================================================
# CORE IMPORTS
# =========================================================

from core.baseline_repository import BaselineRepository
from core.decision_evaluator import DecisionEvaluator
from core.decision_plan import DecisionPlan
from core.state_builder import StateBuilder


# =========================================================
# UI / TOOL IMPORTS
# =========================================================

from tools.loan_vs_leasing import render_loan_vs_leasing_lab

from ui.baseline import render_baseline_setup
from ui.cash_break_even_lab import render_cash_break_even_lab
from ui.cash_fragility_lab import render_cash_fragility_lab
from ui.clv_lab import render_clv_lab
from ui.dashboard import render_dashboard
from ui.data_import import render_data_import
from ui.decision_view import render_decision_view
from ui.inventory_lab import show_inventory_lab
from ui.pricing_lab import render_pricing_lab
from ui.receivables_lab import render_receivables_lab
from ui.suppliers_lab import render_suppliers_lab
from ui.wacc_lab import render_wacc_lab
from ui.pricing_threshold_lab import render_pricing_threshold
from ui.monthly_survival_lab import render_monthly_survival_lab

from ui.complementary_products_lab import (
    render_complementary_products_lab
)

from ui.substitute_products_lab import (
    render_substitute_products_lab
)

from ui.deal_auditor_lab import render_deal_auditor_lab
from ui.stress_test_lab import render_stress_test_lab

from ui.customer_cash_economics_lab import (
    render_customer_cash_economics_lab
)

from ui.inventory_ordering_lab import (
    render_inventory_ordering_lab
)

from ui.salesperson_value_lab import (
    render_salesperson_value_lab
)

from ui.growth_funding_lab import (
    render_growth_funding_lab
)

from ui.working_capital_data_analyzer import (
    render_working_capital_data_analyzer
)

from ui.qspm_lab import render_qspm_lab
from ui.concentration_lab import render_concentration_lab


# =========================================================
# APPLICATION SERVICES
# =========================================================

baseline_repository = BaselineRepository

state_builder = StateBuilder(
    baseline_repository=baseline_repository,
)


# =========================================================
# SAFE BASELINE LOADER
# =========================================================

def get_safe_baseline():
    """
    Returns the active baseline if available.

    Priority:
        1. custom_baseline in session state
        2. BaselineRepository
        3. None
    """

    if "custom_baseline" in st.session_state:
        return st.session_state.custom_baseline

    try:
        return state_builder.build_baseline_only()
    except Exception:
        return None


# =========================================================
# APPLICATION STATE
# =========================================================

def initialize_app() -> None:

    if "decision_plan" not in st.session_state:

        st.session_state.decision_plan = DecisionPlan.create(
            plan_id="main_plan",
            name="Current Decision Plan",
        )

    if "current_page" not in st.session_state:

        st.session_state.current_page = "main"


initialize_app()


# =========================================================
# NAVIGATION
# =========================================================

def navigate_to(page_name: str) -> None:
    st.session_state.current_page = page_name


def go_to_main() -> None:
    st.session_state.current_page = "main"


# =========================================================
# PROJECTION PIPELINE
# =========================================================

def build_projection():

    baseline_state = get_safe_baseline()

    if baseline_state is None:

        st.error(
            "Please set and confirm a Baseline first."
        )

        st.stop()

    decision_plan = st.session_state.get(
        "decision_plan"
    )

    if not isinstance(
        decision_plan,
        DecisionPlan,
    ):

        decision_plan = DecisionPlan.create(
            plan_id="empty_plan",
            name="Empty Decision Plan",
        )

    evaluation = DecisionEvaluator.evaluate(

        baseline_state=baseline_state,

        plan=decision_plan,
    )

    trace = dict(
        evaluation.execution_report
    )

    trace.update(
        {
            "projection_mode":
                "baseline"
                if decision_plan.is_empty
                else "decision_plan",

            "plan":
                {
                    "id":
                        decision_plan.id,

                    "name":
                        decision_plan.name,

                    "decision_count":
                        decision_plan.decision_count,
                },

            "message":
                "Projection generated from "
                "the current Decision Plan.",
        }
    )

    return (
        evaluation.baseline_state,
        evaluation.projected_state,
        evaluation.financial_projection,
        trace,
    )


# =========================================================
# SMALL UI HELPERS
# =========================================================

def home_button(
    label: str,
    page: str,
    key: str,
    description: str,
):

    st.markdown(
        f"### {label}"
    )

    st.caption(
        description
    )

    if st.button(
        "Explore →",
        key=key,
        use_container_width=True,
    ):

        navigate_to(page)
        st.rerun()


def navigation_button(
    label: str,
    page: str,
    key: str,
):

    if st.button(
        label,
        key=key,
        use_container_width=True,
    ):

        navigate_to(page)
        st.rerun()


# =========================================================
# SIDEBAR
# =========================================================

with st.sidebar:

    st.markdown(
        "## 🧠 Managers Lab"
    )

    st.caption(
        "Decision Intelligence for Owner-Managers"
    )

    st.divider()

    # -----------------------------------------------------
    # HOME
    # -----------------------------------------------------

    if st.button(
        "🏠 Home",
        key="sidebar_home",
        use_container_width=True,
    ):

        go_to_main()
        st.rerun()

    # -----------------------------------------------------
    # COMPANY IMPACT
    # -----------------------------------------------------

    if st.button(
        "📊 Company Impact",
        key="sidebar_control_tower",
        use_container_width=True,
    ):

        navigate_to(
            "📊 Control Tower"
        )

        st.rerun()

    st.divider()

    # -----------------------------------------------------
    # BASELINE
    # -----------------------------------------------------

    baseline = get_safe_baseline()

    st.markdown(
        "### 🏢 Your Company"
    )

    if baseline:

        st.success(
            "🔒 Baseline locked"
        )

        st.caption(
            f"Version {getattr(baseline, 'version', 1)}"
        )

    else:

        st.warning(
            "Baseline not set"
        )

    # -----------------------------------------------------
    # PLAN
    # -----------------------------------------------------

    decision_plan = st.session_state.get(
        "decision_plan"
    )

    if isinstance(
        decision_plan,
        DecisionPlan,
    ):

        count = decision_plan.decision_count

        if count == 0:

            st.caption(
                "No decisions selected"
            )

        else:

            st.info(
                f"🎯 {count} decision"
                f"{'s' if count != 1 else ''} in plan"
            )

    st.divider()

    # -----------------------------------------------------
    # SETTINGS
    # -----------------------------------------------------

    with st.expander(
        "⚙️ Settings"
    ):

        if st.button(
            "📥 Import Company Data",
            key="sidebar_import",
            use_container_width=True,
        ):

            navigate_to(
                "📥 Import Data"
            )

            st.rerun()

        if st.button(
            "🗑️ Clear Decision Plan",
            key="sidebar_clear_plan",
            use_container_width=True,
        ):

            st.session_state.decision_plan = (
                DecisionPlan.create(
                    plan_id="main_plan",
                    name="Current Decision Plan",
                )
            )

            st.rerun()

        if st.button(
            "💥 Reset Application",
            key="sidebar_reset",
            use_container_width=True,
        ):

            st.session_state.clear()

            st.session_state.decision_plan = (
                DecisionPlan.create(
                    plan_id="main_plan",
                    name="Current Decision Plan",
                )
            )

            st.session_state.current_page = "main"

            st.rerun()


# =========================================================
# HOME
# =========================================================

def render_home():

    # -----------------------------------------------------
    # HEADER
    # -----------------------------------------------------

    st.title(
        "🧠 Managers Lab"
    )

    st.markdown(
        "### Make better business decisions. "
        "Not more software."
    )

    st.caption(
        "Start with your company. "
        "Choose what you want to improve. "
        "See the financial impact."
    )

    st.divider()

    # -----------------------------------------------------
    # COMPANY SNAPSHOT
    # -----------------------------------------------------

    baseline = get_safe_baseline()

    if baseline is not None:

        try:

            from core.engine import FinancialEngine

            financials = (
                FinancialEngine.calculate_statements(
                    baseline
                )
            )

            income = financials.income_statement
            wc = financials.working_capital

            col1, col2, col3, col4 = st.columns(4)

            with col1:
                st.metric(
                    "Revenue",
                    f"€{income.revenue:,.0f}"
                )

            with col2:
                st.metric(
                    "EBITDA",
                    f"€{income.ebitda:,.0f}"
                )

            with col3:
                st.metric(
                    "Cash",
                    f"€{baseline.drivers.opening_cash:,.0f}"
                )

            with col4:
                st.metric(
                    "Working Capital",
                    f"€{wc.nwc:,.0f}"
                )

        except Exception:

            st.info(
                "Your company baseline is ready."
            )

    else:

        st.info(
            "Set up your company baseline to begin."
        )

        if st.button(
            "🏢 Set Up My Company",
            type="primary",
            use_container_width=False,
        ):

            navigate_to(
                "🏢 Baseline Snapshot"
            )

            st.rerun()

        st.divider()

    # -----------------------------------------------------
    # DECIDE
    # -----------------------------------------------------

    st.markdown(
        "## What are you trying to do?"
    )

    st.caption(
        "Choose the business outcome you want to work on."
    )

    col1, col2 = st.columns(2, gap="large")

    # =====================================================
    # MAKE MORE MONEY
    # =====================================================

    with col1:

        with st.container(border=True):

            st.markdown(
                "## 💰 Make More Money"
            )

            st.caption(
                "Improve price, margin, sales or "
                "customer economics."
            )

            b1, b2 = st.columns(2)

            with b1:

                navigation_button(
                    "Price",
                    "💰 Pricing Lab",
                    "home_price",
                )

            with b2:

                navigation_button(
                    "Sales Volume",
                    "📈 Sales Volume",
                    "home_volume",
                )

            b3, b4 = st.columns(2)

            with b3:

                navigation_button(
                    "Variable Cost",
                    "💧 Cash Break-Even Lab",
                    "home_variable_cost",
                )

            with b4:

                navigation_button(
                    "Customer Economics",
                    "👥 Customer Economics Lab",
                    "home_customer_economics",
                )

    # =====================================================
    # FREE UP CASH
    # =====================================================

    with col2:

        with st.container(border=True):

            st.markdown(
                "## 💧 Free Up Cash"
            )

            st.caption(
                "Reduce cash tied up in customers, "
                "inventory and suppliers."
            )

            b1, b2 = st.columns(2)

            with b1:

                navigation_button(
                    "Receivables",
                    "💶 Receivables Lab",
                    "home_receivables",
                )

            with b2:

                navigation_button(
                    "Inventory",
                    "📦 Inventory Lab",
                    "home_inventory",
                )

            b3, b4 = st.columns(2)

            with b3:

                navigation_button(
                    "Supplier Terms",
                    "🚚 Suppliers & Payables Lab",
                    "home_suppliers",
                )

            with b4:

                navigation_button(
                    "Working Capital",
                    "📐 Working Capital Data Analyzer",
                    "home_working_capital",
                )

    # -----------------------------------------------------
    # FUND GROWTH
    # -----------------------------------------------------

    col1, col2 = st.columns(2, gap="large")

    with col1:

        with st.container(border=True):

            st.markdown(
                "## 🚀 Fund Growth"
            )

            st.caption(
                "Understand growth funding needs "
                "and financing choices."
            )

            b1, b2 = st.columns(2)

            with b1:

                navigation_button(
                    "Growth Funding",
                    "📈 Growth & Funding Lab",
                    "home_growth",
                )

            with b2:

                navigation_button(
                    "Debt & WACC",
                    "🏦 WACC Lab",
                    "home_wacc",
                )

            b3, b4 = st.columns(2)

            with b3:

                navigation_button(
                    "Loan vs Leasing",
                    "🏦 Loan vs Leasing",
                    "home_loan_lease",
                )

            with b4:

                navigation_button(
                    "Strategic Options",
                    "🧠 QSPM Strategic Evaluation",
                    "home_strategy",
                )

    # =====================================================
    # PROTECT BUSINESS
    # =====================================================

    with col2:

        with st.container(border=True):

            st.markdown(
                "## 🛡️ Protect the Business"
            )

            st.caption(
                "Test liquidity, survival and "
                "business fragility."
            )

            b1, b2 = st.columns(2)

            with b1:

                navigation_button(
                    "Cash Fragility",
                    "🩺 Cash Fragility Diagnostic",
                    "home_fragility",
                )

            with b2:

                navigation_button(
                    "Stress Test",
                    "🛡️ Stress Test Simulator",
                    "home_stress",
                )

            b3, b4 = st.columns(2)

            with b3:

                navigation_button(
                    "Monthly Survival",
                    "📅 Monthly Cash Coverage",
                    "home_survival",
                )

            with b4:

                navigation_button(
                    "Deal Auditor",
                    "🔎 Deal Auditor",
                    "home_deal_auditor",
                )

    # -----------------------------------------------------
    # COMPANY IMPACT
    # -----------------------------------------------------

    st.divider()

    st.markdown(
        "## 📊 Company Impact"
    )

    st.caption(
        "See what your decisions mean for the company as a whole."
    )

    if st.button(
        "Open Control Tower →",
        key="home_control_tower",
        type="primary",
        use_container_width=True,
    ):

        navigate_to(
            "📊 Control Tower"
        )

        st.rerun()


# =========================================================
# HOME ROUTE
# =========================================================

current_page = st.session_state.get(
    "current_page",
    "main",
)

if current_page == "main":

    render_home()

    st.stop()


# =========================================================
# BASELINE / DATA
# =========================================================

if current_page == "🏢 Baseline Snapshot":

    render_baseline_setup()
    st.stop()


if current_page == "📥 Import Data":

    render_data_import()
    st.stop()


if current_page == "📐 Working Capital Data Analyzer":

    render_working_capital_data_analyzer()
    st.stop()


# =========================================================
# BASELINE GUARD
# =========================================================

baseline = get_safe_baseline()

if baseline is None:

    st.warning(
        "🔒 No company baseline found."
    )

    st.info(
        "Please set up your company baseline first."
    )

    if st.button(
        "🏠 Back to Home"
    ):

        go_to_main()
        st.rerun()

    st.stop()


# =========================================================
# DECISION LABS
# =========================================================

if current_page == "💰 Pricing Lab":

    render_pricing_lab(
        baseline_state=baseline
    )

    st.stop()


if current_page == "🎯 Pricing Threshold":

    render_pricing_threshold(
        baseline_state=baseline
    )

    st.stop()


if current_page == "💶 Receivables Lab":

    render_receivables_lab(
        baseline_state=baseline
    )

    st.stop()


if current_page == "📦 Inventory Lab":

    show_inventory_lab(
        baseline_state=baseline
    )

    st.stop()


if current_page == "📦 Inventory Ordering Lab":

    render_inventory_ordering_lab(
        baseline_state=baseline
    )

    st.stop()


if current_page == "🚚 Suppliers & Payables Lab":

    render_suppliers_lab(
        baseline_state=baseline
    )

    st.stop()


if current_page == "💧 Cash Break-Even Lab":

    b_state, p_state, fin_proj, trace = (
        build_projection()
    )

    render_cash_break_even_lab(
        baseline_state=b_state,
        projected_state=p_state,
        financial_projection=fin_proj,
    )

    st.stop()


if current_page == "🏦 WACC Lab":

    render_wacc_lab(
        baseline_state=baseline
    )

    st.stop()


if current_page == "🏦 Loan vs Leasing":

    render_loan_vs_leasing_lab(
        baseline_state=baseline
    )

    st.stop()


if current_page == "📈 Growth & Funding Lab":

    b_state, p_state, fin_proj, trace = (
        build_projection()
    )

    render_growth_funding_lab(
        baseline_state=b_state,
        projected_state=p_state,
        financial_projection=fin_proj,
    )

    st.stop()


if current_page == "👥 Customer Economics Lab":

    render_clv_lab(
        baseline_state=baseline
    )

    st.stop()


if current_page == "💼 Customer Cash & Economics":

    render_customer_cash_economics_lab(
        baseline_state=baseline
    )

    st.stop()


if current_page == "🧩 Complementary Products Diagnostic":

    render_complementary_products_lab(
        baseline_state=baseline
    )

    st.stop()


if current_page == "🔄 Substitute Products Diagnostic":

    render_substitute_products_lab(
        baseline_state=baseline
    )

    st.stop()


if current_page == "🔎 Deal Auditor":

    render_deal_auditor_lab(
        baseline_state=baseline
    )

    st.stop()


if current_page == "🎯 Customer Concentration Diagnostic":

    render_concentration_lab(
        baseline_state=baseline
    )

    st.stop()


if current_page == "👤 Salesperson Value Lab":

    render_salesperson_value_lab(
        baseline_state=baseline
    )

    st.stop()


if current_page == "🛡️ Stress Test Simulator":

    render_stress_test_lab(
        baseline_state=baseline
    )

    st.stop()


if current_page == "🩺 Cash Fragility Diagnostic":

    b_state, p_state, fin_proj, trace = (
        build_projection()
    )

    render_cash_fragility_lab(
        baseline_state=b_state,
        projected_state=p_state,
        financial_projection=fin_proj,
    )

    st.stop()


if current_page == "📅 Monthly Cash Coverage":

    b_state, p_state, fin_proj, trace = (
        build_projection()
    )

    render_monthly_survival_lab(
        baseline_state=b_state,
        projected_state=p_state,
    )

    st.stop()


if current_page == "🧠 QSPM Strategic Evaluation":

    decision_plan = st.session_state.get(
        "decision_plan"
    )

    if not isinstance(
        decision_plan,
        DecisionPlan,
    ):

        decision_plan = DecisionPlan.create(
            plan_id="empty_plan",
            name="Empty Decision Plan",
        )

    render_qspm_lab(
        baseline_state=baseline,
        decision_plan=decision_plan,
    )

    st.stop()


# =========================================================
# MANAGEMENT
# =========================================================

if current_page == "🧩 Decision Manager":

    render_decision_view()
    st.stop()


if current_page == "📊 Control Tower":

    b_state, p_state, fin_proj, trace = (
        build_projection()
    )

    render_dashboard(
        baseline_state=b_state,
        projected_state=p_state,
        financial_projection=fin_proj,
        trace=trace,
    )

    st.stop()


# =========================================================
# OPTIONAL / LEGACY ROUTES
# =========================================================

if current_page == "📈 Sales Volume":

    st.info(
        "Sales Volume decision interface "
        "will be connected here."
    )

    if st.button("← Back"):

        go_to_main()
        st.rerun()

    st.stop()
