import streamlit as st
import pandas as pd

# =========================================================
# FIELD TYPES
# =========================================================

FIELD_TYPES = {
    "price": float,
    "variable_cost": float,
    "volume": float,
    "fixed_cost": float,
    "fixed_assets": float,
    "depreciation": float,
    "target_profit_goal": float,
    "opening_cash": float,
    "equity": float,
    "total_debt": float,
    "annual_interest_only": float,
    "annual_debt_service": float,
    "tax_rate": float,
    "ar_days": float,
    "inv_days": float,
    "ap_days": float,
    "wacc": float,
    "cost_of_debt": float,
    # Reported Financial Results 
    "profit_before_tax": float, 
    "tax": float, 
    "net_profit": float,
}


# =========================================================
# NUMBER CLEANING
# =========================================================

def clean_financial_value(value):
    """
    Convert common European / US financial number formats
    into a Python-compatible numeric string.

    Examples:
        450,000.00 -> 450000.00
        450.000,00 -> 450000.00
        150,50      -> 150.50
        150.50      -> 150.50
    """

    if pd.isna(value):
        return "0"

    value_str = str(value).strip()

    value_str = (
        value_str
        .replace("$", "")
        .replace("€", "")
        .replace("£", "")
        .replace(" ", "")
    )

    if not value_str:
        return "0"

    # -----------------------------------------------------
    # Both "." and "," exist
    # -----------------------------------------------------

    if "," in value_str and "." in value_str:

        # European format:
        # 1.234,56
        if value_str.find(".") < value_str.find(","):

            value_str = (
                value_str
                .replace(".", "")
                .replace(",", ".")
            )

        # US format:
        # 1,234.56
        else:

            value_str = value_str.replace(",", "")

    # -----------------------------------------------------
    # Only comma
    # -----------------------------------------------------

    elif "," in value_str:

        parts = value_str.split(",")

        if len(parts) == 2 and len(parts[1]) != 3:

            # Decimal comma:
            # 150,50
            value_str = value_str.replace(",", ".")

        else:

            # Thousands separator:
            # 450,000
            value_str = value_str.replace(",", "")

    return value_str


# =========================================================
# PARSE IMPORT
# =========================================================

def parse_import_file(df):

    raw_data = {}
    errors = []

    for _, row in df.iterrows():

        field = str(
            row["field"]
        ).strip()

        # Ignore unknown fields
        if field not in FIELD_TYPES:
            continue

        raw_value = row["value"]

        try:

            cleaned = clean_financial_value(
                raw_value
            )

            value = FIELD_TYPES[field](
                float(cleaned)
            )

            raw_data[field] = value

        except Exception:

            errors.append(
                f"{field}: could not parse "
                f"'{raw_value}'"
            )

    return raw_data, errors


# =========================================================
# VALIDATION
# =========================================================

def validate_import_data(data):

    errors = []

    required_fields = [
        "price",
        "variable_cost",
        "volume",
        "fixed_cost",
        "fixed_assets",
        "depreciation",
        "target_profit_goal",
        "opening_cash",
        "equity",
        "total_debt",
        "annual_interest_only",
        "annual_debt_service",
        "tax_rate",
        "ar_days",
        "inv_days",
        "ap_days",
        "wacc",
        "cost_of_debt",
        # Reported Financial Results 
        "profit_before_tax", 
        "tax", 
        "net_profit",
    ]

    # -----------------------------------------------------
    # REQUIRED FIELDS
    # -----------------------------------------------------

    for field in required_fields:

        if field not in data:

            errors.append(
                f"Missing required field: {field}"
            )

    # -----------------------------------------------------
    # NON-NEGATIVE VALUES
    # -----------------------------------------------------

    non_negative_fields = [
        "price",
        "variable_cost",
        "volume",
        "fixed_cost",
        "fixed_assets",
        "depreciation",
        "target_profit_goal",
        "opening_cash",
        "equity",
        "total_debt",
        "annual_interest_only",
        "annual_debt_service",
        "ar_days",
        "inv_days",
        "ap_days",
    ]

    for field in non_negative_fields:

        if field in data:

            if data[field] < 0:

                errors.append(
                    f"{field} cannot be negative."
                )

    # -----------------------------------------------------
    # RATES
    # -----------------------------------------------------

    if "tax_rate" in data:

        if not 0 <= data["tax_rate"] <= 100:

            errors.append(
                "Tax rate must be between 0% and 100%."
            )

    if "wacc" in data:

        if not 0 <= data["wacc"] <= 100:

            errors.append(
                "WACC must be between 0% and 100%."
            )

    if "cost_of_debt" in data:

        if not 0 <= data["cost_of_debt"] <= 100:

            errors.append(
                "Cost of debt must be between 0% and 100%."
            )

    # -----------------------------------------------------
    # DEBT CONSISTENCY
    # -----------------------------------------------------

    if (
        "annual_interest_only" in data
        and "annual_debt_service" in data
    ):

        if (
            data["annual_debt_service"]
            < data["annual_interest_only"]
        ):

            errors.append(
                "Annual debt service cannot be lower "
                "than annual interest expense."
            )

    return errors


