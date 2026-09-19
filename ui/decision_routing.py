# ui/decision_routing.py

import streamlit as st

from core.decision_router import DecisionRouter


def render_decision_routing(
    diagnostic_name: str,
    diagnostic_result: dict,
) -> None:
    """
    Render relevant Decision Labs identified by a diagnostic.

    This module only presents routing options.

    It does NOT:
        - create Decisions
        - modify the DecisionPlan
        - execute Decisions
        - modify CompanyState
        - calculate diagnostics
    """

    if not isinstance(diagnostic_result, dict):
        return

    routes = []

    if diagnostic_name == "cash_fragility":
        routes = DecisionRouter.routes_for_cash_fragility(
            diagnostic_result
        )

    if not routes:
        return

    st.divider()

    st.subheader("What can you test next?")

    st.caption(
        "This diagnostic identifies conditions that may be affected "
        "by different management decisions. Choose a decision area "
        "to test its possible impact."
    )

    for route in routes:

        st.markdown(
            f"### {route['label']}"
        )

        st.write(
            route["description"]
        )

        if st.button(
            f"Open {route['decision_area']} Lab",
            key=f"decision_route_{diagnostic_name}_{route['driver']}",
            use_container_width=True,
        ):
            st.session_state.current_page = route["page"]
            st.rerun()
