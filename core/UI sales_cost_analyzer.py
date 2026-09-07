import pandas as pd
import streamlit as st

from core.sales_cost_analyzer import (
    DEFAULT_COST_FIELDS,
    calculate_sales_cost_summary,
)

LABELS = {
    "material_cost": "Product / Material Cost",
    "freight_cost": "Freight / Delivery",
    "packaging_cost": "Packaging",
    "sales_commission": "Sales Commissions",
    "other_variable_cost": "Other Variable Costs",
}

COLUMNS = [
    "date", "product", "quantity", "sales",
    "material_cost", "freight_cost", "packaging_cost",
    "sales_commission", "other_variable_cost",
]

def _fmt_eur(x):
    return f"€{x:,.2f}"

def render_sales_cost_analyzer():
    st.title("📊 Sales & Cost Analyzer")
    st.caption(
        "Turn actual sales data into the Price, Volume and "
        "Variable Cost inputs used by Managers Lab."
    )

    st.info(
        "Price is calculated from actual sales and units sold. "
        "Variable cost is calculated from the variable-cost "
        "components you provide."
    )

    st.subheader("Step 1 — Download Template")
    template = pd.DataFrame([{
        "date": "2026-01-31",
        "product": "Product A",
        "quantity": 100,
        "sales": 18000,
        "material_cost": 10500,
        "freight_cost": 500,
        "packaging_cost": 200,
        "sales_commission": 300,
        "other_variable_cost": 0,
    }], columns=COLUMNS)

    st.download_button(
        "📥 Download Sales & Cost Template",
        template.to_csv(index=False).encode("utf-8"),
        "managers_lab_sales_cost_template.csv",
        "text/csv",
        use_container_width=True,
        key="sales_cost_template_download",
    )

    st.divider()
    st.subheader("Step 2 — Upload Your Sales Data")
    uploaded = st.file_uploader(
        "Upload CSV",
        type=["csv"],
        key="sales_cost_analyzer_upload",
    )
    if uploaded is None:
        return

    try:
        df = pd.read_csv(uploaded)
    except Exception as exc:
        st.error(f"❌ Error reading file: {exc}")
        return

    df.columns = [str(c).strip().lower() for c in df.columns]

    missing = [c for c in ["quantity", "sales"] if c not in df.columns]
    if missing:
        st.error("❌ Missing required columns: " + ", ".join(missing))
        return

    for field in DEFAULT_COST_FIELDS:
        if field not in df.columns:
            df[field] = 0.0

    numeric_fields = ["quantity", "sales", *DEFAULT_COST_FIELDS]
    for field in numeric_fields:
        df[field] = pd.to_numeric(df[field], errors="coerce")

    if df[numeric_fields].isna().any().any():
        st.error("❌ Quantity, sales and cost fields must contain numeric values.")
        return

    if (df[numeric_fields] < 0).any().any():
        st.error("❌ Quantity, sales and cost fields cannot be negative.")
        return

    st.subheader("Step 3 — Review Data")
    st.dataframe(df, use_container_width=True, hide_index=True)

    try:
        summary = calculate_sales_cost_summary(df.to_dict("records"))
    except Exception as exc:
        st.error(f"❌ Could not calculate inputs: {exc}")
        return

    st.subheader("Calculated Operating Inputs")
    c1, c2, c3 = st.columns(3)
    c1.metric("Total Volume", f"{summary.total_volume:,.0f}")
    c2.metric("Total Sales", _fmt_eur(summary.total_sales))
    c3.metric("Weighted Average Price", _fmt_eur(summary.weighted_average_price))

    c1, c2, c3 = st.columns(3)
    c1.metric("Total Variable Cost", _fmt_eur(summary.total_variable_cost))
    c2.metric("Variable Cost / Unit", _fmt_eur(summary.variable_cost_per_unit))
    c3.metric("Gross Margin", f"{summary.gross_margin_pct:.1f}%")

    st.subheader("Variable Cost Breakdown")
    breakdown = []
    for field in DEFAULT_COST_FIELDS:
        total = float(df[field].sum())
        breakdown.append({
            "Cost Component": LABELS[field],
            "Total": _fmt_eur(total),
            "Per Unit": _fmt_eur(total / summary.total_volume),
        })
    st.dataframe(pd.DataFrame(breakdown), use_container_width=True, hide_index=True)

    st.caption(
        "Accounting COGS is not automatically treated as variable cost. "
        "Only the components identified here are used."
    )

    st.divider()
    st.subheader("Use These Values in Company Setup")
    st.write(
        "These values will populate the Baseline Snapshot for review. "
        "They do not lock the baseline automatically."
    )

    if st.button(
        "Use These Values in Company Setup →",
        type="primary",
        use_container_width=True,
        key="sales_cost_use_in_baseline",
    ):
        st.session_state["baseline_price"] = float(summary.weighted_average_price)
        st.session_state["baseline_volume"] = float(summary.total_volume)
        st.session_state["baseline_variable_cost"] = float(summary.variable_cost_per_unit)
        st.session_state["sales_cost_analysis"] = {
            "total_volume": summary.total_volume,
            "total_sales": summary.total_sales,
            "weighted_average_price": summary.weighted_average_price,
            "total_variable_cost": summary.total_variable_cost,
            "variable_cost_per_unit": summary.variable_cost_per_unit,
            "gross_profit": summary.gross_profit,
            "gross_margin_pct": summary.gross_margin_pct,
        }
        st.session_state["current_page"] = "🏢 Baseline Snapshot"
        st.rerun()