# =========================================================
# IMPORT → BASELINE BRIDGE
# =========================================================

def store_imported_baseline(
    raw_data,
    source_name,
    scenario_name,
):
    """
    Store imported data in session_state.

    IMPORTANT:

    This function DOES NOT create or save a CompanyState.

    Import Data is only responsible for importing and
    validating the data.

    Baseline Setup will read this data, allow the user
    to review it, and create the immutable CompanyState
    only when Lock Baseline is pressed.
    """

    # -----------------------------------------------------
    # Canonical imported payload
    # -----------------------------------------------------

    st.session_state[
        "imported_baseline_data"
    ] = dict(raw_data)

    # -----------------------------------------------------
    # Import metadata
    # -----------------------------------------------------

    st.session_state[
        "import_source"
    ] = source_name

    st.session_state[
        "scenario_name"
    ] = scenario_name

    # -----------------------------------------------------
    # Legacy flat keys
    #
    # These are kept because existing modules may still
    # read these keys.
    # -----------------------------------------------------

    for field, value in raw_data.items():

        st.session_state[field] = float(value)

    # -----------------------------------------------------
    # Baseline UI keys
    #
    # These make the values appear immediately in the
    # Baseline Company Snapshot.
    # -----------------------------------------------------

    st.session_state[
        "baseline_price"
    ] = float(
        raw_data["price"]
    )

    st.session_state[
        "baseline_variable_cost"
    ] = float(
        raw_data["variable_cost"]
    )

    st.session_state[
        "baseline_volume"
    ] = float(
        raw_data["volume"]
    )

    st.session_state[
        "baseline_fixed_opex"
    ] = float(
        raw_data["fixed_cost"]
    )

    st.session_state[
        "baseline_depreciation"
    ] = float(
        raw_data["depreciation"]
    )

    st.session_state[
        "baseline_total_debt"
    ] = float(
        raw_data["total_debt"]
    )

    st.session_state[
        "baseline_tax_rate"
    ] = float(
        raw_data["tax_rate"]
    )

    st.session_state[
        "baseline_wacc"
    ] = float(
        raw_data["wacc"]
    )

    st.session_state[
        "baseline_cost_of_debt"
    ] = float(
        raw_data["cost_of_debt"]
    )

    st.session_state[
        "baseline_ar_days"
    ] = float(
        raw_data["ar_days"]
    )

    st.session_state[
        "baseline_inventory_days"
    ] = float(
        raw_data["inv_days"]
    )

    st.session_state[
        "baseline_ap_days"
    ] = float(
        raw_data["ap_days"]
    )

    # -----------------------------------------------------
    # Baseline label
    # -----------------------------------------------------

    st.session_state[
        "baseline_label"
    ] = scenario_name


# =========================================================
# IMPORT VIEW
# =========================================================

