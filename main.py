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
    page_icon="🧪",
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
# UI / TOOL MODULE IMPORTS
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
# APPLICATION STATE INITIALIZATION
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
# NAVIGATION HELPERS
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
            "⚠️ Please set and confirm a Baseline first."
        )

        st.stop()

    decision_plan = st.session_state.get(
        "decision_plan"
    )

    # -----------------------------------------------------
    # NO DECISION PLAN
    # -----------------------------------------------------

    if not isinstance(
        decision_plan,
        DecisionPlan,
    ):

        evaluation = DecisionEvaluator.evaluate(

            baseline_state=baseline_state,

            plan=DecisionPlan.create(
                plan_id="empty_plan",
                name="Empty Decision Plan",
            ),
        )

        trace = dict(
            evaluation.execution_report
        )

        trace.update(
            {
                "projection_mode": "baseline",

                "plan": None,

                "message":
                    "No DecisionPlan exists. "
                    "Projection equals locked baseline.",
            }
        )

        return (
            evaluation.baseline_state,
            evaluation.projected_state,
            evaluation.financial_projection,
            trace,
        )

    # -----------------------------------------------------
    # DECISION PLAN
    # -----------------------------------------------------

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
                "decision_plan",

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
                "DecisionPlan through DecisionEvaluator.",
        }
    )

    return (
        evaluation.baseline_state,
        evaluation.projected_state,
        evaluation.financial_projection,
        trace,
    )


# =========================================================
# SIDEBAR
# =========================================================

