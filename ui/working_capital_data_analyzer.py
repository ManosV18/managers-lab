from __future__ import annotations

from datetime import date

import pandas as pd
import streamlit as st

from tools.working_capital_analysis import (
    WorkingCapitalAnalysisResult,
    analyze_working_capital,
)


# =========================================================
# PAGE
# =========================================================

def render_working_capital_data_analyzer():
    st.header("📐 Working Capital Data Analyzer")

    st.caption(
        """
        Measure actual working-capital operating performance
        directly from transaction history.
        """
    )

    with st.expander(
        "💡 What does this tool do?",
        expanded=True,
    ):

        st.markdown(
            """
            This tool measures the company's actual operating cycle
            from transaction-level data.

            It does not change the company baseline and does not create
            a business decision.

            The measured AR Days, Inventory Days and AP Days can then
            be considered when building or reviewing the Baseline Snapshot.
            """
        )

    # =========================================================
    # ANALYSIS DATE
    # =========================================================

    reference_date = st.date_input(
        "Analysis Date",
        value=date.today(),
        help=(
            "Usually today or the relevant period-end date. "
            "Open invoices are measured up to this date."
        ),
    )

    ar_df = None
    ap_df = None
    inventory_df = None

    # =========================================================
    # AR
    # =========================================================

    st.divider()
    st.subheader("📊 Accounts Receivable")

    ar_col1, ar_col2 = st.columns(2)

    with ar_col1:

        st.download_button(
            "📥 Download AR Template",
            data=_ar_template(),
            file_name="ar_template.csv",
            mime="text/csv",
            use_container_width=True,
        )

    with ar_col2:

        ar_file = st.file_uploader(
            "Upload AR CSV",
            type=["csv"],
            key="wc_analyzer_ar_upload",
        )

    if ar_file is not None:

        try:

            candidate = pd.read_csv(ar_file)

            required = [
                "customer_id",
                "invoice_date",
                "payment_date",
                "amount",
            ]

            missing = [
                column
                for column in required
                if column not in candidate.columns
            ]

            if missing:

                st.error(
                    f"Missing columns: {missing}"
                )

            else:

                ar_df = candidate

                st.dataframe(
                    ar_df.head(),
                    use_container_width=True,
                )

                st.success(
                    "AR transaction data loaded."
                )

        except Exception as exc:

            st.error(
                f"Error reading AR file: {exc}"
            )

    # =========================================================
    # AP
    # =========================================================

    st.divider()
    st.subheader("🤝 Accounts Payable")

    ap_col1, ap_col2 = st.columns(2)

    with ap_col1:

        st.download_button(
            "📥 Download AP Template",
            data=_ap_template(),
            file_name="ap_template.csv",
            mime="text/csv",
            use_container_width=True,
        )

    with ap_col2:

        ap_file = st.file_uploader(
            "Upload AP CSV",
            type=["csv"],
            key="wc_analyzer_ap_upload",
        )

    if ap_file is not None:

        try:

            candidate = pd.read_csv(ap_file)

            required = [
                "supplier_id",
                "invoice_date",
                "payment_date",
                "amount",
            ]

            missing = [
                column
                for column in required
                if column not in candidate.columns
            ]

            if missing:

                st.error(
                    f"Missing columns: {missing}"
                )

            else:

                ap_df = candidate

                st.dataframe(
                    ap_df.head(),
                    use_container_width=True,
                )

                st.success(
                    "AP transaction data loaded."
                )

        except Exception as exc:

            st.error(
                f"Error reading AP file: {exc}"
            )

    # =========================================================
    # INVENTORY
    # =========================================================

    st.divider()
    st.subheader("📦 Inventory")

    inv_col1, inv_col2 = st.columns(2)

    with inv_col1:

        st.download_button(
            "📥 Download Inventory Template",
            data=_inventory_template(),
            file_name="inventory_template.csv",
            mime="text/csv",
            use_container_width=True,
        )

    with inv_col2:

        inventory_file = st.file_uploader(
            "Upload Inventory CSV",
            type=["csv"],
            key="wc_analyzer_inventory_upload",
        )

    if inventory_file is not None:

        try:

            candidate = pd.read_csv(
                inventory_file
            )

            required = [
                "item_id",
                "receipt_date",
                "sale_date",
                "quantity",
            ]

            missing = [
                column
                for column in required
                if column not in candidate.columns
            ]

            if missing:

                st.error(
                    f"Missing columns: {missing}"
                )

            else:

                inventory_df = candidate

                st.dataframe(
                    inventory_df.head(),
                    use_container_width=True,
                )

                st.success(
                    "Inventory transaction data loaded."
                )

        except Exception as exc:

            st.error(
                f"Error reading Inventory file: {exc}"
            )

    # =========================================================
    # ANALYZE
    # =========================================================

    if (
        ar_df is not None
        or ap_df is not None
        or inventory_df is not None
    ):

        st.divider()

        if st.button(
            "▶ Analyze Working Capital",
            type="primary",
            use_container_width=True,
        ):

            result = analyze_working_capital(
                ar_df=ar_df,
                ap_df=ap_df,
                inventory_df=inventory_df,
                reference_date=reference_date,
            )

            _render_results(result)


