import streamlit as st
from typing import Dict, Any

from core.models import CompanyState


# =========================================================
# CONTROL TOWER
# =========================================================

def render_control_tower_dashboard(
    report_data: Dict[str, Any],
) -> None:
    """
    Render the Control Tower.

    New architecture:

        Locked Baseline
              ↓
        Decision Plan
              ↓
        DecisionRunner
              ↓
       Projected State
              ↓
      Financial Impact
              ↓
        Control Tower

    This module is PRESENTATION ONLY.

    It does NOT:
        - execute decisions
        - manage scenarios
        - resolve scenario conflicts
        - calculate financial metrics
        - modify CompanyState
    """

    st.title("🎛️ Control Tower")

    if not report_data:
        st.warning("No report data available.")
        return

    # =====================================================
    # COMPANY STATE
    # =====================================================

    baseline = report_data.get("baseline")
    projected = report_data.get("projected")

    if isinstance(baseline, CompanyState):

        st.subheader("🏢 Company State")

        c1, c2, c3 = st.columns(3)

        c1.metric(
            "Baseline Version",
            baseline.version,
        )

        c2.metric(
            "Baseline",
            baseline.label,
        )

        if isinstance(projected, CompanyState):

            c3.metric(
                "Projected Version",
                projected.version,
            )

        else:

            c3.metric(
                "Projected Version",
                "—",
            )

    else:

        st.warning(
            "No locked baseline CompanyState available."
        )

    st.divider()

    # =====================================================
    # DECISION PLAN
    # =====================================================

    plan = report_data.get("plan")
    decisions = report_data.get("decisions", [])

    if plan:

        st.subheader("🎯 Decision Plan")

        st.write(
            f"**{plan.get('name', 'Unnamed Plan')}**"
        )

        st.caption(
            f"{plan.get('decision_count', len(decisions))} "
            "decision(s) evaluated together against the locked baseline."
        )

        if decisions:

            st.dataframe(
                [
                    {
                        "Decision": decision.get("name"),
                        "Category": decision.get("category"),
                        "Description": decision.get("description"),
                    }
                    for decision in decisions
                ],
                use_container_width=True,
                hide_index=True,
            )

    else:

        st.info(
            "No Decision Plan selected. "
            "Control Tower is showing the locked baseline."
        )

    st.divider()

    # =====================================================
    # STATE COMPARISON
    # =====================================================

    comparison = report_data.get(
        "comparison"
    )

    if comparison:

        st.subheader("📊 Baseline vs Projected")

        drivers_changed = comparison.get(
            "drivers_changed",
            {},
        )

        if drivers_changed:

            rows = []

            for driver, values in (
                drivers_changed.items()
            ):

                if (
                    not isinstance(values, tuple)
                    or len(values) != 2
                ):
                    continue

                baseline_value = values[0]
                projected_value = values[1]

                rows.append(
                    {
                        "Driver": driver,
                        "Baseline": baseline_value,
                        "Projected": projected_value,
                        "Delta": (
                            projected_value
                            - baseline_value
                        ),
                    }
                )

            if rows:

                st.dataframe(
                    rows,
                    use_container_width=True,
                    hide_index=True,
                )

    # =====================================================
    # EXECUTION TRACE
    # =====================================================

    execution = report_data.get(
        "execution"
    )

    if execution:

        with st.expander(
            "🔍 Decision Execution Trace",
            expanded=False,
        ):

            st.json(
                execution
            )

    # =====================================================
    # FINANCIAL IMPACT
    # =====================================================

    financial_impact = report_data.get(
        "financial_impact"
    )

    if financial_impact:

        st.subheader("💰 Financial Impact")

        if isinstance(
            financial_impact,
            dict,
        ):

            rows = []

            for key, value in (
                financial_impact.items()
            ):

                rows.append(
                    {
                        "Metric": key,
                        "Value": value,
                    }
                )

            st.dataframe(
                rows,
                use_container_width=True,
                hide_index=True,
            )

        else:

            st.write(
                financial_impact
            )
