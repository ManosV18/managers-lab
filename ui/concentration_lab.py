"""
ui/concentration_lab.py

Concentration Risk Diagnostic UI.

Presentation layer for:
    core.diagnostics.concentration

Architecture:
    UI
     ↓
    diagnose_concentration()
     ↓
    ConcentrationDiagnosticResult

The UI does not calculate financial or concentration metrics itself.
"""

from typing import Any, Optional
import pandas as pd
import streamlit as st

from diagnostics.concentration import (
    diagnose_concentration,
)


# =========================================================
# HELPERS
# =========================================================

def _format_pct(value: float) -> str:
    """Format decimal percentage as a human-readable percentage."""
    return f"{value * 100:.1f}%"


def _format_number(value: float) -> str:
    """Format numeric value."""
    return f"{value:,.0f}"


# =========================================================
# MAIN RENDER FUNCTION
# =========================================================

def render_concentration_lab(
    baseline_state: Optional[Any] = None,
    **kwargs: Any,
) -> None:
    """
    Render the Concentration Risk Diagnostic.

    The lab is intentionally independent from CompanyState
    because concentration is based on an external dataset
    such as customers, buyers, suppliers, or investors.
    
    Accepts baseline_state and **kwargs to maintain compatibility
    with main.py call patterns across labs.
    """

    st.markdown("## 🔎 Concentration Risk Diagnostic")

    st.caption(
        "Identify whether a small number of customers, buyers, "
        "or relationships create material concentration risk."
    )

    # =====================================================
    # INPUT
    # =====================================================

    st.markdown("### 1. Enter Concentration Data")

    st.caption(
        "Enter one value per line. For example, customer revenue "
        "or transaction value."
    )

    input_mode = st.radio(
        "Input method",
        [
            "Paste values",
            "Enter table",
        ],
        horizontal=True,
        key="concentration_input_mode",
    )

    df = pd.DataFrame(columns=["Name", "Value"])

    # =====================================================
    # PASTE VALUES
    # =====================================================

    if input_mode == "Paste values":

        text_input = st.text_area(
            "Values",
            placeholder=(
                "120000\n"
                "85000\n"
                "45000\n"
                "30000\n"
                "15000"
            ),
            height=180,
            key="concentration_raw_values",
        )

        if text_input.strip():

            lines = (
                text_input
                .strip()
                .splitlines()
            )

            values = []

            for i, line in enumerate(lines):

                cleaned = (
                    line
                    .replace("$", "")
                    .replace("€", "")
                    .replace(",", "")
                    .strip()
                )

                try:
                    value = float(cleaned)

                    if value > 0:
                        values.append(
                            {
                                "Name": f"Item {i + 1}",
                                "Value": value,
                            }
                        )

                except ValueError:
                    continue

            if values:
                df = pd.DataFrame(values)

    # =====================================================
    # TABLE INPUT
    # =====================================================

    else:

        default_data = pd.DataFrame(
            {
                "Name": [
                    "Customer 1",
                    "Customer 2",
                    "Customer 3",
                ],
                "Value": [
                    120000.0,
                    80000.0,
                    50000.0,
                ],
            }
        )

        edited_df = st.data_editor(
            default_data,
            num_rows="dynamic",
            use_container_width=True,
            key="concentration_data_editor",
            column_config={
                "Name": st.column_config.TextColumn(
                    "Name",
                    required=True,
                ),
                "Value": st.column_config.NumberColumn(
                    "Value",
                    min_value=0.0,
                    format="%.0f",
                ),
            },
        )

        if edited_df is not None:
            df = edited_df.copy()

    # =====================================================
    # QUALITATIVE PROTECTION
    # =====================================================

    st.markdown("### 2. Relationship Protection")

    st.caption(
        "These factors help determine whether concentration "
        "is defensible or creates additional diligence risk."
    )

    protection_col1, protection_col2, protection_col3 = st.columns(3)

    with protection_col1:

        contractual_lock_in = st.checkbox(
            "📄 Contractual lock-in",
            value=False,
            key="concentration_contractual_lock_in",
            help=(
                "Is the relationship protected by a meaningful "
                "contract or long-term agreement?"
            ),
        )

    with protection_col2:

        team_owned = st.checkbox(
            "👥 Team-owned relationship",
            value=False,
            key="concentration_team_owned",
            help=(
                "Is the relationship owned by the organization "
                "rather than depending primarily on one individual?"
            ),
        )

    with protection_col3:

        high_switching_cost = st.checkbox(
            "🔒 High switching costs",
            value=False,
            key="concentration_high_switching_cost",
            help=(
                "Would it be difficult or costly for the customer "
                "or buyer to switch to an alternative?"
            ),
        )

    # =====================================================
    # DATA PREVIEW
    # =====================================================

    if df.empty:

        st.info(
            "Enter at least one positive value to run the diagnostic."
        )

        return

    df = df.copy()

    df["Value"] = pd.to_numeric(
        df["Value"],
        errors="coerce",
    )

    df = df.dropna(subset=["Value"])

    df = df[df["Value"] > 0]

    if df.empty:

        st.info(
            "No valid positive values were found."
        )

        return

    # =====================================================
    # RUN DIAGNOSTIC
    # =====================================================

    try:

        result = diagnose_concentration(
            df,
            contractual_lock_in=contractual_lock_in,
            team_owned=team_owned,
            high_switching_cost=high_switching_cost,
        )

    except (TypeError, ValueError) as exc:

        st.error(
            f"Unable to run diagnostic: {exc}"
        )

        return

    metrics = result.metrics
    dependency = result.customer_dependency
    buyer_risk = result.buyer_risk

    # =====================================================
    # EXECUTIVE RESULT
    # =====================================================

    st.divider()

    st.markdown("### 3. Concentration Assessment")

    if metrics.risk_level == "low":

        st.success(f"🟢 {metrics.status}")

    elif metrics.risk_level == "moderate":

        st.warning(f"🟠 {metrics.status}")

    elif metrics.risk_level == "high":

        st.error(f"🔴 {metrics.status}")

    else:

        st.info(metrics.status)

    # =====================================================
    # KPI ROW
    # =====================================================

    kpi1, kpi2, kpi3, kpi4 = st.columns(4)

    with kpi1:

        st.metric(
            "HHI",
            f"{metrics.hhi:,.0f}",
        )

    with kpi2:

        st.metric(
            "Gini",
            f"{metrics.gini:.2f}",
        )

    with kpi3:

        st.metric(
            "Largest Item",
            _format_pct(metrics.top_item_pct),
        )

    with kpi4:

        st.metric(
            "Items → 80%",
            f"{metrics.pareto_count} ({metrics.pareto_items_pct:.1f}%)",
        )

    # =====================================================
    # TOP EXPOSURE
    # =====================================================

    st.markdown("### Largest Exposure")

    exposure_col1, exposure_col2 = st.columns(2)

    with exposure_col1:

        st.metric(
            "Largest Item",
            metrics.top_item_name,
        )

    with exposure_col2:

        st.metric(
            "Largest Item Value",
            _format_number(metrics.total_value * metrics.top_item_pct),
        )

    # =====================================================
    # CUSTOMER DEPENDENCY
    # =====================================================

    st.markdown("### Customer / Buyer Dependency")

    if dependency.material_concentration:

        st.warning(
            f"⚠️ Material concentration: "
            f"the largest item represents "
            f"{_format_pct(dependency.top_customer_pct)} "
            f"of total value."
        )

    else:

        st.success(
            f"🟢 No material single-item concentration: "
            f"largest item represents only "
            f"{_format_pct(dependency.top_customer_pct)}."
        )

    # =====================================================
    # BUYER RISK
    # =====================================================

    st.markdown("### Buyer / Relationship Risk")

    buyer_col1, buyer_col2 = st.columns(2)

    with buyer_col1:

        if buyer_risk.risk_level == "low":

            st.success(buyer_risk.status)

        elif buyer_risk.risk_level == "moderate":

            st.warning(buyer_risk.status)

        else:

            st.error(buyer_risk.status)

    with buyer_col2:

        st.metric(
            "Risk Score",
            f"{buyer_risk.score} / 3",
        )

    # =====================================================
    # DATA TABLE
    # =====================================================

    st.markdown("### Concentration Distribution")

    display_df = (
        df.copy()
        .sort_values(
            by="Value",
            ascending=False,
        )
        .reset_index(drop=True)
    )

    total_value = display_df["Value"].sum()

    display_df["Share"] = display_df["Value"] / total_value

    display_df["Cumulative Share"] = display_df["Share"].cumsum()

    display_df["Share"] = display_df["Share"].map(
        lambda x: f"{x * 100:.1f}%"
    )

    display_df["Cumulative Share"] = display_df["Cumulative Share"].map(
        lambda x: f"{x * 100:.1f}%"
    )

    display_df["Value"] = display_df["Value"].map(
        lambda x: f"{x:,.0f}"
    )

    display_df.index = display_df.index + 1

    st.dataframe(
        display_df,
        use_container_width=True,
        column_config={
            "Name": "Name",
            "Value": "Value",
            "Share": "Share",
            "Cumulative Share": "Cumulative Share",
        },
    )

    # =====================================================
    # INTERPRETATION
    # =====================================================

    st.markdown("### Management Interpretation")

    if metrics.risk_level == "high":

        st.error(
            "The business is materially concentrated. "
            "A relatively small number of relationships account "
            "for a large proportion of value. Management should "
            "consider diversification, retention protection, "
            "and contingency planning."
        )

    elif metrics.risk_level == "moderate":

        st.warning(
            "The business has meaningful concentration exposure. "
            "This may be acceptable if the relationship is durable "
            "and well protected, but it should be monitored."
        )

    elif metrics.risk_level == "low":

        st.success(
            "The value base is relatively diversified. "
            "Concentration is not currently a major exposure "
            "based on the supplied dataset."
        )

    else:

        st.info(
            "There is insufficient data to assess concentration."
        )

    # =====================================================
    # FOOTNOTE
    # =====================================================

    st.caption(
        "HHI uses the standard 0–10,000 concentration scale. "
        "The 25% threshold is used as a practical single-item "
        "concentration flag; it is not a universal regulatory threshold."
    )
