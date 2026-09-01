import streamlit as st

from diagnostics.cash_fragility import (
    calculate_cash_fragility,
)


def _render_status(result):

    status = str(
        result.get(
            "status",
            "Unknown",
        )
    )

    if status == "Healthy":

        st.success(
            f"🟢 Liquidity Status: {status}"
        )

    elif status in (
        "Watch",
        "Moderate",
        "Fragile",
    ):

        st.warning(
            f"🟡 Liquidity Status: {status}"
        )

    elif status in (
        "Critical",
        "Danger",
        "Severe",
    ):

        st.error(
            f"🔴 Liquidity Status: {status}"
        )

    else:

        st.info(
            f"⚪ Liquidity Status: {status}"
        )


def render_cash_fragility_lab(
    baseline_state,
    projected_state,
    financial_projection,
):

    st.header(
        "🩺 Cash Fragility Diagnostic"
    )

    st.info(
        """
        This is a diagnostic view of the company's
        financial health.

        It does not create or execute decisions.
        It reads the baseline and projected CompanyState
        and translates the financial projection into
        liquidity diagnostics.
        """
    )

    # =====================================================
    # DIAGNOSTIC
    # =====================================================

    result = calculate_cash_fragility(
        baseline_state=baseline_state,
        projected_state=projected_state,
        financial_projection=financial_projection,
    )

    # =====================================================
    # STATUS
    # =====================================================

    st.subheader("Liquidity Health")

    _render_status(result)

    # =====================================================
    # CORE METRICS
    # =====================================================

    c1, c2, c3, c4 = st.columns(4)

    cash_on_hand = result.get(
        "cash_on_hand",
        0.0,
    )

    daily_cash_req = result.get(
        "daily_cash_req",
        result.get(
            "daily_op_cost_req",
            0.0,
        ),
    )

    cash_runway = result.get(
        "cash_runway",
        0.0,
    )

    ccc_days = result.get(
        "ccc_days",
        0.0,
    )

    c1.metric(
        "Cash on Hand",
        f"€{cash_on_hand:,.0f}",
    )

    c2.metric(
        "Daily Cash Requirement",
        f"€{daily_cash_req:,.0f}",
    )

    c3.metric(
        "Cash Runway",
        f"{cash_runway:.1f} days",
    )

    c4.metric(
        "Cash Conversion Cycle",
        f"{ccc_days:.1f} days",
    )

    # =====================================================
    # WORKING CAPITAL CASH IMPACT
    # =====================================================

    st.divider()

    st.subheader(
        "💶 Working Capital Cash Impact"
    )

    wc_impact = result.get(
        "wc_cash_impact",
        0.0,
    )

    baseline_cash = result.get(
        "baseline_cash",
        0.0,
    )

    projected_cash = result.get(
        "projected_cash",
        cash_on_hand,
    )

    w1, w2, w3 = st.columns(3)

    w1.metric(
        "Baseline Cash",
        f"€{baseline_cash:,.0f}",
    )

    w2.metric(
        "Projected Cash",
        f"€{projected_cash:,.0f}",
    )

    w3.metric(
        "Cash Released / (Absorbed)",
        f"€{wc_impact:,.0f}",
    )

    # =====================================================
    # LIQUIDITY FRAGILITY
    # =====================================================

    st.divider()

    st.subheader(
        "Liquidity Fragility"
    )

    f1, f2 = st.columns(2)

    fragility_score = result.get(
        "fragility_score",
        0.0,
    )

    runway_after_cycle = result.get(
        "runway_after_cycle",
        0.0,
    )

    f1.metric(
        "Fragility Score",
        f"{fragility_score:.2f}",
    )

    f2.metric(
        "Runway After CCC",
        f"{runway_after_cycle:.1f} days",
    )

    # =====================================================
    # INTERPRETATION
    # =====================================================

    st.divider()

    st.subheader(
        "🧭 Diagnostic Interpretation"
    )

    interpretation = result.get(
        "interpretation",
        "No diagnostic interpretation is available.",
    )

    status_lower = str(
        result.get(
            "status",
            "",
        )
    ).lower()

    if status_lower == "healthy":

        st.success(
            interpretation
        )

    elif status_lower in (
        "critical",
        "danger",
        "severe",
    ):

        st.error(
            interpretation
        )

    else:

        st.warning(
            interpretation
        )

    # =====================================================
    # CHANGE VS BASELINE
    # =====================================================

    if projected_state is not None:

        baseline_result = calculate_cash_fragility(
            baseline_state=baseline_state,
        )

        runway_delta = (
            cash_runway
            - baseline_result.get(
                "cash_runway",
                0.0,
            )
        )

        ccc_delta = (
            ccc_days
            - baseline_result.get(
                "ccc_days",
                0.0,
            )
        )

        st.markdown(
            "#### Change vs Locked Baseline"
        )

        if (
            ccc_delta < 0
            or runway_delta > 0
            or wc_impact > 0
        ):

            st.success(
                "🟢 Liquidity position improved "
                "versus the locked baseline."
            )

        elif (
            ccc_delta > 0
            or runway_delta < 0
            or wc_impact < 0
        ):

            st.error(
                "🔴 Liquidity position deteriorated "
                "versus the locked baseline."
            )

        else:

            st.info(
                "🟡 Liquidity position is broadly "
                "unchanged versus the locked baseline."
            )

        if abs(ccc_delta) > 0.01:

            st.write(
                f"Cash Conversion Cycle changed by "
                f"{ccc_delta:+.1f} days."
            )

        if abs(wc_impact) > 0.01:

            if wc_impact > 0:

                st.write(
                    f"Working-capital changes released "
                    f"€{wc_impact:,.0f} of cash."
                )

            else:

                st.write(
                    f"Working-capital changes absorbed "
                    f"€{abs(wc_impact):,.0f} of cash."
                )

    # =====================================================
    # DIAGNOSTIC INPUTS
    # =====================================================

    with st.expander(
        "🔍 Diagnostic Inputs"
    ):

        st.write(
            {
                "Baseline AR Days":
                    baseline_state.working_capital.ar_days,

                "Projected AR Days":
                    projected_state.working_capital.ar_days,

                "Baseline Inventory Days":
                    baseline_state.working_capital.inventory_days,

                "Projected Inventory Days":
                    projected_state.working_capital.inventory_days,

                "Baseline AP Days":
                    baseline_state.working_capital.ap_days,

                "Projected AP Days":
                    projected_state.working_capital.ap_days,

                "Baseline Cash":
                    baseline_cash,

                "Projected Cash":
                    projected_cash,

                "WC Cash Impact":
                    wc_impact,

                "FCFE Delta":
                    result.get(
                        "fcfe_delta",
                        0.0,
                    ),
            }
        )