def render_data_import():

    st.title(
        "📥 Import Baseline Data"
    )

    st.caption(
        "Import company data from CSV and prepare "
        "the Managers Lab Baseline."
    )

    st.info(
        "Imported data is first loaded into the Baseline "
        "Snapshot. Review the values there before locking "
        "the immutable CompanyState."
    )

    # =====================================================
    # STEP 1 — TEMPLATE
    # =====================================================

    st.subheader(
        "Step 1 — Download Template"
    )

    template_data = """field,value,description
price,150.00,Unit selling price
variable_cost,100.00,Variable cost per unit
volume,12000,Annual units sold
fixed_cost,450000.00,Annual fixed operating costs
fixed_assets,800000.00,Net fixed assets
depreciation,50000.00,Annual depreciation
target_profit_goal,200000.00,Target annual profit
opening_cash,150000.00,Opening cash balance
equity,500000.00,Total equity
total_debt,500000.00,Total debt
annual_interest_only,25000.00,Annual interest expense
annual_debt_service,70000.00,Annual debt service
tax_rate,22.00,Corporate tax rate in %
wacc,8.00,Baseline WACC in %
cost_of_debt,6.00,Cost of debt in %
ar_days,90,Accounts receivable days
inv_days,75,Inventory days
ap_days,45,Accounts payable days
profit_before_tax,150000.00, Reported Profit Before Tax 
tax,33000.00, Reported Tax 
net_profit,117000.00,Reported Net Profit
"""

    st.download_button(
        label="📥 Download CSV Template",
        data=template_data,
        file_name=(
            "managers_lab_baseline_template.csv"
        ),
        mime="text/csv",
        use_container_width=True,
        key="baseline_template_download",
    )

    st.divider()

    # =====================================================
    # STEP 2 — UPLOAD
    # =====================================================

    st.subheader(
        "Step 2 — Upload Completed File"
    )

    uploaded = st.file_uploader(
        "Upload CSV",
        type=["csv"],
        key="baseline_import_upload",
    )

    if uploaded is None:
        return

    # =====================================================
    # READ CSV
    # =====================================================

    try:

        df = pd.read_csv(uploaded)

    except Exception as exc:

        st.error(
            f"❌ Error reading file: {exc}"
        )

        return

    # =====================================================
    # STRUCTURE VALIDATION
    # =====================================================

    if (
        "field" not in df.columns
        or "value" not in df.columns
    ):

        st.error(
            "❌ The CSV must contain "
            "'field' and 'value' columns."
        )

        return

    # =====================================================
    # PREVIEW
    # =====================================================

    st.subheader(
        "Preview"
    )

    st.dataframe(
        df[
            [
                "field",
                "value",
            ]
        ],
        use_container_width=True,
        hide_index=True,
    )

    # =====================================================
    # PARSE
    # =====================================================

    raw_data, parse_errors = (
        parse_import_file(df)
    )

    # =====================================================
    # PARSE ERRORS
    # =====================================================

    if parse_errors:

        st.warning(
            "⚠️ Some values could not be parsed:"
        )

        for error in parse_errors:

            st.write(
                f"- {error}"
            )

    # =====================================================
    # IMPORT SUMMARY
    # =====================================================

    st.subheader(
        "Import Summary"
    )

    c1, c2 = st.columns(2)

    c1.metric(
        "Fields Imported",
        len(raw_data),
    )

    c2.metric(
        "Parsing Errors",
        len(parse_errors),
    )

    # =====================================================
    # CREATE / PREPARE BASELINE
    # =====================================================

    st.divider()

    st.subheader(
        "📥 Prepare Imported Baseline"
    )

    label = st.text_input(
        "Company / Scenario Label",
        value="Imported Baseline",
        key="import_baseline_label",
    )

    if not st.button(
        "📥 Load Data into Baseline",
        type="primary",
        use_container_width=True,
        key="load_imported_baseline",
    ):

        return

    # =====================================================
    # VALIDATE
    # =====================================================

    validation_errors = (
        validate_import_data(
            raw_data
        )
    )

    if parse_errors:

        validation_errors.extend(
            parse_errors
        )

    if validation_errors:

        st.error(
            "❌ Imported data cannot be loaded "
            "into the Baseline."
        )

        for error in validation_errors:

            st.write(
                f"- {error}"
            )

        return

    # =====================================================
    # STORE IMPORTED DATA
    # =====================================================

    try:

        store_imported_baseline(
            raw_data=raw_data,
            source_name=uploaded.name,
            scenario_name=label.strip(),
        )

    except Exception as exc:

        st.error(
            "❌ Could not transfer imported data "
            f"to Baseline: {exc}"
        )

        return

    # =====================================================
    # SUCCESS
    # =====================================================

    st.success(
        "✅ Imported data successfully loaded "
        "into the Baseline Snapshot."
    )

    st.info(
        "➡️ Go to **Baseline Company Snapshot**. "
        "The imported values are now loaded there. "
        "Review them and press **Lock Baseline**."
    )

    # =====================================================
    # IMPORTED DATA CONFIRMATION
    # =====================================================

    st.subheader(
        "🔎 Imported Baseline Confirmation"
    )

    confirmation_rows = [
        {
            "Field": "Price",
            "Value": (
                f"€ {raw_data['price']:,.2f}"
            ),
        },
        {
            "Field": "Variable Cost / Unit",
            "Value": (
                f"€ {raw_data['variable_cost']:,.2f}"
            ),
        },
        {
            "Field": "Volume",
            "Value": (
                f"{raw_data['volume']:,.0f}"
            ),
        },
        {
            "Field": "Fixed Costs",
            "Value": (
                f"€ {raw_data['fixed_cost']:,.0f}"
            ),
        },
        {
            "Field": "Depreciation",
            "Value": (
                f"€ {raw_data['depreciation']:,.0f}"
            ),
        },
        {
            "Field": "Equity",
            "Value": (
                f"€ {raw_data['equity']:,.0f}"
            ),
        },
        {
            "Field": "Total Debt",
            "Value": (
                f"€ {raw_data['total_debt']:,.0f}"
            ),
        },
        {
            "Field": "WACC",
            "Value": (
                f"{raw_data['wacc']:.2f}%"
            ),
        },
        {
            "Field": "Cost of Debt",
            "Value": (
                f"{raw_data['cost_of_debt']:.2f}%"
            ),
        },
        {
            "Field": "Tax Rate",
            "Value": (
                f"{raw_data['tax_rate']:.2f}%"
            ),
        },
        {
            "Field": "AR Days",
            "Value": (
                f"{raw_data['ar_days']:.0f}"
            ),
        },
        {
            "Field": "Inventory Days",
            "Value": (
                f"{raw_data['inv_days']:.0f}"
            ),
        },
        {
            "Field": "AP Days",
            "Value": (
                f"{raw_data['ap_days']:.0f}"
            ),
        },
        {
            "Field": "Profit Before Tax (EBT)",
            "Value": (
                f"€ {raw_data['profit_before_tax']:,.0f}"
            ),
        },
        {
            "Field": "Tax",
            "Value": (
                f"€ {raw_data['tax']:,.0f}"
            ),
        },
        {
            "Field": "Net Profit",
            "Value": (
                f"€ {raw_data['net_profit']:,.0f}"
            ),
        },
    ]
    
   
    st.dataframe(
        confirmation_rows,
        use_container_width=True,
        hide_index=True,
    )
