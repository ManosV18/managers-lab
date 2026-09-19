import streamlit as st

from core.baseline_repository import BaselineRepository
from core.decision_plan import DecisionPlan
from core.state_builder import StateBuilder
from ui.baseline import render_baseline_setup

# =========================================================
# REPOSITORY & BUILDER INITIALIZATION
# =========================================================

baseline_repo = BaselineRepository()
state_builder = StateBuilder(baseline_repository=baseline_repo)


# =========================================================
# HELPER FUNCTIONS & BASELINE GUARANTEES
# =========================================================

def get_safe_baseline():
    """
    Return the real locked baseline when available.
    Otherwise return the Demo Company as a temporary
    starting point without saving it as the user's baseline.
    """
    try:
        return state_builder.build_baseline_only()
    except Exception:
        return state_builder.build_default_baseline()


def has_locked_baseline() -> bool:
    """
    True only when the user has actually locked
    a baseline in BaselineRepository.
    """
    return BaselineRepository.exists()


def navigate_to(page_name: str) -> None:
    st.session_state.current_page = page_name


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
# SIDEBAR RENDER
# =========================================================

def render_sidebar() -> None:
    st.sidebar.title("Managers Lab")
    
    st.sidebar.markdown("### 🏢 Your Company")
    
    if has_locked_baseline():
        st.sidebar.success("🔒 Baseline locked")
        baseline = get_safe_baseline()
        st.sidebar.caption(
            f"Version {getattr(baseline, 'version', 1)}"
        )
        if st.sidebar.button(
            "View Company →",
            key="sidebar_company",
            use_container_width=True,
        ):
            navigate_to("🏢 Baseline Snapshot")
            st.rerun()
    else:
        st.sidebar.info("🧪 Demo Company active")
        if st.sidebar.button(
            "Set Up Your Company →",
            key="sidebar_setup_company",
            use_container_width=True,
        ):
            navigate_to("🏢 Company Setup")
            st.rerun()

    st.sidebar.divider()
    
    # Navigation choices
    pages = [
        "🏢 Company Setup",
        "🏢 Baseline Snapshot",
        "📊 Volume Lab",
        "🏷️ Pricing Lab",
        "💧 Cash Fragility",
        "🗼 Control Tower",
    ]
    
    selected_page = st.sidebar.radio(
        "Navigation",
        pages,
        index=pages.index(st.session_state.current_page) if st.session_state.current_page in pages else 0,
    )
    
    if selected_page != st.session_state.current_page:
        navigate_to(selected_page)
        st.rerun()


# =========================================================
# COMPANY SETUP PAGE RENDER
# =========================================================

def render_company_setup_page() -> None:
    st.title("🏢 Company Setup")

    # =====================================================
    # EXISTING USER BASELINE
    # =====================================================
    if has_locked_baseline():
        st.success("🔒 Your company baseline is locked.")
        st.markdown("### Review your company")
        st.caption(
            "Review the current values and replace the "
            "baseline if you want to work with updated company data."
        )
        st.divider()
        render_baseline_setup()
        return

    # =====================================================
    # DEMO COMPANY
    # =====================================================
    st.info("🧪 You are currently exploring the Managers Lab Demo Company.")
    st.caption(
        "You can use the demo company to explore the tools "
        "without entering any data. When you are ready, "
        "replace it with your own company data."
    )
    st.divider()

    # Two options for setup when no locked baseline exists
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### Enter Manually")
        st.caption("Build your baseline driver by driver.")
        if st.button("Start Manual Setup", key="setup_manual", use_container_width=True):
            st.session_state.show_manual_setup = True

    with col2:
        st.markdown("#### Import Data")
        st.caption("Upload financial statement inputs directly.")
        if st.button("Import Company Data", key="setup_import", use_container_width=True):
            st.session_state.show_import_setup = True

    if st.session_state.get("show_manual_setup", False):
        st.divider()
        render_baseline_setup()


# =========================================================
# MAIN ROUTER
# =========================================================

def main() -> None:
    render_sidebar()
    
    current_page = st.session_state.current_page

    # BASELINE GUARD (Will fallback automatically to Demo Company via get_safe_baseline)
    baseline = get_safe_baseline()
    if baseline is None:
        st.warning("🔒 No company baseline found.")
        st.info("Please complete company setup to continue.")
        if st.button("Go to Setup"):
            navigate_to("🏢 Company Setup")
            st.rerun()
        return

    if current_page == "🏢 Company Setup":
        render_company_setup_page()
    elif current_page == "🏢 Baseline Snapshot":
        st.title("🏢 Baseline Snapshot")
        st.json(baseline.model_dump() if hasattr(baseline, "model_dump") else str(baseline))
    elif current_page == "📊 Volume Lab":
        st.title("📊 Volume Lab")
        st.write(f"Working with company: **{baseline.label}**")
    elif current_page == "🏷️ Pricing Lab":
        st.title("🏷️ Pricing Lab")
        st.write(f"Working with company: **{baseline.label}**")
    elif current_page == "💧 Cash Fragility":
        st.title("💧 Cash Fragility")
        st.write(f"Working with company: **{baseline.label}**")
    elif current_page == "🗼 Control Tower":
        st.title("🗼 Control Tower")
        st.write(f"Working with company: **{baseline.label}**")


if __name__ == "__main__":
    main()