# =========================================================
# RESULTS
# =========================================================

def _render_results(
    result: WorkingCapitalAnalysisResult,
):

    st.subheader(
        "📊 Measured Operating Metrics"
    )

    c1, c2, c3, c4 = st.columns(4)

    c1.metric(
        "AR Days",
        _format_days(result.ar_days),
    )

    c2.metric(
        "Inventory Days",
        _format_days(result.inventory_days),
    )

    c3.metric(
        "AP Days",
        _format_days(result.ap_days),
    )

    c4.metric(
        "Cash Conversion Cycle",
        _format_days(
            result.cash_conversion_cycle
        ),
    )

    # =========================================================
    # CONCENTRATION
    # =========================================================

    if (
        result.top_customer_pct is not None
        or result.top_supplier_pct is not None
    ):

        st.divider()
        st.subheader(
            "🔎 Concentration Diagnostics"
        )

        c1, c2 = st.columns(2)

        with c1:

            if result.top_customer_pct is not None:

                st.metric(
                    "Top Customer Share",
                    f"{result.top_customer_pct:.1f}%",
                )

            if result.customer_hhi is not None:

                st.metric(
                    "Customer HHI",
                    f"{result.customer_hhi:,.0f}",
                )

        with c2:

            if result.top_supplier_pct is not None:

                st.metric(
                    "Top Supplier Share",
                    f"{result.top_supplier_pct:.1f}%",
                )

            if result.supplier_hhi is not None:

                st.metric(
                    "Supplier HHI",
                    f"{result.supplier_hhi:,.0f}",
                )

    # =========================================================
    # INTERPRETATION
    # =========================================================

    st.divider()

    st.info(
        """
        These figures are measured operating metrics derived from
        transaction data.

        They are not automatically written into the CompanyState.

        If you consider them representative of the company's normal
        operating position, use them when building or reviewing the
        Baseline Snapshot.
        """
    )


# =========================================================
# FORMATTING
# =========================================================

def _format_days(
    value,
) -> str:

    if value is None:

        return "—"

    return f"{value:.1f} days"


# =========================================================
# CSV TEMPLATES
# =========================================================

def _ar_template():

    return """customer_id,invoice_date,payment_date,amount
C001,2024-01-15,2024-03-20,12500
C002,2024-02-01,2024-03-15,8200
C003,2024-02-10,,5400
C004,2024-03-01,2024-04-10,15000
C005,2024-03-15,,3200
"""


def _ap_template():

    return """supplier_id,invoice_date,payment_date,amount
S001,2024-01-10,2024-02-08,9800
S002,2024-01-20,2024-02-25,4500
S003,2024-02-05,2024-03-10,12000
S004,2024-02-15,,6700
S005,2024-03-01,2024-04-01,8100
"""


def _inventory_template():

    return """item_id,receipt_date,sale_date,quantity
I001,2024-01-05,2024-02-20,120
I002,2024-01-12,2024-03-01,80
I003,2024-02-01,2024-03-15,60
I004,2024-02-10,,140
I005,2024-03-01,2024-04-05,45
"""