with st.sidebar:

    # =====================================================
    # BRANDING
    # =====================================================

    st.markdown("## 🧠 Managers Lab")

    st.caption(
        "Decision Intelligence System"
    )

    st.divider()

    # =====================================================
    # NAVIGATION
    # =====================================================

    st.markdown("### 🗺️ Navigation")

    if st.session_state.current_page != "main":

        if st.button(
            "🏠 Main Dashboard",
            key="sidebar_main_dashboard",
            use_container_width=True,
        ):
            go_to_main()
            st.rerun()

    if st.button(
        "📊 Control Tower",
        key="sidebar_control_tower",
        use_container_width=True,
    ):
        navigate_to("📊 Control Tower")
        st.rerun()

    st.divider()

    # =====================================================
    # CURRENT STATE
    # =====================================================

    st.markdown("### 🏢 Current State")

    baseline = get_safe_baseline()

    if baseline:

        st.success(
            f"🔒 Baseline: "
            f"{getattr(baseline, 'label', 'Locked')}"
        )

        st.caption(
            f"Version: "
            f"{getattr(baseline, 'version', '1')}"
        )

    else:

        st.warning(
            "⚠️ No locked baseline"
        )

    # -----------------------------------------------------
    # DECISION PLAN
    # -----------------------------------------------------

    decision_plan = st.session_state.get(
        "decision_plan"
    )

    if isinstance(
        decision_plan,
        DecisionPlan,
    ):

        if decision_plan.is_empty:

            st.info(
                "🎯 Decision Plan: Empty"
            )

        else:

            st.info(
                f"🎯 Decision Plan: "
                f"{decision_plan.decision_count} decision(s)"
            )

    st.divider()

    # =====================================================
    # SYSTEM
    # =====================================================

    st.markdown("### ⚙️ System")

    # -----------------------------------------------------
    # CLEAR DECISION PLAN
    # -----------------------------------------------------

    if st.button(
        "🗑️ Clear Decision Plan",
        use_container_width=True,
        key="sidebar_clear_decision_plan",
    ):

        st.session_state.decision_plan = (
            DecisionPlan.create(
                plan_id="main_plan",
                name="Current Decision Plan",
            )
        )

        st.rerun()

    # -----------------------------------------------------
    # RESET APPLICATION
    # -----------------------------------------------------

    if st.button(
        "💥 Reset Application",
        use_container_width=True,
        key="sidebar_reset_application",
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

    st.divider()

    # =====================================================
    # PRODUCT HUNT
    # =====================================================

    st.markdown(
        "### 🚀 Featured on Product Hunt"
    )

    st.markdown(
        """
        <a href="https://www.producthunt.com/products/managers-lab?embed=true&utm_source=badge-featured&utm_medium=badge&utm_campaign=badge-managers-lab"
           target="_blank"
           rel="noopener noreferrer">

            <img
                src="https://api.producthunt.com/widgets/embed-image/v1/featured.svg?post_id=1132085&theme=light"
                alt="Managers' Lab - Built for better decisions. Not more software."
                width="100%"
            />

        </a>
        """,
        unsafe_allow_html=True,
    )

    st.divider()

    # =====================================================
    # ALTERNATIVETO
    # =====================================================

    st.markdown(
        "### 🔎 Listed on AlternativeTo"
    )

    st.markdown(
        """
        <a href="https://alternativeto.net/software/managers-lab/about/"
           target="_blank"
           rel="noopener noreferrer"
           style="
               display:block;
               padding:8px;
               background-color:#262730;
               border-radius:5px;
               text-align:center;
               color:#1E3A8A;
               font-weight:bold;
               text-decoration:none;
           ">
            🔗 View on AlternativeTo
        </a>
        """,
        unsafe_allow_html=True,
    )

# =========================================================
# MAIN DASHBOARD
# =========================================================

def render_main_screen():

    # =====================================================
    # MAIN TWO-COLUMN LAYOUT
    # =====================================================

    col_left, col_right = st.columns(
        [0.42, 0.58],
        gap="large",
    )

    # =====================================================
    # LEFT COLUMN
    # BASELINE
    # =====================================================

    with col_left:

        st.markdown(
            "### 🏢 COMPANY BASELINE"
        )

        st.caption(
            "Edit the numbers, then confirm the baseline below."
        )

        render_baseline_setup()

    # =====================================================
    # RIGHT COLUMN
    # BUSINESS QUESTIONS
    # =====================================================

    with col_right:

        st.markdown(
            "### 🎯 BUSINESS QUESTIONS"
        )

        st.caption(
            "Pick an area of focus to evaluate "
            "strategies against your baseline."
        )

        # =================================================
        # BUSINESS AREA TABS
        # =================================================

        tab_grow, tab_fund, tab_operate, tab_stress = (
            st.tabs(
                [
                    "🚀 Grow",
                    "💰 Fund",
                    "⚙️ Operate",
                    "🛡️ Stress",
                ]
            )
        )

        # =================================================
        # GROW
        # =================================================

        with tab_grow:

            if st.button(
                "💰 Pricing Lab",
                key="m_pricing",
                use_container_width=True,
            ):

                navigate_to(
                    "💰 Pricing Lab"
                )

                st.rerun()

            if st.button(
                "🎯 Pricing Threshold & Sensitivity",
                key="m_pricing_thresh",
                use_container_width=True,
            ):

                navigate_to(
                    "🎯 Pricing Threshold"
                )

                st.rerun()

            if st.button(
                "👥 Customer Economics (CLV)",
                key="m_clv",
                use_container_width=True,
            ):

                navigate_to(
                    "👥 Customer Economics Lab"
                )

                st.rerun()

            if st.button(
                "🧩 Complementary Products Diagnostic",
                key="m_comp_prod",
                use_container_width=True,
            ):

                navigate_to(
                    "🧩 Complementary Products Diagnostic"
                )

                st.rerun()

            if st.button(
                "🔄 Substitute Products Diagnostic",
                key="m_sub_prod",
                use_container_width=True,
            ):

                navigate_to(
                    "🔄 Substitute Products Diagnostic"
                )

                st.rerun()

            if st.button(
                "🧠 QSPM Strategic Evaluation",
                key="m_mgmt_qspm",
                use_container_width=True,
            ):

                navigate_to(
                    "🧠 QSPM Strategic Evaluation"
                )

                st.rerun()
                
        # =================================================
        # FUND
        # =================================================

        with tab_fund:

            if st.button(
                "📈 Growth & Funding Lab",
                key="m_growth_fund",
                use_container_width=True,
            ):

                navigate_to(
                    "📈 Growth & Funding Lab"
                )

                st.rerun()

            if st.button(
                "🏦 WACC Lab",
                key="m_wacc",
                use_container_width=True,
            ):

                navigate_to(
                    "🏦 WACC Lab"
                )

                st.rerun()

            if st.button(
                "⚖️ Loan vs Leasing",
                key="m_loan_lease",
                use_container_width=True,
            ):

                navigate_to(
                    "🏦 Loan vs Leasing"
                )

                st.rerun()

        # =================================================
        # OPERATE
        # =================================================

        with tab_operate:

            if st.button(
                "💧 Cash Break-Even Lab",
                key="m_be",
                use_container_width=True,
            ):

                navigate_to(
                    "💧 Cash Break-Even Lab"
                )

                st.rerun()

            if st.button(
                "🔎 Deal Auditor",
                key="m_deal_audit",
                use_container_width=True,
            ):

                navigate_to(
                    "🔎 Deal Auditor"
                )

                st.rerun()

            if st.button(
                "🎯 Customer Concentration Diagnostic",
                key="m_concentration",
                use_container_width=True,
            ):

                navigate_to(
                    "🎯 Customer Concentration Diagnostic"
                )

                st.rerun()

            if st.button(
                "💼 Customer Cash & Economics",
                key="m_cust_cash",
                use_container_width=True,
            ):

                navigate_to(
                    "💼 Customer Cash & Economics"
                )

                st.rerun()

            if st.button(
                "👤 Salesperson Value Lab",
                key="m_sales_val",
                use_container_width=True,
            ):

                navigate_to(
                    "👤 Salesperson Value Lab"
                )

                st.rerun()

            if st.button(
                "📦 Inventory Lab",
                key="m_inv",
                use_container_width=True,
            ):

                navigate_to(
                    "📦 Inventory Lab"
                )

                st.rerun()

            if st.button(
                "🛒 Inventory Ordering Optimizer",
                key="m_inv_ord",
                use_container_width=True,
            ):

                navigate_to(
                    "📦 Inventory Ordering Lab"
                )

                st.rerun()

            if st.button(
                "💶 Receivables Lab",
                key="m_recv",
                use_container_width=True,
            ):

                navigate_to(
                    "💶 Receivables Lab"
                )

                st.rerun()

            if st.button(
                "🚚 Suppliers & Payables Lab",
                key="m_supp",
                use_container_width=True,
            ):

                navigate_to(
                    "🚚 Suppliers & Payables Lab"
                )

                st.rerun()

            if st.button(
                "📐 Working Capital Data Analyzer",
                key="m_wc_analyzer",
                use_container_width=True,
            ):

                navigate_to(
                    "📐 Working Capital Data Analyzer"
                )

                st.rerun()

        # =================================================
        # STRESS
        # =================================================

        with tab_stress:

            if st.button(
                "🩺 Cash Fragility Diagnostic",
                key="m_fragility",
                use_container_width=True,
            ):

                navigate_to(
                    "🩺 Cash Fragility Diagnostic"
                )

                st.rerun()

            if st.button(
                "📅 Monthly Cash Coverage Analysis",
                key="m_monthly_survival",
                use_container_width=True,
            ):

                navigate_to(
                    "📅 Monthly Cash Coverage"
                )

                st.rerun()

            if st.button(
                "🛡️ Dynamic Stress Test Simulator",
                key="m_stress",
                use_container_width=True,
            ):

                navigate_to(
                    "🛡️ Stress Test Simulator"
                )

                st.rerun()

        # =================================================
        # MANAGEMENT TOOLS
        # =================================================

        st.divider()

        st.markdown(
            "### 📊 MANAGEMENT TOOLS"
        )

        st.caption(
            "Manage decisions, review the company-wide impact, "
            "or import new business data."
        )

        management_col1, management_col2, management_col3 = (
            st.columns(3, gap="small")
        )

        # -------------------------------------------------
        # CONTROL TOWER
        # -------------------------------------------------

        with management_col1:

            if st.button(
                "📊 Control Tower",
                key="m_mgmt_control",
                use_container_width=True,
                type="primary",
            ):

                navigate_to(
                    "📊 Control Tower"
                )

                st.rerun()

        # -------------------------------------------------
        # DECISION MANAGER
        # -------------------------------------------------

        with management_col2:

            if st.button(
                "🧩 Decision Manager",
                key="m_mgmt_decisions",
                use_container_width=True,
            ):

                navigate_to(
                    "🧩 Decision Manager"
                )

                st.rerun()

        # -------------------------------------------------
        # IMPORT DATA
        # -------------------------------------------------

        with management_col3:

            if st.button(
                "📥 Import Company Data",
                key="m_mgmt_import",
                use_container_width=True,
            ):

                navigate_to(
                    "📥 Import Data"
                )

                st.rerun()


# =========================================================
# APPLICATION ROUTER
# =========================================================

current_page = st.session_state.get(
    "current_page",
    "main",
)


# =========================================================
# MAIN HOME ROUTE
# =========================================================

if current_page == "main":

    render_main_screen()

    st.stop()


# =========================================================
# STANDALONE SETUP PAGES
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
# SAFE BASELINE GUARD
# =========================================================

baseline = get_safe_baseline()


if baseline is None:

    st.warning(
        "🔒 NO LOCKED BASELINE FOUND."
    )

    st.info(
        "Please fill in the details on the Home Page "
        "and confirm the Baseline."
    )

    if st.button(
        "🏠 Back to Home"
    ):

        go_to_main()

        st.rerun()

    st.stop()


# =========================================================
# INDIVIDUAL DECISION LABS
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
# MANAGEMENT ROUTES
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
